import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ===============================
# LOAD DATASET
# ===============================
df = pd.read_csv("IPC_DATASET.csv").fillna("")

# Safety: Ensure required columns exist
required_cols = [
    "section_id", "section_title", "chapter_title",
    "law_text", "main_text", "proviso",
    "explanation", "illustration",
    "exception", "punishment_text", "keywords"
]

for col in required_cols:
    if col not in df.columns:
        df[col] = ""

# ===============================
# SEARCH TEXT
# ===============================
df["search_text"] = (
    df["section_title"].astype(str) + " " +
    df["law_text"].astype(str) + " " +
    df["keywords"].astype(str)
)

# ===============================
# VECTORIZE
# ===============================
vectorizer = TfidfVectorizer(
    stop_words="english",
    ngram_range=(1, 2),
    sublinear_tf=True,
    max_features=20000
)

tfidf_matrix = vectorizer.fit_transform(df["search_text"])

# ===============================
# SERIALIZER
# ===============================
def _row(r):
    return {
        "section": str(r["section_id"]),
        "title": r["section_title"],
        "chapter": r["chapter_title"],
        "law_text": r["law_text"],
        "main_text": r["main_text"],
        "proviso": r["proviso"],
        "explanation": r["explanation"],
        "illustration": r["illustration"],
        "exception": r["exception"],
        "punishment": r["punishment_text"],
        "keywords": r.get("keywords", "")
    }

# ===============================
# SEARCH
# ===============================
def search_ipc(query: str, top_k: int = 6):
    query = query.strip()
    if not query:
        return []

    if query.isdigit():
       match = df[df["section_id"].astype(str).str.contains(f"^{query}", regex=True)]
       if not match.empty:
          return [_row(match.iloc[0])]


    q_vec = vectorizer.transform([query])
    scores = cosine_similarity(q_vec, tfidf_matrix)[0]
    ranked = scores.argsort()[::-1][:top_k]

    if scores[ranked[0]] < 0.02:
        return []

    return [_row(df.iloc[i]) for i in ranked]

# ===============================
# SECTION DETAIL
# ===============================
def get_section_by_id(section_id: str):
    row = df[df["section_id"].astype(str) == section_id]
    if row.empty:
        return None
    return _row(row.iloc[0])

# ===============================
# AUTOCOMPLETE
# ===============================
def autocomplete_ipc(query: str, limit: int = 5):
    q = query.lower().strip()
    if len(q) < 2:
        return []

    matches = df[
        df["section_id"].astype(str).str.startswith(q) |
        df["section_title"].str.lower().str.contains(q)
    ].head(limit)

    return [
        {"section": str(r["section_id"]), "title": r["section_title"]}
        for _, r in matches.iterrows()
    ]
