import pandas as pd
import yfinance as yf
from enum import Enum
from typing import List, Dict
import requests

NANOSECONDS_PER_SECOND = 1_000_000_000


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


class IndexType(Enum):
    STRING = "string"
    DATETIME = "datetime"
    EPOCH = "epoch"
    INDEX = "index"


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


class MarketDataProvider:
    """
    Module to fetch and manage financial time series from Yahoo Finance.
    Provides summary, raw data, and interpolated data methods.
    """

    def __init__(self, max_cache_size=100):
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

        data = yf.download(
            name,
            start=start,
            end=end,
            progress=False,
            auto_adjust=False,
            multi_level_index=False,
        )
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
            df = self._download(
                name, start, end or pd.Timestamp.today().strftime("%Y-%m-%d")
            )
            deltas = df.index.to_series().diff().dropna()
            resolution = deltas.mode()[0] if not deltas.empty else pd.Timedelta("NaT")
            summaries.append(
                {
                    "name": name,
                    "date_min": df.index.min().date(),
                    "date_max": df.index.max().date(),
                    "resolution": str(resolution),
                    "fields": list(df.columns),
                }
            )
        return pd.DataFrame(summaries)

    # ------------------------------------------------------------
    def get_raw(self, name: str, start: str, end: str, field: DataField):
        """Returns raw data for a given ticker and field."""
        df = self._download(name, start, end)
        col = field.value
        if col not in df.columns:
            raise KeyError(f"Field '{col}' not available for {name}.")
        return df[[col]].rename(columns={col: "value"})

    def get_interpolated(
        self,
        name: str,
        start: str,
        end: str,
        field: DataField,
        resolution: Period,
        index_type: IndexType = IndexType.DATETIME,
    ):
        """
        Returns interpolated data for a given ticker, field, and resolution.
        Performs flat extrapolation to the left and right of the original data range.

        Parameters
        ----------
        name : str
            Ticker symbol of the financial instrument.
        start : str
            Start date (inclusive) in 'YYYY-MM-DD' format.
        end : str
            End date (inclusive) in 'YYYY-MM-DD' format.
        field : DataField
            The financial data field to retrieve (e.g., CLOSE, OPEN).
        resolution : Period
            The target temporal resolution, e.g., Period(1, TimeUnit.DAYS) or Period(3, TimeUnit.MONTHS).
        index_type : IndexType, optional
            Defines the format of the time index in the output:
            - STRING → 'YYYY-MM-DD'
            - DATETIME → pandas datetime index (default)
            - EPOCH → seconds since 1970-01-01
            - INDEX → integer positions (0, 1, 2, …)

        Returns
        -------
        pd.DataFrame
            A DataFrame indexed according to `index_type`, containing interpolated and extrapolated values.
        """
        df = self.get_raw(name, start, end, field)
        freq = resolution.to_pandas_freq()

        # Create full time grid
        full_index = pd.date_range(start=start, end=end, freq=freq)

        # Interpolate + extrapolate flat
        interpolated = df.reindex(full_index).interpolate(method="time").ffill().bfill()

        # Format index according to index_type
        if index_type == IndexType.STRING:
            interpolated.index = interpolated.index.strftime("%Y-%m-%d")
        elif index_type == IndexType.EPOCH:
            interpolated.index = (
                interpolated.index.astype("int64") / NANOSECONDS_PER_SECOND
            )
        elif index_type == IndexType.INDEX:
            interpolated.index = range(len(interpolated))

        interpolated.index.name = "date"
        return interpolated

    def get_dataset(
        self,
        names: List[str],
        field: DataField,
        start: str,
        end: str,
        resolution: Period,
        index_type: IndexType = IndexType.DATETIME,
    ) -> Dict[str, pd.DataFrame]:
        """Returns interpolated data for the given tickers, field and resolution in a common time grid"""
        return {
            name: self.get_interpolated(name, start, end, field, resolution, index_type)
            for name in names
        }

