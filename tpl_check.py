html=f"""<html><head><meta charset=utf-8><style>
*{{box-sizing:border-box}}
body{{font-family:'Noto Sans CJK KR';margin:0;padding:64px;background:#fff;color:#111827;width:2000px}}
.top{{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:34px}}
h1{{font-size:60px;margin:0;font-weight:900;letter-spacing:-1.5px}}
.sub{{font-size:26px;color:#6b7280;margin-top:14px}}
.badge{{font-size:26px;font-weight:800;background:#111827;color:#fff;border-radius:999px;padding:10px 28px}}
.score{{display:flex;gap:22px;margin-bottom:34px}}
.sc{{flex:1;border-radius:18px;padding:24px 30px;display:flex;align-items:center;justify-content:space-between}}
.sc .t{{font-size:26px;font-weight:700}} .sc .n{{font-size:64px;font-weight:900}}
.s1{{background:#ecfdf5;color:#047857}} .s2{{background:#fffbeb;color:#b45309}} .s3{{background:#fef2f2;color:#b91c1c}} .s4{{background:#f3f4f6;color:#4b5563}}
table{{border-collapse:collapse;width:100%;font-size:30px}}
thead th{{font-size:23px;font-weight:700;color:#fff;background:#1f2937;padding:18px 18px;text-align:left}}
td{{padding:24px 18px;border-bottom:2px solid #e5e7eb;vertical-align:middle}}
tr:nth-child(even) td{{background:#f9fafb}}
td.nm{{font-weight:900;font-size:31px;width:430px}} td.cr{{color:#4b5563;width:400px}}
td.v{{font-size:44px;font-weight:900;color:#1e40af;width:200px;text-align:right;padding-right:34px}}
td.dt{{color:#374151}}
.st{{display:inline-block;font-size:24px;font-weight:900;padding:8px 18px;border-radius:10px;color:#fff}}
.no{{background:#dc2626}} .half{{background:#f59e0b}} .yes{{background:#059669}} .wait{{background:#6b7280}} .info{{background:#2563eb}}
.cm{{font-size:21px;color:#6b7280;margin-top:8px}}
h2{{font-size:34px;font-weight:900;margin:46px 0 18px}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}}
.sb{{background:#f9fafb;border:2px solid #e5e7eb;border-radius:16px;padding:22px 26px;position:relative}}
.sn{{font-size:23px;color:#4b5563;font-weight:700}} .sv{{font-size:32px;font-weight:900;margin-top:8px}}
.st.sm{{position:absolute;top:20px;right:22px;font-size:19px;padding:5px 12px}}
.con{{margin-top:40px;background:#111827;color:#fff;border-radius:18px;padding:30px 36px;font-size:28px;line-height:1.65}}
.con b{{color:#fbbf24}}
.note{{font-size:20px;color:#9ca3af;margin-top:22px}}
</style></head><body>
<div class=top><div><h1>바닥 신호 점검표 — 핵심 지표</h1>
<div class=sub>SOXL 진입 판단용 · 3개 이상 동시 충족 시 1·2차 진입, 4개 이상이면 비중 확대</div></div>
<div class=badge>{BADGE}</div></div>
<div class=score>
<div class="sc s1"><span class=t>충족</span><span class=n>{SC[0]}</span></div>
<div class="sc s2"><span class=t>부분 충족</span><span class=n>{SC[1]}</span></div>
<div class="sc s3"><span class=t>미충족</span><span class=n>{SC[2]}</span></div>
<div class="sc s4"><span class=t>판단 대기</span><span class=n>{SC[3]}</span></div>
</div>
<table><thead><tr><th>지표</th><th>바닥 기준</th><th style="text-align:right;padding-right:34px">현재</th><th>추이</th><th>판정</th></tr></thead><tbody>{rows}</tbody></table>
<h2>보조 지표</h2><div class=grid>{subs}</div>
<div class=con>{CONCL}</div>
<div class=note>{NOTE}</div>
</body></html>"""

