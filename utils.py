import csv
import os
import re

import numpy as np
import pandas as pd

try:
    from rank_bm25 import BM25Okapi
except ImportError:  # pragma: no cover
    BM25Okapi = None


DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ipc_act.csv")

CONCEPT_MAP = {
    "theft": {"definition": ["378"], "punishment": ["379"], "related": ["380", "381", "382"], "aliases": ["steal", "stealing", "stolen"]},
    "robbery": {"definition": ["390"], "punishment": ["392"], "related": ["393", "394"], "aliases": ["loot", "looting"]},
    "dacoity": {"definition": ["391"], "punishment": ["395"], "related": ["396", "399", "402"], "aliases": ["gang robbery"]},
    "extortion": {"definition": ["383"], "punishment": ["384"], "related": ["385", "386", "387", "388", "389"], "aliases": ["fear of injury"]},
    "murder": {"definition": ["300"], "punishment": ["302"], "related": ["299", "301", "304", "307"], "aliases": ["kill", "killed", "killing"]},
    "culpable homicide": {"definition": ["299"], "punishment": ["304"], "related": ["300", "301", "304A", "307", "308"], "aliases": ["homicide"]},
    "rape": {"definition": ["375"], "punishment": ["376"], "related": ["376A", "376B", "376C", "376D", "376DA", "376DB", "376E"], "aliases": ["sexual assault"]},
    "assault": {"definition": ["351"], "punishment": ["352"], "related": ["353", "354", "355", "356", "357", "358"], "aliases": ["attack"]},
    "defamation": {"definition": ["499"], "punishment": ["500"], "related": ["501", "502"], "aliases": ["defame", "reputation"]},
    "cheating": {"definition": ["415"], "punishment": ["420"], "related": ["416", "417", "418", "419"], "aliases": ["cheat", "fraud"]},
    "fraud": {"definition": ["415"], "punishment": ["420"], "related": ["416", "417", "418", "419"], "aliases": ["fraudulent", "deception"]},
    "kidnapping": {"definition": ["359"], "punishment": ["363"], "related": ["364", "364A", "365", "366"], "aliases": ["kidnap", "abduction"]},
    "criminal intimidation": {"definition": ["503"], "punishment": ["506"], "related": ["507", "508", "509"], "aliases": ["threat", "threaten", "intimidate"]},
}

GUIDED_SUGGESTIONS = [
    {"query": "section 420", "title": "Go directly to Section 420", "kind": "guided"},
    {"query": "what is murder", "title": "Definition style question", "kind": "guided"},
    {"query": "punishment for robbery", "title": "Punishment style question", "kind": "guided"},
    {"query": "bailable vs non-bailable", "title": "General legal concept question", "kind": "guided"},
    {"query": "what is punishment in ipc", "title": "Broad IPC concept question", "kind": "guided"},
    {"query": "cognizable vs non-cognizable", "title": "Procedural classification question", "kind": "guided"},
]

QUESTION_PATTERNS = {
    "punishment": ["punishment", "sentence", "penalty", "liable", "how many years", "what is the punishment"],
    "definition": ["what is", "define", "definition", "meaning of", "explain", "what does"],
    "section_lookup": ["section", "sec"],
    "chapter_lookup": ["chapter"],
}

GENERIC_QUERY_TOKENS = {
    "what", "is", "mean", "meaning", "by", "tell", "me", "about", "ipc", "section",
    "sections", "law", "legal", "offence", "offences", "crime", "punishment", "definition",
    "details", "explain", "chapter", "code", "indian", "penal",
    "type", "types", "kind", "kinds", "category", "categories",
    "how", "many", "number", "count", "present", "there",
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text)).strip()


def normalize_for_search(text: str) -> str:
    text = normalize_text(text).lower()
    text = re.sub(r"[^a-z0-9\s-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", normalize_for_search(text))


with open(DATA_PATH, encoding="utf-8-sig", newline="") as handle:
    df = pd.DataFrame(list(csv.DictReader(handle))).fillna("")

df.rename(
    columns={
        "section": "section_id",
        "chapter": "chapter_title",
        "title": "section_title",
        "content": "law_text",
    },
    inplace=True,
)