## Update this list from https://en.wikipedia.org/wiki/List_of_S%26P_500_companies
# running in console
TICKERS_RETRIEVAL_SCRIPT = """
(() => {
   const rows = document.querySelectorAll("#constituents tbody tr");
   const tickers = Array.from(rows)
     .map(row => row.querySelector("td a")?.textContent.trim())
     .filter(Boolean);
   console.log("[\n  '" + tickers.join("',  '") + "'\n]");
 })();
"""

AVAILABLE_TICKERS =  [
  'MMM',  'AOS',  'ABT',  'ABBV',  'ACN',  'ADBE',  'AMD',  'AES',  'AFL',  'A',  'APD',  'ABNB',  'AKAM',  'ALB',  'ARE',  'ALGN',  'ALLE',  'LNT',  'ALL',  'GOOGL',  'GOOG',  'MO',  'AMZN',  'AMCR',  'AEE',  'AEP',  'AXP',  'AIG',  'AMT',  'AWK',  'AMP',  'AME',  'AMGN',  'APH',  'ADI',  'AON',  'APA',  'APO',  'AAPL',  'AMAT',  'APP',  'APTV',  'ACGL',  'ADM',  'ANET',  'AJG',  'AIZ',  'T',  'ATO',  'ADSK',  'ADP',  'AZO',  'AVB',  'AVY',  'AXON',  'BKR',  'BALL',  'BAC',  'BAX',  'BDX',  'BRK.B',  'BBY',  'TECH',  'BIIB',  'BLK',  'BX',  'XYZ',  'BK',  'BA',  'BKNG',  'BSX',  'BMY',  'AVGO',  'BR',  'BRO',  'BF.B',  'BLDR',  'BG',  'BXP',  'CHRW',  'CDNS',  'CPT',  'CPB',  'COF',  'CAH',  'KMX',  'CCL',  'CARR',  'CAT',  'CBOE',  'CBRE',  'CDW',  'COR',  'CNC',  'CNP',  'CF',  'CRL',  'SCHW',  'CHTR',  'CVX',  'CMG',  'CB',  'CHD',  'CI',  'CINF',  'CTAS',  'CSCO',  'C',  'CFG',  'CLX',  'CME',  'CMS',  'KO',  'CTSH',  'COIN',  'CL',  'CMCSA',  'CAG',  'COP',  'ED',  'STZ',  'CEG',  'COO',  'CPRT',  'GLW',  'CPAY',  'CTVA',  'CSGP',  'COST',  'CTRA',  'CRWD',  'CCI',  'CSX',  'CMI',  'CVS',  'DHR',  'DRI',  'DDOG',  'DVA',  'DAY',  'DECK',  'DE',  'DELL',  'DAL',  'DVN',  'DXCM',  'FANG',  'DLR',  'DG',  'DLTR',  'D',  'DPZ',  'DASH',  'DOV',  'DOW',  'DHI',  'DTE',  'DUK',  'DD',  'EMN',  'ETN',  'EBAY',  'ECL',  'EIX',  'EW',  'EA',  'ELV',  'EME',  'EMR',  'ETR',  'EOG',  'EPAM',  'EQT',  'EFX',  'EQIX',  'EQR',  'ERIE',  'ESS',  'EL',  'EG',  'EVRG',  'ES',  'EXC',  'EXE',  'EXPE',  'EXPD',  'EXR',  'XOM',  'FFIV',  'FDS',  'FICO',  'FAST',  'FRT',  'FDX',  'FIS',  'FITB',  'FSLR',  'FE',  'FI',  'F',  'FTNT',  'FTV',  'FOXA',  'FOX',  'BEN',  'FCX',  'GRMN',  'IT',  'GE',  'GEHC',  'GEV',  'GEN',  'GNRC',  'GD',  'GIS',  'GM',  'GPC',  'GILD',  'GPN',  'GL',  'GDDY',  'GS',  'HAL',  'HIG',  'HAS',  'HCA',  'DOC',  'HSIC',  'HSY',  'HPE',  'HLT',  'HOLX',  'HD',  'HON',  'HRL',  'HST',  'HWM',  'HPQ',  'HUBB',  'HUM',  'HBAN',  'HII',  'IBM',  'IEX',  'IDXX',  'ITW',  'INCY',  'IR',  'PODD',  'INTC',  'IBKR',  'ICE',  'IFF',  'IP',  'IPG',  'INTU',  'ISRG',  'IVZ',  'INVH',  'IQV',  'IRM',  'JBHT',  'JBL',  'JKHY',  'J',  'JNJ',  'JCI',  'JPM',  'K',  'KVUE',  'KDP',  'KEY',  'KEYS',  'KMB',  'KIM',  'KMI',  'KKR',  'KLAC',  'KHC',  'KR',  'LHX',  'LH',  'LRCX',  'LW',  'LVS',  'LDOS',  'LEN',  'LII',  'LLY',  'LIN',  'LYV',  'LKQ',  'LMT',  'L',  'LOW',  'LULU',  'LYB',  'MTB',  'MPC',  'MAR',  'MMC',  'MLM',  'MAS',  'MA',  'MTCH',  'MKC',  'MCD',  'MCK',  'MDT',  'MRK',  'META',  'MET',  'MTD',  'MGM',  'MCHP',  'MU',  'MSFT',  'MAA',  'MRNA',  'MHK',  'MOH',  'TAP',  'MDLZ',  'MPWR',  'MNST',  'MCO',  'MS',  'MOS',  'MSI',  'MSCI',  'NDAQ',  'NTAP',  'NFLX',  'NEM',  'NWSA',  'NWS',  'NEE',  'NKE',  'NI',  'NDSN',  'NSC',  'NTRS',  'NOC',  'NCLH',  'NRG',  'NUE',  'NVDA',  'NVR',  'NXPI',  'ORLY',  'OXY',  'ODFL',  'OMC',  'ON',  'OKE',  'ORCL',  'OTIS',  'PCAR',  'PKG',  'PLTR',  'PANW',  'PSKY',  'PH',  'PAYX',  'PAYC',  'PYPL',  'PNR',  'PEP',  'PFE',  'PCG',  'PM',  'PSX',  'PNW',  'PNC',  'POOL',  'PPG',  'PPL',  'PFG',  'PG',  'PGR',  'PLD',  'PRU',  'PEG',  'PTC',  'PSA',  'PHM',  'PWR',  'QCOM',  'DGX',  'RL',  'RJF',  'RTX',  'O',  'REG',  'REGN',  'RF',  'RSG',  'RMD',  'RVTY',  'HOOD',  'ROK',  'ROL',  'ROP',  'ROST',  'RCL',  'SPGI',  'CRM',  'SBAC',  'SLB',  'STX',  'SRE',  'NOW',  'SHW',  'SPG',  'SWKS',  'SJM',  'SW',  'SNA',  'SOLV',  'SO',  'LUV',  'SWK',  'SBUX',  'STT',  'STLD',  'STE',  'SYK',  'SMCI',  'SYF',  'SNPS',  'SYY',  'TMUS',  'TROW',  'TTWO',  'TPR',  'TRGP',  'TGT',  'TEL',  'TDY',  'TER',  'TSLA',  'TXN',  'TPL',  'TXT',  'TMO',  'TJX',  'TKO',  'TTD',  'TSCO',  'TT',  'TDG',  'TRV',  'TRMB',  'TFC',  'TYL',  'TSN',  'USB',  'UBER',  'UDR',  'ULTA',  'UNP',  'UAL',  'UPS',  'URI',  'UNH',  'UHS',  'VLO',  'VTR',  'VLTO',  'VRSN',  'VRSK',  'VZ',  'VRTX',  'VTRS',  'VICI',  'V',  'VST',  'VMC',  'WRB',  'GWW',  'WAB',  'WMT',  'DIS',  'WBD',  'WM',  'WAT',  'WEC',  'WFC',  'WELL',  'WST',  'WDC',  'WY',  'WSM',  'WMB',  'WTW',  'WDAY',  'WYNN',  'XEL',  'XYL',  'YUM',  'ZBRA',  'ZBH',  'ZTS'
]
