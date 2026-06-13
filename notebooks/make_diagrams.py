# -*- coding: utf-8 -*-
"""교육용 개념 다이어그램 3종 (matplotlib, 한글 안전).
   1) 파이프라인 흐름   2) 두 질문=인과 사슬   3) GATED 빈칸 채우기
   출력: guide/img/ 와 images/ 양쪽에 PNG 저장."""
import os, shutil
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
try:
    import koreanize_matplotlib
except Exception:
    for _f in ["Malgun Gothic", "AppleGothic", "NanumGothic"]:
        try: plt.rcParams["font.family"] = _f; break
        except Exception: pass
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
GUIDE_IMG = os.path.join(HERE, "..", "guide", "img")
DOCS_IMG  = os.path.join(HERE, "..", "images")
os.makedirs(GUIDE_IMG, exist_ok=True)

CAT = {"seq":"#c4b5fd","str":"#a78bfa","form":"#34d399","stress":"#fbbf24",
       "stab":"#f87171","out":"#fb923c"}

def box(ax, x, y, w, h, text, fc, tc="white", fs=11, ec="none", weight="bold", r=0.06):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r*100}",
                       linewidth=1.4, facecolor=fc, edgecolor=ec, mutation_aspect=1)
    ax.add_patch(p)
    ax.text(x+w/2, y+h/2, text, ha="center", va="center", fontsize=fs,
            color=tc, fontweight=weight, linespacing=1.45)

def arrow(ax, x1, y1, x2, y2, label=None, color="#94a3b8", lw=2.4, fs=9.5):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", lw=lw, color=color,
                                shrinkA=2, shrinkB=2))
    if label:
        ax.text((x1+x2)/2, max(y1, y2)+2.5, label, ha="center", va="bottom",
                fontsize=fs, color="#475569", fontweight="bold")

def save(fig, name):
    for d in (GUIDE_IMG, DOCS_IMG):
        fig.savefig(os.path.join(d, name), dpi=150, bbox_inches="tight",
                    facecolor="white")
    plt.close(fig)
    print("saved", name)


# ── 1) 파이프라인 흐름 ────────────────────────────────────────────────
def fig_pipeline():
    fig, ax = plt.subplots(figsize=(13, 4.2)); ax.set_xlim(0, 132); ax.set_ylim(0, 46); ax.axis("off")
    ax.text(66, 43, "AI 파이프라인 — 논문에서 지식그래프, 그리고 예측까지",
            ha="center", fontsize=15, fontweight="bold", color="#1e293b")
    cols = ["#3b82f6", "#14b8a6", "#8b5cf6", "#f59e0b", "#ec4899"]
    labels = ["PubMed\n논문 수집\n62,281편", "관련 논문\n선별\n5,576편",
              "인과 엣지\n추출·표준화\n32,939개", "네트워크\n그래프\n(실습 결승선)",
              "mAb-GATED\n예측\n(개념)"]
    xs = [2, 28.5, 55, 81.5, 108]; w, h, y = 22, 19, 13
    for i,(x,c,t) in enumerate(zip(xs,cols,labels)):
        # 마지막(GATED)은 점선 테두리로 '개념'임을 표시
        box(ax, x, y, w, h, t, c, fs=10.5, ec=("#be185d" if i==4 else "none"))
        if i==4:
            ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0,rounding_size=6",
                        fill=False, linewidth=2, linestyle=(0,(4,3)), edgecolor="#be185d"))
    steplabels = ["STEP 2\nGPT 필터", "STEP 3\nGPT 추출", "시각화", "STEP 4\n학습(개념)"]
    for i in range(4):
        arrow(ax, xs[i]+w, y+h/2, xs[i+1], y+h/2, steplabels[i], lw=2.6)
    ax.text(2, 6.5, "STEP 1", fontsize=9, color="#3b82f6", fontweight="bold")
    ax.text(66, 3.4, "← 학생 실습은 '네트워크 그래프'까지 · GATED는 개념 설명 →",
            ha="center", fontsize=10, color="#64748b", style="italic")
    save(fig, "diagram_pipeline.png")