for column in [
    "section_id",
    "chapter_title",
    "section_title",
    "law_text",
    "keywords",
    "aliases",
    "normalized_text",
    "explainer_steps",
    "example_scenario",
    "linked_punishment_section",
    "plain_english",
    "punishment_summary",
    "punishment_min_term",
    "punishment_max_term",
    "punishment_life",
    "punishment_death",
    "fine_possible",
    "bailable_status",
    "cognizable_status",
    "triable_by",
    "legal_notes",
]:
    if column not in df.columns:
        df[column] = ""
    df[column] = df[column].astype(str)

df["section_id"] = df["section_id"].str.strip()
df = df[~df["section_title"].str.startswith(("Subs.", "Ins.", "Rep.", "Regulation"), na=False)].copy()
df = df[~df["section_title"].str.startswith("[", na=False)].copy()
df.reset_index(drop=True, inplace=True)

df["search_blob"] = (
    df["section_id"]
    + " "
    + df["chapter_title"]
    + " "
    + df["section_title"]
    + " "
    + df["keywords"]
    + " "
    + df["aliases"]
    + " "
    + df["normalized_text"]
    + " "
    + df["law_text"]
)

bm25 = BM25Okapi(df["search_blob"].apply(tokenize).tolist()) if BM25Okapi else None


def _row(row: pd.Series) -> dict:
    return {
        "section": str(row["section_id"]),
        "title": normalize_text(row["section_title"]),
        "chapter": normalize_text(row.get("chapter_title", "")),
        "keywords": normalize_text(row.get("keywords", "")),
        "aliases": normalize_text(row.get("aliases", "")),
        "law_text": normalize_text(row["law_text"]),
        "explainer_steps": normalize_text(row.get("explainer_steps", "")),
        "example_scenario": normalize_text(row.get("example_scenario", "")),
        "linked_punishment_section": normalize_text(row.get("linked_punishment_section", "")),
        "plain_english": normalize_text(row.get("plain_english", "")),
        "punishment_summary": normalize_text(row.get("punishment_summary", "")),
        "punishment_min_term": normalize_text(row.get("punishment_min_term", "")),
        "punishment_max_term": normalize_text(row.get("punishment_max_term", "")),
        "punishment_life": normalize_text(row.get("punishment_life", "")),
        "punishment_death": normalize_text(row.get("punishment_death", "")),
        "fine_possible": normalize_text(row.get("fine_possible", "")),
        "bailable_status": normalize_text(row.get("bailable_status", "")),
        "cognizable_status": normalize_text(row.get("cognizable_status", "")),
        "triable_by": normalize_text(row.get("triable_by", "")),
        "legal_notes": normalize_text(row.get("legal_notes", "")),
    }


def extract_section_id(query: str) -> str | None:
    match = re.search(r"\b(\d{1,3}(?:-[a-z]|[a-z]{0,2})?)\b", query.lower())
    return match.group(1).upper() if match else None


def detect_question_type(query: str) -> str:
    q = normalize_for_search(query)
    if any(pattern in q for pattern in ["bailable", "non bailable", "non-bailable", "bail"]):
        return "bail_status"
    if any(pattern in q for pattern in ["cognizable", "non cognizable", "non-cognizable"]):
        return "cognizable_status"
    if any(pattern in q for pattern in ["triable", "which court", "what court", "court of trial", "tried by"]):
        return "triable_by"
    for question_type, patterns in QUESTION_PATTERNS.items():
        if any(pattern in q for pattern in patterns):
            return question_type
    return "general"


def detect_concept(query: str) -> str | None:
    q = normalize_for_search(query)
    ranked = []
    for concept, config in CONCEPT_MAP.items():
        candidates = [concept] + config.get("aliases", [])
        for candidate in candidates:
            candidate_norm = normalize_for_search(candidate)
            if candidate_norm and candidate_norm in q:
                ranked.append((len(candidate_norm.split()), len(candidate_norm), concept))
                break
    if not ranked:
        return None
    ranked.sort(reverse=True)
    return ranked[0][2]


