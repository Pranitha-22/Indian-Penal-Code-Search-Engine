from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import html
import os
import re

from utils import (
    autocomplete_ipc,
    detect_all_concepts,
    detect_concept,
    detect_question_type,
    get_dataset_chapter_count,
    get_dataset_section_count,
    extract_section_id,
    get_related_sections_for_detail,
    get_section_by_id,
    search_ipc,
)


app = FastAPI(title="IPC AI Legal Assistant")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


conversation_memory = {"last_query": None}
STATIC_VERSION = "20260326-primary-link-clean-v3"

GENERAL_KNOWLEDGE = [
    {
        "patterns": ["what is ipc", "explain ipc", "about ipc", "indian penal code"],
        "title": "Indian Penal Code Overview",
        "answer": (
            "The Indian Penal Code, 1860, is the main substantive criminal law text that defines offences and prescribes punishments. "
            "It explains what conduct amounts to offences such as murder, theft, robbery, cheating, defamation, rape, and criminal intimidation. "
            "For procedural issues like bail, cognizable or non-cognizable classification, and trial process, you usually need criminal procedure law in addition to the IPC."
        ),
        "sections": [],
    },
    {
        "patterns": ["what is punishment", "types of punishment", "how many types of punishment", "punishment in ipc", "section 53"],
        "title": "Punishments Under IPC",
        "answer": (
            "In IPC, punishment means the legal consequence imposed for an offence after conviction. "
            "Section 53 traditionally lists five kinds of punishments: death, imprisonment for life, imprisonment (rigorous or simple), forfeiture of property, and fine. "
            "The exact punishment depends on the specific offence section."
        ),
        "sections": ["53"],
    },
    {
        "patterns": ["rigorous imprisonment", "simple imprisonment", "difference between rigorous and simple imprisonment"],
        "title": "Rigorous vs Simple Imprisonment",
        "answer": (
            "Rigorous imprisonment involves hard labour, while simple imprisonment does not. "
            "When an IPC section prescribes imprisonment, the exact nature and duration depend on the wording of that section and the sentencing decision in the case."
        ),
        "sections": ["53"],
    },
    {
        "patterns": ["life imprisonment", "what is life imprisonment", "meaning of life imprisonment"],
        "title": "Life Imprisonment in IPC",
        "answer": (
            "Life imprisonment is one of the punishments recognized by IPC. "
            "It is not the same thing as a short fixed term such as seven or ten years. "
            "For offence-specific punishment, the relevant IPC offence section still has to be identified."
        ),
        "sections": ["53"],
    },
    {
        "patterns": ["fine in ipc", "what is fine in ipc", "what is forfeiture of property"],
        "title": "Fine and Forfeiture Under IPC",
        "answer": (
            "Fine and forfeiture of property are punishment types recognized in IPC. "
            "Whether a court may impose them depends on the wording of the specific offence section and the facts of the case."
        ),
        "sections": ["53"],
    },
    {
        "patterns": ["bailable", "non bailable", "non-bailable", "difference between bailable and non bailable", "difference between bailable and non-bailable"],
        "title": "Bailable vs Non-Bailable",
        "answer": (
            "Bailable and non-bailable are not classifications created by IPC sections themselves. "
            "They come from criminal procedure law and are offence-specific. "
            "A bailable offence generally gives the accused a right to bail, while a non-bailable offence does not create an automatic right and bail depends on the court. "
            "To answer correctly, the offence or section must be identified first."
        ),
        "sections": [],
    },
    {
        "patterns": ["cognizable", "non cognizable", "non-cognizable", "difference between cognizable and non cognizable", "difference between cognizable and non-cognizable"],
        "title": "Cognizable vs Non-Cognizable",
        "answer": (
            "Cognizable and non-cognizable are also procedural classifications, not standalone IPC definitions. "
            "In a cognizable offence, police may generally register and investigate without prior magistrate permission. "
            "In a non-cognizable offence, the procedural requirements are narrower. "
            "The correct classification depends on the particular offence and procedural schedule."
        ),
        "sections": [],
    },
    {
        "patterns": ["how many years of punishment", "how many years in ipc", "years of punishment in ipc"],
        "title": "Punishment Terms in IPC",
        "answer": (
            "IPC does not have one single punishment term for all offences. "
            "The punishment depends on the specific section. Some offences carry fine, some carry short imprisonment, some carry life imprisonment, and a few may carry death. "
            "Ask about a specific offence or section to get the actual punishment range."
        ),
        "sections": ["53"],
    },
    {
        "patterns": ["types of offences in ipc", "major offences in ipc", "what offences are in ipc"],
        "title": "Major IPC Offence Categories",
        "answer": (
            "IPC covers many offence groups, including offences against the human body, offences against property, offences relating to marriage, defamation, cheating, criminal intimidation, and public order related offences. "
            "A stronger answer depends on the offence group you want to explore."
        ),
        "sections": [],
    },
]

