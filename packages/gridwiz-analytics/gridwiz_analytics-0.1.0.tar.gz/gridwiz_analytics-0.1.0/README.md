# gridwiz_analytics

Utilities to analyze GridWiz e-bike data from Excel files. **You provide the file at call-time** (e.g., `July.xlsx`).

## Install
```bash
pip install .
# or build first:
python -m build && pip install dist/*.whl
```

## Usage
```python
from gridwiz_analytics import (
    RevenueTrendAnalyzer, PeakUsageAnalyzer,
    HourlyPeakAnalyzer, BikeUsageAnalyzer,
    DailyRevenueAnalyzer, DailyRidingAnalyzer
)

# Revenue per parking spot (read Excel when you instantiate)
rev = RevenueTrendAnalyzer("July.xlsx")
print(rev.total_revenue_by_spot())
rev.plot_revenue_by_spot(selected_spots=[
    "Gridwiz Parking Area","Fakultas Teknik","Fakultas Kedokteran"
])

# Peak usage by day for selected spots
peak = PeakUsageAnalyzer("Agustus.xlsx")
peak.plot_daily_peak_usage(["Islamic Center"])

# Hourly usage for top-N spots
hourly = HourlyPeakAnalyzer("august.xlsx")
hourly.plot_hourly_usage_top_spots(from_spots=["Islamic Center","UTTARA"], top_n=5)

# Total usage counts (filtered list)
bike = BikeUsageAnalyzer("data_july.xlsx")
bike.plot_usage([
    "Gridwiz Parking Area","Fakultas Teknik","UPT Perpustakaan","Rektorat"
])

# Daily revenue per spot (wide date range filled with zeros)
daily_rev = DailyRevenueAnalyzer("16-26.xlsx")
daily_rev.plot_daily_revenue(["Gridwiz Parking Area","Fakultas Teknik"])

# Daily riding counts per spot
daily_ride = DailyRidingAnalyzer("16-26.xlsx")
daily_ride.plot_daily_riding(["Islamic Center","UTTARA"], title="Daily Riding Partnership")
```
