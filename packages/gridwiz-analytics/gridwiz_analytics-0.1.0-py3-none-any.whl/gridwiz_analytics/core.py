import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class RevenueTrendAnalyzer:
    def __init__(self, file_path):
        self.df = pd.read_excel(file_path)
        self._setup_translation()
        self._clean()

    def _setup_translation(self):
        self.parking_translation = {
            "Gridwiz Parking Area": "Warehouse Parking",
            "Fakultas Ekonomi dan Bisnis": "Economic and bussiness",
            "Fakultas Teknik": "Engineering",
            "UPT Perpustakaan": "Unram Library",
            "Fakultas Kedokteran": "Medical",
            "UNRAM Sport Center": "Unram Sport Center",
            "Fakultas Teknologi Pangan dan Agroindustri": "Fatepa",
            "Fakultas Peternakan": "Animal Science",
            "Rektorat": "Rectorat",
            "Masjid Baabul Hikmah": "Masjid Babul Hikmah",
            "Fakultas Hukum, Ilmu Sosial, dan Ilmu Politik": "Fisipol",
            "Program Studi Farmasi": "Pharmacy",
            "LPMPP UNRAM": "LPMPP",
            "Asrama Putri": "Girls' Dormitory",
            "Magister Ekonomi": "Magister Economic",
            "PUSTIK": "UPT Pustik",
            "Fakultas Pertanian": "Agriculture",
            "Fakultas Matematika dan Ilmu Pengetahuan Alam": "Faculty of Math and Natural Sciences",
            "Pasca sarjana": "Postgraduate",
            "D3 Ekonomi": "Associate Degree Economics",
            "Fakultas Keguruan dan Ilmu Pengetahuan": "Faculty of Education and Science",
            "out of parking area": "out of parking area"
        }

    def _clean(self):
        self.df.columns = self.df.columns.str.strip()
        self.df['Car rental stations'] = self.df['Car rental stations'].astype(str).str.strip()
        self.df['Car rental stations'] = self.df['Car rental stations'].replace(['nan', 'NaN', '', 'None'], 'out of parking area')
        self.df['Car rental stations'] = self.df['Car rental stations'].fillna('out of parking area')

    def total_revenue_by_spot(self, selected_spots=None):
        if 'Actual amount' not in self.df.columns:
            raise ValueError("Kolom 'Actual amount' tidak ditemukan.")

        df_filtered = self.df.copy()
        if selected_spots:
            df_filtered = df_filtered[df_filtered['Car rental stations'].isin(selected_spots)]

        grouped = df_filtered.groupby('Car rental stations')['Actual amount'].sum()
        grouped.index = [self.parking_translation.get(name, name) for name in grouped.index]
        return grouped.sort_values(ascending=False)

    def plot_revenue_by_spot(self, selected_spots=None, title='Total Revenue per Parking Spot'):
        revenue = self.total_revenue_by_spot(selected_spots)

        if revenue.empty:
            print("No revenue data found for the selected spots.")
            return

        norm = plt.Normalize(revenue.min(), revenue.max())
        cmap = plt.cm.get_cmap('RdYlGn')
        colors = cmap(norm(revenue.values))

        plt.figure(figsize=(max(12, len(revenue) * 0.6), 8))
        bars = plt.bar(revenue.index, revenue.values, color=colors)

        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, yval + (yval * 0.02),
                     f"{int(yval):,}", ha='center', va='bottom', fontsize=9)

        plt.title(title, fontsize=14)
        plt.xlabel("Parking Spot", fontsize=12)
        plt.ylabel("Total Revenue (Rp)", fontsize=12)
        plt.xticks(rotation=35, ha='right', fontsize=10)
        plt.yticks(fontsize=10)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()


