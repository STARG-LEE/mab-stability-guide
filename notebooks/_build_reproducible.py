# -*- coding: utf-8 -*-
"""원본 step1~4 → '재현용' 노트북 4종 생성.
   - DB(사설 MySQL) 제거 → CSV 파일로 단계 연결
   - 자격증명 전부 제거(OpenAI 키만 각자 입력)
   - step1~3은 로직 그대로 새로 작성, step4는 원본을 받아 DB셀만 교체(모델코드 verbatim 유지)
   출력: notebooks/full/  (step1_collect / step2_filter / step3_extract / step4_gated)
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "full")
os.makedirs(OUT, exist_ok=True)
ORIG_STEP4 = r"C:\Users\leesh\Downloads\step4_mab_gated_colab_(1).ipynb"

def md(s):   return {"cell_type": "markdown", "metadata": {}, "source": s}
def code(s): return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": s}
def write_nb(cells, name):
    nb = {"cells": cells, "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3"},
          "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
    p = os.path.join(OUT, name)
    json.dump(nb, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("wrote", name)

REPO = "STARG-LEE/mab-stability-guide"
SAMPLE_EDGES = "https://raw.githubusercontent.com/STARG-LEE/mab-causal-network-v2/main/step2c_v4d_causal_edges_summary.csv"


# ════════════════════════════════════════════════════════════════════
# STEP 1 — PubMed 수집  →  step1_abstracts.csv
# ════════════════════════════════════════════════════════════════════
s1 = []
s1.append(md(
"# STEP 1 — PubMed 논문 초록 수집 (재현용)\n"
"\n"
"PubMed에서 mAb 안정성 관련 논문의 **제목·초록**을 모아 `step1_abstracts.csv` 로 저장합니다.\n"
"\n"
"| | |\n|---|---|\n"
"| **입력** | 없음 (PubMed 공개 API) |\n"
"| **출력** | `step1_abstracts.csv` (pmid, title, abstract, year, journal) |\n"
"| **필요** | 인터넷만 (OpenAI 키 불필요·무료) |\n"
"| **다음** | 이 CSV를 STEP 2에 넣습니다 |\n"
"\n"
"> 💡 원본 연구는 126개 검색어로 62,281편을 모았습니다. 여기서는 **빠르게 따라하도록 작게** 설정했어요. "
"`SEARCH_QUERIES` 와 `MAX_RESULTS_PER_QUERY` 를 키우면 규모를 늘릴 수 있습니다."
))
s1.append(code("!pip install -q requests xmltodict pandas\nprint('준비 완료')"))
s1.append(code(
"import requests, time, xmltodict, pandas as pd\n"
"\n"
"# ── 설정 (여기만 바꾸면 됩니다) ───────────────────────────────\n"
"PUBMED_EMAIL = 'student@example.com'      # NCBI 권장: 아무 이메일\n"
"MAX_RESULTS_PER_QUERY = 40                # 쿼리당 최대 논문 수 (작게 시작)\n"
"SEARCH_QUERIES = [\n"
"    '\"monoclonal antibody\" AND \"stability\" AND \"formulation\"',\n"
"    '\"monoclonal antibody\" AND (\"aggregation\" OR \"viscosity\")',\n"
"    '\"therapeutic antibody\" AND \"stability\"',\n"
"]\n"
"print(f'검색어 {len(SEARCH_QUERIES)}개, 쿼리당 최대 {MAX_RESULTS_PER_QUERY}편')"
))
s1.append(code(
"def search_pubmed(query, max_results=40):\n"
"    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'\n"
"    p = {'db':'pubmed','term':query,'retmax':max_results,'retmode':'json','email':PUBMED_EMAIL}\n"
"    r = requests.get(url, params=p, timeout=30); r.raise_for_status()\n"
"    d = r.json().get('esearchresult', {})\n"
"    return d.get('idlist', []), int(d.get('count', '0'))\n"
"\n"
"def fetch_abstracts(pmids):\n"
"    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'\n"
"    arts = []\n"
"    for i in range(0, len(pmids), 200):\n"
"        batch = pmids[i:i+200]\n"
"        p = {'db':'pubmed','id':','.join(batch),'rettype':'xml','retmode':'xml','email':PUBMED_EMAIL}\n"
"        r = requests.get(url, params=p, timeout=60); r.raise_for_status()\n"
"        papers = xmltodict.parse(r.text).get('PubmedArticleSet', {}).get('PubmedArticle', [])\n"
"        if isinstance(papers, dict): papers = [papers]\n"
"        for a in papers:\n"
"            try:\n"
"                mc = a['MedlineCitation']\n"
"                pmid = mc['PMID']['#text'] if isinstance(mc['PMID'], dict) else mc['PMID']\n"
"                art = mc['Article']\n"
"                title = art.get('ArticleTitle', '')\n"
"                if isinstance(title, dict): title = title.get('#text', '')\n"
"                ab = art.get('Abstract', {}).get('AbstractText', '')\n"
"                if isinstance(ab, list):\n"
"                    parts = []\n"
"                    for x in ab:\n"
"                        if isinstance(x, dict):\n"
"                            lab = x.get('@Label', ''); txt = x.get('#text', '')\n"
"                            parts.append(f'{lab}: {txt}' if lab else txt)\n"
"                        else: parts.append(str(x))\n"
"                    ab = ' '.join(parts)\n"
"                elif isinstance(ab, dict): ab = ab.get('#text', '')\n"
"                year = art.get('Journal', {}).get('JournalIssue', {}).get('PubDate', {}).get('Year', 'N/A')\n"
"                journal = art.get('Journal', {}).get('Title', 'N/A')\n"
"                if ab and str(ab) != 'None' and len(str(ab)) > 50:\n"
"                    arts.append({'pmid':str(pmid),'title':str(title),'abstract':str(ab),'year':year,'journal':journal})\n"
"            except (KeyError, TypeError):\n"
"                continue\n"
"        time.sleep(0.4)   # NCBI rate limit 준수\n"
"    return arts\n"
"\n"
"print('함수 정의 완료')"
))
s1.append(code(
"all_pmids = set()\n"
"for i, q in enumerate(SEARCH_QUERIES, 1):\n"
"    pmids, total = search_pubmed(q, MAX_RESULTS_PER_QUERY)\n"
"    all_pmids.update(pmids)\n"
"    print(f'[{i}/{len(SEARCH_QUERIES)}] {len(pmids)}건 (전체 {total}건) | {q[:50]}')\n"
"    time.sleep(0.4)\n"
"print(f'\\n중복 제거 후 {len(all_pmids)}편 → 초록 다운로드...')\n"
"\n"
"articles = fetch_abstracts(list(all_pmids))\n"
"df = pd.DataFrame(articles)\n"
"df.to_csv('step1_abstracts.csv', index=False, encoding='utf-8-sig')\n"
"print(f'\\n✅ 저장: step1_abstracts.csv  ({len(df)}편)')\n"
"df.head(3)"
))
s1.append(md(
"### ✅ STEP 1 완료\n"
"`step1_abstracts.csv` 가 만들어졌습니다.\n"
"\n"
"- **Colab:** 왼쪽 파일창에서 이 CSV를 다운로드해 두거나, STEP 2를 같은 런타임에서 이어 실행하세요.\n"
"- **다음:** `step2_filter.ipynb` 를 열어 이 CSV를 업로드(또는 같은 런타임 사용)합니다."
))
write_nb(s1, "step1_collect.ipynb")


# ════════════════════════════════════════════════════════════════════
# STEP 2 — GPT 관련성 필터  step1_abstracts.csv → step2_filtered.csv
# ════════════════════════════════════════════════════════════════════
s2 = []
s2.append(md(
"# STEP 2 — GPT 관련성 필터 (재현용)\n"
"\n"
"STEP 1이 모은 논문 중 **mAb 안정성과 진짜 관련 있는 것만** GPT로 골라 `step2_filtered.csv` 로 저장합니다.\n"
"\n"
"| | |\n|---|---|\n"
"| **입력** | `step1_abstracts.csv` (STEP 1 출력) |\n"
"| **출력** | `step2_filtered.csv` (+ relevant, reason 컬럼) |\n"
"| **필요** | OpenAI API 키 |\n"
"\n"
"> 🔑 Colab 왼쪽 🔑(보안 비밀)에 `OPENAI_API_KEY` 를 넣거나, 아래 셀 실행 시 입력하세요.\n"
"> 💰 `gpt-4o-mini` 기준 논문 수십 편 = 수십 원 수준. (원본 연구는 gpt-5-mini 사용)"
))
s2.append(code("!pip install -q openai pandas\nprint('준비 완료')"))
s2.append(code(
"import os, json, time, pandas as pd\n"
"from getpass import getpass\n"
"\n"
"# ── OpenAI 키 ──────────────────────────────────────────────\n"
"OPENAI_KEY = ''\n"
"try:\n"
"    from google.colab import userdata\n"
"    OPENAI_KEY = userdata.get('OPENAI_API_KEY') or ''\n"
"except Exception:\n"
"    OPENAI_KEY = os.environ.get('OPENAI_API_KEY', '')\n"
"if not OPENAI_KEY:\n"
"    OPENAI_KEY = getpass('OpenAI API key: ').strip()\n"
"\n"
"from openai import OpenAI\n"
"client = OpenAI(api_key=OPENAI_KEY)\n"
"MODEL      = 'gpt-4o-mini'   # 저렴·범용 (원본: gpt-5-mini)\n"
"BATCH_SIZE = 10              # GPT 한 번에 판단할 논문 수\n"
"print('OpenAI 준비 완료, 모델:', MODEL)"
))
s2.append(code(
"# 입력 불러오기 (STEP 1 출력)\n"
"import os\n"
"if not os.path.exists('step1_abstracts.csv'):\n"
"    raise FileNotFoundError('step1_abstracts.csv 가 없습니다. STEP 1을 먼저 실행하거나 파일을 업로드하세요.')\n"
"df_all = pd.read_csv('step1_abstracts.csv')\n"
"print(f'입력 논문: {len(df_all)}편')\n"
"df_all.head(2)"
))
s2.append(code(
'SYSTEM_PROMPT = """You are an expert in monoclonal antibody (mAb) formulation and stability.\n'
'\n'
'Your task: Judge whether each article contains MECHANISTIC information relevant to mAb stability.\n'
'\n'
'RELEVANT (relevant=true) if the article covers ANY of:\n'
'- Physical stability of mAb: aggregation, viscosity, particle formation, turbidity, opalescence\n'
'- Chemical stability of mAb: oxidation, deamidation, isomerization, fragmentation, charge variants, glycosylation\n'
'- Biological stability: conformational stability, Tm, binding activity, potency, ADCC\n'
'- Effect of formulation conditions (excipients, pH, buffer, concentration) on mAb stability\n'
'- Effect of stress conditions (freeze-thaw, thermal, agitation, light, lyophilization) on stability\n'
'- Stability testing methods (SEC-HPLC, DLS, DSC, CE-SDS, etc.)\n'
'- Downstream consequences of instability: immunogenicity, ADA, PK changes, safety\n'
'\n'
'NOT RELEVANT (relevant=false) if:\n'
'- mAb used only as a detection/research tool (e.g., ELISA reagent, flow cytometry)\n'
'- Clinical efficacy/trial with no stability content\n'
'- Stability of non-mAb molecules with mAb mentioned only peripherally\n'
'\n'
'Respond ONLY with a JSON array, one object per article.\n'
'Format: [{"pmid": "...", "relevant": true/false, "reason": "one sentence"}]\n'
'No markdown, no text outside the JSON array."""\n'
"\n"
"def filter_batch(articles):\n"
"    lines = [f'PMID: {a[\"pmid\"]}\\nTitle: {str(a[\"title\"])[:200]}\\nAbstract: {str(a[\"abstract\"])[:500]}' for a in articles]\n"
"    user = '\\n\\n---\\n\\n'.join(lines)\n"
"    for attempt in range(3):\n"
"        try:\n"
"            r = client.chat.completions.create(model=MODEL,\n"
"                messages=[{'role':'system','content':SYSTEM_PROMPT},{'role':'user','content':user}],\n"
"                max_completion_tokens=2000)\n"
"            txt = r.choices[0].message.content.replace('```json','').replace('```','').strip()\n"
"            return json.loads(txt)\n"
"        except Exception as e:\n"
"            if attempt < 2: time.sleep(2)\n"
"            else:\n"
"                print('  batch 실패, 보수적으로 통과:', str(e)[:60])\n"
"                return [{'pmid':a['pmid'],'relevant':True,'reason':'filter_failed'} for a in articles]\n"
"print('필터 함수 정의 완료')"
))
s2.append(code(
"from collections import OrderedDict\n"
"records = df_all.to_dict('records')\n"
"amap = {str(a['pmid']): a for a in records}\n"
"results = []\n"
"for i in range(0, len(records), BATCH_SIZE):\n"
"    batch = records[i:i+BATCH_SIZE]\n"
"    res = filter_batch(batch)\n"
"    results.extend(res)\n"
"    rel = sum(1 for r in res if r.get('relevant'))\n"
"    print(f'  {i+len(batch)}/{len(records)} 처리 · 이 배치 관련 {rel}/{len(batch)}')\n"
"    time.sleep(0.5)\n"
"\n"
"# 결과를 원본에 합쳐 저장\n"
"rmap = {str(r.get('pmid')): r for r in results}\n"
"rows = []\n"
"for a in records:\n"
"    r = rmap.get(str(a['pmid']), {'relevant': True, 'reason': ''})\n"
"    rows.append({**a, 'relevant': 1 if r.get('relevant') else 0, 'relevance_reason': str(r.get('reason',''))[:300]})\n"
"out = pd.DataFrame(rows)\n"
"out.to_csv('step2_filtered.csv', index=False, encoding='utf-8-sig')\n"
"keep = int(out['relevant'].sum())\n"
"print(f'\\n✅ 저장: step2_filtered.csv | 관련 {keep} / 전체 {len(out)} ({keep/len(out)*100:.0f}%)')\n"
"out[['pmid','relevant','relevance_reason']].head(6)"
))
s2.append(md(
"### ✅ STEP 2 완료\n"
"`step2_filtered.csv` 의 `relevant=1` 인 논문만 STEP 3에서 인과관계를 추출합니다.\n"
"\n"
"**다음:** `step3_extract.ipynb`"
))
write_nb(s2, "step2_filter.ipynb")

