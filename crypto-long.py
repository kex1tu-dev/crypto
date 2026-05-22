import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

tickers = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD']
crypto_dfs = {}

startData = '2024-05-01'
endData = '2025-05-01'
for ticker in tickers:
    df = yf.download(ticker, start=startData, end=endData, interval='1d', progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df_4h = df.resample('4h').agg({
        'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
    }).dropna()
    crypto_dfs[ticker] = df_4h

print("Результаты инвестиций при бюджете 1000$")


def simulate_strategies(ticker, df):
    start_price = df['Close'].iloc[0]
    end_price = df['Close'].iloc[-1]

    #HODL: покупаем на все сумму в первый день
    hodl_coins = 1000 / start_price
    hodl_result = hodl_coins * end_price
    hodl_profit = hodl_result - 1000

    #DCA: делим бюджет на 4 покупки по 250 долларов
    dca_coins = 0
    buy_indices = [0, len(df) // 4, len(df) // 2, 3 * len(df) // 4]

    for idx in buy_indices:
        price_at_moment = df['Close'].iloc[idx]
        dca_coins += 250 / price_at_moment

    dca_result = dca_coins * end_price
    dca_profit = dca_result - 1000

    staking_coins = hodl_coins * 1.01
    staking_result = staking_coins * end_price
    staking_profit = staking_result - 1000

    print(f"\nМонета: {ticker}")
    print(f"Цена в начале: ${start_price:.2f} | Цена в конце: ${end_price:.2f}")
    print(f"\tHODL: Итог ${hodl_result:.2f} (Прибыль: ${hodl_profit:.2f})")
    print(f"\tDCA:  Итог ${dca_result:.2f} (Прибыль: ${dca_profit:.2f})")
    print(f"\tStake: Итог ${staking_result:.2f} (Прибыль: ${staking_profit:.2f})")


for ticker in tickers:
    simulate_strategies(ticker, crypto_dfs[ticker])

fig, axes = plt.subplots(2, 2, figsize=(14, 8))
fig.suptitle(f'Курсы криптовалют с {startData} по {endData}', fontsize=16)
axes = axes.flatten()

for i, ticker in enumerate(tickers):
    axes[i].plot(crypto_dfs[ticker].index, crypto_dfs[ticker]['Close'], color='teal')
    axes[i].set_title(f'График {ticker}')
    axes[i].set_ylabel('Цена (USD)')
    axes[i].grid(True, linestyle='--', alpha=0.6)
    axes[i].tick_params(axis='x', rotation=30)

plt.tight_layout()
plt.show()
