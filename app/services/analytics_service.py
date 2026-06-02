from typing import Any

import pandas as pd


class AnalyticsService:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def summary(self) -> dict[str, int]:
        return {
            "total_countries": self._nunique("country"),
            "total_products": self._nunique("product"),
            "total_years": self._nunique("year"),
            "total_records": int(len(self.data)),
            "crop_record_count": int((self.data["type"] == "crop").sum()) if not self.data.empty else 0,
            "livestock_record_count": int((self.data["type"] == "livestock").sum()) if not self.data.empty else 0,
        }

    def countries(self) -> list[str]:
        return self._sorted_unique("country")

    def products(self, product_type: str | None = None) -> list[str]:
        data = self._filter_type(self.data, product_type)
        return sorted(data["product"].dropna().unique().tolist()) if not data.empty else []

    def filters(self) -> dict[str, Any]:
        years = self._sorted_unique("year")
        return {
            "countries": self.countries(),
            "product_types": self._sorted_unique("type"),
            "product_names": self.products(),
            "year_range": {"min": min(years), "max": max(years)} if years else None,
            "years": years,
            "units": self._sorted_unique("unit"),
        }

    def trend(self, country: str, product: str, product_type: str | None = None) -> dict[str, Any]:
        data = self._filter_type(self.data, product_type)
        data = data[
            (data["country"].str.casefold() == country.casefold())
            & (data["product"].str.casefold() == product.casefold())
        ]
        if data.empty:
            return {"country": country, "product": product, "type": product_type, "series": []}

        series = (
            data.groupby("year", as_index=False)["yield"]
            .mean()
            .sort_values("year")
            .rename(columns={"yield": "value"})
        )
        return {
            "country": data["country"].iloc[0],
            "product": data["product"].iloc[0],
            "type": data["type"].iloc[0],
            "unit": data["unit"].mode().iloc[0] if not data["unit"].mode().empty else "unknown",
            "series": self._records(series),
        }

    def comparison(self, product: str, year: int, product_type: str | None = None) -> dict[str, Any]:
        data = self._filter_type(self.data, product_type)
        data = data[
            (data["product"].str.casefold() == product.casefold())
            & (data["year"] == year)
        ]
        if data.empty:
            return {"product": product, "type": product_type, "year": year, "countries": []}

        result = (
            data.groupby(["country", "unit"], as_index=False)["yield"]
            .mean()
            .sort_values("yield", ascending=False)
            .rename(columns={"yield": "value"})
        )
        return {
            "product": data["product"].iloc[0],
            "type": data["type"].iloc[0],
            "year": year,
            "countries": self._records(result),
        }

    def country_profile(self, country: str) -> dict[str, Any]:
        data = self.data[self.data["country"].str.casefold() == country.casefold()]
        if data.empty:
            return {
                "country": country,
                "available_crop_products": [],
                "available_livestock_products": [],
                "years_available": [],
                "latest_values": [],
                "trend_summaries": [],
            }

        latest_year = int(data["year"].max())
        latest = data[data["year"] == latest_year].copy()
        latest = latest.rename(columns={"yield": "value"})

        return {
            "country": data["country"].iloc[0],
            "available_crop_products": self.products_for_country(data, "crop"),
            "available_livestock_products": self.products_for_country(data, "livestock"),
            "years_available": self._sorted_unique("year", data),
            "latest_values": self._records(
                latest[["product", "type", "year", "value", "unit"]].sort_values(["type", "product"])
            ),
            "trend_summaries": self._trend_summaries(data),
        }

    def products_for_country(self, data: pd.DataFrame, product_type: str) -> list[str]:
        subset = data[data["type"] == product_type]
        return sorted(subset["product"].dropna().unique().tolist())

    def dataset_context(self, question: str) -> dict[str, Any]:
        tokens = question.casefold()
        countries = [c for c in self.countries() if c.casefold() in tokens]
        products = [p for p in self.products() if p.casefold() in tokens]
        return {
            "matched_countries": countries,
            "matched_products": products,
            "summary": self.summary(),
        }

    def data_rows(self, type_filter: str | None = None, country: str | None = None, product: str | None = None, year_min: int | None = None, year_max: int | None = None) -> list[dict[str, Any]]:
        df = self.data
        if type_filter and type_filter.casefold() != "all":
            df = df[df["type"].str.casefold() == type_filter.casefold()]
        if country and country.casefold() != "all":
            df = df[df["country"].str.casefold() == country.casefold()]
        if product and product.casefold() != "all":
            df = df[df["product"].str.casefold() == product.casefold()]
        if year_min is not None:
            df = df[df["year"] >= year_min]
        if year_max is not None:
            df = df[df["year"] <= year_max]
            
        return self._records(df)

    def heatmap(self) -> dict[str, Any]:
        countries = self._sorted_unique("country")[:10]
        products = self._sorted_unique("product")[:10]
        
        cells = []
        for c in countries:
            for p in products:
                subset = self.data[(self.data["country"] == c) & (self.data["product"] == p)]
                avg_yield = float(subset["yield"].mean()) if not subset.empty else None
                record_count = len(subset)
                cells.append({
                    "country": c,
                    "product": p,
                    "avg_yield": avg_yield,
                    "record_count": record_count
                })
        return {
            "countries": countries,
            "products": products,
            "cells": cells
        }

    def insights(self, product: str, year_min: int | None = None, year_max: int | None = None) -> dict[str, Any]:
        df = self.data
        if year_min is not None:
            df = df[df["year"] >= year_min]
        if year_max is not None:
            df = df[df["year"] <= year_max]
            
        prod_df = df[df["product"].str.casefold() == product.casefold()] if product else df
        
        # Highest Yield Country
        highest_country = {"label": "Highest Yield Country", "value": "—", "sub": "0 avg"}
        if not prod_df.empty:
            avg_yields = prod_df.groupby("country")["yield"].mean()
            if not avg_yields.empty:
                top_c = avg_yields.idxmax()
                top_v = avg_yields.max()
                highest_country = {"label": "Highest Yield Country", "value": top_c, "sub": f"{round(top_v)} avg"}

        # Fastest Growing & Largest Decline
        fastest = {"label": "Fastest Growing Product", "value": "—", "sub": "0% over period"}
        decliner = {"label": "Largest Decline", "value": "—", "sub": "0%"}
        
        if year_min is not None and year_max is not None:
            fastest_pct = -1000
            decline_pct = 1000
            fastest_p = "—"
            decliner_p = "—"
            
            for p in self.products():
                p_df = self.data[self.data["product"] == p]
                start = p_df[p_df["year"] == year_min]
                end = p_df[p_df["year"] == year_max]
                if not start.empty and not end.empty:
                    s = start["yield"].mean()
                    e = end["yield"].mean()
                    if s > 0:
                        pct = ((e - s) / s) * 100
                        if pct > fastest_pct:
                            fastest_pct = pct
                            fastest_p = p
                        if pct < decline_pct:
                            decline_pct = pct
                            decliner_p = p
                            
            if fastest_p != "—":
                fastest = {"label": "Fastest Growing Product", "value": fastest_p, "sub": f"+{fastest_pct:.1f}% over period"}
            if decliner_p != "—":
                decliner = {"label": "Largest Decline", "value": decliner_p, "sub": f"{decline_pct:.1f}%"}

        # Most reported
        most_reported = {"label": "Most Reported Product", "value": "—", "sub": "0 records"}
        if not self.data.empty:
            counts = self.data["product"].value_counts()
            if not counts.empty:
                top_p = counts.idxmax()
                top_c = counts.max()
                most_reported = {"label": "Most Reported Product", "value": str(top_p), "sub": f"{top_c} records"}

        return {
            "highest_yield_country": highest_country,
            "fastest_growing_product": fastest,
            "largest_decline_product": decliner,
            "most_reported_product": most_reported
        }

    def _trend_summaries(self, data: pd.DataFrame) -> list[dict[str, Any]]:
        summaries: list[dict[str, Any]] = []
        for (product, product_type), rows in data.groupby(["product", "type"]):
            by_year = rows.groupby("year", as_index=False)["yield"].mean().sort_values("year")
            if len(by_year) < 2:
                direction = "not enough data"
                change_percent = None
            else:
                first = float(by_year.iloc[0]["yield"])
                last = float(by_year.iloc[-1]["yield"])
                change_percent = round(((last - first) / first) * 100, 2) if first else None
                direction = "increasing" if last > first else "decreasing" if last < first else "stable"
            summaries.append(
                {
                    "product": product,
                    "type": product_type,
                    "direction": direction,
                    "change_percent": change_percent,
                }
            )
        return summaries

    def _filter_type(self, data: pd.DataFrame, product_type: str | None) -> pd.DataFrame:
        if not product_type:
            return data
        return data[data["type"].str.casefold() == product_type.casefold()]

    def _nunique(self, column: str) -> int:
        return int(self.data[column].nunique()) if column in self.data and not self.data.empty else 0

    def _sorted_unique(self, column: str, data: pd.DataFrame | None = None) -> list[Any]:
        frame = self.data if data is None else data
        if frame.empty or column not in frame:
            return []
        return sorted(frame[column].dropna().unique().tolist())

    def _records(self, frame: pd.DataFrame) -> list[dict[str, Any]]:
        return frame.where(pd.notnull(frame), None).to_dict(orient="records")

