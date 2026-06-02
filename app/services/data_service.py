from pathlib import Path
from typing import Iterable

import pandas as pd


STANDARD_COLUMNS = ["country", "product", "type", "year", "yield", "unit", "source_file"]


class DataService:
    """Loads and normalizes CSV/Excel files into one predictable table."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self._data: pd.DataFrame | None = None

    def get_data(self) -> pd.DataFrame:
        if self._data is None:
            self._data = self._load_all_files()
        return self._data.copy()

    def reload(self) -> pd.DataFrame:
        self._data = self._load_all_files()
        return self.get_data()

    def _load_all_files(self) -> pd.DataFrame:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        files = list(self._iter_data_files())
        frames = [self._read_file(path) for path in files]
        frames = [frame for frame in frames if frame is not None and not frame.empty]

        if not frames:
            return pd.DataFrame(columns=STANDARD_COLUMNS)

        data = pd.concat(frames, ignore_index=True)
        data = self._normalize_columns(data)
        return self._clean_rows(data)

    def _iter_data_files(self) -> Iterable[Path]:
        patterns = ("*.csv", "*.xlsx", "*.xls")
        for pattern in patterns:
            yield from self.data_dir.glob(pattern)

    def _read_file(self, path: Path) -> pd.DataFrame | None:
        try:
            if path.suffix.lower() == ".csv":
                frame = pd.read_csv(path)
            else:
                frame = pd.read_excel(path)
        except Exception:
            return None

        frame["source_file"] = path.name
        return frame

    def _normalize_columns(self, frame: pd.DataFrame) -> pd.DataFrame:
        rename_map: dict[str, str] = {}
        for column in frame.columns:
            normalized = self._normalize_name(column)
            if normalized in {"country", "area", "location", "island", "territory"}:
                rename_map[column] = "country"
            elif normalized in {"product", "item", "commodity", "crop", "livestock"}:
                rename_map[column] = "product"
            elif normalized in {"type", "category", "product_type", "dataset", "domain"}:
                rename_map[column] = "type"
            elif normalized in {"year", "time_period", "period"}:
                rename_map[column] = "year"
            elif normalized in {"yield", "value", "yield_value", "measure", "amount"}:
                rename_map[column] = "yield"
            elif normalized in {"unit", "units", "unit_of_measure", "uom"}:
                rename_map[column] = "unit"

        return frame.rename(columns=rename_map)

    def _clean_rows(self, frame: pd.DataFrame) -> pd.DataFrame:
        missing = {"country", "product", "year", "yield"} - set(frame.columns)
        if missing:
            return pd.DataFrame(columns=STANDARD_COLUMNS)

        clean = frame.copy()
        if "type" not in clean.columns:
            clean["type"] = clean["source_file"].apply(self._infer_type_from_text)
        else:
            clean["type"] = clean["type"].fillna("").astype(str)
            clean["type"] = clean.apply(
                lambda row: row["type"] or self._infer_type_from_text(row["source_file"]),
                axis=1,
            )

        if "unit" not in clean.columns:
            clean["unit"] = "unknown"

        clean["country"] = clean["country"].astype(str).str.strip()
        clean["product"] = clean["product"].astype(str).str.strip()
        clean["type"] = clean["type"].astype(str).str.strip().str.lower()
        clean["type"] = clean["type"].replace(
            {
                "crops": "crop",
                "crop yield": "crop",
                "livestock yield": "livestock",
                "animals": "livestock",
            }
        )
        clean["year"] = pd.to_numeric(clean["year"], errors="coerce").astype("Int64")
        clean["yield"] = pd.to_numeric(clean["yield"], errors="coerce")
        clean["unit"] = clean["unit"].fillna("unknown").astype(str).str.strip()

        clean = clean.dropna(subset=["country", "product", "year", "yield"])
        clean = clean[(clean["country"] != "") & (clean["product"] != "")]
        clean["year"] = clean["year"].astype(int)
        clean["type"] = clean["type"].where(clean["type"].isin(["crop", "livestock"]), "unknown")

        return clean[STANDARD_COLUMNS].sort_values(["country", "product", "type", "year"])

    def _infer_type_from_text(self, value: object) -> str:
        text = str(value).lower()
        if "livestock" in text:
            return "livestock"
        if "crop" in text:
            return "crop"
        return "unknown"

    def _normalize_name(self, value: object) -> str:
        return str(value).strip().lower().replace(" ", "_").replace("-", "_")