# ── 2) 두 질문 = 인과 사슬 ────────────────────────────────────────────
def fig_chain():
    fig, ax = plt.subplots(figsize=(12.5, 5.0)); ax.set_xlim(0, 130); ax.set_ylim(0, 52); ax.axis("off")
    ax.text(65, 48.5, "안정성을 둘러싼 두 질문 = 인과 사슬",
            ha="center", fontsize=15, fontweight="bold", color="#1e293b")
    # 결정요인 컨테이너
    box(ax, 2, 9, 40, 30, "", "#f1f5f9", ec="#cbd5e1", r=0.05)
    ax.text(22, 35.5, "결정요인 (Determinants)", ha="center", fontsize=11.5,
            fontweight="bold", color="#334155")
    chips = [("서열\nsequence", CAT["seq"]), ("구조\nstructure", CAT["str"]),
             ("제형\nformulation", CAT["form"]), ("스트레스\nstress", CAT["stress"])]
    cx = [5.5, 24]; cy = [21.5, 11.5]; ci = 0
    for r_ in range(2):
        for c_ in range(2):
            t,col = chips[ci]; ci += 1
            box(ax, cx[c_], cy[r_], 16.5, 8.2, t, col, tc="#1e293b", fs=9.5)
    # 안정성
    box(ax, 56, 16, 20, 16, "안정성 지표\nStability\n응집·점도·산화…", CAT["stab"], fs=10.5)
    # 결과
    box(ax, 92, 16, 32, 16, "임상·품질 결과\nOutcomes\n효능·면역원성·약동학", CAT["out"], fs=10.5)
    arrow(ax, 42, 24, 56, 24, "Q1  무엇이 영향?", color="#64748b", lw=2.8, fs=10.5)
    arrow(ax, 76, 24, 92, 24, "Q2  무엇에 영향?", color="#64748b", lw=2.8, fs=10.5)
    ax.text(65, 5.5, "그래프도 이 순서로 읽어요 — 왼쪽 결정요인 → 가운데 안정성 → 오른쪽 결과",
            ha="center", fontsize=10.5, color="#475569", fontweight="bold")
    save(fig, "diagram_chain.png")


# ── 3) GATED 빈칸 채우기 ──────────────────────────────────────────────
def fig_gated():
    fig, ax = plt.subplots(figsize=(13, 4.8)); ax.set_xlim(0, 134); ax.set_ylim(0, 50); ax.axis("off")
    ax.text(67, 46.5, "mAb-GATED = 빈칸 채우기 (마스킹된 안정성 노드 예측)",
            ha="center", fontsize=15, fontweight="bold", color="#1e293b")
    # 입력
    box(ax, 1, 12, 23, 22, "입력\n6개 카테고리\n이웃(원인 조건)", "#0ea5e9", fs=10.5)
    ax.text(12.5, 8, "예) 고농도·진탕·low pH", ha="center", fontsize=8.6, color="#0369a1")
    # 3단계 두뇌
    stages = [("① PubMedBERT\n의미 임베딩", "#6366f1"),
              ("② GAT\n이웃 정보 집약", "#8b5cf6"),
              ("③ Transformer\n인코더–디코더", "#a855f7")]
    xs = [30, 54.5, 79]; w, h, y = 21, 20, 13
    for (t,c),x in zip(stages, xs):
        box(ax, x, y, w, h, t, c, fs=10)
    # 출력(빈칸)
    box(ax, 104, 12, 27, 22, "정답\n가려진 안정성 노드", "#f87171", fs=10.5)
    ax.text(117.5, 17.5, "( ??? )", ha="center", fontsize=15, color="white", fontweight="bold")
    pts = [24, 30, 51, 54.5, 75, 79, 100, 104]
    for i in range(0, len(pts), 2):
        arrow(ax, pts[i], y+h/2, pts[i+1], y+h/2, lw=2.4)
    ax.text(67, 4, "이웃만 보고 가려진 안정성 지표를 맞힌다 → 잘 맞히면 '문헌 패턴은 학습 가능'",
            ha="center", fontsize=10, color="#64748b", style="italic")
    save(fig, "diagram_gated.png")


if __name__ == "__main__":
    fig_pipeline(); fig_chain(); fig_gated()
    print("done -> guide/img and images")