def detect_all_concepts(query: str) -> list[str]:
    q = normalize_for_search(query)
    ranked = []
    for concept, config in CONCEPT_MAP.items():
        candidates = [concept] + config.get("aliases", [])
        for candidate in candidates:
            candidate_norm = normalize_for_search(candidate)
            if candidate_norm and candidate_norm in q:
                ranked.append((len(candidate_norm.split()), len(candidate_norm), concept))
                break
    ranked.sort(reverse=True)
    ordered = []
    seen = set()
    for _, _, concept in ranked:
        if concept not in seen:
            ordered.append(concept)
            seen.add(concept)
    return ordered


def is_low_signal_query(query: str) -> bool:
    tokens = tokenize(query)
    if not tokens:
        return True

    if extract_section_id(query):
        return False

    if detect_concept(query):
        return False

    if detect_question_type(query) == "chapter_lookup":
        return False

    informative = [token for token in tokens if token not in GENERIC_QUERY_TOKENS and len(token) > 2]
    return len(informative) == 0


def get_section_by_id(section_id: str):
    key = str(section_id).strip().upper()
    row = df[df["section_id"].str.upper() == key]
    if row.empty:
        return None
    return _row(row.iloc[0])


def get_dataset_section_count() -> int:
    return int(len(df))


def get_dataset_chapter_count() -> int:
    chapters = (
        df["chapter_title"]
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .str.lower()
        .unique()
    )
    return int(len(chapters))


def get_related_sections_for_detail(section_id: str, chapter: str, limit: int = 3) -> list[dict]:
    key = str(section_id).strip().upper()
    try:
        base_num = int(re.match(r"^(\d+)", key).group(1))
    except Exception:
        base_num = None

    chapter_matches = []
    if chapter:
        chapter_rows = df[df["chapter_title"].str.strip().str.lower() == str(chapter).strip().lower()]
        for _, row in chapter_rows.iterrows():
            sid = str(row["section_id"]).strip().upper()
            if sid == key:
                continue
            m = re.match(r"^(\d+)", sid)
            if not m or base_num is None:
                continue
            diff = abs(int(m.group(1)) - base_num)
            chapter_matches.append((diff, sid, _row(row)))

    chapter_matches.sort(key=lambda item: (item[0], item[1]))
    related = []
    seen = set()
    for _, sid, row in chapter_matches:
        if sid in seen:
            continue
        related.append(row)
        seen.add(sid)
        if len(related) >= limit:
            return related

    title = get_section_by_id(section_id)
    if title:
        for item in search_ipc(title.get("title", ""), top_k=limit + 2):
            sid = str(item.get("section", "")).strip().upper()
            if sid == key or sid in seen:
                continue
            related.append(item)
            seen.add(sid)
            if len(related) >= limit:
                break

    return related


def get_sections_by_ids(section_ids: list[str]) -> list[dict]:
    rows = []
    seen = set()
    for section_id in section_ids:
        item = get_section_by_id(section_id)
        if item and item["section"] not in seen:
            rows.append(item)
            seen.add(item["section"])
    return rows


def chapter_lookup(query: str, top_k: int = 5) -> list[dict]:
    q = normalize_for_search(query)
    q = re.sub(r"\bchapter\b", "", q).strip()
    if not q:
        return []
    matches = df[df["chapter_title"].str.lower().str.contains(q, na=False, regex=False)]
    return [_row(row) for _, row in matches.head(top_k).iterrows()]


def autocomplete_ipc(query: str, limit: int = 5):
    q = normalize_for_search(query)
    if not q:
        return []

    matches = df[
        df["section_title"].str.lower().str.contains(q, na=False, regex=False)
        | df["section_id"].str.lower().str.startswith(q, na=False)
        | df["aliases"].str.lower().str.contains(q, na=False, regex=False)
        | df["keywords"].str.lower().str.contains(q, na=False, regex=False)
    ].head(limit)

    suggestions = []
    seen = set()

    for item in GUIDED_SUGGESTIONS:
        haystack = normalize_for_search(f"{item['query']} {item['title']}")
        if q in haystack:
            key = ("guided", item["query"])
            if key not in seen:
                suggestions.append(item.copy())
                seen.add(key)
        if len(suggestions) >= limit:
            return suggestions

    for _, row in matches.iterrows():
        item = {
            "section": row["section_id"],
            "title": normalize_text(row["section_title"]),
            "query": f"section {row['section_id']}",
            "kind": "section",
        }
        key = ("section", item["section"])
        if key not in seen:
            suggestions.append(item)
            seen.add(key)
        if len(suggestions) >= limit:
            break

    return suggestions


