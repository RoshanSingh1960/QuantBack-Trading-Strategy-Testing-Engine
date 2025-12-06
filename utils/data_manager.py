import os 
import requests 
import pandas as pd 
from datetime import datetime, timedelta 
from config import EODHD_API_KEY, EODHD_BASE_URL, DATA_DIR 
 
class DataManager: 
    def __init__(self, api_key=EODHD_API_KEY, base_url=EODHD_BASE_URL, data_dir=DATA_DIR): 
        self.api_key = api_key 
        self.base_url = base_url 
        self.data_dir = data_dir 
        os.makedirs(self.data_dir, exist_ok=True) 
 
    def _fetch_eod_data(self, ticker: str, start_date: str = None, end_date: str = None) -> dict: 
        """Fetches EOD data for a given ticker from the EODHD API.""" 
        endpoint = f"{self.base_url}/eod/{ticker}" 
        params = { 
            "api_token": self.api_key, 
            "fmt": "json" 
        } 
        if start_date: 
            params["from"] = start_date 
        if end_date: 
            params["to"] = end_date 
 
        try: 
            response = requests.get(endpoint, params=params) 
            response.raise_for_status() 
            return response.json() 
        except requests.exceptions.RequestException as e: 
            print(f"Error fetching data for {ticker}: {e}") 
            return None 
 
    def get_eod_data(self, ticker: str, force_download: bool = False) -> pd.DataFrame: 
        """ 
        Retrieves EOD data for a ticker. Checks cache first, downloads if not found or forced. 
        """ 
        file_path = os.path.join(self.data_dir, f"{ticker}.csv") 
 
        if os.path.exists(file_path) and not force_download: 
            print(f"Loading cached data for {ticker} from {file_path}") 
            try: 
                df = pd.read_csv(file_path) 
                print(f"CSV columns found: {list(df.columns)}") 
                 
                # Find date column 
                date_col = None 
                possible_date_cols = ['Date', 'date', 'DATE'] 
                for col in possible_date_cols: 
                    if col in df.columns: 
                        date_col = col 
                        break 
                 
                if date_col: 
                    df = pd.read_csv(file_path, index_col=date_col, parse_dates=True) 
                else: 
                    df = pd.read_csv(file_path, index_col=0, parse_dates=True) 
                     
                return self._normalize_data(df) 
            except Exception as e: 
                print(f"Error reading cache: {e}. Forcing download...") 
                force_download = True 
 
        print(f"Fetching fresh data for {ticker}...") 
        end_date = datetime.now() 
        start_date = end_date - timedelta(days=370) 
 
        raw_data = self._fetch_eod_data( 
            ticker,  
            start_date=start_date.strftime("%Y-%m-%d"),  
            end_date=end_date.strftime("%Y-%m-%d") 
        ) 
 
        if raw_data: 
            df = pd.DataFrame(raw_data) 
            df.to_csv(file_path, index=False) 
            print(f"Data cached to {file_path}") 
            return self._normalize_data(df) 
        else: 
            return pd.DataFrame() 
 
    def _normalize_data(self, df: pd.DataFrame) -> pd.DataFrame: 
        """Normalizes the DataFrame.""" 
        if df.empty: 
            return df 
 
        print(f"Raw columns: {list(df.columns)}") 
        df.columns = df.columns.str.lower() 
 
        # Find and rename columns 
        column_mapping = { 
            'date': 'Date', 
            'open': 'Open', 
            'high': 'High', 
            'low': 'Low', 
            'close': 'Close', 
            'volume': 'Volume' 
        } 
        df = df.rename(columns=column_mapping) 
 
        # Set date index 
        if 'Date' in df.columns: 
            df['Date'] = pd.to_datetime(df['Date']) 
            df = df.set_index('Date') 
        else: 
            print("No Date column found!") 
            return pd.DataFrame() 
 
        df = df.sort_index() 
         
        # Clean data 
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume'] 
        for col in required_cols: 
            if col in df.columns: 
                df[col] = pd.to_numeric(df[col], errors='coerce') 
         
        df = df.dropna(subset=required_cols) 
        print(f"Normalized shape: {df.shape}") 
        return df