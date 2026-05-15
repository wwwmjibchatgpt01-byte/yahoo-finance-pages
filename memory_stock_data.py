import yfinance as yf
import datetime

tickers = ["2337.TW", "8299.TWO", "2408.TW", "2344.TW", "MU", "WDC", "STX", "005930.KS", "000660.KS"] # SNDK was acquired by WDC, maybe exclude it or handle error
data = []

for t in tickers:
    try:
        tk = yf.Ticker(t)
        hist = tk.history(period="ytd")
        if not hist.empty:
            start_price = hist['Close'].iloc[0]
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else start_price
            
            daily_change = ((current_price - prev_price) / prev_price) * 100
            ytd_return = ((current_price - start_price) / start_price) * 100
            
            data.append(f"{t}: {tk.info.get('shortName', t)} | Daily: {daily_change:.2f}% | YTD: {ytd_return:.2f}%")
        else:
            data.append(f"{t}: Data unavailable")
    except Exception as e:
        data.append(f"{t}: Error {e}")

print("\n".join(data))