# ════════════════════════════════════════════════════════════════════
# STEP 3 — GPT 인과관계 추출·표준화·집계  step2_filtered.csv → step3_edges.csv
# ════════════════════════════════════════════════════════════════════
s3 = []
s3.append(md(
"# STEP 3 — 인과관계 추출 → 표준화 → 집계 (재현용) ⭐\n"
"\n"
"파이프라인의 **핵심**. 관련 논문 초록에서 GPT가 **(원인 → 관계 → 결과)** 삼중항을 뽑고, 표현을 통일(표준화)한 뒤, "
"같은 관계가 몇 번 나왔는지 세어 **엣지 표** `step3_edges.csv` 를 만듭니다.\n"
"\n"
"| | |\n|---|---|\n"
"| **입력** | `step2_filtered.csv` (relevant=1) |\n"
"| **출력** | `step3_edges.csv` (cause, category_cause, effect, category_effect, relationship, frequency, num_papers) |\n"
"| **필요** | OpenAI API 키 |\n"
"\n"
"```\nStage 2a 추출   초록 → (원인, 관계, 결과) 삼중항\nStage 2b 표준화  같은 뜻 표현을 표준 용어로 통일\nStage 2c 집계   (원인,관계,결과)별 빈도·논문수 → 엣지 표\n```\n"
"> 💰 비용 절약을 위해 기본 `LIMIT=30` 편만 처리합니다. 키우려면 값을 올리세요."
))
s3.append(code("!pip install -q openai pandas\nprint('준비 완료')"))
s3.append(code(
"import os, re, json, time, pandas as pd\n"
"from collections import Counter, defaultdict\n"
"from getpass import getpass\n"
"\n"
"OPENAI_KEY = ''\n"
"try:\n"
"    from google.colab import userdata\n"
"    OPENAI_KEY = userdata.get('OPENAI_API_KEY') or ''\n"
"except Exception:\n"
"    OPENAI_KEY = os.environ.get('OPENAI_API_KEY', '')\n"
"if not OPENAI_KEY:\n"
"    OPENAI_KEY = getpass('OpenAI API key: ').strip()\n"
"from openai import OpenAI\n"
"client = OpenAI(api_key=OPENAI_KEY)\n"
"\n"
"MODEL           = 'gpt-4o-mini'   # 원본: gpt-5-mini\n"
"LIMIT           = 30              # 처리할 관련 논문 수 (비용)\n"
"NORM_BATCH_SIZE = 80              # 표준화 배치 크기\n"
"print('준비 완료, 모델:', MODEL)"
))
s3.append(code(
"# 입력: STEP 2의 관련 논문\n"
"if not os.path.exists('step2_filtered.csv'):\n"
"    raise FileNotFoundError('step2_filtered.csv 가 없습니다. STEP 2를 먼저 실행하세요.')\n"
"df_f = pd.read_csv('step2_filtered.csv')\n"
"df_rel = df_f[df_f['relevant'] == 1].head(LIMIT).reset_index(drop=True)\n"
"print(f'관련 논문 {int(df_f[\"relevant\"].sum())}편 중 앞 {len(df_rel)}편 처리')"
))
# 표준 노드 목록 (원본 CANONICAL_NODES 축약 가능 — 여기선 핵심만 유지)
s3.append(code(
'CANONICAL_NODES = """\n'
'aggregation, viscosity, particle formation, colloidal stability, self-association, solubility,\n'
'hmw species, monomer content, adsorption, turbidity, opalescence,\n'
'oxidation, deamidation, isomerization, fragmentation, degradation, charge variants, glycosylation,\n'
'disulfide bond, conformational stability, thermal stability, melting temperature, protein unfolding,\n'
'storage stability, in vivo stability, binding activity, binding affinity, potency, immunogenicity,\n'
'pharmacokinetics, half-life, clearance, efficacy, higher-order structure, amino acid sequence,\n'
'concentration, ph, low ph, polysorbate 80, polysorbate 20, sucrose, trehalose, arginine, histidine,\n'
'surfactant, excipients, buffer composition, ionic strength, thermal stress, agitation, freeze-thaw,\n'
'light exposure, oxidative stress, lyophilization, shear stress, air-water interface\n'
'"""\n'
"canonical_list = [t.strip() for t in CANONICAL_NODES.split(',') if t.strip()]\n"
"print(f'표준 노드 {len(canonical_list)}개')"
))
s3.append(code(
'EXTRACTION_SYSTEM_PROMPT = """You are an expert pharmaceutical scientist specializing in monoclonal antibody (mAb) formulation and stability.\n'
'\n'
'Extract MECHANISTIC relationships relevant to mAb STABILITY from the abstract.\n'
'These are directional associations explicitly described by the authors (physical/chemical/biological mechanisms), not statistically inferred effects.\n'
'\n'
'=== 6 NODE CATEGORIES ===\n'
'sequence       : amino acid sequence features (CDR residue, mutation, glycosylation site)\n'
'structure      : 3D structural features (hydrophobic patch, disulfide bond, Fc domain)\n'
'formulation    : formulation components (PS80, sucrose, pH, arginine, concentration)\n'
'stress         : stress conditions (thermal stress, freeze-thaw, agitation, light)\n'
'stability      : stability properties & degradation (aggregation, deamidation, Tm, viscosity)\n'
'quality_outcome: measurable quality results (particle formation, immunogenicity, charge variant, PK)\n'
'\n'
'=== RELATION TYPES ===\n'
'Positive: stabilizes, inhibits, prevents, decreases, shields\n'
'Negative: destabilizes, promotes, increases, induces, aggregates, oxidizes, deamidates, isomerizes, fragments, unfolds, adsorbs, precipitates, degrades\n'
'Neutral : correlates, modifies, binds, requires\n'
'\n'
'Use specific terms: "low pH" not "pH", "elevated temperature" not "temperature".\n'
'\n'
'Return ONLY JSON: {"relations":[{"cause":"...","category_cause":"...","effect":"...","category_effect":"...","relationship":"...","confidence":"high/medium/low","evidence":"key phrase (max 30 words)"}]}\n'
'No markdown, no text outside the JSON."""\n'
"\n"
"def clean_text(t):\n"
"    if not isinstance(t, str): t = str(t)\n"
"    rep = {'\\u00b0':' deg ','\\u00b1':'+/-','\\u2265':'>=','\\u2264':'<=','\\u00b5':'u','\\u03b1':'alpha','\\u03b2':'beta','\\u2013':'-','\\u2014':'-'}\n"
"    for k,v in rep.items(): t = t.replace(k, v)\n"
"    return t.encode('ascii','ignore').decode('ascii')\n"
"\n"
"def extract_relations(title, abstract):\n"
"    user = f'Title: {clean_text(title)}\\nAbstract: {clean_text(abstract)}'\n"
"    for attempt in range(3):\n"
"        try:\n"
"            r = client.chat.completions.create(model=MODEL,\n"
"                messages=[{'role':'system','content':EXTRACTION_SYSTEM_PROMPT},{'role':'user','content':user}],\n"
"                max_completion_tokens=4000)\n"
"            txt = r.choices[0].message.content.replace('```json','').replace('```','').strip()\n"
"            return json.loads(txt).get('relations', [])\n"
"        except Exception as e:\n"
"            if attempt < 2: time.sleep(2)\n"
"            else: print('  추출 실패:', str(e)[:60]); return []\n"
"print('Stage 2a 함수 정의 완료')"
))
s3.append(code(
"# Stage 2a 실행: 초록 → 관계 추출\n"
"raw = []\n"
"for idx, row in df_rel.iterrows():\n"
"    rels = extract_relations(row['title'], row['abstract'])\n"
"    for rel in rels:\n"
"        rel['pmid'] = str(row['pmid'])\n"
"        raw.append(rel)\n"
"    if (idx+1) % 10 == 0: print(f'  {idx+1}/{len(df_rel)} 편, 누적 관계 {len(raw)}개')\n"
"    time.sleep(0.2)\n"
"df_raw = pd.DataFrame(raw)\n"
"print(f'\\n✅ Stage 2a: 원시 관계 {len(df_raw)}개')\n"
"df_raw.head(6)"
))
s3.append(code(
'NORMALIZATION_SYSTEM_PROMPT = """You are an expert in mAb stability terminology.\n'
'Map each input term to the most appropriate canonical term from the reference list.\n'
'If none fits, keep the original but make it concise and lowercase.\n'
'\n'
'CANONICAL REFERENCE TERMS:\n'
'""" + \', \'.join(canonical_list) + """\n'
'\n'
'RULES:\n'
'1. Map synonyms/variants to the canonical term (e.g. "protein aggregation" -> "aggregation").\n'
'2. Keep condition-specific terms distinct (e.g. "low pH" and "high pH" stay separate).\n'
'3. Use lowercase, concise English.\n'
'\n'
'Return ONLY JSON: {"original term": "canonical term", ...}  No markdown."""\n'
"\n"
"def normalize_terms(terms):\n"
"    uniq = sorted(set(str(t) for t in terms if t and str(t) != 'nan'))\n"
"    mapping = {}\n"
"    for i in range(0, len(uniq), NORM_BATCH_SIZE):\n"
"        batch = uniq[i:i+NORM_BATCH_SIZE]\n"
"        prompt = 'Normalize these mAb stability terms:\\n' + '\\n'.join(f'- {t}' for t in batch)\n"
"        for attempt in range(3):\n"
"            try:\n"
"                r = client.chat.completions.create(model=MODEL,\n"
"                    messages=[{'role':'system','content':NORMALIZATION_SYSTEM_PROMPT},{'role':'user','content':prompt}],\n"
"                    max_completion_tokens=4000)\n"
"                txt = r.choices[0].message.content.replace('```json','').replace('```','').strip()\n"
"                mapping.update(json.loads(txt)); break\n"
"            except Exception as e:\n"
"                if attempt < 2: time.sleep(2)\n"
"                else:\n"
"                    for t in batch: mapping[t] = t\n"
"        time.sleep(0.5)\n"
"    return mapping\n"
"\n"
"# Stage 2b 실행\n"
"if len(df_raw):\n"
"    cmap = normalize_terms(df_raw['cause'].tolist())\n"
"    emap = normalize_terms(df_raw['effect'].tolist())\n"
"    df_raw['cause']  = df_raw['cause'].map(lambda x: cmap.get(str(x), str(x)).lower().strip())\n"
"    df_raw['effect'] = df_raw['effect'].map(lambda x: emap.get(str(x), str(x)).lower().strip())\n"
"    print(f'✅ Stage 2b 표준화 완료 (cause {df_raw[\"cause\"].nunique()}종, effect {df_raw[\"effect\"].nunique()}종)')\n"
"else:\n"
"    print('추출된 관계가 없습니다. LIMIT를 늘리거나 STEP 1 검색어를 넓혀보세요.')"
))
s3.append(code(
"# Stage 2c 집계: (cause, effect, relationship)별 빈도·논문수\n"
"agg = defaultdict(lambda: {'count':0,'pmids':set(),'cc':Counter(),'ce':Counter(),'conf':Counter(),'ev':[]})\n"
"for _, r in df_raw.iterrows():\n"
"    key = (str(r['cause']), str(r['effect']), str(r.get('relationship','correlates')))\n"
"    a = agg[key]; a['count'] += 1; a['pmids'].add(str(r.get('pmid','')))\n"
"    a['cc'][str(r.get('category_cause',''))] += 1; a['ce'][str(r.get('category_effect',''))] += 1\n"
"    a['conf'][str(r.get('confidence','medium'))] += 1\n"
"    ev = str(r.get('evidence',''))[:120]\n"
"    if ev and ev != 'nan': a['ev'].append(ev)\n"
"rows = []\n"
"for (cause, effect, rel), a in agg.items():\n"
"    rows.append({'cause':cause,'category_cause':a['cc'].most_common(1)[0][0] if a['cc'] else '',\n"
"                 'effect':effect,'category_effect':a['ce'].most_common(1)[0][0] if a['ce'] else '',\n"
"                 'relationship':rel,'frequency':a['count'],'num_papers':len(a['pmids']),\n"
"                 'main_confidence':a['conf'].most_common(1)[0][0] if a['conf'] else 'medium',\n"
"                 'sample_evidence':a['ev'][0] if a['ev'] else ''})\n"
"edges = pd.DataFrame(rows).sort_values('frequency', ascending=False).reset_index(drop=True)\n"
"edges.to_csv('step3_edges.csv', index=False, encoding='utf-8-sig')\n"
"print(f'✅ 저장: step3_edges.csv | 고유 엣지 {len(edges)}개')\n"
"edges.head(12)"
))
s3.append(md(
"### ✅ STEP 3 완료\n"
"`step3_edges.csv` 가 **그래프의 재료이자 GATED 모델의 학습 데이터**입니다.\n"
"\n"
"- **그래프만 그리려면:** `02_draw_graph.ipynb` 에 이 CSV를 넣으세요.\n"
"- **모델까지:** `step4_gated.ipynb` 로.\n"
"\n"
"> ⚠️ 소규모(30편)라 엣지가 적습니다. 원본 논문 수준(32,939 엣지)을 보려면 LIMIT·검색어를 크게 키우거나, "
"STEP 4에서 제공되는 **공개 엣지 데이터**로 학습하세요."
))
write_nb(s3, "step3_extract.ipynb")