class PeakUsageAnalyzer:
    def __init__(self, filepath):
        self.df = pd.read_excel(filepath)
        self._clean()

    def _clean(self):
        self.df['Car rental stations'] = self.df['Car rental stations'].astype(str).str.strip()
        self.df['Car rental stations'] = self.df['Car rental stations'].fillna('Unknown')
        self.df['Start time'] = pd.to_datetime(self.df['Start time'], errors='coerce')
        self.df['date'] = self.df['Start time'].dt.date

    def get_daily_usage(self, selected_spots):
        if not selected_spots:
            raise ValueError("selected_spots tidak boleh kosong.")
        filtered_df = self.df[self.df['Car rental stations'].isin(selected_spots)]
        usage = filtered_df.groupby(['Car rental stations', 'date']).size().reset_index(name='count')
        return usage

    def plot_daily_peak_usage(self, selected_spots, title='Daily Usage per Parking Zone'):
        usage = self.get_daily_usage(selected_spots)

        plt.figure(figsize=(12, 6))
        for spot in selected_spots:
            spot_data = usage[usage['Car rental stations'] == spot]
            plt.plot(spot_data['date'], spot_data['count'], marker='o', label=spot)

            for _, row in spot_data.iterrows():
                plt.text(row['date'], row['count'] + 0.3, str(row['count']),
                         ha='center', va='bottom', fontsize=8)

        plt.title(title)
        plt.xlabel("Tanggal")
        plt.ylabel("Jumlah Penggunaan")
        plt.xticks(rotation=45)
        plt.grid(True, axis='y', linestyle='--', alpha=0.5)
        plt.legend(title='Parking Spot')
        plt.tight_layout()
        plt.show()


class HourlyPeakAnalyzer:
    def __init__(self, filepath):
        self.df = pd.read_excel(filepath)
        self._setup_translation()
        self._clean()

    def _setup_translation(self):
        self.parking_translation = {
            "Gridwiz Parking Area": "Warehouse Parking",
            "Fakultas Ekonomi dan Bisnis": "Economic and bussiness",
            "Fakultas Teknik": "Engineering",
            "UPT Perpustakaan": "Unram Library",
            "Fakultas Kedokteran": "Medical",
            "UNRAM Sport Center": "Unram Sport Center",
            "Fakultas Teknologi Pangan dan Agroindustri": "Fatepa",
            "Fakultas Peternakan": "Animal Science",
            "Rektorat": "Rectorat",
            "Masjid Baabul Hikmah": "Masjid Babul Hikmah",
            "Fakultas Hukum, Ilmu Sosial, dan Ilmu Politik": "Fisipol",
            "Program Studi Farmasi": "Pharmacy",
            "LPMPP UNRAM": "LPMPP",
            "Asrama Putri": "Girls' Dormitory",
            "Magister Ekonomi": "Magister Economic",
            "PUSTIK": "UPT Pustik",
            "Fakultas Pertanian": "Agriculture",
            "Fakultas Matematika dan Ilmu Pengetahuan Alam": "Faculty of Math and Natural Sciences",
            "Pasca sarjana": "Postgraduate",
            "D3 Ekonomi": "Associate Degree Economics",
            "Fakultas Keguruan dan Ilmu Pengetahuan": "Faculty of Education and Science",
            "out of parking area": "out of parking area"
        }

    def _clean(self):
        self.df['Car rental stations'] = self.df['Car rental stations'].astype(str).str.strip()
        self.df['Car rental stations'] = self.df['Car rental stations'].replace(
            ['nan', '', 'NaN', 'None'], 'out of parking area'
        )
        self.df['Car rental stations'] = self.df['Car rental stations'].fillna('out of parking area')
        self.df['Start Time'] = pd.to_datetime(self.df['Start Time'], errors='coerce')
        self.df['hour'] = self.df['Start Time'].dt.hour

    def get_top_parking_spots(self, from_spots=None, top_n=5):
        filtered_df = self.df.copy()
        if from_spots:
            filtered_df = filtered_df[filtered_df['Car rental stations'].isin(from_spots)]
        counts = filtered_df['Car rental stations'].value_counts().head(top_n).index.tolist()
        return counts

    def get_hourly_usage(self, selected_spots):
        df_filtered = self.df[self.df['Car rental stations'].isin(selected_spots)]
        usage = df_filtered.groupby(['Car rental stations', 'hour']).size().reset_index(name='count')
        return usage

    def plot_hourly_usage_top_spots(self, from_spots=None, top_n=5, title='Hourly Usage for Top Parking Spots'):
        top_spots = self.get_top_parking_spots(from_spots, top_n)
        usage = self.get_hourly_usage(top_spots)

        plt.figure(figsize=(12, 6))
        for spot in top_spots:
            translated_spot = self.parking_translation.get(spot, spot)
            spot_data = usage[usage['Car rental stations'] == spot]
            plt.plot(spot_data['hour'], spot_data['count'], marker='o', label=translated_spot)

            for _, row in spot_data.iterrows():
                plt.text(row['hour'], row['count'] + 0.5, str(row['count']),
                         ha='center', va='bottom', fontsize=8)

        plt.title(title)
        plt.xlabel("Hour of Day (0–23)")
        plt.ylabel("Number of Uses")
        plt.xticks(range(0, 24))
        plt.grid(True, axis='y', linestyle='--', alpha=0.5)
        plt.legend(title='Parking Spot')
        plt.tight_layout()
        plt.show()


