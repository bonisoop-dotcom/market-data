"""매일 미국장 마감 후 정확한 종가·지표를 받아 data/latest.json 에 저장."""
import json, io, datetime as dt, urllib.request
import pandas as pd, yfinance as yf

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}
PEAKS = {"SOXL": ("2026-06-22", 300.77), "^IXIC": ("2026-10-06", 27600.0)}

def get(url, headers=None, tries=3, timeout=90):
    import time
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={**UA, **(headers or {})})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:
            last = e; time.sleep(5 * (i + 1))
    raise last

out = {"generated_utc": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z", "errors": []}

# 1) 종가: SOXL, 나스닥, 반도체지수, VIX
px = yf.download(["SOXL", "^IXIC", "^SOX", "^VIX"], period="1y", interval="1d",
                 auto_adjust=False, progress=False)["Close"].dropna(how="all")
BASE = px["^IXIC"].dropna().index[-1]
for t in ["SOXL", "^IXIC", "^SOX", "^VIX"]:
    s = px[t].dropna()
    s = s[s.index <= BASE]
    d = {"date": s.index[-1].strftime("%Y-%m-%d"), "close": round(float(s.iloc[-1]), 2),
         "prev_close": round(float(s.iloc[-2]), 2),
         "chg_pct": round((s.iloc[-1] / s.iloc[-2] - 1) * 100, 2),
         "last10": {i.strftime("%m/%d"): round(float(v), 2) for i, v in s.tail(10).items()}}
    if t in PEAKS:
        pdate, ppx = PEAKS[t]
        hi = s[s.index >= pdate]
        if hi.max() > ppx:  # 신고가 갱신 시 고점 교체
            ppx, pdate = float(hi.max()), hi.idxmax().strftime("%Y-%m-%d")
        after = s[s.index >= pdate]
        d.update(peak_date=pdate, peak=round(ppx, 2),
                 drawdown_pct=round((s.iloc[-1] / ppx - 1) * 100, 1),
                 breakeven_pct=round((ppx / s.iloc[-1] - 1) * 100, 1),
                 days_since_peak=(s.index[-1] - pd.Timestamp(pdate)).days,
                 low=round(float(after.min()), 2), low_date=after.idxmin().strftime("%Y-%m-%d"),
                 low_dd_pct=round((after.min() / ppx - 1) * 100, 1))
    if t == "^SOX":
        lo20 = s.iloc[:-1].tail(20).min()
        d.update(ma20=round(float(s.tail(20).mean()), 2), ma200=round(float(s.tail(200).mean()), 2),
                 prior20_low=round(float(lo20), 2), new_low=bool(s.iloc[-1] < lo20))
    if t == "^VIX":
        d.update(max20=round(float(s.tail(20).max()), 2),
                 max20_date=s.tail(20).idxmax().strftime("%Y-%m-%d"))
    out[t.strip("^")] = d

# 2) CNN 공포탐욕지수
try:
    fg = json.loads(get("https://production.dataviz.cnn.io/index/fearandgreed/graphdata",
                        {"Accept": "application/json, text/plain, */*", "Accept-Language": "en-US,en;q=0.9",
                         "Origin": "https://edition.cnn.com", "Referer": "https://edition.cnn.com/"}))
    f = fg["fear_and_greed"]
    out["fear_greed"] = {"score": round(f["score"], 1), "rating": f["rating"],
                         "timestamp": f["timestamp"], "prev_close": round(f["previous_close"], 1),
                         "prev_week": round(f["previous_1_week"], 1)}
except Exception as e:
    out["errors"].append(f"fear_greed: {e}")

# 3) FRED: 2년물 금리, 하이일드 스프레드
for key, sid in [("us2y", "DGS2"), ("hy_oas", "BAMLH0A0HYM2")]:
    try:
        if key == "us2y":
            raise RuntimeError("use treasury")  # 2년물은 재무부 공식 데이터 우선 (FRED는 GitHub 서버에서 자주 막힘)
        df = pd.read_csv(io.BytesIO(get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}", tries=1, timeout=40)))
        df.columns = ["date", "v"]; df = df[pd.to_numeric(df.v, errors="coerce").notna()]
        df.v = df.v.astype(float)
        out[key] = {"date": df.date.iloc[-1], "value": df.v.iloc[-1],
                    "chg_1m": round(df.v.iloc[-1] - df.v.iloc[-22], 2),
                    "max_3m": df.v.tail(63).max()}
    except Exception as e:
        if key == "us2y":
            try:
                y = dt.date.today().year
                rows = []
                for yr in (y - 1, y):
                    u = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
                         f"daily-treasury-rates.csv/{yr}/all?type=daily_treasury_yield_curve&field_tdr_date_value={yr}&page&_format=csv")
                    rows.append(pd.read_csv(io.BytesIO(get(u)))[["Date", "2 Yr"]])
                t = pd.concat(rows); t["Date"] = pd.to_datetime(t["Date"]); t = t.sort_values("Date")
                out[key] = {"date": t.Date.iloc[-1].strftime("%Y-%m-%d"), "value": float(t["2 Yr"].iloc[-1]),
                            "chg_1m": round(float(t["2 Yr"].iloc[-1] - t["2 Yr"].iloc[-22]), 2),
                            "max_3m": float(t["2 Yr"].tail(63).max()), "src": "treasury"}
                continue
            except Exception as e2:
                e = f"{e} / treasury: {e2}"
        out["errors"].append(f"{key}: {e}")


# 4) S&P 500 시장폭: 200일선 위 종목 비율, 52주 신고가/신저가 수
try:
    tbl = pd.read_html(io.BytesIO(get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")))[0]
    tick = [t.replace(".", "-") for t in tbl["Symbol"]]
    c = yf.download(tick, period="14mo", interval="1d", auto_adjust=False, progress=False, threads=True)["Close"]
    c = c.dropna(axis=1, thresh=210)
    last = c.ffill().iloc[-1]
    ma200 = c.rolling(200).mean().iloc[-1]
    hi = c.tail(252).max(); lo = c.tail(252).min()
    ok = last.notna() & ma200.notna()
    out["breadth"] = {"date": c.index[-1].strftime("%Y-%m-%d"),
                      "above200_pct": round(float((last[ok] > ma200[ok]).mean() * 100), 1),
                      "new_highs": int((last >= hi).sum()), "new_lows": int((last <= lo).sum()),
                      "n": int(ok.sum())}
except Exception as e:
    out["errors"].append(f"breadth: {e}")

# 5) 원달러 환율
try:
    fx = yf.download("KRW=X", period="1mo", progress=False)["Close"].dropna()
    fx = fx.iloc[:, 0] if hasattr(fx, "columns") else fx
    out["usdkrw"] = {"date": fx.index[-1].strftime("%Y-%m-%d"), "value": round(float(fx.iloc[-1]), 1)}
except Exception as e:
    out["errors"].append(f"usdkrw: {e}")

import os; os.makedirs("data", exist_ok=True)
json.dump(out, open("data/latest.json", "w"), ensure_ascii=False, indent=2)
json.dump(out, open(f"data/{out['SOXL']['date']}.json", "w"), ensure_ascii=False, indent=2)
print(json.dumps(out, ensure_ascii=False, indent=2))