# ════════════════════════════════════════════════════════════════════
# STEP 4 — 원본을 받아 DB 셀만 CSV로 교체 (모델 코드 verbatim 유지)
# ════════════════════════════════════════════════════════════════════
nb4 = json.load(open(ORIG_STEP4, encoding="utf-8"))
cells4 = nb4["cells"]

INTRO4 = (
"# STEP 4 — mAb-GATED 모델 학습 (재현용)\n"
"\n"
"`step3_edges.csv`(또는 공개 엣지 데이터)로 **mAb-GATED** 를 학습합니다. "
"그래프에서 안정성 노드를 가리고 이웃으로 맞히는 '빈칸 채우기' 모델이에요.\n"
"\n"
"| | |\n|---|---|\n"
"| **입력** | `step3_edges.csv` (없으면 공개 엣지 자동 다운로드) |\n"
"| **출력** | 학습된 모델 `mab_gated.pt`, 결과 `results.json` |\n"
"| **필요** | **GPU 런타임** (Colab 메뉴: 런타임 → 런타임 유형 변경 → T4 GPU) · OpenAI 키 불필요 |\n"
"\n"
"> 🔧 원본 연구 노트북을 **그대로** 쓰되, 사설 DB 접속 부분만 CSV 로딩으로 바꿨습니다(모델 코드는 동일).\n"
"> ⚠️ 소규모 데이터면 성능 수치는 논문과 다릅니다. 공개 엣지(2,436개)로 돌리면 의미 있는 결과를 볼 수 있어요."
)