class BikeUsageAnalyzer:
    def __init__(self, filepath):
        self.df = pd.read_excel(filepath)
        self._setup_translation()
        self._clean_data()

    def _setup_translation(self):
        self.parking_translation = {
            "Gridwiz Parking Area": "Warehouse Parking",
            "Fakultas Ekonomi dan Bisnis": "Economic and bussiness",
            "Fakultas Teknik": "Engineering",
            "UPT Perpustakaan": "Unram Library",
            "Fakultas Kedokteran": "Medical",
            "UNRAM Sport Center": "Unram Sport Center",
            "Fakultas Teknologi Pangan dan Agroindustri": "Fatepa",
            "Fakultas Peternakan": "Animal Science",
            "Rektorat": "Rectorat",
            "Masjid Baabul Hikmah": "Masjid Babul Hikmah",
            "Fakultas Hukum, Ilmu Sosial, dan Ilmu Politik": "Fisipol",
            "Program Studi Farmasi": "Pharmacy",
            "LPMPP UNRAM": "LPMPP",
            "Asrama Putri": "Girls' Dormitory",
            "Magister Ekonomi": "Magister Economic",
            "PUSTIK": "UPT Pustik",
            "Fakultas Pertanian": "Agriculture",
            "Fakultas Matematika dan Ilmu Pengetahuan Alam": "Faculty of Math and Natural Sciences",
            "Pasca sarjana": "Postgraduate",
            "D3 Ekonomi": "Associate Degree Economics",
            "Fakultas Keguruan dan Ilmu Pengetahuan": "Faculty of Education and Science",
            "out of parking area": "out of parking area"
        }

    def _clean_data(self):
        self.df['Car rental stations'] = self.df['Car rental stations'].astype(str).str.strip()
        self.df['Start time'] = pd.to_datetime(self.df['Start time'], errors='coerce')
        self.df['Car rental stations'] = self.df['Car rental stations'].replace(['nan', 'None', '', 'NaN'], 'out of parking area')
        self.df['Car rental stations'] = self.df['Car rental stations'].fillna('out of parking area')

    def get_all_parking_spots(self):
        return self.df['Car rental stations'].unique().tolist()

    def filter_by_spots(self, indo_spots):
        return self.df[self.df['Car rental stations'].isin(indo_spots)]

    def count_usage(self, indo_spots):
        filtered_df = self.filter_by_spots(indo_spots)
        counts = filtered_df['Car rental stations'].value_counts().sort_values(ascending=False)
        counts.index = [self.parking_translation.get(name, name) for name in counts.index]
        return counts

    def plot_usage(self, indo_spots, title='Total Usage (Filtered)'):
        usage_counts = self.count_usage(indo_spots)
        width = max(10, len(usage_counts) * 0.6)
        plt.figure(figsize=(width, 6))
        ax = usage_counts.plot(kind='bar', color='mediumseagreen')
        for i, value in enumerate(usage_counts.values):
            ax.text(i, value + 0.5, str(value), ha='center', va='bottom', fontsize=10)
        plt.title(title)
        plt.xlabel('Parking Spot')
        plt.ylabel('Usage Count')
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.show()


