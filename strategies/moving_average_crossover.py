import pandas as pd 
import numpy as np 
from indicators.calculator import IndicatorCalculator 
 
class MovingAverageCrossover: 
    def __init__(self, short_window: int = 5, long_window: int =40): 
        self.short_window = short_window 
        self.long_window = long_window 
 
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame: 
        """Generate clean buy/sell signals using .loc to fix pandas warnings.""" 
        # Make a copy to avoid SettingWithCopyWarning 
        df = df.copy() 
         
        # Add SMAs if not present 
        calc = IndicatorCalculator() 
        df = calc.add_sma(df, window=self.short_window, name=f'SMA_{self.short_window}') 
        df = calc.add_sma(df, window=self.long_window, name=f'SMA_{self.long_window}') 
         
        # Generate crossover signals (actual crossovers, not just above/below) 
        df['short_sma_prev'] = df[f'SMA_{self.short_window}'].shift(1) 
        df['long_sma_prev'] = df[f'SMA_{self.long_window}'].shift(1) 
         
        # Buy signal: short MA crosses ABOVE long MA 
        df['buy_signal'] = ( 
            (df[f'SMA_{self.short_window}'] > df[f'SMA_{self.long_window}']) &  
            (df['short_sma_prev'] <= df['long_sma_prev']) 
        ).astype(int) 
         
        # Sell signal: short MA crosses BELOW long MA   
        df['sell_signal'] = ( 
            (df[f'SMA_{self.short_window}'] < df[f'SMA_{self.long_window}']) &  
            (df['short_sma_prev'] >= df['long_sma_prev']) 
        ).astype(int) 
         
        return df.dropna()