POPULAR_QUERIES = [
    "Murder",
    "Theft",
    "Robbery",
    "Cheating",
    "Defamation",
    "Bailable vs Non-Bailable",
    "Types of Punishment",
]


def format_section_payload(item: dict) -> dict:
    return {
        "section": item["section"],
        "title": item["title"],
        "chapter": item.get("chapter", ""),
        "keywords": item.get("keywords", ""),
        "snippet": trim_text(item["law_text"], 240),
        "law_text": item.get("law_text", ""),
        "explainer_steps": item.get("explainer_steps", ""),
        "example_scenario": item.get("example_scenario", ""),
        "plain_english": item.get("plain_english", ""),
        "punishment_summary": item.get("punishment_summary", ""),
        "punishment_min_term": item.get("punishment_min_term", ""),
        "punishment_max_term": item.get("punishment_max_term", ""),
        "punishment_life": item.get("punishment_life", ""),
        "punishment_death": item.get("punishment_death", ""),
        "fine_possible": item.get("fine_possible", ""),
        "bailable_status": item.get("bailable_status", ""),
        "cognizable_status": item.get("cognizable_status", ""),
        "triable_by": item.get("triable_by", ""),
        "legal_notes": item.get("legal_notes", ""),
    }


def should_show_general_explainer(query: str, title: str = "") -> bool:
    probe = f"{query} {title}".lower()
    return not re.search(
        r"\b(types?|kinds?|categories|how many|number of|count|overview|about)\b",
        probe,
        flags=re.IGNORECASE,
    )


