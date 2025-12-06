import pandas as pd 
import numpy as np 
from datetime import datetime 
 
class Backtester: 
    def __init__(self, initial_capital: float = 100000.0, commission: float = 0.001): 
        self.initial_capital = initial_capital 
        self.commission = commission 
        self.portfolio_history = pd.DataFrame(columns=['Date', 'Capital', 'Holdings', 'Shares', 'Trade_Type', 'Trade_Price', 'Trade_Value', 'PnL']) 
 
    def run_backtest(self, df: pd.DataFrame, strategy_name: str = "Strategy") -> dict: 
        """ 
        Runs the backtest simulation based on buy/sell signals. 
        Assumes 'buy_signal' and 'sell_signal' columns exist in the DataFrame. 
        Trades are executed at the 'Close' price of the signal day. 
        """ 
        capital = self.initial_capital 
        shares = 0 
        in_position = False 
        trade_log = [] 
        portfolio_values = [] 
        equity_curve_data = [] 
 
        # Iterate through the data day by day 
        for i, row in df.iterrows(): 
            current_date = i 
            current_close = row['Close'] 
 
            # Record portfolio value at the start of each day 
            current_portfolio_value = capital + (shares * current_close) 
            equity_curve_data.append({'Date': current_date, 'Portfolio_Value': current_portfolio_value}) 
 
            # Buy signal 
            if row['buy_signal'] == 1 and not in_position: 
                # Calculate how many shares can be bought 
                available_capital = capital * (1 - self.commission) # Account for commission 
                num_shares_to_buy = int(available_capital / current_close) 
 
                if num_shares_to_buy > 0: 
                    cost = num_shares_to_buy * current_close 
                    capital -= cost 
                    capital -= cost * self.commission # Deduct commission from capital 
                    shares += num_shares_to_buy 
                    in_position = True 
                    trade_log.append({ 
                        'Date': current_date, 
                        'Type': 'BUY', 
                        'Price': current_close, 
                        'Shares': num_shares_to_buy, 
                        'Value': cost, 
                        'Capital_After_Trade': capital, 
                        'Portfolio_Value': capital + (shares * current_close) 
                    }) 
                    print(f"{current_date.strftime('%Y-%m-%d')} - BUY {num_shares_to_buy} shares at {current_close:.2f}. Capital: {capital:.2f}") 
 
            # Sell signal 
            elif row['sell_signal'] == 1 and in_position: 
                revenue = shares * current_close 
                capital += revenue 
                capital -= revenue * self.commission # Deduct commission from capital 
                trade_log.append({ 
                    'Date': current_date, 
                    'Type': 'SELL', 
                    'Price': current_close, 
                    'Shares': shares, 
                    'Value': revenue, 
                    'Capital_After_Trade': capital, 
                    'Portfolio_Value': capital + (shares * current_close) 
                }) 
                print(f"{current_date.strftime('%Y-%m-%d')} - SELL {shares} shares at {current_close:.2f}. Capital: {capital:.2f}") 
                shares = 0 
                in_position = False 
 
        # Final portfolio value at the end of the backtest 
        final_portfolio_value = capital + (shares * df['Close'].iloc[-1] if shares > 0 else 0) 
        equity_curve_data.append({'Date': df.index[-1], 'Portfolio_Value': final_portfolio_value}) 
 
        equity_curve_df = pd.DataFrame(equity_curve_data).set_index('Date') 
        equity_curve_df = equity_curve_df.loc[~equity_curve_df.index.duplicated(keep='first')] 
 
 
        # Prepare results 
        results = { 
            'initial_capital': self.initial_capital, 
            'final_capital': final_portfolio_value, 
            'trade_log': pd.DataFrame(trade_log), 
            'equity_curve': equity_curve_df 
        } 
        return results 
 
    def analyze_performance(self, equity_curve: pd.DataFrame, trade_log: pd.DataFrame, df_original: pd.DataFrame) -> dict: 
        """Calculates performance metrics with empty trade_log handling.""" 
        if equity_curve.empty or 'Portfolio_Value' not in equity_curve.columns: 
            return {"error": "Equity curve is empty or malformed."} 
 
        equity_curve = equity_curve.sort_index() 
        total_return = (equity_curve['Portfolio_Value'].iloc[-1] / equity_curve['Portfolio_Value'].iloc[0]) - 1 
        equity_curve['Peak'] = equity_curve['Portfolio_Value'].cummax() 
        equity_curve['Drawdown'] = (equity_curve['Portfolio_Value'] - equity_curve['Peak']) / equity_curve['Peak'] 
        max_drawdown = equity_curve['Drawdown'].min() 
 
        num_years = (equity_curve.index[-1] - equity_curve.index[0]).days / 365.25 
        cagr = ((equity_curve['Portfolio_Value'].iloc[-1] / equity_curve['Portfolio_Value'].iloc[0])**(1/num_years)) - 1 if num_years > 0 else 0 
 
        daily_returns = equity_curve['Portfolio_Value'].pct_change().dropna() 
        volatility = daily_returns.std() * np.sqrt(252) if not daily_returns.empty else 0 
        sharpe_ratio = (cagr - 0) / volatility if volatility > 0 else 0 
 
    # SAFE trade_log handling 
        if trade_log.empty: 
            num_trades = 0 
            win_rate = 0 
            avg_pnl_per_trade = 0 
            total_pnl = 0 
            wins = 0 
        else: 
            num_trades = len(trade_log[trade_log['Type'] == 'SELL']) if 'Type' in trade_log.columns else 0 
            # Simple metrics - just count trades for now 
            wins = 0 
            win_rate = 0 
            avg_pnl_per_trade = 0 
            total_pnl = 0 
 
        buy_hold_return = (df_original['Close'].iloc[-1] / df_original['Close'].iloc[0]) - 1 if len(df_original) > 1 else 0 
 
        metrics = { 
            'Total Return': f"{total_return:.2%}", 
            'Max Drawdown': f"{max_drawdown:.2%}", 
            'CAGR': f"{cagr:.2%}", 
            'Sharpe Ratio': f"{sharpe_ratio:.2f}", 
            'Volatility (Annualized)': f"{volatility:.2%}", 
            'Number of Trades': num_trades, 
            'Winning Trades': wins, 
            'Win Rate': f"{win_rate:.2f}%", 
            'Total PnL': f"{total_pnl:.2f}", 
            'Average PnL per Trade': f"{avg_pnl_per_trade:.2f}", 
            'Buy and Hold Return': f"{buy_hold_return:.2%}" 
    } 
        return metrics