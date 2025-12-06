import matplotlib.pyplot as plt 
import pandas as pd 
import os 
from config import REPORTS_DIR 
from datetime import datetime 
 
class Plotter: 
    def __init__(self, reports_dir=REPORTS_DIR): 
        self.reports_dir = reports_dir 
        os.makedirs(self.reports_dir, exist_ok=True) 
 
    def plot_price_action_with_signals(self, df: pd.DataFrame, ticker: str, strategy_name: str, indicators: list = None): 
        """ 
        Plots price action, indicators, and buy/sell signals. 
        """ 
        plt.figure(figsize=(15, 8)) 
        plt.plot(df.index, df['Close'], label='Close Price', alpha=0.7) 
 
        if indicators: 
            for ind in indicators: 
                if ind in df.columns: 
                    plt.plot(df.index, df[ind], label=ind, linestyle='--', alpha=0.7) 
 
        # Plot buy signals 
        buy_dates = df[df['buy_signal'] == 1].index 
        buy_prices = df[df['buy_signal'] == 1]['Close'] 
        plt.scatter(buy_dates, buy_prices, marker='^', color='green', s=100, label='Buy Signal', alpha=1, zorder=5) 
 
        # Plot sell signals 
        sell_dates = df[df['sell_signal'] == 1].index 
        sell_prices = df[df['sell_signal'] == 1]['Close'] 
        plt.scatter(sell_dates, sell_prices, marker='v', color='red', s=100, label='Sell Signal', alpha=1, zorder=5) 
 
        plt.title(f'{ticker} Price Action with {strategy_name} Signals') 
        plt.xlabel('Date') 
        plt.ylabel('Price') 
        plt.legend() 
        plt.grid(True) 
        plt.tight_layout() 
        plt.savefig(os.path.join(self.reports_dir, f'{ticker}_{strategy_name}_signals.png')) 
        plt.close() 
        print(f"Generated signal plot: {os.path.join(self.reports_dir, f'{ticker}_{strategy_name}_signals.png')}") 
 
    def plot_equity_curve(self, equity_curve_df: pd.DataFrame, ticker: str, strategy_name: str): 
        """ 
        Plots the equity curve of the backtest. 
        """ 
        if equity_curve_df.empty or 'Portfolio_Value' not in equity_curve_df.columns: 
            print("Cannot plot equity curve: DataFrame is empty or missing 'Portfolio_Value' column.") 
            return 
 
        plt.figure(figsize=(15, 8)) 
        plt.plot(equity_curve_df.index, equity_curve_df['Portfolio_Value'], label='Portfolio Value', color='blue') 
        plt.title(f'{ticker} {strategy_name} Equity Curve') 
        plt.xlabel('Date') 
        plt.ylabel('Portfolio Value') 
        plt.legend() 
        plt.grid(True) 
        plt.tight_layout() 
        plt.savefig(os.path.join(self.reports_dir, f'{ticker}_{strategy_name}_equity_curve.png')) 
        plt.close() 
        print(f"Generated equity curve plot: {os.path.join(self.reports_dir, f'{ticker}_{strategy_name}_equity_curve.png')}") 
 
    def generate_report_file(self, ticker: str, strategy_name: str, metrics: dict, trade_log_df: pd.DataFrame): 
        """ 
        Generates a text report summarizing backtest results. 
        """ 
        report_path = os.path.join(self.reports_dir, f'{ticker}_{strategy_name}_report.txt') 
        with open(report_path, 'w') as f: 
            f.write(f"--- Backtest Report for {ticker} using {strategy_name} ---\n\n") 
            f.write(f"Date Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n") 
            f.write("Performance Metrics:\n") 
            for key, value in metrics.items(): 
                f.write(f"- {key}: {value}\n") 
            f.write("\n") 
 
            f.write("Trade Log (First 10 and Last 10 Entries):\n") 
            if not trade_log_df.empty: 
                f.write(trade_log_df.head(10).to_string() + "\n") 
                if len(trade_log_df) > 20: 
                    f.write("...\n") 
                f.write(trade_log_df.tail(10).to_string() + "\n") 
            else: 
                f.write("No trades executed.\n") 
 
            f.write(f"\nPlots generated: {ticker}_{strategy_name}_signals.png, {ticker}_{strategy_name}_equity_curve.png\n") 
            f.write("\n--- End of Report ---\n") 
        print(f"Generated report file: {report_path}")