def detect_structural_query(query: str) -> dict | None:
    q = query.lower().strip()

    has_ipc_overview_intent = (
        "ipc" in q
        and re.search(r"\b(what is ipc|what is indian penal code|indian penal code|about ipc|explain ipc)\b", q)
    )
    asks_section_count = bool(re.search(r"\b(how many|number of|count)\s+sections\b", q))
    asks_chapter_count = bool(re.search(r"\b(how many|number of|count)\s+chapters\b", q))
    asks_chapters_and_sections = bool(
        re.search(r"\bchapters?\b", q)
        and re.search(r"\bsections?\b", q)
        and re.search(r"\b(how many|number of|count)\b", q)
    )

    if "ipc" in q and (has_ipc_overview_intent or asks_section_count or asks_chapter_count or asks_chapters_and_sections):
        section_count = get_dataset_section_count()
        chapter_count = get_dataset_chapter_count()
        return {
            "answer_mode": "general",
            "general_title": "Indian Penal Code Overview",
            "answer": (
                "The Indian Penal Code, 1860, is the main substantive criminal law text that defines offences and prescribes punishments. "
                f"In this app's current dataset, there are {chapter_count} distinct chapter headings and {section_count} section entries. "
                "The Code covers topics such as general explanations, punishments, offences against the State, offences against the human body, offences against property, defamation, cheating, and criminal intimidation."
            ),
            "sections": [],
            "query_type": "general",
            "concept": "",
            "show_explainer": False,
        }

    if asks_section_count and "ipc" in q:
        count = get_dataset_section_count()
        return {
            "answer_mode": "general",
            "general_title": "How Many Sections Are In This IPC Dataset?",
            "answer": (
                f"This app currently contains {count} IPC section entries in its dataset. "
                "IPC is organized across many chapters, and the exact number of section entries in the app depends on the dataset copy being used here."
            ),
            "sections": [],
            "query_type": "general",
            "concept": "",
            "show_explainer": False,
        }

    if re.search(r"\b(section categories|types of section categories|types of sections|categories of sections)\b", q):
        sections = []
        for section_id in ["53", "299", "378", "499", "503"]:
            item = get_section_by_id(section_id)
            if item:
                sections.append(format_section_payload(item))
        return {
            "answer_mode": "general",
            "general_title": "IPC Section Categories",
            "answer": (
                "IPC sections are grouped chapter-wise by subject matter, not by a single fixed 'section category' list. "
                "Major groups include general explanations, punishments, general exceptions, offences against the State, offences against the human body, offences against property, defamation, cheating, and criminal intimidation."
            ),
            "sections": sections,
            "query_type": "general",
            "concept": "",
            "show_explainer": False,
        }

    concept = detect_concept(q)
    if concept and re.search(r"\b(types?|kinds?|categories)\s+of\b", q):
        related = search_ipc(f"what is {concept}", top_k=4)
        sections = []
        seen = set()
        for item in related:
            sid = item.get("section", "")
            if not sid or sid in seen:
                continue
            seen.add(sid)
            sections.append(format_section_payload(item))
        return {
            "answer_mode": "general",
            "general_title": f"Related IPC Sections for {concept.title()}",
            "answer": (
                f"IPC does not usually present {concept} as a simple list of 'types'. "
                f"The better way to understand it is to look at the main definition section, the punishment section, and closely related sections that modify, aggravate, or distinguish the offence."
            ),
            "sections": sections,
            "query_type": "general",
            "concept": concept,
            "show_explainer": False,
        }

    return None


def normalize_query(query: str) -> str:
    query = query.lower().strip()
    replacements = {
        "stoles": "steals",
        "stealed": "steal",
        "snatch": "theft",
        "loot": "robbery",
        "what is mean by": "what is",
        "what is meant by": "what is",
        "mean by": "",
        "meaning of": "what is",
        "tell me about": "what is",
    }
    for source, target in replacements.items():
        query = query.replace(source, target)
    query = re.sub(r"\bdoes\s+(.+?)\s+is\s+(bailable|cognizable)\b", r"is \1 \2", query)
    query = re.sub(r"\bwhat\s+is\s+mean\s+by\b", "what is", query)
    query = re.sub(r"\bwhat\s+is\s+meant\s+by\b", "what is", query)
    return re.sub(r"\s+", " ", query).strip()


def enrich_query(query: str) -> str:
    last_query = conversation_memory["last_query"]
    follow_up_tokens = {"punishment", "explain", "details", "definition", "meaning"}

    if not last_query:
        return query

    if detect_general_knowledge(query):
        return query

    if query in follow_up_tokens:
        return f"{last_query} {query}"

    return query


def detect_general_knowledge(query: str):
    q = query.lower().strip()
    if detect_concept(q) or extract_section_id(q):
        return None
    for item in GENERAL_KNOWLEDGE:
        if any(pattern in q for pattern in item["patterns"]):
            return item
    return None


def detect_comparison_query(query: str) -> list[str]:
    q = query.lower().strip()
    if "difference between" not in q and " vs " not in q and " versus " not in q:
        return []
    concepts = detect_all_concepts(q)
    return concepts[:2] if len(concepts) >= 2 else []


def canonicalize_query(query: str) -> str:
    question_type = detect_question_type(query)
    concept = detect_concept(query)

    if not concept:
        return query

    if question_type == "punishment":
        return f"punishment for {concept}"
    if question_type == "bail_status":
        return f"is {concept} bailable"
    if question_type == "cognizable_status":
        return f"is {concept} cognizable"
    if question_type == "triable_by":
        return f"which court tries {concept}"
    if question_type in {"definition", "general"}:
        return f"what is {concept}"

    return query


