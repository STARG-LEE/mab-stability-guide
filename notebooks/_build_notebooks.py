# -*- coding: utf-8 -*-
"""두 개의 실습 노트북(.ipynb)을 생성하는 빌더."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))

def md(src):  return {"cell_type": "markdown", "metadata": {}, "source": src}
def code(src):return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": src}

def write_nb(cells, path):
    nb = {"cells": cells,
          "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3"},
                       "language_info": {"name": "python"}},
          "nbformat": 4, "nbformat_minor": 5}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print("wrote", path)


# ════════════════════════════════════════════════════════════════════
#  노트북 1 : 전체 파이프라인 실습 (크롤링 → 필터 → 추출 → 그래프)
# ════════════════════════════════════════════════════════════════════
n1 = []

n1.append(md(
"# 🧪 실습 1 — mAb 안정성 인과 네트워크 만들기 (PubMed → GPT → 그래프)\n"
"\n"
"이 노트북 하나로 **논문 수집 → 관련 논문 골라내기 → 인과관계 추출 → 그래프 그리기**까지 직접 해봅니다.\n"
"\n"
"```\n"
"STEP 1  PubMed에서 논문 초록 수집      (무료, 인터넷만 있으면 됨)\n"
"STEP 2  GPT로 '안정성과 관련된' 논문만 필터링   (OpenAI 키 필요 · 없으면 건너뜀)\n"
"STEP 3  GPT로 (원인 → 관계 → 결과) 추출        (OpenAI 키 필요 · 없으면 샘플 사용)\n"
"STEP 4  내가 만든 표를 네트워크 그래프로 시각화   (무료)\n"
"```\n"
"\n"
"> 💡 **OpenAI 키가 없어도 괜찮아요.** STEP 2·3은 건너뛰고, 연구팀이 공개한 실제 데이터(샘플)로 STEP 4 그래프를 그릴 수 있습니다.\n"
"> 키가 있으면 아주 적은 양(논문 20편 정도, 수십 원 수준)만 써서 '내 그래프'를 직접 만들 수 있습니다.\n"
"\n"
"> ⚠️ GATED **모델 학습(STEP 5)** 은 이 실습 범위가 아닙니다. 개념은 마지막 셀과 교안에서 설명합니다."
))

n1.append(md("## 0. 준비 — 패키지 설치\n\n`koreanize-matplotlib` 는 그래프의 **한글 깨짐(□□□)** 을 막아주는 라이브러리예요(Colab에 한글 폰트가 없어 필요)."))
n1.append(code(
"!pip install -q requests xmltodict pandas networkx matplotlib koreanize-matplotlib openai\n"
"print('설치 완료')"
))

# ---- STEP 1 ----
n1.append(md(
"## STEP 1 — PubMed에서 논문 초록 수집\n"
"\n"
"PubMed(미국 국립의학도서관)의 무료 API로 'mAb 안정성' 관련 논문 제목·초록을 가져옵니다.\n"
"검색어를 바꾸면 다른 주제도 모을 수 있어요. (실습이니 논문 수는 적게!)"
))
n1.append(code(
"import requests, xmltodict, time, pandas as pd\n"
"\n"
"PUBMED_EMAIL = 'student@example.com'   # NCBI 권장: 아무 이메일\n"
"QUERIES = [\n"
"    '\"monoclonal antibody\" AND \"aggregation\" AND \"formulation\"',\n"
"    '\"monoclonal antibody\" AND \"viscosity\"',\n"
"]\n"
"MAX_PER_QUERY = 40   # 쿼리당 최대 논문 수 (실습용으로 작게)\n"
"\n"
"def search_pubmed(query, retmax=40):\n"
"    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'\n"
"    p = {'db':'pubmed','term':query,'retmax':retmax,'retmode':'json','email':PUBMED_EMAIL}\n"
"    r = requests.get(url, params=p, timeout=30); r.raise_for_status()\n"
"    return r.json().get('esearchresult',{}).get('idlist',[])\n"
"\n"
"def fetch_abstracts(pmids):\n"
"    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'\n"
"    out = []\n"
"    for i in range(0, len(pmids), 100):\n"
"        batch = pmids[i:i+100]\n"
"        p = {'db':'pubmed','id':','.join(batch),'rettype':'xml','retmode':'xml','email':PUBMED_EMAIL}\n"
"        r = requests.get(url, params=p, timeout=60); r.raise_for_status()\n"
"        arts = xmltodict.parse(r.text).get('PubmedArticleSet',{}).get('PubmedArticle',[])\n"
"        if isinstance(arts, dict): arts = [arts]\n"
"        for a in arts:\n"
"            try:\n"
"                mc = a['MedlineCitation']\n"
"                pmid = mc['PMID']['#text'] if isinstance(mc['PMID'], dict) else mc['PMID']\n"
"                art = mc['Article']\n"
"                title = art.get('ArticleTitle','')\n"
"                if isinstance(title, dict): title = title.get('#text','')\n"
"                ab = art.get('Abstract',{}).get('AbstractText','')\n"
"                if isinstance(ab, list):\n"
"                    ab = ' '.join([x.get('#text','') if isinstance(x, dict) else str(x) for x in ab])\n"
"                elif isinstance(ab, dict): ab = ab.get('#text','')\n"
"                year = art.get('Journal',{}).get('JournalIssue',{}).get('PubDate',{}).get('Year','N/A')\n"
"                if ab and len(str(ab)) > 50:\n"
"                    out.append({'pmid':pmid,'title':str(title),'abstract':str(ab),'year':year})\n"
"            except Exception:\n"
"                continue\n"
"        time.sleep(0.4)   # NCBI 예의: 너무 빨리 요청하지 않기\n"
"    return out\n"
"\n"
"pmids = set()\n"
"for q in QUERIES:\n"
"    found = search_pubmed(q, MAX_PER_QUERY)\n"
"    pmids.update(found)\n"
"    print(f'  검색 {len(found):>3}건 | {q}')\n"
"    time.sleep(0.4)\n"
"\n"
"articles = fetch_abstracts(list(pmids))\n"
"df1 = pd.DataFrame(articles)\n"
"df1.to_csv('step1_abstracts.csv', index=False, encoding='utf-8-sig')\n"
"print(f'\\n✅ 수집 완료: {len(df1)}편  → step1_abstracts.csv 저장')\n"
"df1.head(3)"
))

# ---- STEP 2 ----
n1.append(md(
"## STEP 2 — GPT로 '안정성 관련 논문'만 골라내기 (필터링)\n"
"\n"
"검색만으로는 엉뚱한 논문도 섞입니다(예: 항체를 단순 '검출 시약'으로만 쓴 논문).\n"
"GPT에게 제목+초록을 보여주고 **관련=1 / 비관련=0** 을 판단하게 합니다.\n"
"\n"
"> 🔑 아래 셀에서 OpenAI 키를 넣습니다. **키가 없으면 그냥 Enter** → 필터를 건너뛰고 전체를 다음 단계로 넘깁니다."
))
n1.append(code(
"import os\n"
"from getpass import getpass\n"
"\n"
"OPENAI_KEY = ''\n"
"try:\n"
"    from google.colab import userdata        # Colab의 비밀키 저장소\n"
"    OPENAI_KEY = userdata.get('OPENAI_API_KEY') or ''\n"
"except Exception:\n"
"    OPENAI_KEY = os.environ.get('OPENAI_API_KEY','')\n"
"if not OPENAI_KEY:\n"
"    OPENAI_KEY = getpass('OpenAI API key 입력 (없으면 그냥 Enter): ').strip()\n"
"\n"
"USE_GPT = bool(OPENAI_KEY)\n"
"MODEL   = 'gpt-4o-mini'   # 저렴하고 충분히 똑똑한 모델 (연구 원본은 gpt-5-mini 사용)\n"
"print('🟢 GPT 사용 모드' if USE_GPT else '⚪ 키 없음 → STEP 2·3 건너뜀, STEP 4에서 샘플 데이터 사용')"
))
n1.append(code(
"if USE_GPT:\n"
"    from openai import OpenAI\n"
"    import json, time\n"
"    client = OpenAI(api_key=OPENAI_KEY)\n"
"\n"
"    FILTER_SYS = (\n"
"        'You are an expert in monoclonal antibody (mAb) stability. '\n"
"        'Decide if the article contains mechanistic information about mAb stability '\n"
"        '(aggregation, viscosity, oxidation, deamidation, formulation effects, stress effects, '\n"
"        'immunogenicity from instability, etc.). '\n"
"        'Answer ONLY a JSON object: {\"relevant\": true/false, \"reason\": \"one short sentence\"}.'\n"
"    )\n"
"\n"
"    def is_relevant(title, abstract):\n"
"        try:\n"
"            r = client.chat.completions.create(\n"
"                model=MODEL,\n"
"                messages=[{'role':'system','content':FILTER_SYS},\n"
"                          {'role':'user','content':f'Title: {title}\\nAbstract: {abstract[:1500]}'}],\n"
"                max_completion_tokens=120)\n"
"            txt = r.choices[0].message.content.replace('```json','').replace('```','').strip()\n"
"            return bool(json.loads(txt).get('relevant', True))\n"
"        except Exception as e:\n"
"            print('  (판단 실패, 일단 통과)', str(e)[:60]); return True\n"
"\n"
"    flags = []\n"
"    for i, row in df1.iterrows():\n"
"        flags.append(1 if is_relevant(row['title'], row['abstract']) else 0)\n"
"        time.sleep(0.2)\n"
"    df1['relevant'] = flags\n"
"    df2 = df1[df1['relevant'] == 1].copy()\n"
"    print(f'✅ 관련 논문 {len(df2)} / 전체 {len(df1)}')\n"
"else:\n"
"    df2 = df1.copy()\n"
"    print('⚪ 필터 건너뜀 → 전체', len(df2), '편을 그대로 사용')"
))

# ---- STEP 3 ----
n1.append(md(
"## STEP 3 — GPT로 인과관계 (원인 → 관계 → 결과) 추출\n"
"\n"
"이 단계가 파이프라인의 **핵심**입니다. 초록 한 편에서 다음 같은 삼중항(triplet)을 뽑아냅니다.\n"
"\n"
"| cause(원인) | relationship(관계) | effect(결과) |\n"
"|---|---|---|\n"
"| thermal stress | promotes | aggregation |\n"
"| polysorbate 80 | inhibits | aggregation |\n"
"| low pH | promotes | deamidation |\n"
"\n"
"각 노드는 6개 카테고리(sequence/structure/formulation/stress/stability/quality_outcome) 중 하나로 분류됩니다.\n"
"\n"
"> 💰 비용을 아끼려고 **앞쪽 20편만** 처리합니다. (키가 없으면 이 셀은 자동으로 건너뜁니다.)"
))
n1.append(code(
"LIMIT = 20   # 비용 절약: 관련 논문 중 앞 20편만\n"
"\n"
"EXTRACT_SYS = (\n"
"    'You are a pharmaceutical scientist. Extract mechanistic relationships about mAb stability '\n"
"    'from the abstract as directed triplets.\\n'\n"
"    '6 node categories: sequence, structure, formulation, stress, stability, quality_outcome.\\n'\n"
"    'Relation types: stabilizes, destabilizes, increases, decreases, inhibits, promotes, induces, '\n"
"    'prevents, requires, modifies, binds, shields, aggregates, oxidizes, deamidates, isomerizes, '\n"
"    'fragments, unfolds, adsorbs, precipitates, degrades, correlates.\\n'\n"
"    'Return ONLY JSON: {\"relations\":[{\"cause\":\"\",\"category_cause\":\"\",\"effect\":\"\",'\n"
"    '\"category_effect\":\"\",\"relationship\":\"\",\"confidence\":\"high/medium/low\"}]}.'\n"
")\n"
"\n"
"def extract_relations(title, abstract):\n"
"    try:\n"
"        r = client.chat.completions.create(\n"
"            model=MODEL,\n"
"            messages=[{'role':'system','content':EXTRACT_SYS},\n"
"                      {'role':'user','content':f'Title: {title}\\nAbstract: {abstract[:2500]}'}],\n"
"            max_completion_tokens=1500)\n"
"        txt = r.choices[0].message.content.replace('```json','').replace('```','').strip()\n"
"        return json.loads(txt).get('relations', [])\n"
"    except Exception as e:\n"
"        print('  (추출 실패)', str(e)[:60]); return []\n"
"\n"
"rows = []\n"
"if USE_GPT:\n"
"    for i, row in df2.head(LIMIT).iterrows():\n"
"        for rel in extract_relations(row['title'], row['abstract']):\n"
"            rel['pmid'] = row['pmid']\n"
"            rows.append(rel)\n"
"        time.sleep(0.2)\n"
"    raw = pd.DataFrame(rows)\n"
"    print(f'✅ 추출된 관계: {len(raw)}개')\n"
"    display(raw.head(8))\n"
"else:\n"
"    print('⚪ 키가 없어 추출을 건너뜁니다. STEP 4에서 공개 샘플 데이터로 그래프를 그립니다.')"
))
n1.append(md(
"### STEP 3-b — 표준화(간단 버전) + 엣지 집계\n"
"\n"
"같은 뜻의 표현을 하나로 모으고(여기선 소문자/공백 정리만), 같은 (원인,관계,결과)가 몇 번 나왔는지 세어\n"
"**엣지 요약표**를 만듭니다. 이 표가 그래프의 재료이자, 실제 연구에서는 GATED 모델의 학습 데이터가 됩니다.\n"
"\n"
"> 🔎 원본 연구에서는 이 표준화도 GPT가 수행해 수만 개의 표현을 수백 개 표준 용어로 정리합니다(STEP 3 노트북 참고)."
))
n1.append(code(
"import os\n"
"if USE_GPT and len(rows) > 0:\n"
"    raw['cause']  = raw['cause'].astype(str).str.lower().str.strip()\n"
"    raw['effect'] = raw['effect'].astype(str).str.lower().str.strip()\n"
"    edges = (raw.groupby(['cause','category_cause','effect','category_effect','relationship'])\n"
"                .size().reset_index(name='frequency')\n"
"                .sort_values('frequency', ascending=False))\n"
"    edges['num_papers'] = edges['frequency']   # 실습 단순화\n"
"    edges.to_csv('step3_edges.csv', index=False, encoding='utf-8-sig')\n"
"    print(f'✅ 내 엣지표: {len(edges)}개 → step3_edges.csv 저장')\n"
"    display(edges.head(10))\n"
"else:\n"
"    print('⚪ 추출 결과가 없어 엣지표를 만들지 않았습니다(샘플로 진행).')"
))

# ---- STEP 4 ----
n1.append(md(
"## STEP 4 — 네트워크 그래프 그리기 🎨\n"
"\n"
"이제 엣지표를 **그래프**로 그립니다. 먼저 그릴 데이터를 정합니다.\n"
"- 내가 GPT로 만든 `step3_edges.csv` 가 있으면 그것을 사용\n"
"- 없으면 연구팀이 공개한 **실제 전체 그래프 데이터(샘플)** 를 내려받아 사용"
))
n1.append(code(
"import os, pandas as pd\n"
"SAMPLE_URL = 'https://raw.githubusercontent.com/STARG-LEE/mab-causal-network-v2/main/step2c_v4d_causal_edges_summary.csv'\n"
"\n"
"if os.path.exists('step3_edges.csv'):\n"
"    g = pd.read_csv('step3_edges.csv')\n"
"    SRC = '내가 GPT로 만든 데이터'\n"
"else:\n"
"    g = pd.read_csv(SAMPLE_URL)\n"
"    SRC = '연구팀 공개 샘플(전체 그래프)'\n"
"print(f'그래프 데이터: {SRC} — 엣지 {len(g):,}개')\n"
"g.head(5)"
))
n1.append(md(
"### 색 규칙 (웹 시각화 index.html 과 동일)\n"
"- **노드 색 = 6개 카테고리** · **노드 크기 = 등장 빈도**\n"
"- **화살표 색 = 방향성**: 🟢 초록=안정화/억제, 🔴 빨강=불안정/촉진, ⚪ 회색=중립"
))
n1.append(code(
"%matplotlib inline\n"
"import networkx as nx, matplotlib.pyplot as plt\n"
"from matplotlib.lines import Line2D\n"
"try:\n"
"    import koreanize_matplotlib            # 한글 깨짐 방지(자동으로 한글 폰트 적용)\n"
"except Exception:\n"
"    for _f in ['Malgun Gothic','AppleGothic','NanumGothic']:   # 폴백\n"
"        try: plt.rcParams['font.family']=_f; break\n"
"        except Exception: pass\n"
"plt.rcParams['axes.unicode_minus']=False\n"
"\n"
"CAT_COLOR = {'sequence':'#c4b5fd','structure':'#a78bfa','formulation':'#34d399',\n"
"             'stress':'#fbbf24','stability':'#f87171','quality_outcome':'#fb923c'}\n"
"POSITIVE = {'stabilizes','decreases','inhibits','prevents','shields'}\n"
"NEGATIVE = {'destabilizes','increases','promotes','induces','aggregates','oxidizes',\n"
"            'deamidates','isomerizes','fragments','unfolds','adsorbs','precipitates','degrades','denatures'}\n"
"def rel_color(r):\n"
"    if r in POSITIVE: return '#22c55e'\n"
"    if r in NEGATIVE: return '#ef4444'\n"
"    return '#94a3b8'\n"
"\n"
"# 노드 카테고리 / 빈도 사전\n"
"node_cat, strength = {}, {}\n"
"for _, r in g.iterrows():\n"
"    node_cat.setdefault(str(r['cause']),  str(r['category_cause']))\n"
"    node_cat.setdefault(str(r['effect']), str(r['category_effect']))\n"
"    strength[str(r['cause'])]  = strength.get(str(r['cause']),0)  + int(r['frequency'])\n"
"    strength[str(r['effect'])] = strength.get(str(r['effect']),0) + int(r['frequency'])\n"
"\n"
"# 너무 빽빽하면 가독성↓ → 빈도 상위 100개 엣지만\n"
"sub = g.sort_values('frequency', ascending=False).head(100)\n"
"G = nx.DiGraph()\n"
"for _, r in sub.iterrows():\n"
"    G.add_edge(str(r['cause']), str(r['effect']), rel=str(r['relationship']), w=int(r['frequency']))\n"
"\n"
"pos = nx.spring_layout(G, k=0.9, iterations=150, seed=42)\n"
"fig, ax = plt.subplots(figsize=(14,10)); fig.patch.set_facecolor('#0a0e17'); ax.set_facecolor('#0a0e17')\n"
"nx.draw_networkx_edges(G,pos,edge_color=[rel_color(G[u][v]['rel']) for u,v in G.edges()],\n"
"                       width=[0.5+G[u][v]['w']*0.1 for u,v in G.edges()],alpha=0.55,\n"
"                       arrows=True,arrowsize=9,connectionstyle='arc3,rad=0.08',ax=ax)\n"
"nx.draw_networkx_nodes(G,pos,node_color=[CAT_COLOR.get(node_cat.get(n,''),'#888') for n in G.nodes()],\n"
"                       node_size=[120+strength.get(n,0)*3 for n in G.nodes()],\n"
"                       edgecolors='#0a0e17',linewidths=0.5,ax=ax)\n"
"big = sorted(G.nodes(), key=lambda n:-strength.get(n,0))[:20]\n"
"nx.draw_networkx_labels(G,pos,labels={n:n for n in big},font_size=8,font_color='#e8ecf4',ax=ax)\n"
"ax.set_title('내 mAb 안정성 인과 네트워크 (빈도 상위 100 엣지)',color='#e8ecf4',fontsize=14,fontweight='bold')\n"
"ax.legend(handles=[Line2D([0],[0],marker='o',color='w',markerfacecolor=c,markersize=10,label=k) for k,c in CAT_COLOR.items()],\n"
"          loc='upper left',framealpha=0.2,labelcolor='#e8ecf4',fontsize=8)\n"
"ax.axis('off'); plt.tight_layout(); plt.savefig('my_network.png',dpi=150,facecolor='#0a0e17'); plt.show()\n"
"print('🖼️  my_network.png 저장 완료')"
))

n1.append(md(
"### (선택) 살아있는 웹 시각화에 내 CSV 올려보기\n"
"\n"
"연구팀의 **인터랙티브 웹 그래프**에는 *CSV 업로드* 기능이 있습니다.\n"
"방금 만든 `step3_edges.csv`(또는 `my_network` 데이터)를 그대로 올리면 마우스로 끌고 확대/필터링할 수 있어요.\n"
"\n"
"🔗 **https://starg-lee.github.io/mab-causal-network-v2/**  → 왼쪽 패널의 *Upload CSV* 클릭 → 내 CSV 선택\n"
"\n"
"필요한 컬럼: `cause, category_cause, effect, category_effect, relationship, frequency, num_papers`"
))

# ---- STEP 5 concept ----
n1.append(md(
"## STEP 5 (개념만) — GATED 모델은 무엇을 할까?\n"
"\n"
"여기까지가 **직접 실습**입니다. 실제 연구는 이 엣지표로 **mAb-GATED** 라는 AI 모델을 학습시킵니다.\n"
"\n"
"**한 줄 요약:** 그래프에서 정답 노드 하나를 가린 뒤(\"빈칸 채우기\"), 주변 이웃 노드들을 보고\n"
"가려진 **안정성 지표**가 무엇인지 맞히도록 학습합니다.\n"
"\n"
"```\n"
"입력 : (formulation, stress, structure ... 6개 카테고리의 이웃 노드들)\n"
"   ↓  PubMedBERT 임베딩으로 단어 의미 초기화\n"
"   ↓  GAT (그래프 이웃 정보 모으기)\n"
"   ↓  Transformer 인코더-디코더\n"
"정답 : 가려진 stability 노드  (예: aggregation? viscosity? oxidation?)\n"
"```\n"
"\n"
"성능(원본 논문, 테스트셋): **MRR 0.88, Hits@1 84.6%** — 빈도/단순기법 기반 베이스라인을 크게 능가.\n"
"자세한 구조와 결과는 **교안**과 `step4_mab_gated_colab.ipynb` 원본을 참고하세요.\n"
"\n"
"---\n"
"### 🏁 도전 과제\n"
"1. STEP 1의 검색어를 바꿔 다른 주제(예: `oxidation`, `freeze-thaw`)로 나만의 그래프를 만들어 보세요.\n"
"2. STEP 4에서 `aggregation` 한 노드의 이웃만 골라 그려 보세요(`02_그래프_그리기.ipynb` 참고).\n"
"3. 초록=좋은 방향, 빨강=나쁜 방향. 내 그래프에서 빨강 화살표가 가장 많이 향하는 노드는 무엇인가요?"
))

write_nb(n1, os.path.join(HERE, "01_실습_파이프라인.ipynb"))


# ════════════════════════════════════════════════════════════════════
#  노트북 2 : 그래프 그리기 집중 (공개 실제 데이터 사용, API 불필요)
# ════════════════════════════════════════════════════════════════════
n2 = []
n2.append(md(
"# 📊 실습 2 — 공개 데이터로 '논문 속 인과 그래프' 그리기\n"
"\n"
"OpenAI 키 없이, **연구팀이 공개한 실제 엣지 데이터**(2,436개 엣지)로 그래프 4종을 그려봅니다.\n"
"\n"
"1. 관계 유형 분포 (어떤 관계가 많은가)\n"
"2. 허브 노드 Top 15 (무엇이 네트워크의 중심인가)\n"
"3. 네트워크 백본 (빈도 높은 연결만 모은 전체 지도)\n"
"4. 특정 노드의 이웃 (ego network — 예: aggregation)\n"
"\n"
"> 데이터 출처: https://github.com/STARG-LEE/mab-causal-network-v2"
))
n2.append(code(
"!pip install -q pandas networkx matplotlib koreanize-matplotlib\n"
"import pandas as pd, networkx as nx, matplotlib.pyplot as plt\n"
"from matplotlib.lines import Line2D\n"
"try:\n"
"    import koreanize_matplotlib            # 한글 깨짐 방지(자동으로 한글 폰트 적용)\n"
"except Exception:\n"
"    for _f in ['Malgun Gothic','AppleGothic','NanumGothic']:   # 폴백\n"
"        try: plt.rcParams['font.family']=_f; break\n"
"        except Exception: pass\n"
"plt.rcParams['axes.unicode_minus']=False\n"
"%matplotlib inline\n"
"\n"
"URL = 'https://raw.githubusercontent.com/STARG-LEE/mab-causal-network-v2/main/step2c_v4d_causal_edges_summary.csv'\n"
"df = pd.read_csv(URL)\n"
"print('엣지', len(df), '| 컬럼', list(df.columns))\n"
"df.head()"
))
n2.append(md(
"## 색 규칙 정의 (웹 시각화와 동일)\n"
"노드=카테고리 6색, 화살표=방향성 3색(초록/빨강/회색)."
))
n2.append(code(
"CAT_COLOR = {'sequence':'#c4b5fd','structure':'#a78bfa','formulation':'#34d399',\n"
"             'stress':'#fbbf24','stability':'#f87171','quality_outcome':'#fb923c'}\n"
"CAT_KOR = {'sequence':'Sequence(서열)','structure':'Structure(구조)','formulation':'Formulation(제형)',\n"
"           'stress':'Stress(스트레스)','stability':'Stability(안정성)','quality_outcome':'Quality(품질)'}\n"
"POSITIVE = {'stabilizes','decreases','inhibits','prevents','shields'}\n"
"NEGATIVE = {'destabilizes','increases','promotes','induces','aggregates','oxidizes',\n"
"            'deamidates','isomerizes','fragments','unfolds','adsorbs','precipitates','degrades','denatures'}\n"
"def rel_color(r):\n"
"    if r in POSITIVE: return '#22c55e'\n"
"    if r in NEGATIVE: return '#ef4444'\n"
"    return '#94a3b8'\n"
"\n"
"node_cat, strength = {}, {}\n"
"for _, r in df.iterrows():\n"
"    node_cat.setdefault(str(r['cause']),  str(r['category_cause']))\n"
"    node_cat.setdefault(str(r['effect']), str(r['category_effect']))\n"
"    strength[str(r['cause'])]  = strength.get(str(r['cause']),0)  + int(r['frequency'])\n"
"    strength[str(r['effect'])] = strength.get(str(r['effect']),0) + int(r['frequency'])\n"
"print('노드 수:', len(node_cat))"
))
n2.append(md("## 그림 1 — 관계 유형 분포"))
n2.append(code(
"vc = df['relationship'].value_counts().head(15)[::-1]\n"
"plt.figure(figsize=(9,6))\n"
"plt.barh(vc.index, vc.values, color=[rel_color(r) for r in vc.index], edgecolor='white')\n"
"for y,v in enumerate(vc.values): plt.text(v+3,y,f'{v:,}',va='center',fontsize=9)\n"
"plt.title('관계 유형 분포 Top 15  (초록=안정화·빨강=불안정·회색=중립)',fontweight='bold')\n"
"plt.xlabel('엣지 수'); plt.tight_layout(); plt.show()"
))
n2.append(md(
"💬 **읽기:** `modifies`, `correlates`, `decreases` 가 가장 많습니다. "
"즉, 문헌은 단정적인 인과보다 '수식/상관' 같은 **중립적·정량적 표현**을 많이 씁니다."
))
n2.append(md("## 그림 2 — 허브 노드 Top 15"))
n2.append(code(
"s = pd.Series(strength).sort_values(ascending=False).head(15)[::-1]\n"
"plt.figure(figsize=(9,6))\n"
"plt.barh(s.index, s.values, color=[CAT_COLOR.get(node_cat.get(n,''),'#888') for n in s.index], edgecolor='white')\n"
"for y,v in enumerate(s.values): plt.text(v+5,y,f'{v:,}',va='center',fontsize=9)\n"
"plt.title('허브 노드 Top 15  (막대=총 빈도, 색=카테고리)',fontweight='bold')\n"
"plt.xlabel('총 빈도(in+out)')\n"
"plt.legend(handles=[Line2D([0],[0],marker='o',color='w',markerfacecolor=c,markersize=10,label=CAT_KOR[k]) for k,c in CAT_COLOR.items()],\n"
"           loc='lower right',fontsize=8)\n"
"plt.tight_layout(); plt.show()"
))
n2.append(md(
"💬 **읽기:** `aggregation`(응집), `immunogenicity`(면역원성), `binding activity`(결합능)이 "
"네트워크의 **허브**입니다 — mAb 안정성 문제의 길목."
))
n2.append(md("## 그림 3 — 네트워크 백본 (빈도 상위 120 엣지)"))
n2.append(code(
"sub = df.sort_values('frequency', ascending=False).head(120)\n"
"G = nx.DiGraph()\n"
"for _, r in sub.iterrows():\n"
"    G.add_edge(str(r['cause']), str(r['effect']), rel=str(r['relationship']), w=int(r['frequency']))\n"
"pos = nx.spring_layout(G, k=0.9, iterations=200, seed=42)\n"
"fig,ax = plt.subplots(figsize=(15,11)); fig.patch.set_facecolor('#0a0e17'); ax.set_facecolor('#0a0e17')\n"
"nx.draw_networkx_edges(G,pos,edge_color=[rel_color(G[u][v]['rel']) for u,v in G.edges()],\n"
"                       width=[0.5+G[u][v]['w']*0.12 for u,v in G.edges()],alpha=0.55,arrows=True,\n"
"                       arrowsize=9,connectionstyle='arc3,rad=0.08',ax=ax)\n"
"nx.draw_networkx_nodes(G,pos,node_color=[CAT_COLOR.get(node_cat.get(n,''),'#888') for n in G.nodes()],\n"
"                       node_size=[120+strength.get(n,0)*4 for n in G.nodes()],edgecolors='#0a0e17',linewidths=0.5,ax=ax)\n"
"big = sorted(G.nodes(), key=lambda n:-strength.get(n,0))[:22]\n"
"nx.draw_networkx_labels(G,pos,labels={n:n for n in big},font_size=8,font_color='#e8ecf4',ax=ax)\n"
"ax.set_title('mAb 안정성 인과 네트워크 — 백본(상위 120 엣지)',color='#e8ecf4',fontsize=15,fontweight='bold')\n"
"ax.legend(handles=[Line2D([0],[0],marker='o',color='w',markerfacecolor=c,markersize=11,label=CAT_KOR[k]) for k,c in CAT_COLOR.items()],\n"
"          loc='upper left',framealpha=0.2,labelcolor='#e8ecf4',fontsize=9)\n"
"ax.axis('off'); plt.tight_layout(); plt.show()"
))
n2.append(md("## 그림 4 — 특정 노드의 이웃만 보기 (ego network)\n\n`CENTER` 를 바꿔서 다른 노드도 살펴보세요 (예: `viscosity`, `oxidation`, `immunogenicity`)."))
n2.append(code(
"CENTER = 'aggregation'   # ← 바꿔보세요\n"
"TOP = 18\n"
"rel = df[(df['cause']==CENTER)|(df['effect']==CENTER)].sort_values('frequency',ascending=False).head(TOP)\n"
"G = nx.DiGraph()\n"
"for _, r in rel.iterrows():\n"
"    G.add_edge(str(r['cause']), str(r['effect']), rel=str(r['relationship']), w=int(r['frequency']))\n"
"pos = nx.spring_layout(G, k=1.2, iterations=200, seed=7)\n"
"plt.figure(figsize=(13,9))\n"
"nx.draw_networkx_edges(G,pos,edge_color=[rel_color(G[u][v]['rel']) for u,v in G.edges()],\n"
"                       width=[1.0+G[u][v]['w']*0.15 for u,v in G.edges()],alpha=0.7,arrows=True,\n"
"                       arrowsize=16,connectionstyle='arc3,rad=0.08')\n"
"nx.draw_networkx_nodes(G,pos,node_color=[CAT_COLOR.get(node_cat.get(n,''),'#888') for n in G.nodes()],\n"
"                       node_size=[2600 if n==CENTER else 900 for n in G.nodes()],edgecolors='#333',linewidths=1.0)\n"
"nx.draw_networkx_labels(G,pos,font_size=9)\n"
"nx.draw_networkx_edge_labels(G,pos,edge_labels={(u,v):G[u][v]['rel'] for u,v in G.edges()},font_size=7,\n"
"                             font_color='#444',bbox=dict(boxstyle='round,pad=0.1',fc='white',ec='none',alpha=0.6))\n"
"plt.title(f\"'{CENTER}' 노드 중심 인과 이웃 (ego network)\",fontsize=14,fontweight='bold')\n"
"plt.axis('off'); plt.tight_layout(); plt.show()"
))
n2.append(md(
"## 정리\n"
"- 색·크기·화살표 **세 가지 시각 신호**만으로 수천 편 논문의 인과 지식을 한 장에 담았습니다.\n"
"- 같은 데이터가 **GATED 모델**의 학습 재료가 됩니다(다음 단계).\n"
"- 마우스로 직접 만지는 버전: **https://starg-lee.github.io/mab-causal-network-v2/**"
))

write_nb(n2, os.path.join(HERE, "02_그래프_그리기.ipynb"))
print("\n두 노트북 생성 완료")
