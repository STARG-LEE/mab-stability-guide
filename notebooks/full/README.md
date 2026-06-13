# 🔬 전체 연구 파이프라인 재현 (step1 → step4)

원본 연구의 **4단계 파이프라인을 그대로** 따라할 수 있게 만든 재현용 노트북입니다.
사설 DB(개인 MySQL 서버)를 제거하고 **CSV 파일로 단계를 연결**해서, OpenAI 키만 있으면 누구나 Colab에서 돌릴 수 있습니다.

```
step1 ─▶ step1_abstracts.csv ─▶ step2 ─▶ step2_filtered.csv ─▶ step3 ─▶ step3_edges.csv ─▶ step4 (GATED)
 수집                              필터                            추출·표준화·집계              모델 학습
```

| 단계 | 노트북 | 입력 | 출력 | 필요 | Colab |
|---|---|---|---|---|---|
| 1 | `step1_collect.ipynb` | PubMed(공개) | `step1_abstracts.csv` | 인터넷 | [열기](https://colab.research.google.com/github/STARG-LEE/mab-stability-guide/blob/main/notebooks/full/step1_collect.ipynb) |
| 2 | `step2_filter.ipynb` | step1 CSV | `step2_filtered.csv` | OpenAI 키 | [열기](https://colab.research.google.com/github/STARG-LEE/mab-stability-guide/blob/main/notebooks/full/step2_filter.ipynb) |
| 3 | `step3_extract.ipynb` | step2 CSV | `step3_edges.csv` | OpenAI 키 | [열기](https://colab.research.google.com/github/STARG-LEE/mab-stability-guide/blob/main/notebooks/full/step3_extract.ipynb) |
| 4 | `step4_gated.ipynb` | step3 CSV (또는 공개 엣지) | `mab_gated.pt`, `results.json` | **GPU 런타임** | [열기](https://colab.research.google.com/github/STARG-LEE/mab-stability-guide/blob/main/notebooks/full/step4_gated.ipynb) |

## 어떻게 따라하나
1. **순서대로** step1 → 2 → 3 → 4 를 같은 Colab 세션에서 이어 실행하면 CSV가 자동으로 넘어갑니다.
   (세션을 새로 열면, 앞 단계가 만든 CSV를 왼쪽 파일창에 **업로드**하세요.)
2. **step2·3** 은 OpenAI 키가 필요합니다 — Colab 왼쪽 🔑(보안 비밀)에 `OPENAI_API_KEY` 등록.
3. **step4** 는 GPU가 필요합니다 — Colab 메뉴 **런타임 → 런타임 유형 변경 → T4 GPU**.

## 규모 / 비용
- 기본값은 **빠르게 따라하도록 작게** 설정되어 있습니다(step1 검색어 3개·40편, step3 30편).
- 각 노트북 위쪽의 `MAX_RESULTS_PER_QUERY`, `LIMIT` 등을 키우면 규모를 늘릴 수 있습니다.
- 모델(`gpt-4o-mini`) 기준 step2+3 합쳐 **수백 원** 수준(소규모 기준). 원본 논문은 `gpt-5-mini` 사용.
- 소규모면 엣지가 적어 **성능 수치는 논문과 다릅니다.** step4는 데이터가 없으면 **공개 엣지(2,436개)** 를 자동으로 받아 학습합니다.

## ⚠️ 보안 안내
- 이 노트북들에는 **DB 비밀번호·서버 주소가 전혀 없습니다**(전부 제거). 안심하고 공유하세요.
- 반대로 **원본 step1~4(개인 DB 비번이 박혀 있는 버전)는 공개 업로드하지 마세요.**

## 더 간단히 체험만?
전체 과정이 부담되면, 한 노트북으로 수집→그래프까지 한 번에 보는 **간편 버전**도 있습니다:
- `../01_pipeline_practice.ipynb` (간편 파이프라인) · `../02_draw_graph.ipynb` (그래프만, 키 불필요)
- 친절한 웹 안내서: https://starg-lee.github.io/mab-stability-guide/guide/