def trim_text(text: str, limit: int = 900) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    cutoff = text.rfind(".", 0, limit)
    if cutoff < 240:
        cutoff = text.rfind(" ", 0, limit)
    if cutoff < 240:
        cutoff = limit
    return text[: cutoff + 1].strip()


def clean_summary_text(text: str) -> str:
    text = re.sub(r"\s+", " ", str(text)).strip()
    text = re.sub(r"\b\d+\[", "", text)
    text = text.replace("]", "")
    text = re.sub(r"\b\d+\s*\*\s*(?:\*\s*)+", "", text)

    display_fixes = {
        r"\bpu\s+nishment\b": "punishment",
        r"\bimpriso\s+nment\b": "imprisonment",
        r"\bkidna\s+pping\b": "kidnapping",
        r"\bcommi\s+tting\b": "committing",
        r"\bserva\s+nt\b": "servant",
        r"\bha\s+rm\b": "harm",
        r"\bdivi\s+ne\b": "divine",
        r"\bprecau\s+tion\b": "precaution",
        r"\bcommuni\s+cation\b": "communication",
        r"\bintimida\s+tion\b": "intimidation",
        r"\bstateme\s+nts\b": "statements",
        r"\bag\s+ainst\b": "against",
        r"\bmen\s+tioned\b": "mentioned",
        r"\bpriso\s+ner\b": "prisoner",
        r"\bsuff\s+ering\b": "suffering",
        r"\bitis\b": "it is",
        r"\btheo\s+ffence\b": "the offence",
        r"\btakinga\b": "taking a",
        r"\binfluencea\b": "influence a",
        r"\bwitha\b": "with a",
        r"\bservantof\b": "servant of",
        r"\bservantwith\b": "servant with",
        r"\bservantby\b": "servant by",
        r"\bnon\s+-attendance\b": "non-attendance",
    }
    for pattern, replacement in display_fixes.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text


