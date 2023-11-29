import polars as pl
import numpy as np
from functime.feature_extractors import FeatureExtractor

# Load commodities price data
y = pl.read_parquet("https://github.com/neocortexdb/functime/raw/main/data/commodities.parquet")

# Get column names ("commodity_type", "time", "price")
entity_col, time_col, value_col = y.columns

# Extract a single feature from a single time-series
binned_entropy = (
    pl.Series(np.random.normal(0, 1, size=10))
    .ts.binned_entropy(bin_count=10)
)

# 🔥 Also works on LazyFrames with query optimization
features = (
    pl.LazyFrame({
        "index": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        "value": np.random.normal(0, 1, size=10)
    })
    .select(
        pl.col("value").ts.binned_entropy(bin_count=10),
        pl.col("value").ts.lempel_ziv_complexity(threshold=3),
        pl.col("value").ts.longest_streak_above_mean(),
    )
)

# 🚄 Extract features blazingly fast on many
# stacked time-series using `group_by`
features = (
    y.group_by(entity_col)
    .agg(
        pl.col(value_col).ts.binned_entropy(bin_count=10),
        pl.col(value_col).ts.lempel_ziv_complexity(threshold=3),
        pl.col(value_col).ts.longest_streak_above_mean(),
    )
)

# 🚄 Extract features blazingly fast on windows
# of many time-series using `group_by_dynamic`
features = (
    # Compute rolling features at yearly intervals
    y.group_by_dynamic(
        time_col,
        every="12mo",
        by=entity_col,
    )
    .select(
        pl.col("value").ts.binned_entropy(bin_count=10),
        pl.col("value").ts.lempel_ziv_complexity(threshold=3),
        pl.col("value").ts.longest_streak_above_mean(),
    )
)