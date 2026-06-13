# -*- coding: utf-8 -*-
"""교육용 개념 다이어그램 3종을 깔끔한 SVG 벡터로 생성.
   guide/img/ 와 images/ 양쪽에 .svg 저장."""
import os

GUIDE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "guide", "img")
DOCS  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "images")
FONT = "'Pretendard','Malgun Gothic','Apple SD Gothic Neo','Noto Sans KR',sans-serif"

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def header(w, h):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="{FONT}">
<defs>
<filter id="sh" x="-20%" y="-20%" width="140%" height="140%">
  <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#0f172a" flood-opacity="0.18"/>
</filter>
<marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
  <path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/>
</marker>
{GRADS}
</defs>
<rect x="0" y="0" width="{w}" height="{h}" fill="white"/>
'''

def grad(gid, c1, c2):
    return (f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>')

GRADS = "".join([
    grad("gBlue", "#3b82f6", "#1d4ed8"), grad("gTeal", "#10b981", "#047857"),
    grad("gPurple", "#8b5cf6", "#6d28d9"), grad("gAmber", "#f59e0b", "#d97706"),
    grad("gPink", "#ec4899", "#be185d"), grad("gCyan", "#0ea5e9", "#0369a1"),
    grad("gIndigo", "#6366f1", "#4338ca"), grad("gViolet", "#a855f7", "#7e22ce"),
    grad("gRed", "#f87171", "#dc2626"), grad("gOut", "#fb923c", "#ea580c"),
])

def box(x, y, w, h, fill, lines, sizes=None, colors=None, rx=18, dash=False, anchor_lines=True):
    """둥근 박스 + 가운데 정렬 여러 줄 텍스트."""
    stroke = 'stroke="#be185d" stroke-width="2.5" stroke-dasharray="7 5"' if dash else ''
    s = f'<g filter="url(#sh)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" {stroke}/></g>'
    n = len(lines)
    sizes = sizes or [15]*n
    colors = colors or ["#ffffff"]*n
    total = sum(sizes) + (n-1)*7
    cy = y + h/2 - total/2
    for i, ln in enumerate(lines):
        cy += sizes[i]
        weight = 800 if i == 0 else 600
        s += (f'<text x="{x+w/2}" y="{cy}" text-anchor="middle" font-size="{sizes[i]}" '
              f'font-weight="{weight}" fill="{colors[i]}">{esc(ln)}</text>')
        cy += 7
    return s

def badge(x, y, num, color):
    return (f'<circle cx="{x}" cy="{y}" r="14" fill="#ffffff" filter="url(#sh)"/>'
            f'<text x="{x}" y="{y+5}" text-anchor="middle" font-size="15" font-weight="800" fill="{color}">{num}</text>')

def arrow(x1, y, x2):
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#94a3b8" stroke-width="3" marker-end="url(#arr)"/>'

def text(x, y, s, size=14, color="#475569", weight=700, anchor="middle", italic=False):
    st = ' font-style="italic"' if italic else ''
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{color}"{st}>{esc(s)}</text>'

def save(name, svg):
    for d in (GUIDE, DOCS):
        with open(os.path.join(d, name), "w", encoding="utf-8") as f:
            f.write(svg)
    print("saved", name)


# ════════════════ 1) 파이프라인 ════════════════
def pipeline():
    W, H = 1100, 250
    s = header(W, H).replace("{GRADS}", GRADS)
    s += text(W/2, 36, "AI 파이프라인 — 논문에서 지식그래프, 그리고 예측까지", size=22, color="#0f172a", weight=800)
    bw, bh, by = 162, 110, 64
    xs = [16, 232, 448, 664, 880]
    grads = ["url(#gBlue)", "url(#gTeal)", "url(#gPurple)", "url(#gAmber)", "url(#gPink)"]
    badgecol = ["#1d4ed8", "#047857", "#6d28d9", "#d97706", "#be185d"]
    labels = [["PubMed", "논문 수집", "62,281편"],
              ["관련 논문", "선별", "5,576편"],
              ["인과 엣지", "추출·표준화", "32,939개"],
              ["네트워크", "그래프", "(실습 결승선)"],
              ["mAb-GATED", "예측", "(개념)"]]
    nums = ["1", "2", "3", "4", "▶"]
    procs = ["GPT 필터", "GPT 추출", "시각화", "학습"]
    cy = by + bh/2
    for i, x in enumerate(xs):
        s += box(x, by, bw, bh, grads[i], labels[i],
                 sizes=[16, 14, 14], colors=["#fff", "#fff", "#e2e8f0"], dash=(i == 4))
        s += badge(x+20, by+20, nums[i], badgecol[i])
        if i < 4:
            gx1, gx2 = x+bw+6, xs[i+1]-6
            s += arrow(gx1, cy, gx2)
            s += text((gx1+gx2)/2, by+bh+24, procs[i], size=12.5, color="#64748b", weight=700)
    s += text(W/2, H-14, "← 학생 실습은 '네트워크 그래프'까지  ·  GATED는 개념 설명 →",
              size=14, color="#64748b", weight=600, italic=True)
    s += "</svg>"
    save("diagram_pipeline.svg", s)


# ════════════════ 2) 인과 사슬 ════════════════
def chain():
    W, H = 1240, 300
    s = header(W, H).replace("{GRADS}", GRADS)
    s += text(W/2, 38, "안정성을 둘러싼 두 질문 = 인과 사슬", size=22, color="#0f172a", weight=800)
    # 결정요인 컨테이너
    cx, cy_, cw, ch = 24, 78, 384, 180
    s += f'<rect x="{cx}" y="{cy_}" width="{cw}" height="{ch}" rx="20" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1.5"/>'
    s += text(cx+cw/2, cy_+28, "결정요인 (Determinants)", size=15.5, color="#334155", weight=800)
    chips = [("서열", "sequence", "#c4b5fd"), ("구조", "structure", "#a78bfa"),
             ("제형", "formulation", "#34d399"), ("스트레스", "stress", "#fbbf24")]
    chw, chh = 168, 60
    cxs = [cx+18, cx+cw-18-chw]
    cys = [cy_+44, cy_+44+chh+12]
    for i, (ko, en, col) in enumerate(chips):
        bx = cxs[i % 2]; byy = cys[i//2]
        s += f'<g filter="url(#sh)"><rect x="{bx}" y="{byy}" width="{chw}" height="{chh}" rx="14" fill="{col}"/></g>'
        s += text(bx+chw/2, byy+27, ko, size=15, color="#1e293b", weight=800)
        s += text(bx+chw/2, byy+45, en, size=12, color="#334155", weight=600)
    midy = cy_ + ch/2
    # 안정성 (라벨이 칸과 겹치지 않게 박스 사이 간격을 넓게)
    stx, stw = 558, 150
    s += box(stx, midy-58, stw, 116, "url(#gRed)",
             ["안정성 지표", "Stability", "응집·점도·산화…"], sizes=[16, 13, 14],
             colors=["#fff", "#fee2e2", "#fff"])
    # 결과
    oux, ouw = 858, 362
    s += box(oux, midy-58, ouw, 116, "url(#gOut)",
             ["임상·품질 결과", "Outcomes", "효능·면역원성·약동학"], sizes=[16, 13, 14],
             colors=["#fff", "#ffedd5", "#fff"])
    # 화살표 + Q 라벨
    s += arrow(cx+cw+6, midy, stx-6)
    s += text((cx+cw+stx)/2, midy-16, "Q1  무엇이 영향?", size=13.5, color="#334155", weight=800)
    s += arrow(stx+stw+6, midy, oux-6)
    s += text((stx+stw+oux)/2, midy-16, "Q2  무엇에 영향?", size=13.5, color="#334155", weight=800)
    s += text(W/2, H-16, "그래프도 이 순서로 읽어요 — 왼쪽 결정요인 → 가운데 안정성 → 오른쪽 결과",
              size=14, color="#475569", weight=700)
    s += "</svg>"
    save("diagram_chain.svg", s)


# ════════════════ 3) GATED 빈칸 채우기 ════════════════
def gated():
    W, H = 1140, 250
    s = header(W, H).replace("{GRADS}", GRADS)
    s += text(W/2, 36, "mAb-GATED = 빈칸 채우기 (마스킹된 안정성 노드 예측)", size=22, color="#0f172a", weight=800)
    by, bh = 66, 112
    midy = by + bh/2
    # 입력
    inx, inw = 16, 184
    s += box(inx, by, inw, bh, "url(#gCyan)", ["입력", "6개 카테고리", "이웃(원인 조건)"],
             sizes=[16, 14, 14], colors=["#fff", "#e0f2fe", "#fff"])
    s += text(inx+inw/2, by+bh+22, "예) 고농도·진탕·low pH", size=12, color="#0369a1", weight=700)
    # 3단계
    stages = [(["① PubMedBERT", "의미 임베딩"], "url(#gIndigo)"),
              (["② GAT", "이웃 정보 집약"], "url(#gPurple)"),
              (["③ Transformer", "인코더–디코더"], "url(#gViolet)")]
    sw = 176
    sxs = [240, 240+sw+44, 240+2*(sw+44)]
    for (lines, gr), x in zip(stages, sxs):
        s += box(x, by, sw, bh, gr, lines, sizes=[15.5, 14], colors=["#fff", "#ede9fe"])
    # 출력 (정답/가려진 노드/??? 를 3줄로 깔끔히 스택)
    oux, ouw = sxs[-1]+sw+44, 204
    s += box(oux, by, ouw, bh, "url(#gRed)", ["정답", "가려진 안정성 노드", "( ??? )"],
             sizes=[15, 12.5, 21], colors=["#fff", "#fee2e2", "#fff"])
    # 화살표 체인
    pts = [inx+inw] + sxs + [oux]
    ends = sxs + [oux]
    starts = [inx+inw, sxs[0]+sw, sxs[1]+sw, sxs[2]+sw]
    for x1, x2 in zip(starts, ends):
        s += arrow(x1+6, midy, x2-6)
    s += text(W/2, H-14, "이웃만 보고 가려진 안정성 지표를 맞힌다 → 잘 맞히면 '문헌 패턴은 학습 가능'",
              size=14, color="#64748b", weight=600, italic=True)
    s += "</svg>"
    save("diagram_gated.svg", s)


if __name__ == "__main__":
    pipeline(); chain(); gated()
    print("done -> guide/img and images (.svg)")
