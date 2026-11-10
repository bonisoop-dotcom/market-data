R=[
("2011",("11.02.17","11.10.03",228,"-72.6","+265","+713",1337,"$1.25 → $0.34"),("11.04.29","11.10.03",157,"-18.7","+23","+123",1386,"2,873.54 → 2,335.83")),
("2015–16",("15.06.01","16.02.11",255,"-62.9","+170","+1,205",760,"$2.78 → $1.03"),("15.07.20","16.02.11",206,"-18.2","+22","+90",930,"5,218.86 → 4,266.84")),
("2018",("18.03.12","18.12.24",287,"-66.7","+200","+386",422,"$13.46 → $4.48"),("18.08.29","18.12.24",117,"-23.6","+31","+59",422,"8,109.69 → 6,192.92")),
("2020",("20.02.19","20.03.20",30,"-80.4","+410","+1,612",647,"$21.78 → $4.27"),("20.02.19","20.03.23",33,"-30.1","+43","+134",606,"9,817.18 → 6,860.67")),
("2022",("21.12.27","22.10.14",291,"-90.5","+953","+890",635,"$73.09 → $6.94"),("21.11.19","22.12.28",404,"-36.4","+57","+98",719,"16,057.44 → 10,213.29")),
("2024–25",("24.07.10","25.04.08",272,"-88.0","+731","+3,546",440,"$68.74 → $8.25"),("24.12.16","25.04.08",113,"-24.3","+32","+81",546,"20,173.89 → 15,267.91")),
("2026 현재",CUR_S,CUR_Q),
("평균",(None,None,227,"-76.9",None,None,707,""),(None,None,172,"-25.2",None,None,768,"")),
]
def cells(x,cur):
    a,b,d,dd,need,up,days,px=x
    per = "" if a is None else f'{a} → {"<span class=live>진행 중</span>" if b is None else b}'
    return (f'<td class=dt>{per}</td><td class=px>{px}</td><td class=n>{d}{"일째" if cur else "일"}</td>'
            f'<td class="n neg">{dd}%</td><td class="n mute">{need+"%" if need else ("—" if a else "")}</td>'
            f'<td class="n pos">{up+"%" if up else ("—" if a else "")}</td><td class="n rise">{f"{days:,}일" if days else "—"}</td>')
body=""
for yr,s,q in R:
    cls = "cur" if "현재" in yr else ("avg" if yr=="평균" else "")
    cur = cls=="cur"
    body+=(f'<tbody class="{cls}"><tr class=s><th class=yr rowspan=2>{yr}</th><td class=tag><span class="pill ps">SOXL</span></td>{cells(s,cur)}</tr>'
           f'<tr class=q><td class=tag><span class="pill pq">나스닥</span></td>{cells(q,cur)}</tr></tbody>')
html=f"""<html><head><meta charset=utf-8><style>
*{{box-sizing:border-box}}
body{{font-family:'Noto Sans CJK KR';margin:0;padding:64px 64px 56px;background:#fff;color:#111827;width:2400px}}
.top{{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:38px}}
h1{{font-size:60px;margin:0;font-weight:900;letter-spacing:-1.5px}}
.sub{{font-size:26px;color:#6b7280;margin-top:14px}}
.badge{{font-size:26px;font-weight:800;background:#111827;color:#fff;border-radius:999px;padding:10px 28px}}
table{{border-collapse:collapse;width:100%;font-size:31px;font-variant-numeric:tabular-nums}}
thead th{{font-size:24px;font-weight:700;color:#fff;background:#1f2937;padding:18px 16px;text-align:right}}
thead th.l{{text-align:left}}
thead th:last-child{{background:#1e40af}}
td,th.yr{{padding:14px 16px}}
th.yr{{text-align:left;font-weight:900;width:200px;vertical-align:middle;font-size:32px;background:#f9fafb;border-right:1px solid #e5e7eb}}
tbody{{border-bottom:2px solid #d1d5db}}
tr.s td{{padding-top:20px}} tr.q td{{padding-bottom:20px}}
tr.q td{{background:#f5f8fd}}
td.n{{text-align:right}} td.px{{color:#111827;font-weight:700;white-space:nowrap}} tr.q td.px{{color:#1e3a8a}} tr.s td.px{{color:#7f1d1d}} td.dt{{color:#1f2937}}
td.neg{{color:#dc2626;font-weight:800}} td.pos{{color:#059669;font-weight:800}} td.mute{{color:#6b7280;font-weight:600}}
td.rise{{color:#1e40af;font-weight:900;background:#eaf0fb}}
tr.q td.rise{{background:#dfe8f8}}
.pill{{font-size:22px;font-weight:900;padding:6px 14px;border-radius:8px;color:#fff}}
.ps{{background:#dc2626}} .pq{{background:#2563eb}}
td.tag{{width:150px}}
tbody.cur th,tbody.cur td{{background:#fef3c7!important;font-weight:800}}
tbody.cur td.rise{{color:#9ca3af}}
.live{{color:#c2410c;font-weight:900}}
tbody.avg{{border-top:3px solid #111827;border-bottom:none}}
tbody.avg td{{font-weight:800}}
.foot{{display:flex;gap:26px;margin-top:36px}}
.card{{flex:1;border-radius:16px;padding:24px 30px;font-size:25px;line-height:1.7;color:#1f2937}}
.c1{{background:#fef2f2;border-left:8px solid #dc2626}} .c2{{background:#eff6ff;border-left:8px solid #2563eb}}
.card b{{font-size:28px}}
.note{{font-size:20px;color:#9ca3af;margin-top:22px}}
</style></head><body>
<div class=top><div><h1>SOXL vs 나스닥 — 역대 하락장 비교</h1>
<div class=sub>일간 종가 기준 · 저점→다음 고점 = 저점부터 다음 하락장 시작 고점까지</div></div>
<div class=badge>{BADGE}</div></div>
<table><thead><tr><th class=l>하락장</th><th class=l>구분</th><th class=l>고점 → 저점</th><th class=l>가격 (고점 → 저점)</th><th>하락기간</th><th>하락률</th><th>본전 필요</th><th>저점→다음 고점</th><th>상승기간</th></tr></thead>
{body}</table>
<div class=foot>
<div class='card c1'>{CARD1}</div>
<div class='card c2'>{CARD2}</div>
</div>
<div class=note>데이터: Yahoo Finance 등 일간 종가(분할 조정) · 평균은 과거 6회 기준 · SOXL 과거 가격은 분할 조정 기준(2026 고점과 표의 변화율로 환산) · 투자 조언 아님</div>
</body></html>"""

