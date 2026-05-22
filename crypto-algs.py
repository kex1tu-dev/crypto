import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def add_indicators(df):
    # Скользящие средние (SMA)
    df['SMA_10'] = df['Close'].rolling(window=10).mean()
    df['SMA_30'] = df['Close'].rolling(window=30).mean()

    # Индикатор RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df


def backtest_strategy(df, strategy_type, initial_balance=1000):
    usd_balance = initial_balance
    crypto_balance = 0
    buy_signals = []
    sell_signals = []

    for i in range(1, len(df)):
        price = df['Close'].iloc[i]

        if strategy_type == 'SMA':
            buy_condition = df['SMA_10'].iloc[i] > df['SMA_30'].iloc[i] and df['SMA_10'].iloc[i - 1] <= df['SMA_30'].iloc[i - 1]
            sell_condition = df['SMA_10'].iloc[i] < df['SMA_30'].iloc[i] and df['SMA_10'].iloc[i - 1] >= df['SMA_30'].iloc[i - 1]

        elif strategy_type == 'RSI':
            buy_condition = df['RSI'].iloc[i] < 30 and df['RSI'].iloc[i - 1] >= 30
            sell_condition = df['RSI'].iloc[i] > 70 and df['RSI'].iloc[i - 1] <= 70

        if buy_condition and usd_balance > 0:
            crypto_balance = usd_balance / price
            usd_balance = 0
            buy_signals.append((df.index[i], price))

        elif sell_condition and crypto_balance > 0:
            usd_balance = crypto_balance * price
            crypto_balance = 0
            sell_signals.append((df.index[i], price))

    final_usd = usd_balance + (crypto_balance * df['Close'].iloc[-1])
    return final_usd, buy_signals, sell_signals


print("Загрузка данных по крипте")
tickers = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD']
results = {}

for ticker in tickers:
    df = yf.download(ticker, period='1mo', interval='4h', progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

    df_4h = df.resample('4h').agg(
        {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}).dropna()
    df_4h = add_indicators(df_4h)
    results[ticker] = df_4h

strategy = ''
while strategy not in ('SMA', 'RSI'):
    strategy = input('Введите индикатор (SMA или RSI): ')

print("\nРезультаты трейдинга")
for ticker in tickers:
    df = results[ticker]
    final_balance, buys, sells = backtest_strategy(df, strategy)

    plt.figure(figsize=(12, 6))

    plt.plot(df.index, df['Close'], label=f'Цена {ticker}', alpha=0.5, color='gray')
    plt.plot(df.index, df['SMA_10'], label='SMA 10 (Быстрая)', color='blue', alpha=0.7)
    plt.plot(df.index, df['SMA_30'], label='SMA 30 (Медленная)', color='orange', alpha=0.7)

    if buys:
        buy_dates, buy_prices = zip(*buys)
        plt.scatter(buy_dates, buy_prices, marker='^', color='green', s=150, label='Покупка', zorder=5)

    if sells:
        sell_dates, sell_prices = zip(*sells)
        plt.scatter(sell_dates, sell_prices, marker='v', color='red', s=150, label='Продажа', zorder=5)

    plt.title(f'Работа индикатора {strategy} на {ticker}\nИтог: ${final_balance:.2f}', fontsize=14, fontweight='bold')
    plt.ylabel('Цена (USD)')
    plt.legend(loc='best')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

plt.show()