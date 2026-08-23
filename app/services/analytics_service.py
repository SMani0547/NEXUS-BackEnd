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
        product_types = [
            product_type
            for product_type in self._sorted_unique("type")
            if product_type.casefold() in tokens
        ]
        years = self._sorted_unique("year")
        latest_year = max(years) if years else None
        country_profiles = []
        for country in countries[:3]:
            profile = self.country_profile(country)
            country_profiles.append(
                {
                    "country": profile["country"],
                    "years_available": {
                        "min": min(profile["years_available"]) if profile["years_available"] else None,
                        "max": max(profile["years_available"]) if profile["years_available"] else None,
                        "count": len(profile["years_available"]),
                    },
                    "available_crop_products": profile["available_crop_products"][:12],
                    "available_livestock_products": profile["available_livestock_products"][:12],
                    "latest_values": profile["latest_values"][:8],
                    "trend_summaries": sorted(
                        profile["trend_summaries"],
                        key=lambda item: abs(item["change_percent"] or 0),
                        reverse=True,
                    )[:8],
                }
            )

        trend_snapshots = []
        for country in countries[:3]:
            for product in products[:4]:
                trend = self.trend(country, product)
                snapshot = self._compact_trend(trend)
                if snapshot:
                    trend_snapshots.append(snapshot)

        product_comparisons = []
        if latest_year is not None:
            for product in products[:4]:
                comparison = self.comparison(product, latest_year)
                product_comparisons.append(
                    {
                        "product": comparison["product"],
                        "type": comparison["type"],
                        "year": comparison["year"],
                        "top_countries": comparison["countries"][:8],
                    }
                )

        return {
            "matched_countries": countries,
            "matched_products": products,
            "matched_product_types": product_types,
            "summary": self.summary(),
            "year_range": {"min": min(years), "max": max(years)} if years else None,
            "country_profiles": country_profiles,
            "trend_snapshots": trend_snapshots,
            "product_comparisons_latest_year": product_comparisons,
            "general_insights": self.insights(products[0] if products else "", min(years) if years else None, latest_year),
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

    def type_summary(self) -> dict[str, Any]:
        years = self._sorted_unique("year")
        types: dict[str, Any] = {}
        for product_type in ("crop", "livestock"):
            subset = self.data[self.data["type"] == product_type] if not self.data.empty else self.data
            top = (
                subset.groupby("product")["yield"].mean().sort_values(ascending=False).head(5)
                if not subset.empty
                else pd.Series(dtype=float)
            )
            types[product_type] = {
                "product_count": int(subset["product"].nunique()) if not subset.empty else 0,
                "record_count": int(len(subset)),
                "avg_yield": float(subset["yield"].mean()) if not subset.empty else None,
                "unit": subset["unit"].mode().iloc[0] if not subset.empty and not subset["unit"].mode().empty else None,
                "top_products": [{"product": name, "avg_yield": float(value)} for name, value in top.items()],
            }

        coverage = (
            self.data.groupby("country", as_index=False)
            .agg(year_min=("year", "min"), year_max=("year", "max"), record_count=("year", "size"))
            .sort_values("country")
            if not self.data.empty
            else pd.DataFrame(columns=["country", "year_min", "year_max", "record_count"])
        )

        return {
            "year_range": {"min": min(years), "max": max(years)} if years else None,
            "total_countries": self._nunique("country"),
            "total_records": int(len(self.data)),
            "types": types,
            "coverage": self._records(coverage),
        }

    def multi_country_trend(
        self,
        product: str,
        countries: list[str] | None = None,
        year_min: int | None = None,
        year_max: int | None = None,
        product_type: str | None = None,
    ) -> dict[str, Any]:
        data = self._filter_type(self.data, product_type)
        data = data[data["product"].str.casefold() == product.casefold()]
        if year_min is not None:
            data = data[data["year"] >= year_min]
        if year_max is not None:
            data = data[data["year"] <= year_max]
        if countries:
            wanted = {country.casefold() for country in countries if country}
            data = data[data["country"].str.casefold().isin(wanted)]

        if data.empty:
            return {"product": product, "type": product_type, "unit": None, "series": []}

        grouped = (
            data.groupby(["country", "year"], as_index=False)["yield"]
            .mean()
            .sort_values(["country", "year"])
            .rename(columns={"yield": "value"})
        )
        series = [
            {"country": country, "points": self._records(rows[["year", "value"]])}
            for country, rows in grouped.groupby("country")
        ]
        return {
            "product": data["product"].iloc[0],
            "type": data["type"].iloc[0],
            "unit": data["unit"].mode().iloc[0] if not data["unit"].mode().empty else "unknown",
            "series": series,
        }

    def product_rankings(
        self,
        product_type: str | None = None,
        year: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        data = self._filter_type(self.data, product_type)
        if year is not None:
            data = data[data["year"] == year]
        if data.empty:
            return {"type": product_type, "year": year, "products": []}

        ranked = (
            data.groupby(["product", "type"], as_index=False)
            .agg(avg_yield=("yield", "mean"), country_count=("country", "nunique"), record_count=("yield", "size"))
            .sort_values("avg_yield", ascending=False)
            .head(max(1, limit))
        )
        return {"type": product_type, "year": year, "products": self._records(ranked)}

    def heatmap(self) -> dict[str, Any]:
        return self.enhanced_heatmap(limit_countries=10, limit_products=10)

    def enhanced_heatmap(
        self,
        product_type: str | None = None,
        limit_countries: int = 20,
        limit_products: int = 20,
    ) -> dict[str, Any]:
        data = self._filter_type(self.data, product_type)
        if data.empty:
            return {"type": product_type, "countries": [], "products": [], "cells": []}

        countries = data["country"].value_counts().head(max(1, limit_countries)).index.tolist()
        products = data["product"].value_counts().head(max(1, limit_products)).index.tolist()
        subset = data[data["country"].isin(countries) & data["product"].isin(products)]
        grouped = subset.groupby(["country", "product"], as_index=False).agg(
            avg_yield=("yield", "mean"),
            record_count=("yield", "size"),
        )
        lookup = {(row["country"], row["product"]): row for row in self._records(grouped)}
        cells = []
        for country in countries:
            for product in products:
                row = lookup.get((country, product))
                cells.append(
                    {
                        "country": country,
                        "product": product,
                        "avg_yield": row["avg_yield"] if row else None,
                        "record_count": int(row["record_count"]) if row else 0,
                    }
                )
        return {
            "type": product_type,
            "countries": countries,
            "products": products,
            "cells": cells,
        }

    def year_heatmap(self, product: str | None = None, product_type: str | None = None) -> dict[str, Any]:
        data = self._filter_type(self.data, product_type)
        resolved_product = None
        if product:
            data = data[data["product"].str.casefold() == product.casefold()]
            resolved_product = data["product"].iloc[0] if not data.empty else product

        if data.empty:
            return {
                "product": resolved_product,
                "type": product_type,
                "axis": "year_country" if product else "year_product",
                "years": [],
                "countries": [],
                "products": [],
                "cells": [],
            }

        if product:
            grouped = (
                data.groupby(["year", "country"], as_index=False)["yield"]
                .mean()
                .rename(columns={"yield": "avg_yield"})
            )
            years = self._sorted_unique("year", data)
            countries = self._sorted_unique("country", data)
            return {
                "product": resolved_product,
                "type": data["type"].iloc[0],
                "axis": "year_country",
                "years": years,
                "countries": countries,
                "products": [resolved_product] if resolved_product else [],
                "cells": self._records(grouped),
            }

        grouped = (
            data.groupby(["year", "product"], as_index=False)["yield"]
            .mean()
            .rename(columns={"yield": "avg_yield"})
        )
        years = self._sorted_unique("year", data)
        products = self._sorted_unique("product", data)
        return {
            "product": None,
            "type": product_type,
            "axis": "year_product",
            "years": years,
            "countries": [],
            "products": products,
            "cells": self._records(grouped),
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

    def _compact_trend(self, trend: dict[str, Any]) -> dict[str, Any] | None:
        series = trend.get("series", [])
        if not series:
            return None

        first = series[0]
        latest = series[-1]
        first_value = float(first["value"]) if first.get("value") is not None else None
        latest_value = float(latest["value"]) if latest.get("value") is not None else None
        change_percent = None
        if first_value and latest_value is not None:
            change_percent = round(((latest_value - first_value) / first_value) * 100, 2)

        return {
            "country": trend.get("country"),
            "product": trend.get("product"),
            "type": trend.get("type"),
            "unit": trend.get("unit"),
            "first_year": first.get("year"),
            "first_value": first_value,
            "latest_year": latest.get("year"),
            "latest_value": latest_value,
            "change_percent": change_percent,
            "sample_count": len(series),
        }

    def _nunique(self, column: str) -> int:
        return int(self.data[column].nunique()) if column in self.data and not self.data.empty else 0

    def _sorted_unique(self, column: str, data: pd.DataFrame | None = None) -> list[Any]:
        frame = self.data if data is None else data
        if frame.empty or column not in frame:
            return []
        return sorted(frame[column].dropna().unique().tolist())

    def _records(self, frame: pd.DataFrame) -> list[dict[str, Any]]:
        return frame.where(pd.notnull(frame), None).to_dict(orient="records")