def text_token_set(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", clean_summary_text(text).lower()))


def build_section_keyword_html(result: dict) -> str:
    raw_keywords = result.get("keywords", "")
    if not raw_keywords:
        return ""

    blocked_terms = {
        "offence",
        "offences",
        "thing",
        "explanation",
        "code",
        "chapter",
        "section",
        "provisions",
        "liable",
        "offenders",
        "ipc",
        "indian",
        "penal",
        "kind",
        "kinds",
        "type",
        "types",
    }

    context_tokens = (
        text_token_set(result.get("title", ""))
        | text_token_set(result.get("chapter", ""))
        | text_token_set(result.get("plain_english", ""))
    )

    useful_keywords = []
    seen = set()

    for item in raw_keywords.split(","):
        label = clean_summary_text(item)
        key = label.lower().strip()
        if not key or len(key) <= 2:
            continue
        if key.isdigit():
            continue
        if re.fullmatch(r"[ivxlcdm]+", key):
            continue
        if key in blocked_terms:
            continue

        item_tokens = set(re.findall(r"[a-z0-9]+", key))
        if not item_tokens:
            continue
        if item_tokens.issubset(context_tokens):
            continue
        if len(item_tokens) == 1 and any(key != token and key in token for token in context_tokens):
            continue
        if key in seen:
            continue

        seen.add(key)
        useful_keywords.append(label)

    return "".join(f'<span class="chip chip-muted">{html.escape(item)}</span>' for item in useful_keywords[:6])


def is_definition_like_section(section: dict) -> bool:
    title = clean_summary_text(section.get("title", "")).lower()
    if title.startswith("punishment for"):
        return False

    body = clean_summary_text(section.get("law_text", "")).lower()
    return bool(
        re.search(
            r"\bis of two kinds\b|\bis said to\b|\bmeans\b|\bdenotes\b|\bincludes\b",
            body,
            flags=re.IGNORECASE,
        )
    )


def should_show_detail_explainer(section: dict) -> bool:
    has_custom_steps = bool(str(section.get("explainer_steps", "")).strip())
    has_custom_scenario = bool(str(section.get("example_scenario", "")).strip())
    title = clean_summary_text(section.get("title", "")).lower()
    is_punishment_title = title.startswith("punishment for")

    if is_definition_like_section(section):
        return False

    if is_punishment_title:
        return True

    return has_custom_steps or has_custom_scenario


def brief_answer_text(text: str, limit: int = 360) -> str:
    text = clean_summary_text(text)
    text = re.split(r"Illustrations?|Explanation|Exception", text, maxsplit=1, flags=re.IGNORECASE)[0]
    return trim_text(text, limit)


def build_structured_answer(query: str, section: dict) -> str | None:
    question_type = detect_question_type(query)

    if question_type == "bail_status" and section.get("bailable_status"):
        extra = f" It is {section['cognizable_status'].lower()}." if section.get("cognizable_status") else ""
        return f"Section {section['section']} IPC is {section['bailable_status'].lower()}.{extra}"

    if question_type == "cognizable_status" and section.get("cognizable_status"):
        extra = f" It is {section['bailable_status'].lower()}." if section.get("bailable_status") else ""
        return f"Section {section['section']} IPC is {section['cognizable_status'].lower()}.{extra}"

    if question_type == "triable_by" and section.get("triable_by"):
        return f"Section {section['section']} IPC is triable by {section['triable_by']}."

    if question_type == "punishment" and section.get("punishment_summary"):
        return section["punishment_summary"]

    if (
        question_type in {"definition", "general"}
        and section.get("plain_english")
        and not re.search(r"\bhow many types\b|\bwhat is punishment\b", query, flags=re.IGNORECASE)
    ):
        return section["plain_english"]

    if re.search(r"\bhow many years\b|\bmaximum punishment\b|\bmax punishment\b|\bterm of punishment\b", query, flags=re.IGNORECASE):
        if section.get("punishment_summary"):
            return section["punishment_summary"]

    return None


def summarize_for_question(query: str, section: dict) -> str:
    structured = build_structured_answer(query, section)
    if structured:
        return structured

    question_type = detect_question_type(query)
    body = section["law_text"]

    if question_type == "punishment":
        punish_match = re.search(r"shall be punished.*", body, flags=re.IGNORECASE)
        if punish_match:
            return brief_answer_text(punish_match.group(0), 260)

    if question_type == "definition":
        definition_match = re.split(r"Illustrations?|Exception|Explanation", body, maxsplit=1, flags=re.IGNORECASE)[0]
        return brief_answer_text(definition_match, 420)

    return brief_answer_text(body, 420)


def detail_text_html(text: str) -> str:
    text = clean_summary_text(text)
    text = html.escape(text)
    blocks = re.split(r"(?=Illustrations?:|Explanation\s*\d*\.?â€”|Exception\.?â€”)", text)
    paragraphs = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        paragraphs.append(f"<p>{block}</p>")
    return "".join(paragraphs)


def generate_answer(query: str, sections: list[dict]) -> str:
    if not sections:
        return (
            "No reliable IPC match was found for that query. Try a section number like 420 or 375, "
            "or ask directly for an offence such as robbery, theft, rape, murder, cheating, kidnapping, or criminal intimidation."
        )

    primary = sections[0]
    question_type = detect_question_type(query)
    concept = detect_concept(query)
    body = summarize_for_question(query, primary)

    lines = [f"Section {primary['section']} IPC", primary["title"]]
    if primary.get("chapter"):
        lines.append(primary["chapter"])

    if concept:
        lines.append(f"Matched concept: {concept.title()}")

    lines.append("")

    if question_type == "punishment":
        lines.append("Punishment answer:")
    elif question_type == "definition":
        lines.append("Definition answer:")
    elif question_type == "chapter_lookup":
        lines.append("Chapter match:")
    else:
        lines.append("Relevant IPC answer:")

    lines.append(body)

    if len(sections) > 1:
        lines.append("")
        lines.append("Related sections:")
        for item in sections[1:4]:
            lines.append(f"- Section {item['section']}: {item['title']}")

    return "\n".join(lines)


def build_comparison_payload(concepts: list[str]) -> dict:
    entries = []
    for concept in concepts:
        result = search_ipc(f"what is {concept}", top_k=2)
        if not result:
            continue
        primary = result[0]
        entries.append(
            {
                "concept": concept,
                "section": primary["section"],
                "title": primary["title"],
                "chapter": primary.get("chapter", ""),
                "plain_english": primary.get("plain_english", "") or primary.get("law_text", ""),
                "punishment_summary": primary.get("punishment_summary", ""),
                "bailable_status": primary.get("bailable_status", ""),
                "cognizable_status": primary.get("cognizable_status", ""),
                "triable_by": primary.get("triable_by", ""),
            }
        )

    if len(entries) < 2:
        return {}

    return {
        "answer_mode": "comparison",
        "general_title": f"{entries[0]['concept'].title()} vs {entries[1]['concept'].title()}",
        "answer": (
            f"{entries[0]['concept'].title()} and {entries[1]['concept'].title()} are different IPC concepts. "
            "Compare the definition, punishment, bail status, cognizable status, and trial forum before treating them as the same."
        ),
        "comparison": entries,
    }


@app.post("/ask")
def ask(req: SearchRequest):
    user_query = req.query.strip()
    normalized_query = enrich_query(normalize_query(user_query))

    structural = detect_structural_query(normalized_query)
    if structural:
        structural["query"] = user_query
        return JSONResponse(structural)

    general = detect_general_knowledge(normalized_query)
    if general:
        sections = []
        seen_sections = set()

        def add_item(item: dict):
            sid = item.get("section", "")
            if not sid or sid in seen_sections:
                return
            seen_sections.add(sid)
            sections.append(format_section_payload(item))

        for section_id in general.get("sections", []):
            item = get_section_by_id(section_id)
            if item:
                add_item(item)

        if sections:
            related = get_related_sections_for_detail(sections[0]["section"], sections[0].get("chapter", ""), limit=3)
            for item in related:
                add_item(item)

        return JSONResponse(
            {
                "answer_mode": "general",
                "general_title": general["title"],
                "answer": general["answer"],
                "sections": sections,
                "query": user_query,
                "query_type": "general",
                "concept": "",
                "show_explainer": should_show_general_explainer(user_query, general["title"]),
            }
        )

    query = canonicalize_query(normalized_query)

    comparison_concepts = detect_comparison_query(query)
    if comparison_concepts:
        payload = build_comparison_payload(comparison_concepts)
        if payload:
            payload["query"] = user_query
            payload["query_type"] = detect_question_type(query)
            payload["concept"] = detect_concept(query) or ""
            return JSONResponse(payload)

    results = search_ipc(query, top_k=req.top_k)

    query_type = detect_question_type(query)
    if results and query_type in {"section_lookup", "definition", "general", "punishment"}:
        primary = results[0]
        seen = {str(item.get("section", "")).strip().upper() for item in results}
        related = get_related_sections_for_detail(primary["section"], primary.get("chapter", ""), limit=3)
        for item in related:
            sid = str(item.get("section", "")).strip().upper()
            if not sid or sid in seen:
                continue
            results.append(item)
            seen.add(sid)
            if len(results) >= max(req.top_k, 4):
                break

    answer = generate_answer(query, results)
    conversation_memory["last_query"] = query

    formatted = [format_section_payload(item) for item in results]

    return JSONResponse(
        {
            "answer_mode": "section",
            "general_title": "",
            "answer": answer,
            "sections": formatted,
            "query": user_query,
            "query_type": detect_question_type(query),
            "concept": detect_concept(query) or "",
        }
    )


@app.get("/autocomplete")
def autocomplete(q: str):
    return autocomplete_ipc(q)


@app.get("/section/{section_id}", response_class=HTMLResponse)
def section_detail(section_id: str):
    result = get_section_by_id(section_id)
    if not result:
        safe_id = html.escape(section_id)
        return HTMLResponse(
            f"""
            <!DOCTYPE html>
            <html lang="en">
              <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Section {safe_id} not found</title>
                <link rel="stylesheet" href="/static/index.css?v={STATIC_VERSION}">
              </head>
              <body>
                <header class="top-bar">
                  <div>About</div>
                  <div>Legal</div>
                </header>
                <main class="detail-page">
                  <div class="detail-shell">
                    <a class="detail-back" href="/">Back to search</a>
                    <section class="detail-card">
                      <span class="eyebrow">SECTION LOOKUP</span>
                      <h1>Section {safe_id} not found</h1>
                      <p class="detail-text">This section is missing from the current dataset.</p>
                    </section>
                  </div>
                </main>
              </body>
            </html>
            """,
            status_code=404,
        )

    section = html.escape(result["section"])
    chapter_value = result.get("chapter", "")
    chapter = html.escape(chapter_value)
    title = html.escape(result["title"])
    law_text = detail_text_html(result["law_text"])

    fact_pills = []
    if result.get("bailable_status"):
        fact_pills.append(f'<span class="chip">{html.escape(result["bailable_status"])}</span>')
    if result.get("cognizable_status"):
        fact_pills.append(f'<span class="chip">{html.escape(result["cognizable_status"])}</span>')
    if result.get("triable_by"):
        fact_pills.append(f'<span class="chip">{html.escape(result["triable_by"])}</span>')
    facts_pills_html = "".join(fact_pills)

    fact_rows = []
    if result.get("plain_english"):
        fact_rows.append(
            f'<div class="meta-detail-row"><span class="meta-detail-label">Meaning</span><span class="meta-detail-value">{html.escape(clean_summary_text(result["plain_english"]))}</span></div>'
        )
    if result.get("punishment_summary"):
        fact_rows.append(
            f'<div class="meta-detail-row"><span class="meta-detail-label">Punishment</span><span class="meta-detail-value">{html.escape(clean_summary_text(result["punishment_summary"]))}</span></div>'
        )
    if result.get("punishment_max_term"):
        fact_rows.append(
            f'<div class="meta-detail-row"><span class="meta-detail-label">Maximum term</span><span class="meta-detail-value">{html.escape(clean_summary_text(result["punishment_max_term"]))}</span></div>'
        )
    if result.get("linked_punishment_section"):
        fact_rows.append(
            f'<div class="meta-detail-row"><span class="meta-detail-label">Punishment section</span><span class="meta-detail-value">Section {html.escape(result["linked_punishment_section"])} IPC</span></div>'
        )
    if result.get("legal_notes"):
        fact_rows.append(
            f'<div class="meta-detail-row"><span class="meta-detail-label">Note</span><span class="meta-detail-value">{html.escape(clean_summary_text(result["legal_notes"]))}</span></div>'
        )
    metadata_html = ""
    if facts_pills_html or fact_rows:
        pill_html = f'<div class="meta-pill-row">{facts_pills_html}</div>' if facts_pills_html else ""
        detail_html = f'<div class="meta-detail-list">{"".join(fact_rows)}</div>' if fact_rows else ""
        metadata_html = f'<div class="meta-panel">{pill_html}{detail_html}</div>'

    explainer_html = ""
    if should_show_detail_explainer(result):
        raw_steps = [item.strip() for item in str(result.get("explainer_steps", "")).split("|") if item.strip()]
        title_base = result["title"].rstrip(".").strip() or f"Section {result['section']}"
        is_punishment_title = title_base.lower().startswith("punishment for")

        if raw_steps:
            explainer_steps = raw_steps
        else:
            explainer_steps = [
                "Identify the offence",
                "Confirm the section applies",
                "Read the punishment rule",
                "Apply the sentence range",
            ]

        explainer_scenario = clean_summary_text(str(result.get("example_scenario", "")).strip())
        explainer_scenario = re.sub(r"^example\s*:\s*", "", explainer_scenario, flags=re.IGNORECASE)
        if not explainer_scenario and is_punishment_title:
            explainer_scenario = f"After identifying the offence, read Section {result['section']} to see the punishment the law allows."

        steps_html = '<div class="explainer-arrow" aria-hidden="true">&rarr;</div>'.join(
            f'<div class="explainer-step"><span class="explainer-index">{idx}</span><span class="explainer-text">{html.escape(step)}</span></div>'
            for idx, step in enumerate(explainer_steps, start=1)
        )
        scenario_html = (
            f'<div class="explainer-scenario"><strong>Example Scenario:</strong><span>{html.escape(explainer_scenario)}</span></div>'
            if explainer_scenario
            else ""
        )
        explainer_html = (
            f'<section class="explainer-panel">'
            f'<div class="sources-header"><span class="eyebrow">Visual Explainer</span><h3>How {html.escape(title_base)} Works</h3></div>'
            f'<div class="explainer-flow">{steps_html}</div>'
            f'{scenario_html}'
            f'</section>'
        )

    related_sections = get_related_sections_for_detail(result["section"], chapter_value, limit=3)
    related_html = ""
    if related_sections:
        cards = []
        for item in related_sections:
            item_section = html.escape(item.get("section", ""))
            item_title = html.escape(item.get("title", ""))
            item_chapter = html.escape(item.get("chapter", ""))
            preview = item.get("plain_english") or item.get("punishment_summary") or trim_text(item.get("law_text", ""), 180)
            preview_html = html.escape(clean_summary_text(preview))
            chapter_html = f'<div class="chip-row"><span class="chip">{item_chapter}</span></div>' if item_chapter else ""
            card = f"""
            <article class="result-card" onclick="window.location.href='/section/{item_section}'">
              <div class="result-top">
                <span class="result-section">Section {item_section}</span>
                <span class="result-action">Related section</span>
              </div>
              <h4>{item_title}</h4>
              {chapter_html}
              <p>{preview_html}</p>
            </article>
            """
            cards.append(card)
        related_html = f"""
          <section class="sources-panel">
            <div class="sources-header">
              <span class="eyebrow">RELATED</span>
              <h3>Relevant Sections</h3>
            </div>
            <div class="result-grid">{"".join(cards)}</div>
          </section>
        """

    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Section {section} IPC</title>
      <link rel="stylesheet" href="/static/index.css?v={STATIC_VERSION}">
    </head>
    <body>
      <header class="top-bar">
        <div>About</div>
        <div>Legal</div>
      </header>
      <main class="detail-page">
        <div class="detail-shell">
          <a class="detail-back" href="/">Back to search</a>
          <section class="detail-card">
            <span class="eyebrow">SECTION DETAIL</span>
            <h1>Section {section} IPC</h1>
            <h2>{title}</h2>
            <div class="chip-row">
              <span class="chip">{chapter}</span>
            </div>
            {metadata_html}
            <div class="detail-text">{law_text}</div>
          </section>
          {explainer_html}
          {related_html}
        </div>
      </main>
    </body>
    </html>
    """)


@app.get("/", response_class=HTMLResponse)
def home():
    popular_html = "".join(
        f"<button onclick=\"query.value='{html.escape(item)}'; askAI()\">{html.escape(item)}</button>"
        for item in POPULAR_QUERIES
    )
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>IPC Search</title>
  <link rel="stylesheet" href="/static/index.css?v={STATIC_VERSION}">
</head>
<body>
  <header class="top-bar">
    <div>About</div>
    <div>Legal</div>
  </header>

  <div id="app" class="home">
    <main id="main">
      <div class="hero">
        <h1 class="hero-title">Indian Penal Code</h1>
        <p class="hero-sub">Ask section questions, offence questions, punishment questions, bail questions, and broader IPC concept questions.</p>
      </div>

      <div class="search-box">
        <input id="query" placeholder="Ask about sections, punishments, bail, cognizable rules, or offence meanings..." autocomplete="off">
        <button onclick="askAI()" aria-label="Search">Search</button>
        <div id="suggestions" class="suggestions"></div>
      </div>

      <div class="popular">
        <h4>POPULAR CATEGORIES</h4>
        <div class="categories">
          {popular_html}
        </div>
      </div>

      <div id="results"></div>
    </main>
  </div>

  <script src="/static/app.js?v={STATIC_VERSION}"></script>
</body>
</html>
"""
