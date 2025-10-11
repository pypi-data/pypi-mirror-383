import pandas as pd
import yfinance as yf
from enum import Enum


class DataField(Enum):
    """Available financial data fields."""
    OPEN = "Open"
    HIGH = "High"
    LOW = "Low"
    CLOSE = "Close"
    ADJ_CLOSE = "Adj Close"
    VOLUME = "Volume"

    @classmethod
    def parse(cls, value: str):
        """
        Parses a string (case-insensitive) into a DataField.
        Raises ValueError if the string does not match any field.
        """
        normalized = value.strip().lower()
        for field in cls:
            if field.value.lower() == normalized:
                return field
        raise ValueError(f"Unknown data field: {value}")

class TimeUnit(Enum):
    """Supported time units for interpolation resolution."""
    DAYS = "D"
    MONTHS = "M"
    YEARS = "Y"


class Period:
    """Represents a time resolution with unit and magnitude."""
    def __init__(self, value: int, unit: TimeUnit):
        if value <= 0:
            raise ValueError("Period value must be positive.")
        self.value = value
        self.unit = unit

    def to_pandas_freq(self) -> str:
        """Converts the period to a pandas-compatible frequency string."""
        return f"{self.value}{self.unit.value}"

    def __str__(self):
        return self.to_pandas_freq()


class MarketData:
    """
    Module to fetch and manage financial time series from Yahoo Finance.
    Provides summary, raw data, and interpolated data methods.
    """

    def __init__(self, max_cache_size = 100):
        self.cache = {}
        self.max_cache_size = max_cache_size
        self.cache_keys = []

    # ------------------------------------------------------------
    def _download(self, name: str, start: str, end: str) -> pd.DataFrame:
        """Downloads and caches data from Yahoo Finance."""
        key = (name, start, end)
        if key in self.cache:
            print("hit")
            return self.cache[key]

        data = yf.download(name, start=start, end=end, progress=False, auto_adjust=False, multi_level_index=False)
        if data.empty:
            raise ValueError(f"No data retrieved for {name} between {start} and {end}.")

        data.index = pd.to_datetime(data.index)
        # Store in cache, if cache is full, pop first
        if self.max_cache_size <= len(self.cache_keys):
            key_to_pop = self.cache_keys[0]
            self.cache.pop(key_to_pop)
        self.cache[key] = data
        self.cache_keys = self.cache_keys[1:] + [key]
        
        return data

    # ------------------------------------------------------------
    def get_available_fields(self, name: str, start: str, end: str):
        """Returns the available fields for a given ticker."""
        df = self._download(name, start, end)
        return [DataField.parse(column) for column in df.columns]

    # ------------------------------------------------------------
    def get_summary(self, names, start="2000-01-01", end=None):
        """
        Returns a summary for each ticker:
        - name
        - min/max date
        - average resolution
        - available fields
        """
        summaries = []
        for name in names:
            df = self._download(name, start, end or pd.Timestamp.today().strftime("%Y-%m-%d"))
            deltas = df.index.to_series().diff().dropna()
            resolution = deltas.mode()[0] if not deltas.empty else pd.Timedelta("NaT")
            summaries.append({
                "name": name,
                "date_min": df.index.min().date(),
                "date_max": df.index.max().date(),
                "resolution": str(resolution),
                "fields": list(df.columns)
            })
        return pd.DataFrame(summaries)

    # ------------------------------------------------------------
    def get_raw(self, name: str, start: str, end: str, field: DataField):
        """Returns raw data for a given ticker and field."""
        df = self._download(name, start, end)
        col = field.value
        if col not in df.columns:
            raise KeyError(f"Field '{col}' not available for {name}.")
        return df[[col]].rename(columns={col: "value"})

    # ------------------------------------------------------------
    def get_interpolated(self, name: str, start: str, end: str, field: DataField, resolution: Period):
        """
        Returns interpolated data for a given ticker, field, and resolution.
        Example: Period(1, TimeUnit.DAYS), Period(3, TimeUnit.MONTHS)
        """
        df = self.get_raw(name, start, end, field)
        freq = resolution.to_pandas_freq()

        # Create full time grid
        full_index = pd.date_range(start=start, end=end, freq=freq)

        # Reindex and interpolate
        interpolated = df.reindex(full_index).interpolate(method="time")
        interpolated.index.name = "date"
        return interpolated
