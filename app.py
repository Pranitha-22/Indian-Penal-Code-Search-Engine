from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from utils import search_ipc, get_section_by_id, autocomplete_ipc

app = FastAPI(title="IPC Search Engine")
app.mount("/static", StaticFiles(directory="../static"), name="static")


class SearchRequest(BaseModel):
    query: str
    top_k: int = 6


# ===============================
# HOME
# ===============================
@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>IPC Search</title>
  <link rel="stylesheet" href="/static/index.css">
</head>
<body>

<header class="top-bar">
  <div>About</div>
  <div>Legal</div>
</header>

<div id="app" class="home">
  <main id="main">

    <div class="hero">
      <h1 class="hero-title">
        Indian Penal Code
      </h1>

      <p class="hero-sub">
        Digital search interface for IPC sections, punishments and chapters.
      </p>
    </div>

    <div class="search-box">
      <input id="query"
        placeholder="Search IPC sections, offenses, punishments..."
        autocomplete="off">
      <button onclick="search()">🔍</button>
      <div id="suggestions" class="suggestions"></div>
    </div>

    <div class="popular">
      <h4>POPULAR CATEGORIES</h4>
      <div class="categories">
        <button onclick="query.value='Murder'; search()">Murder</button>
        <button onclick="query.value='Theft'; search()">Theft</button>
        <button onclick="query.value='Fraud'; search()">Fraud</button>
        <button onclick="query.value='Assault'; search()">Assault</button>
        <button onclick="query.value='Kidnapping'; search()">Kidnapping</button>
        <button onclick="query.value='Defamation'; search()">Defamation</button>
      </div>
    </div>

    <div id="results"></div>

  </main>
</div>

<script src="/static/app.js"></script>
</body>
</html>
"""


# ===============================
# SNIPPET FOR SEARCH ONLY
# ===============================
def make_snippet(text, query, window=150):
    text_lower = text.lower()
    query_lower = query.lower()

    idx = text_lower.find(query_lower)
    if idx == -1:
        return text[:300] + "..."

    start = max(0, idx - window)
    end = min(len(text), idx + window)

    return "..." + text[start:end] + "..."


# ===============================
# SEARCH API
# ===============================
@app.post("/search")
def search(req: SearchRequest):
    results = search_ipc(req.query, req.top_k)

    return JSONResponse([
        {
            "section": r["section"],
            "title": r["title"],
            "chapter": r["chapter"],
            # use full law_text only for snippet
            "description": make_snippet(r["law_text"], req.query)
        }
        for r in results
    ])


# ===============================
# AUTOCOMPLETE
# ===============================
@app.get("/autocomplete")
def autocomplete(q: str):
    return autocomplete_ipc(q)


# ===============================
# SECTION PAGE (STRUCTURED ONLY)
# ===============================
@app.get("/section/{section_id}", response_class=HTMLResponse)
def section(section_id: str):
    d = get_section_by_id(section_id)
    if not d:
        return "<h2 style='padding:40px'>Section not found</h2>"

    # structured fields only
    main_text = (d.get("main_text") or "").replace("\n", "<br><br>")
    explanation = (d.get("explanation") or "").replace("\n", "<br><br>")
    illustration = (d.get("illustration") or "").replace("\n", "<br><br>")
    punishment = (d.get("punishment_text") or "").replace("\n", "<br><br>")

    explanation_block = ""
    if explanation:
        explanation_block = f"""
        <section style="margin-top:32px">
          <h2>Explanation</h2>
          <div style="background:#f8f9fa;border-left:4px solid #1a73e8;padding:16px;line-height:1.7">
            {explanation}
          </div>
        </section>
        """

    illustration_block = ""
    if illustration:
        illustration_block = f"""
        <section style="margin-top:32px">
          <h2>Illustrations</h2>
          <div style="background:#f1f8f4;border-left:4px solid #138808;padding:16px;line-height:1.7">
            {illustration}
          </div>
        </section>
        """

    punishment_block = ""
    if punishment:
        punishment_block = f"""
        <section style="margin-top:32px">
          <h2>Punishment</h2>
          <div style="background:#fdf3f3;border-left:4px solid #d93025;padding:16px;line-height:1.7;font-weight:500">
            {punishment}
          </div>
        </section>
        """

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>IPC Section {d['section']}</title>
  <link rel="stylesheet" href="/static/index.css">
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif&display=swap" rel="stylesheet">
</head>

<body>

<header class="top-bar">
  <div><a class="back" href="javascript:history.back()">← Back</a></div>
  <div>Legal</div>
</header>

<main class="detail serif">

  <h1>Section {d['section']} — {d['title']}</h1>
  <h3 style="color:#5f6368;margin-top:4px">{d['chapter']}</h3>

  <section style="margin-top:32px">
    <div class="law-text">
      {main_text}
    </div>
  </section>

  {explanation_block}
  {illustration_block}
  {punishment_block}

</main>

</body>
</html>
"""
