"""data/latest.json + config.json → 이미지 2장(out/*.png) + 텔레그램 요약(out/summary.txt)"""
import json, os, datetime as dt
D = json.load(open("data/latest.json")); C = json.load(open("config.json"))
os.makedirs("out", exist_ok=True)
S, Q, X, V = D["SOXL"], D["IXIC"], D["SOX"], D["VIX"]
FG, Y2, HY, BR, FX = (D.get(k) for k in ["fear_greed", "us2y", "hy_oas", "breadth", "usdkrw"])
base = S["date"]; md = lambda d: f"{int(d[5:7])}/{int(d[8:10])}"
BADGE = f"{base.replace('-', '.')} 종가 기준"
note_date = lambda d: "" if d == base else f" ({md(d)} 기준)"

# ---------- 표 ----------
def cur(p, close, dollar):
    f = (lambda x: f"${x:,.2f}") if dollar else (lambda x: f"{x:,.2f}")
    return (p["peak_date"][2:].replace("-", "."), None, p["days_since_peak"], f"{p['drawdown_pct']:.1f}",
            f"+{p['breakeven_pct']:.1f}" if p["breakeven_pct"] < 100 else f"+{p['breakeven_pct']:.0f}",
            None, None, f"{f(p['peak'])} → {f(close)}")
CUR_S, CUR_Q = cur(S, S["close"], True), cur(Q, Q["close"], False)
CARD1 = (f"<b>SOXL 2026</b><br>고점 ${S['peak']:,.2f} ({md(S['peak_date'])}) → 최저 종가 ${S['low']:,.2f} "
         f"({md(S['low_date'])}, {S['low_dd_pct']}%)<br>{md(base)} 종가 ${S['close']:,.2f} ({S['chg_pct']:+.2f}%)")
CARD2 = (f"<b>나스닥 2026</b><br>고점 {Q['peak']:,.0f} ({md(Q['peak_date'])}) → 최저 종가 {Q['low']:,.0f} "
         f"({md(Q['low_date'])}, {Q['low_dd_pct']}%)<br>{md(base)} 종가 {Q['close']:,.2f} ({Q['chg_pct']:+.2f}%) · VIX {V['close']}")
g = dict(CUR_S=CUR_S, CUR_Q=CUR_Q, BADGE=BADGE, CARD1=CARD1, CARD2=CARD2)
exec(open("tpl_table.py").read(), g); open("out/table.html", "w").write(g["html"])

# ---------- 점검표 판정 ----------
core = []
vj = "yes" if V["max20"] >= 40 and V["close"] < V["max20"] * 0.85 else ("half" if V["max20"] >= 30 and V["close"] < V["max20"] else "no")
core.append(("VIX 정점 후 꺾임", "40~50 급등 후 하락", f"{V['close']}",
             f"20일 최고 {V['max20']} ({md(V['max20_date'])}) → {V['close']}", vj,
             {"yes": "투매 정점 통과", "half": "급등했으나 40 미만", "no": "수준 낮음"}[vj]))
if BR:
    b = BR["above200_pct"]; bj = "yes" if b <= 20 else ("half" if b <= 30 else "no")
    core.append(("S&P 200일선 위 종목 비율", "20% 이하", f"{b:.0f}%", f"{BR['n']}종목 계산{note_date(BR['date'])}", bj,
                 {"yes": "항복 구간", "half": "근접", "no": "아직 멀었음"}[bj]))
else:
    core.append(("S&P 200일선 위 종목 비율", "20% 이하", "—", "수집 실패", "wait", "판단 불가"))
if FG:
    s = FG["score"]; fj = "yes" if s <= 10 else ("half" if s <= 25 else "no")
    core.append(("CNN 공포탐욕지수", "10 이하", f"{s:.0f}", f"전일 {FG['prev_close']:.0f} · 1주 전 {FG['prev_week']:.0f}", fj,
                 {"yes": "극단적 공포 바닥권", "half": "극단적 공포 구간", "no": "공포 부족"}[fj]))
else:
    core.append(("CNN 공포탐욕지수", "10 이하", "—", "수집 실패", "wait", "판단 불가"))
if Y2:
    off = Y2["max_3m"] - Y2["value"]; yj = "yes" if off >= 0.40 else ("half" if off >= 0.15 else "no")
    core.append(("미 2년물 국채 금리", "고점 후 하락 전환", f"{Y2['value']:.2f}%",
                 f"한 달 {Y2['chg_1m']:+.2f}%p · 3개월 고점 {Y2['max_3m']:.2f}%{note_date(Y2['date'])}", yj,
                 {"yes": "뚜렷한 하락 전환", "half": "하락 중, 확인 필요", "no": "고점권"}[yj]))