# 셀 3 교체: 드라이브 마운트 + DB 자격증명 제거 → 로컬 경로
config_src = cells4[3]["source"]
if isinstance(config_src, list): config_src = "".join(config_src)
# CONFIG dict 시작 위치부터 유지하되, 앞의 drive.mount/경로/DB키를 정리
new_cell3 = (
"import os\n"
"# (재현용) Google Drive 마운트·사설 DB 제거 → 로컬 폴더 사용\n"
"LOCAL_DIR  = './'\n"
"RESULT_DIR = './gated_out/'\n"
"os.makedirs(RESULT_DIR, exist_ok=True)\n"
"\n"
"CONFIG = {\n"
"    'result_dir':   RESULT_DIR,\n"
"    'local_dir':    LOCAL_DIR,\n"
"    'edges_csv':    'step3_edges.csv',                 # STEP 3 출력\n"
"    'sample_url':   '" + SAMPLE_EDGES + "',  # 없으면 공개 엣지\n"
"\n"
"    'min_freq':     1,\n"
"    'K':            5,\n"
"    'bert_model':   'pritamdeka/S-PubMedBert-MS-MARCO',\n"
"    'bert_dim':     768,\n"
"    'bert_batch':   64,\n"
"\n"
"    'hidden_dim':   128, 'nhead': 4, 'enc_layers': 2, 'dec_layers': 2,\n"
"    'dropout': 0.2, 'gat_heads': 4, 'gat_layers': 2,\n"
"\n"
"    'lr': 0.001, 'epochs': 500, 'patience': 50, 'batch_size': 64, 'label_smooth': 0.1,\n"
"\n"
"    'distmult_dim': 128, 'distmult_epochs': 500, 'distmult_neg': 50, 'distmult_margin': 3.0,\n"
"}\n"
"\n"
"CAT_ORDER = ['formulation', 'stress', 'stability', 'quality_outcome', 'structure', 'sequence']\n"
"K = CONFIG['K']\n"
"print('재현용 설정 로드 — 사설 DB/드라이브 없이 CSV로 동작')\n"
"print(f'K = {K} neighbors/category')"
)
cells4[3]["source"] = new_cell3

