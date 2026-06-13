# -*- coding: utf-8 -*-
"""
mAb 인과 네트워크 그래프 그리기 (교육용)
=======================================
step3 에서 만든 엣지 요약 CSV(cause, relationship, effect, frequency ...)를
읽어서 D3.js 웹 시각화와 '똑같은 색 규칙'으로 그래프를 그립니다.

- 노드 색 = 6개 도메인 카테고리
- 노드 크기 = 등장 빈도(frequency 합)
- 화살표 색 = 관계의 방향성(초록=안정화, 빨강=불안정화, 회색=중립)

실행:  python draw_graph.py
결과:  ../images/ 폴더에 PNG 4장 저장
"""
import os
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("Agg")                      # 화면 없이 파일로만 저장
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# ── 한글 폰트 ── koreanize_matplotlib 우선(자동), 없으면 시스템 폰트 폴백 ──
try:
    import koreanize_matplotlib            # pip install koreanize-matplotlib
except Exception:
    for _f in ["Malgun Gothic", "AppleGothic", "NanumGothic"]:
        try:
            plt.rcParams["font.family"] = _f
            break
        except Exception:
            continue
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
CSV  = os.path.join(HERE, "..", "data", "mab_causal_edges_summary.csv")
OUT  = os.path.join(HERE, "..", "images")
os.makedirs(OUT, exist_ok=True)

# ── 1) D3 시각화와 동일한 색 규칙 ───────────────────────────────────
# (1-A) 노드 카테고리 색  ── index.html 범례와 동일
CAT_COLOR = {
    "sequence":        "#c4b5fd",   # 연보라  : 아미노산 서열
    "structure":       "#a78bfa",   # 보라    : 3차 구조
    "formulation":     "#34d399",   # 초록    : 제형(부형제/완충액)
    "stress":          "#fbbf24",   # 노랑    : 스트레스 조건
    "stability":       "#f87171",   # 빨강    : 안정성/분해 지표
    "quality_outcome": "#fb923c",   # 주황    : 품질 결과(CQA)
}
CAT_KOR = {
    "sequence": "Sequence(서열)", "structure": "Structure(구조)",
    "formulation": "Formulation(제형)", "stress": "Stress(스트레스)",
    "stability": "Stability(안정성)", "quality_outcome": "Quality(품질결과)",
}

# (1-B) 관계 → 방향성(색)  ── index.html REL_CONFIG 와 동일
POSITIVE = {"stabilizes", "decreases", "inhibits", "prevents", "shields"}
NEGATIVE = {"destabilizes", "increases", "promotes", "induces", "aggregates",
            "oxidizes", "deamidates", "isomerizes", "fragments", "unfolds",
            "adsorbs", "precipitates", "degrades", "denatures"}
# 그 외(modifies, correlates, binds, requires ...)는 중립

def rel_color(rel: str) -> str:
    if rel in POSITIVE: return "#22c55e"   # 초록: 좋은 방향(안정화/억제)
    if rel in NEGATIVE: return "#ef4444"   # 빨강: 나쁜 방향(불안정/촉진)
    return "#94a3b8"                       # 회색: 중립(상관/수식)

# ── 2) 데이터 읽기 ──────────────────────────────────────────────────
df = pd.read_csv(CSV)
print(f"엣지 {len(df):,}개, 노드(원인) {df['cause'].nunique()} / (결과) {df['effect'].nunique()}")

# 노드별 카테고리 사전 (원인/결과 양쪽에서 모음)
node_cat = {}
for _, r in df.iterrows():
    node_cat.setdefault(str(r["cause"]),  str(r["category_cause"]))
    node_cat.setdefault(str(r["effect"]), str(r["category_effect"]))

# 노드별 총 빈도(크기용) = 들어오고 나가는 frequency 합
strength = {}
for _, r in df.iterrows():
    strength[str(r["cause"])]  = strength.get(str(r["cause"]),  0) + int(r["frequency"])
    strength[str(r["effect"])] = strength.get(str(r["effect"]), 0) + int(r["frequency"])