if X["new_low"]:
    xj, xc = "no", "신저점 경신"
elif X["close"] <= X["prior20_low"] * 1.05:
    xj, xc = "yes", "저점 재시험 후 지지"
else:
    xj, xc = "wait", "재시험 전"
core.append(("반도체지수 신저점 실패", "재하락 시 직전 저점 유지", f"{X['close']:,.0f}",
             f"20일 저점 {X['prior20_low']:,.0f} · {X['chg_pct']:+.2f}%", xj, xc))
cnt = [sum(c[4] == k for c in core) for k in ["yes", "half", "no", "wait"]]

hy = HY["value"] if HY else None
sub = [("52주 신고가 / 신저가", f"{BR['new_highs']} / {BR['new_lows']}" if BR else "—",
        ("yes" if BR and BR["new_lows"] > 150 else "half" if BR and BR["new_lows"] > 60 else "no") if BR else "wait"),
       ("AAII 강세-약세 차이", f"{C['aaii_spread']}", C["aaii_judge"]),
       ("BofA 펀드매니저 현금", f"{C['bofa_cash']} ({C['bofa_date']})", "no"),
       ("BofA 강세·약세 지표", f"{C['bofa_bb']}", "no"),
       ("하이일드 스프레드", f"{hy:.2f}%" if hy else "미확인", ("yes" if hy >= 5 else "half" if hy >= 4 else "no") if hy else "wait"),
       ("원달러 환율", f"{FX['value']:,.1f}원" if FX else "—", "info")]

ok = cnt[0]
if ok >= 3:
    CONCL = f"<b>⚠️ 진입 신호</b> — 핵심 지표 {ok}개 충족. 분할 진입 계획 점검."
elif cnt[0] + cnt[1] >= 3:
    CONCL = f"<b>결론</b> — 공포가 커지는 중. 충족 {cnt[0]} · 부분 {cnt[1]}.<br>VIX 40~50 급등과 시장폭 붕괴 확인까지 <b>대기</b>."
else:
    CONCL = f"<b>결론</b> — 시장 전체의 항복 신호 아직 없음. 충족 {cnt[0]} · 부분 {cnt[1]}.<br>기존 계획대로 <b>대기</b>."
NOTE = "자동 수집: 야후 파이낸스 · CNN · FRED · 위키피디아(S&P500 구성종목) / 수동: AAII · BofA · 투자 조언 아님"
lab = {"no": "미충족", "half": "부분 충족", "wait": "대기", "info": "참고", "yes": "충족"}
rows = "".join(f'<tr><td class=nm>{a}</td><td class=cr>{b}</td><td class=v>{c}</td><td class=dt>{d}</td><td><span class="st {e}">{lab[e]}</span><div class=cm>{f}</div></td></tr>' for a, b, c, d, e, f in core)
subs = "".join(f'<div class=sb><div class=sn>{a}</div><div class=sv>{b}</div><span class="st sm {c}">{lab[c]}</span></div>' for a, b, c in sub)
g = dict(rows=rows, subs=subs, BADGE=BADGE, SC=cnt, CONCL=CONCL, NOTE=NOTE)
exec(open("tpl_check.py").read(), g); open("out/check.html", "w").write(g["html"])

# ---------- 요약 ----------
wd = "월화수목금토일"[dt.date.fromisoformat(base).weekday()]
lines = []
if ok >= 3 or (V["max20"] >= 50 and V["close"] < V["max20"]):
    lines.append("⚠️ 진입 신호")
lines += [f"기준: {md(base)}({wd}) 미국장 종가",
          f"SOXL ${S['close']:,.2f} ({S['chg_pct']:+.2f}%) · 고점 대비 {S['drawdown_pct']}%",
          f"나스닥 {Q['close']:,.0f} ({Q['chg_pct']:+.2f}%) · 고점 대비 {Q['drawdown_pct']}%",
          f"VIX {V['close']} ({V['chg_pct']:+.1f}%)" + (f" · 공탐 {FG['score']:.0f}" if FG else ""),
          f"점검표: 충족 {cnt[0]}/5 · 부분 {cnt[1]}",
          f"진입까지: VIX 종가 50까지 {max(0, 50 - V['close']):.1f}p · 나스닥 -20%까지 {max(0, Q['drawdown_pct'] + 20):.1f}%p"]
if D.get("errors"):
    lines.append("수집 실패: " + ", ".join(e.split(":")[0] for e in D["errors"]))
lines.append("투자 조언 아님")
open("out/summary.txt", "w").write("\n".join(lines))
print("\n".join(lines))