# 셀 7 교체: DB 로드 → CSV 로드
new_cell7 = (
"# (재현용) 사설 DB 대신 CSV 로드\n"
"import os, pandas as pd\n"
"if os.path.exists(CONFIG['edges_csv']):\n"
"    df_raw = pd.read_csv(CONFIG['edges_csv']); print('STEP 3 결과 사용:', CONFIG['edges_csv'])\n"
"else:\n"
"    df_raw = pd.read_csv(CONFIG['sample_url']); print('공개 엣지 데이터 사용 (STEP 3 결과 없음)')\n"
"\n"
"# 컬럼 표준화: cause_std/effect_std → cause/effect (있을 때만)\n"
"df_raw = df_raw.rename(columns={'cause_std': 'cause', 'effect_std': 'effect'})\n"
"df = df_raw[df_raw['frequency'] >= CONFIG['min_freq']].copy().reset_index(drop=True)\n"
"print(f'엣지 {len(df_raw):,} → {len(df):,} (frequency >= {CONFIG[\"min_freq\"]})')\n"
"print('Columns:', list(df.columns))\n"
"\n"
"# 빈도만큼 행 복제 (원본과 동일: 자주 보고된 관계가 더 자주 샘플링됨)\n"
"df_rep = df.loc[df.index.repeat(df['frequency'])].copy().reset_index(drop=True)\n"
"print(f'복제 후 행: {len(df_rep):,}')\n"
"print(df_rep['category_effect'].value_counts().to_string())"
)
cells4[7]["source"] = new_cell7

# 최종 저장 셀(32)에서 google.colab files / drive 의존 제거 — 그대로 둬도 무방하나 download 호출만 보호
# (원본은 shutil.copy 실패 시 colab_files.download; 로컬이면 copy 성공하므로 그대로 둠)

cells4 = [md(INTRO4)] + cells4
write_nb(cells4, "step4_gated.ipynb")

print("step1~4 재현용 노트북 작성 완료 → notebooks/full/")