# ════════════════════════════════════════════════════════════════════
# 그림 1. 관계 유형 분포 (방향성 색으로)
# ════════════════════════════════════════════════════════════════════
def fig1_relation_distribution():
    vc = df["relationship"].value_counts().head(15)[::-1]
    colors = [rel_color(r) for r in vc.index]
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(vc.index, vc.values, color=colors, edgecolor="white")
    for y, v in enumerate(vc.values):
        ax.text(v + max(vc.values) * 0.01, y, f"{v:,}", va="center", fontsize=9)
    ax.set_title("관계(relationship) 유형 분포 Top 15\n초록=안정화 · 빨강=불안정화 · 회색=중립",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("엣지 수")
    legend = [Line2D([0],[0],color="#22c55e",lw=8,label="Positive (안정화/억제)"),
              Line2D([0],[0],color="#ef4444",lw=8,label="Negative (불안정/촉진)"),
              Line2D([0],[0],color="#94a3b8",lw=8,label="Neutral (상관/수식)")]
    ax.legend(handles=legend, loc="lower right", fontsize=9)
    plt.tight_layout()
    p = os.path.join(OUT, "01_relation_distribution.png")
    plt.savefig(p, dpi=150, bbox_inches="tight"); plt.close()
    print("저장:", p)


# ════════════════════════════════════════════════════════════════════
# 그림 2. 허브 노드 Top 15 (카테고리 색으로)
# ════════════════════════════════════════════════════════════════════
def fig2_top_hubs():
    s = pd.Series(strength).sort_values(ascending=False).head(15)[::-1]
    colors = [CAT_COLOR.get(node_cat.get(n, ""), "#888888") for n in s.index]
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(s.index, s.values, color=colors, edgecolor="white")
    for y, v in enumerate(s.values):
        ax.text(v + max(s.values) * 0.01, y, f"{v:,}", va="center", fontsize=9)
    ax.set_title("가장 중심이 되는 허브 노드 Top 15\n(막대 길이 = 총 등장 빈도, 색 = 도메인 카테고리)",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("총 빈도 (in + out)")
    handles = [Line2D([0],[0],marker="o",color="w",markerfacecolor=c,markersize=11,label=CAT_KOR[k])
               for k, c in CAT_COLOR.items()]
    ax.legend(handles=handles, loc="lower right", fontsize=8.5)
    plt.tight_layout()
    p = os.path.join(OUT, "02_top_hubs.png")
    plt.savefig(p, dpi=150, bbox_inches="tight"); plt.close()
    print("저장:", p)


# ════════════════════════════════════════════════════════════════════
# 그림 3. 네트워크 '백본' — 빈도 높은 엣지만 (가독성)
# ════════════════════════════════════════════════════════════════════
def fig3_network_backbone(top_edges=120):
    sub = df.sort_values("frequency", ascending=False).head(top_edges)
    G = nx.DiGraph()
    for _, r in sub.iterrows():
        G.add_edge(str(r["cause"]), str(r["effect"]),
                   rel=str(r["relationship"]), w=int(r["frequency"]))

    pos = nx.spring_layout(G, k=0.9, iterations=200, seed=42)
    node_colors = [CAT_COLOR.get(node_cat.get(n, ""), "#888888") for n in G.nodes()]
    node_sizes  = [120 + strength.get(n, 0) * 4 for n in G.nodes()]
    edge_colors = [rel_color(G[u][v]["rel"]) for u, v in G.edges()]
    edge_widths = [0.5 + G[u][v]["w"] * 0.12 for u, v in G.edges()]

    fig, ax = plt.subplots(figsize=(15, 11))
    fig.patch.set_facecolor("#0a0e17"); ax.set_facecolor("#0a0e17")  # D3 처럼 어두운 배경
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=edge_widths,
                           alpha=0.55, arrows=True, arrowsize=9,
                           connectionstyle="arc3,rad=0.08", ax=ax)
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes,
                           edgecolors="#0a0e17", linewidths=0.5, ax=ax)
    # 라벨은 허브(빈도 상위)만
    big = sorted(G.nodes(), key=lambda n: -strength.get(n, 0))[:22]
    nx.draw_networkx_labels(G, pos, labels={n: n for n in big},
                            font_size=8, font_color="#e8ecf4", ax=ax)
    ax.set_title(f"mAb 안정성 인과 네트워크 — 빈도 상위 {top_edges}개 엣지 (백본)",
                 fontsize=15, fontweight="bold", color="#e8ecf4")
    handles = [Line2D([0],[0],marker="o",color="w",markerfacecolor=c,markersize=11,label=CAT_KOR[k])
               for k, c in CAT_COLOR.items()]
    ax.legend(handles=handles, loc="upper left", fontsize=9, framealpha=0.2,
              labelcolor="#e8ecf4")
    ax.axis("off")
    plt.tight_layout()
    p = os.path.join(OUT, "03_network_backbone.png")
    plt.savefig(p, dpi=150, bbox_inches="tight", facecolor="#0a0e17"); plt.close()
    print("저장:", p)


# ════════════════════════════════════════════════════════════════════
# 그림 4. 특정 노드 주변만 보기 (ego network) — 예: aggregation
# ════════════════════════════════════════════════════════════════════
def fig4_ego(center="aggregation", top=18):
    rel = df[(df["cause"] == center) | (df["effect"] == center)].copy()
    rel = rel.sort_values("frequency", ascending=False).head(top)
    G = nx.DiGraph()
    for _, r in rel.iterrows():
        G.add_edge(str(r["cause"]), str(r["effect"]),
                   rel=str(r["relationship"]), w=int(r["frequency"]))
    if center not in G:        # 데이터에 없으면 가장 큰 허브로 대체
        center = pd.Series(strength).idxmax()
    pos = nx.spring_layout(G, k=1.2, iterations=200, seed=7)
    node_colors = [CAT_COLOR.get(node_cat.get(n, ""), "#888888") for n in G.nodes()]
    node_sizes  = [2600 if n == center else 900 for n in G.nodes()]
    edge_colors = [rel_color(G[u][v]["rel"]) for u, v in G.edges()]
    edge_widths = [1.0 + G[u][v]["w"] * 0.15 for u, v in G.edges()]

    fig, ax = plt.subplots(figsize=(13, 9))
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=edge_widths,
                           alpha=0.7, arrows=True, arrowsize=16,
                           connectionstyle="arc3,rad=0.08", ax=ax)
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes,
                           edgecolors="#333", linewidths=1.0, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=9, ax=ax)
    # 엣지에 관계 이름 표시
    elabels = {(u, v): G[u][v]["rel"] for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=elabels, font_size=7,
                                 font_color="#444", ax=ax,
                                 bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.6))
    ax.set_title(f"'{center}' 노드를 중심으로 한 인과 이웃 (ego network)",
                 fontsize=14, fontweight="bold")
    ax.axis("off")
    plt.tight_layout()
    p = os.path.join(OUT, "04_ego_aggregation.png")
    plt.savefig(p, dpi=150, bbox_inches="tight"); plt.close()
    print("저장:", p)


if __name__ == "__main__":
    fig1_relation_distribution()
    fig2_top_hubs()
    fig3_network_backbone()
    fig4_ego()
    print("\n완료! ../images 폴더를 확인하세요.")
