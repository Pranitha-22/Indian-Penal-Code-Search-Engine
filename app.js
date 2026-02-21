const app = document.getElementById("app");
const input = document.getElementById("query");
const results = document.getElementById("results");
const suggestions = document.getElementById("suggestions");

let activeIndex = -1;
let debounceTimer = null;
let isLoading = false;

/* ================================
   SAFE FETCH WRAPPER
================================ */
async function safeFetch(url, options = {}) {
  try {
    const res = await fetch(url, options);
    if (!res.ok) throw new Error("Server error");
    return await res.json();
  } catch (err) {
    console.error(err);
    return { error: true };
  }
}

/* ================================
   LOADING STATE
================================ */
function setLoading(state) {
  isLoading = state;
  if (state) {
    results.innerHTML = `
      <div class="loading">
        <div class="spinner"></div>
        <p>Searching…</p>
      </div>
    `;
  }
}

/* ================================
   KEYBOARD HANDLING
================================ */
input?.addEventListener("keydown", e => {
  if (e.key === "Enter") {
    const items = suggestions.children;
    if (items.length && activeIndex >= 0) {
      items[activeIndex].click();
    } else {
      search();
    }
  }

  if (e.key === "ArrowDown") move(1);
  if (e.key === "ArrowUp") move(-1);
});

/* ================================
   INPUT DEBOUNCE
================================ */
input?.addEventListener("input", () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(fetchSuggestions, 250);
});

/* ================================
   AUTOCOMPLETE
================================ */
async function fetchSuggestions() {
  const q = input.value.trim();
  if (q.length < 2) {
    suggestions.style.display = "none";
    return;
  }

  const data = await safeFetch(`/autocomplete?q=${encodeURIComponent(q)}`);
  if (!data || data.error) return;

  suggestions.innerHTML = "";
  activeIndex = -1;

  if (!data.length) {
    suggestions.style.display = "none";
    return;
  }

  data.forEach(s => {
    const div = document.createElement("div");
    div.className = "suggestion";
    div.textContent = `Section ${s.section} — ${s.title}`;
    div.onclick = () => {
      suggestions.style.display = "none";
      openSection(s.section);
    };
    suggestions.appendChild(div);
  });

  suggestions.style.display = "block";
}

/* ================================
   NAVIGATION
================================ */
function move(d) {
  const items = suggestions.children;
  if (!items.length) return;

  activeIndex = (activeIndex + d + items.length) % items.length;
  [...items].forEach(i => i.classList.remove("active"));
  items[activeIndex].classList.add("active");
}

/* ================================
   SEARCH
================================ */
async function search() {
  if (isLoading) return;

  const q = input.value.trim();
  if (!q) return;

  suggestions.style.display = "none";
  setLoading(true);

  history.pushState({ q }, "", `/?q=${encodeURIComponent(q)}`);

  const data = await safeFetch("/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: q, top_k: 8 })
  });

  setLoading(false);
  results.innerHTML = "";

  if (!data || data.error) {
    results.innerHTML = "<p class='error'>Server unavailable. Try again.</p>";
    return;
  }

  if (!data.length) {
    results.innerHTML = "<p>No results found.</p>";
    return;
  }

  data.forEach(r => {
    const div = document.createElement("div");
    div.className = "result";

    div.innerHTML = `
      <div class="title">
        Section ${r.section} — ${r.title}
      </div>
      <div class="url">ipc.india.gov.in › section-${r.section}</div>
      <div class="snippet">${r.description}</div>
    `;

    div.querySelector(".title").onclick = () => openSection(r.section);
    results.appendChild(div);
  });
}

/* ================================
   SECTION
================================ */
function openSection(id) {
  window.location.href = `/section/${id}`;
}

/* ================================
   RESTORE STATE ON BACK
================================ */
window.addEventListener("popstate", event => {
  if (event.state?.q) {
    input.value = event.state.q;
    search();
  }
});