class DailyRevenueAnalyzer:
    def __init__(self, filepath):
        self.df = pd.read_excel(filepath)
        self._clean()

    def _clean(self):
        self.df.columns = self.df.columns.str.strip()
        self.df['Car rental stations'] = self.df['Car rental stations'].astype(str).str.strip()
        self.df['Car rental stations'] = self.df['Car rental stations'].replace(['nan', 'NaN', '', 'None'], 'out of parking area')
        self.df['Car rental stations'] = self.df['Car rental stations'].fillna('out of parking area')
        self.df['Start Time'] = pd.to_datetime(self.df['Start Time'], errors='coerce')
        self.df['date'] = self.df['Start Time'].dt.date

    def get_daily_revenue(self, selected_spots=None):
        if 'Actual amount' not in self.df.columns:
            raise ValueError("Kolom 'Actual amount' tidak ditemukan.")

        df_filtered = self.df.copy()
        if selected_spots:
            df_filtered = df_filtered[df_filtered['Car rental stations'].isin(selected_spots)]

        all_dates = pd.date_range(start=df_filtered['date'].min(), end=df_filtered['date'].max())

        results = []
        for spot in df_filtered['Car rental stations'].unique():
            spot_df = df_filtered[df_filtered['Car rental stations'] == spot]
            daily = (
                spot_df.groupby('date')['Actual amount']
                .sum()
                .reindex(all_dates, fill_value=0)
                .reset_index()
                .rename(columns={'index': 'date', 'Actual amount': 'revenue'})
            )
            daily['Car rental stations'] = spot
            results.append(daily)

        revenue_full = pd.concat(results, ignore_index=True)
        return revenue_full

    def plot_daily_revenue(self, selected_spots=None, title='Daily Revenue per Parking Spot'):
        revenue = self.get_daily_revenue(selected_spots)
        if revenue.empty:
            print("Tidak ada data revenue yang ditemukan untuk spot yang dipilih.")
            return

        plt.figure(figsize=(12, 6))
        for spot in revenue['Car rental stations'].unique():
            spot_data = revenue[revenue['Car rental stations'] == spot]
            plt.plot(spot_data['date'], spot_data['revenue'], marker='o', label=spot)
            for _, row in spot_data.iterrows():
                if row['revenue'] > 0:
                    plt.text(row['date'], row['revenue'] + 1000, f"{int(row['revenue']):,}",
                             ha='center', va='bottom', fontsize=8)
        plt.title(title)
        plt.xlabel("Tanggal")
        plt.ylabel("Revenue (Rp)")
        plt.xticks(rotation=45)
        plt.grid(True, axis='y', linestyle='--', alpha=0.5)
        plt.legend(title='Parking Spot')
        plt.tight_layout()
        plt.show()


class DailyRidingAnalyzer:
    def __init__(self, filepath):
        self.df = pd.read_excel(filepath)
        self._clean()

    def _clean(self):
        self.df.columns = self.df.columns.str.strip()
        self.df['Car rental stations'] = self.df['Car rental stations'].astype(str).str.strip()
        self.df['Car rental stations'] = self.df['Car rental stations'].replace(['nan', 'NaN', '', 'None'], 'out of parking area')
        self.df['Car rental stations'] = self.df['Car rental stations'].fillna('out of parking area')
        self.df['Start Time'] = pd.to_datetime(self.df['Start Time'], errors='coerce')
        self.df['date'] = self.df['Start Time'].dt.date

    def get_daily_riding(self, selected_spots=None):
        df_filtered = self.df.copy()
        if selected_spots:
            df_filtered = df_filtered[df_filtered['Car rental stations'].isin(selected_spots)]
        all_dates = pd.date_range(start=df_filtered['date'].min(), end=df_filtered['date'].max())
        results = []
        for spot in df_filtered['Car rental stations'].unique():
            spot_df = df_filtered[df_filtered['Car rental stations'] == spot]
            daily = (
                spot_df.groupby('date').size()
                .reindex(all_dates, fill_value=0)
                .reset_index()
                .rename(columns={'index': 'date', 0: 'riding_count'})
            )
            daily['Car rental stations'] = spot
            results.append(daily)
        riding_full = pd.concat(results, ignore_index=True)
        return riding_full

    def plot_daily_riding(self, selected_spots=None, title='Daily Riding per Parking Spot'):
        riding = self.get_daily_riding(selected_spots)
        if riding.empty:
            print("Tidak ada data riding yang ditemukan untuk spot yang dipilih.")
            return

        plt.figure(figsize=(12, 6))
        for spot in riding['Car rental stations'].unique():
            spot_data = riding[riding['Car rental stations'] == spot]
            plt.plot(spot_data['date'], spot_data['riding_count'], marker='o', label=spot)
            for _, row in spot_data.iterrows():
                if row['riding_count'] > 0:
                    plt.text(row['date'], row['riding_count'] + 0.2, str(row['riding_count']),
                             ha='center', va='bottom', fontsize=8)
        plt.title(title)
        plt.xlabel("Tanggal")
        plt.ylabel("Jumlah Riding")
        plt.xticks(rotation=45)
        plt.grid(True, axis='y', linestyle='--', alpha=0.5)
        plt.legend(title='Parking Spot')
        plt.tight_layout()
        plt.show()


__all__ = [
    "RevenueTrendAnalyzer",
    "PeakUsageAnalyzer",
    "HourlyPeakAnalyzer",
    "BikeUsageAnalyzer",
    "DailyRevenueAnalyzer",
    "DailyRidingAnalyzer",
]
