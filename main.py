import argparse 
from datetime import datetime 
import pandas as pd 
 
from utils.data_manager import DataManager 
from indicators.calculator import IndicatorCalculator 
from strategies.moving_average_crossover import MovingAverageCrossover 
from utils.backtester import Backtester 
from utils.plotter import Plotter 
from config import EODHD_API_KEY 
 
def main(): 
    parser = argparse.ArgumentParser(description="EODHD Backtesting Engine") 
    parser.add_argument("--ticker", type=str, required=True, help="Stock ticker symbol (e.g., AAPL.US)") 
    parser.add_argument("--strategy", type=str, default="MACrossover", choices=["MACrossover"], 
                        help="Strategy to use for backtesting (e.g., MACrossover)") 
    parser.add_argument("--force_download", action="store_true", 
                        help="Force download fresh data, ignoring cache.") 
    args = parser.parse_args() 
 
    ticker = args.ticker 
    strategy_choice = args.strategy 
 
    print(f"--- Starting Backtest for {ticker} with {strategy_choice} strategy ---") 
 
    # 1. Data Retrieval and Normalization 
    data_manager = DataManager(api_key=EODHD_API_KEY) 
    df = data_manager.get_eod_data(ticker, force_download=args.force_download) 
 
    if df.empty: 
        print(f"Could not retrieve data for {ticker}. Exiting.") 
        return 
 
    # Keep a copy of the original data for benchmark calculation if needed 
    df_original = df.copy() 
 
    # 2. Technical Indicator Layer 
    indicator_calculator = IndicatorCalculator() 
    # Add only the necessary indicators for MACrossover (SMA_20, SMA_50) 
    # The add_all_common_indicators in calculator.py should already be simplified 
    df = indicator_calculator.add_all_common_indicators(df) 
 
    # 3. Strategy Module 
    if strategy_choice == "MACrossover": 
        strategy = MovingAverageCrossover(short_window=20, long_window=50) 
        df = strategy.generate_signals(df) 
 
        # Ensure 'buy_signal' and 'sell_signal' are present and numeric 
        if 'buy_signal' not in df.columns or 'sell_signal' not in df.columns: 
            print("Strategy did not generate 'buy_signal' or 'sell_signal' columns. Exiting.") 
            return 
 
        df['buy_signal'] = pd.to_numeric(df['buy_signal'], errors='coerce').fillna(0).astype(int) 
        df['sell_signal'] = pd.to_numeric(df['sell_signal'], errors='coerce').fillna(0).astype(int) 
 
    else: 
        print(f"Strategy '{strategy_choice}' not recognized.") 
        return 
    # Drop rows with NaN values AFTER all indicators and signals have been generated. 
    # This ensures that only rows where signals cannot be calculated are removed. 
    df = df.dropna() 
 
    if df.empty: 
        print("DataFrame is empty after strategy signal generation and NaN removal. Not enough data. Exiting.") 
        return
 
    # 4. Back-testing Simulation 
    backtester = Backtester(initial_capital=100000.0, commission=0.001) 
    backtest_results = backtester.run_backtest(df, strategy_name=strategy_choice) 
 
    trade_log = backtest_results.get('trade_log', pd.DataFrame()) 
    equity_curve = backtest_results.get('equity_curve', pd.DataFrame()) 
 
    # 5. Performance Evaluation 
    metrics = backtester.analyze_performance(equity_curve, trade_log, df_original) 
 
    # 6. Reporting and Visualization 
    plotter = Plotter() 
    plotter.plot_price_action_with_signals(df, ticker, strategy_choice, indicators=['SMA_20', 'SMA_50']) 
    plotter.plot_equity_curve(equity_curve, ticker, strategy_choice) 
    plotter.generate_report_file(ticker, strategy_choice, metrics, trade_log) 
 
    print("\n--- Backtest Summary ---") 
    for key, value in metrics.items(): 
        print(f"{key}: {value}") 
    print("\n--- Backtest Complete ---") 
 
if __name__ == "__main__": 
    main()