def rule_based_search(query: str, top_k: int = 5) -> list[dict]:
    qtype = detect_question_type(query)
    section_id = extract_section_id(query)
    concept = detect_concept(query)

    if section_id:
        exact = get_section_by_id(section_id)
        return [exact] if exact else []

    if qtype == "chapter_lookup":
        chapter_results = chapter_lookup(query, top_k=top_k)
        if chapter_results:
            return chapter_results

    if concept:
        config = CONCEPT_MAP[concept]
        ordered_ids = []
        if qtype in {"punishment", "bail_status", "cognizable_status", "triable_by"}:
            ordered_ids.extend(config["punishment"])
            ordered_ids.extend(config["definition"])
        elif qtype == "definition":
            ordered_ids.extend(config["definition"])
            ordered_ids.extend(config["punishment"])
        else:
            ordered_ids.extend(config["definition"])
            ordered_ids.extend(config["punishment"])
        ordered_ids.extend(config["related"])
        results = get_sections_by_ids(ordered_ids)
        if results:
            return results[:top_k]

    return []


def bm25_search(query: str, top_k: int = 5) -> list[dict]:
    if is_low_signal_query(query):
        return []

    q = normalize_text(query)
    q_lower = q.lower()
    q_tokens = tokenize(q)
    scores = np.array(bm25.get_scores(q_tokens), dtype=float) if bm25 else np.zeros(len(df), dtype=float)

    title_boost = df["section_title"].str.lower().str.contains(q_lower, na=False, regex=False).astype(float).to_numpy() * 10.0
    chapter_boost = df["chapter_title"].str.lower().str.contains(q_lower, na=False, regex=False).astype(float).to_numpy() * 5.0
    alias_boost = df["aliases"].str.lower().str.contains(q_lower, na=False, regex=False).astype(float).to_numpy() * 9.0
    keyword_boost = df["keywords"].str.lower().str.contains(q_lower, na=False, regex=False).astype(float).to_numpy() * 7.0
    normalized_boost = df["normalized_text"].str.lower().str.contains(q_lower, na=False, regex=False).astype(float).to_numpy() * 4.0
    definition_boost = np.zeros(len(df), dtype=float)

    if detect_question_type(query) == "definition":
        definition_boost += df["law_text"].str.lower().str.contains(
            r"\bis said to\b|\bmeans\b|\bdenotes\b|\bincludes\b",
            na=False,
            regex=True,
        ).astype(float).to_numpy() * 7.0

    for token in q_tokens:
        title_boost += df["section_title"].str.lower().str.contains(token, na=False, regex=False).astype(float).to_numpy() * 1.5
        alias_boost += df["aliases"].str.lower().str.contains(token, na=False, regex=False).astype(float).to_numpy() * 2.0
        keyword_boost += df["keywords"].str.lower().str.contains(token, na=False, regex=False).astype(float).to_numpy() * 1.2

    final_scores = scores + title_boost + chapter_boost + alias_boost + keyword_boost + normalized_boost + definition_boost
    ranked_idx = np.argsort(final_scores)[::-1]

    results = []
    seen = set()
    for idx in ranked_idx:
        if final_scores[idx] <= 0:
            continue
        row = _row(df.iloc[idx])
        if row["section"] in seen:
            continue
        seen.add(row["section"])
        results.append(row)
        if len(results) >= top_k:
            break
    return results


def search_ipc(query: str, top_k: int = 5):
    direct = rule_based_search(query, top_k=top_k)
    if direct:
        return direct

    return bm25_search(query, top_k=top_k)
