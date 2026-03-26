const input = document.getElementById("query");
const results = document.getElementById("results");
const suggestions = document.getElementById("suggestions");

const DEFAULT_EXAMPLES = [
  "section 420",
  "what is murder",
  "punishment for robbery",
  "bailable vs non-bailable",
];

const FRIENDLY_CONCEPT_GUIDES = {
  kidnapping: {
    definition:
      "Under IPC, kidnapping has two forms: kidnapping from India and kidnapping from lawful guardianship.",
    simple:
      "In simple terms, it usually means taking a person in a way the law forbids, especially taking a minor or protected person away without lawful consent.",
    example:
      "Example: taking a child away from a lawful guardian without permission can amount to kidnapping.",
  },
  theft: {
    definition:
      "Under IPC, theft means dishonestly taking movable property out of another person's possession without that person's consent.",
    simple:
      "In simple terms, it is taking someone else's movable property without permission and with a dishonest intention.",
    example:
      "Example: secretly taking another person's phone or wallet without consent can amount to theft.",
  },
  robbery: {
    definition:
      "Under IPC, robbery is an aggravated form of theft or extortion involving violence, fear of instant harm, or immediate threat.",
    simple:
      "In simple terms, it is not just stealing. It is stealing or extorting property by using force or threatening immediate harm.",
    example:
      "Example: snatching money while threatening a person with a weapon can amount to robbery.",
  },
  assault: {
    definition:
      "Under IPC, assault means a gesture or preparation that makes another person apprehend that criminal force is about to be used.",
    simple:
      "In simple terms, assault can happen even before actual physical contact, if the conduct makes the other person fear immediate force.",
    example:
      "Example: raising a weapon in a threatening way so that another person fears immediate attack can amount to assault.",
  },
  cheating: {
    definition:
      "Under IPC, cheating means deceiving a person and thereby dishonestly or fraudulently inducing that person to deliver property, consent to something, or act in a way that causes harm.",
    simple:
      "In simple terms, it is using deception to make someone part with money, property, or legal rights.",
    example:
      "Example: lying to someone to get their money by making a false promise can amount to cheating.",
  },
  defamation: {
    definition:
      "Under IPC, defamation means making or publishing an imputation about a person with the intention, knowledge, or reason to believe that it will harm that person's reputation.",
    simple:
      "In simple terms, it is harming another person's reputation by making damaging statements in a way the law recognizes as wrongful.",
    example:
      "Example: publishing a false accusation that lowers a person's reputation can amount to defamation.",
  },
  murder: {
    definition:
      "Under IPC, murder is culpable homicide that falls within Section 300 and is not covered by any of the statutory exceptions.",
    simple:
      "In simple terms, it is a form of unlawful killing where the law treats the intention or knowledge as serious enough to classify it as murder.",
    example:
      "Example: intentionally causing a fatal injury in circumstances covered by Section 300 can amount to murder.",
  },
  "culpable homicide": {
    definition:
      "Under IPC, culpable homicide means causing death by doing an act with the intention of causing death, the intention of causing such bodily injury as is likely to cause death, or the knowledge that the act is likely to cause death.",
    simple:
      "In simple terms, it is unlawful killing where the act is done with a legally significant intention or knowledge about the risk of death.",
    example:
      "Example: causing a fatal injury knowing that death is likely can amount to culpable homicide.",
  },
  extortion: {
    definition:
      "Under IPC, extortion means intentionally putting a person in fear of injury and thereby dishonestly inducing that person to deliver property or valuable security.",
    simple:
      "In simple terms, it is getting money, property, or valuable security from someone by threatening harm.",
    example:
      "Example: threatening to injure someone unless they hand over money can amount to extortion.",
  },
  dacoity: {
    definition:
      "Under IPC, dacoity is robbery committed by five or more persons acting together.",
    simple:
      "In simple terms, it is gang robbery involving at least five people.",
    example:
      "Example: a group of five or more persons jointly committing robbery can amount to dacoity.",
  },
  rape: {
    definition:
      "Under IPC, rape is defined by Section 375 and depends on the legally specified acts and the absence of legally valid consent or other circumstances listed in the section.",
    simple:
      "In simple terms, it involves sexual acts that the law treats as rape because valid consent is absent or the situation falls within Section 375.",
    example:
      "Example: sexual intercourse without legally valid consent can amount to rape under Section 375.",
  },
  "criminal intimidation": {
    definition:
      "Under IPC, criminal intimidation means threatening a person with injury to body, reputation, or property, with intent to cause alarm or to compel that person to do or omit an act.",
    simple:
      "In simple terms, it is using threats to frighten someone or force them to act in a particular way.",
    example:
      "Example: threatening to harm someone unless they obey a demand can amount to criminal intimidation.",
  },
};

function cleanDisplayText(value) {
  let text = String(value ?? "")
    .replace(/\s+/g, " ")
    .trim();

  text = text.replace(/\b\d+\[/g, "");
  text = text.replace(/]/g, "");
  text = text.replace(/\b\d+\s*\*\s*(?:\*\s*)+/g, "");

  const replacements = [
    [/\bpu\s+nishment\b/gi, "punishment"],
    [/\bimpriso\s+nment\b/gi, "imprisonment"],
    [/\bkidna\s+pping\b/gi, "kidnapping"],
    [/\bcommi\s+tting\b/gi, "committing"],
    [/\bserva\s+nt\b/gi, "servant"],
    [/\bha\s+rm\b/gi, "harm"],
    [/\bdivi\s+ne\b/gi, "divine"],
    [/\bprecau\s+tion\b/gi, "precaution"],
    [/\bcommuni\s+cation\b/gi, "communication"],
    [/\bintimida\s+tion\b/gi, "intimidation"],
    [/\bstateme\s+nts\b/gi, "statements"],
    [/\bag\s+ainst\b/gi, "against"],
    [/\bmen\s+tioned\b/gi, "mentioned"],
    [/\bpriso\s+ner\b/gi, "prisoner"],
    [/\bsuff\s+ering\b/gi, "suffering"],
    [/\bitis\b/gi, "it is"],
    [/\btheo\s+ffence\b/gi, "the offence"],
    [/\btakinga\b/gi, "taking a"],
    [/\binfluencea\b/gi, "influence a"],
    [/\bwitha\b/gi, "with a"],
    [/\bservantof\b/gi, "servant of"],
    [/\bservantwith\b/gi, "servant with"],
    [/\bservantby\b/gi, "servant by"],
    [/\bnon\s+-attendance\b/gi, "non-attendance"],
  ];

  replacements.forEach(([pattern, replacement]) => {
    text = text.replace(pattern, replacement);
  });

  return text;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function renderPrimarySectionNote(sectionId) {
  if (!sectionId) {
    return "";
  }
  const safeSectionId = escapeHtml(sectionId);
  const href = `/section/${encodeURIComponent(String(sectionId))}`;
  return `
    <div class="source-note">
      <strong>Primary Section:</strong>
      <a class="source-note-link" href="${href}" onclick="event.stopPropagation()">
        Section ${safeSectionId} IPC
      </a>
    </div>
  `;
}

function renderLoading() {
  results.innerHTML = `
    <div class="loading-card">
      <div class="spinner"></div>
      <div>
        <h3>Searching IPC</h3>
        <p>Checking sections, punishments, offence meanings, chapters, and broader IPC concepts.</p>
      </div>
    </div>
  `;
}

function renderError() {
  results.innerHTML = `
    <div class="error-card">
      <h3>Search failed</h3>
      <p>The UI is not getting a valid response from the backend. Reload the server and try again.</p>
    </div>
  `;
}

function renderEmpty(message) {
  const examples = DEFAULT_EXAMPLES
    .map((item) => `<button class="try-chip" type="button" onclick="loadSuggestion('${escapeHtml(item)}')">${escapeHtml(item)}</button>`)
    .join("");

  results.innerHTML = `
    <div class="empty-card">
      <h3>No clear IPC match</h3>
      <p>${escapeHtml(message)}</p>
      <div class="try-chip-row">${examples}</div>
    </div>
  `;
}

async function safeFetch(url, options = {}) {
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(error);
    return { error: true };
  }
}

function normalizeLines(answer) {
  return String(answer || "")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
}

function isChapterLine(line) {
  return /^chapter\b/i.test(line);
}

function isMetaLine(line) {
  return (
    /^section\s+[0-9]/i.test(line) ||
    isChapterLine(line) ||
    /^matched concept:/i.test(line) ||
    /^(relevant ipc answer|punishment answer|definition answer|section answer|chapter answer):/i.test(line)
  );
}

function parseAnswer(answer) {
  const lines = normalizeLines(answer);
  const summaryLines = [];
  const relatedLines = [];
  let inRelated = false;

  for (const line of lines) {
    if (/^related sections:/i.test(line)) {
      inRelated = true;
      continue;
    }

    if (inRelated) {
      if (/^-\s*section\s+/i.test(line)) {
        relatedLines.push(line.replace(/^-+\s*/, ""));
      }
      continue;
    }

    if (!isMetaLine(line)) {
      summaryLines.push(line);
    }
  }

  return {
    summary: summaryLines.join(" "),
    related: relatedLines,
  };
}

function buildConceptExplainer(context, primary) {
  const sectionRef = primary && primary.section ? `Section ${primary.section}` : "the relevant section";
  const sourceTitle = String(context.generalTitle || context.query || "").toLowerCase();

  if (/punishment/.test(sourceTitle)) {
    return {
      label: "Visual Explainer",
      title: "How Punishment Works",
      steps: [
        "Identify the offence section",
        "Read the punishment type or term",
        "Check whether fine, life term, or death is allowed",
        "Apply the punishment rule to the offence",
      ],
      scenario: `After identifying the offence, read ${sectionRef} or the linked punishment section to see the kind of punishment the law allows.`,
    };
  }

  if (/bailable|bail/.test(sourceTitle)) {
    return {
      label: "Visual Explainer",
      title: "How Bail Classification Works",
      steps: [
        "Identify the offence or section",
        "Check the procedural classification",
        "Confirm whether bail is a right or court-controlled",
        "Apply that classification to the offence",
      ],
      scenario: `Start with the offence section, then check whether the law treats it as bailable or non-bailable before giving a bail answer.`,
    };
  }

  if (/cognizable/.test(sourceTitle)) {
    return {
      label: "Visual Explainer",
      title: "How Cognizable Classification Works",
      steps: [
        "Identify the offence or section",
        "Check the procedural classification",
        "See whether police powers depend on prior court permission",
        "Apply that classification to the offence",
      ],
      scenario: `Start with the offence section, then check whether the law treats it as cognizable or non-cognizable before answering the query.`,
    };
  }

  return {
    label: "Visual Explainer",
    title: `How ${titleCaseTitle(context.generalTitle || primary?.title || "This Topic")} Works`,
    steps: [
      "Identify the legal concept",
      "Read the governing section or rule",
      "Check how the concept applies in practice",
      "Link it back to the relevant IPC sections",
    ],
    scenario: `Read the governing IPC section first, then compare the concept with the user's question before giving the answer.`,
  };
}

function isDefinitionLikeSection(primary) {
  const title = cleanDisplayText(primary && primary.title).toLowerCase();
  if (/^punishment for/.test(title)) {
    return false;
  }

  const body = cleanDisplayText(primary && primary.law_text).toLowerCase();
  return /\bis of two kinds\b|\bis said to\b|\bmeans\b|\bdenotes\b|\bincludes\b/i.test(body);
}

function genericExplainer(primary, context = {}) {
  const title = String(primary.title || "").replace(/\.$/, "").trim();
  const lowerTitle = title.toLowerCase();
  const queryType = context.queryType || "general";
  const answerMode = context.answerMode || "section";

  if (answerMode === "general") {
    return buildConceptExplainer(context, primary);
  }

  if (queryType === "section_lookup") {
    return {
      label: "Visual Explainer",
      title: `How to Read Section ${primary.section}`,
      steps: [
        "Read the section title and scope",
        "Identify the conduct the section covers",
        "Check the required intent, effect, or exception",
        "Apply the section to the facts",
      ],
      scenario: `Read Section ${primary.section} carefully, then compare the conduct, intent, effect, and any listed exceptions before deciding whether it applies.`,
    };
  }

  if (queryType === "punishment" || lowerTitle.startsWith("punishment for")) {
    return {
      label: "Visual Explainer",
      title: `How ${title || `Section ${primary.section}`} Works`,
      steps: [
        "Identify the offence",
        "Confirm the section applies",
        "Read the punishment rule",
        "Apply the sentence range",
      ],
      scenario: `First confirm the offence section applies, then read how Section ${primary.section} states the punishment.`,
    };
  }

  return {
    label: "Visual Explainer",
    title: `How ${title || `Section ${primary.section}`} Works`,
    steps: [
      "Identify the act or conduct",
      "Check intent or knowledge",
      "Match facts to the legal ingredients",
      "Apply the section",
    ],
    scenario: `Compare the facts with the legal ingredients in Section ${primary.section} before deciding whether it applies.`,
  };
}

function datasetExplainer(primary, context = {}) {
  const rawSteps = String(primary.explainer_steps || "")
    .split("|")
    .map((item) => item.trim())
    .filter(Boolean);
  const rawScenario = String(primary.example_scenario || "").trim();

  if (!rawSteps.length && !rawScenario) {
    return null;
  }

  const fallback = genericExplainer(primary, context);
  return {
    label: "Visual Explainer",
    title: `How ${titleCaseTitle(primary.title)} Works`,
    steps: rawSteps.length ? rawSteps : fallback.steps,
    scenario: rawScenario,
  };
}

function titleCaseTitle(title) {
  const clean = String(title || "").replace(/\.$/, "").trim();
  return clean || "This Section";
}

function detectClientQuestionType(data) {
  const q = String((data && data.query) || "").toLowerCase().trim();
  if (/^\d+[a-z-]*$/i.test(q) || /\b(section|sec)\s+\d+[a-z-]*\b/i.test(q)) {
    return "section_lookup";
  }
  if (data && data.query_type) {
    return data.query_type;
  }
  if (/\b(bailable|non bailable|non-bailable|bail)\b/.test(q)) {
    return "bail_status";
  }
  if (/\b(cognizable|non cognizable|non-cognizable)\b/.test(q)) {
    return "cognizable_status";
  }
  if (/\b(triable|which court|what court|court of trial|tried by)\b/.test(q)) {
    return "triable_by";
  }
  if (/\b(punishment|sentence|penalty|how many years|maximum punishment|max punishment|term of punishment)\b/.test(q)) {
    return "punishment";
  }
  if (/\b(what is|define|definition|meaning of|explain|what does)\b/.test(q)) {
    return "definition";
  }
  return "general";
}

function stripTrailingPeriod(text) {
  return String(text || "").replace(/\.$/, "").trim();
}

function sectionSubject(primary) {
  const base = stripTrailingPeriod(primary.title).replace(/^punishment for\s+/i, "");
  return base || `section ${primary.section}`;
}

function capitalizeSentence(text) {
  const clean = String(text || "").trim();
  if (!clean) {
    return "";
  }
  return clean.charAt(0).toUpperCase() + clean.slice(1);
}

function buildAnswerHeading(data, primary, queryType) {
  const subject = sectionSubject(primary);

  if (queryType === "bail_status") {
    return `Is ${subject.toLowerCase()} bailable?`;
  }
  if (queryType === "cognizable_status") {
    return `Is ${subject.toLowerCase()} cognizable?`;
  }
  if (queryType === "triable_by") {
    return `Which court tries ${subject.toLowerCase()}?`;
  }
  if (queryType === "punishment") {
    return `Punishment for ${subject.toLowerCase()}`;
  }
  if (queryType === "definition") {
    return `What is ${subject.toLowerCase()}?`;
  }

  return stripTrailingPeriod(primary.title);
}

function buildHumanAnswer(data, primary, parsed, queryType) {
  const subject = sectionSubject(primary);
  const plain = cleanDisplayText(primary.plain_english || "");
  const punishment = cleanDisplayText(primary.punishment_summary || "");
  const parsedSummary = cleanDisplayText(parsed.summary || "");
  const concept = String((data && data.concept) || "").toLowerCase().trim();
  const guide = FRIENDLY_CONCEPT_GUIDES[concept];

  if (queryType === "bail_status" && primary.bailable_status) {
    const lines = [`${capitalizeSentence(subject)} is ${primary.bailable_status.toLowerCase()}.`];
    if (primary.cognizable_status) {
      lines.push(`It is ${primary.cognizable_status.toLowerCase()}.`);
    }
    if (primary.triable_by) {
      lines.push(`It is generally tried by ${primary.triable_by}.`);
    }
    return lines.join(" ");
  }

  if (queryType === "cognizable_status" && primary.cognizable_status) {
    const lines = [`${capitalizeSentence(subject)} is ${primary.cognizable_status.toLowerCase()}.`];
    if (primary.bailable_status) {
      lines.push(`It is ${primary.bailable_status.toLowerCase()}.`);
    }
    return lines.join(" ");
  }

  if (queryType === "triable_by" && primary.triable_by) {
    return `${capitalizeSentence(subject)} is generally tried by ${primary.triable_by}.`;
  }

  if (queryType === "punishment") {
    if (punishment) {
      return `Under IPC, ${subject.toLowerCase()} is punishable with ${punishment.charAt(0).toLowerCase()}${punishment.slice(1)}`;
    }
    if (parsedSummary) {
      return parsedSummary;
    }
  }

  if ((queryType === "definition" || queryType === "general") && guide) {
    return [guide.definition, guide.simple, guide.example].filter(Boolean).join(" ");
  }

  if ((queryType === "definition" || queryType === "general") && plain) {
    if (/is of two kinds:/i.test(cleanDisplayText(primary.law_text || ""))) {
      const kindsText = cleanDisplayText(primary.law_text || "")
        .replace(/^.*?is of two kinds:\s*/i, "")
        .replace(/\.$/, "");
      return `Under IPC, ${subject.toLowerCase()} has two forms: ${kindsText}.`;
    }
    return plain;
  }

  return plain || parsedSummary || primary.snippet || "Relevant IPC text found.";
}

function renderMetadataFacts(primary, queryType) {
  const facts = [];

  const showStatusPills = ["bail_status", "cognizable_status", "triable_by", "punishment", "section_lookup"].includes(queryType);

  if (showStatusPills && primary.bailable_status) {
    facts.push(`<span class="meta-pill">${escapeHtml(primary.bailable_status)}</span>`);
  }
  if (showStatusPills && primary.cognizable_status) {
    facts.push(`<span class="meta-pill">${escapeHtml(primary.cognizable_status)}</span>`);
  }
  if (showStatusPills && primary.triable_by) {
    facts.push(`<span class="meta-pill">${escapeHtml(primary.triable_by)}</span>`);
  }

  const detailRows = [];

  if (queryType === "punishment" && primary.punishment_max_term) {
    detailRows.push(`
      <div class="meta-detail-row">
        <span class="meta-detail-label">Maximum term</span>
        <span class="meta-detail-value">${escapeHtml(primary.punishment_max_term)}</span>
      </div>
    `);
  }

  if (queryType === "bail_status" && primary.punishment_summary) {
    detailRows.push(`
      <div class="meta-detail-row">
        <span class="meta-detail-label">Punishment</span>
        <span class="meta-detail-value">${escapeHtml(primary.punishment_summary)}</span>
      </div>
    `);
  }

  if ((queryType === "definition" || queryType === "general") && primary.linked_punishment_section && primary.linked_punishment_section !== primary.section) {
    detailRows.push(`
      <div class="meta-detail-row">
        <span class="meta-detail-label">Punishment section</span>
        <span class="meta-detail-value">Section ${escapeHtml(primary.linked_punishment_section)} IPC</span>
      </div>
    `);
  }

  if (!facts.length && !detailRows.length) {
    return "";
  }

  return `
    <div class="meta-panel">
      ${facts.length ? `<div class="meta-pill-row">${facts.join("")}</div>` : ""}
      ${detailRows.length ? `<div class="meta-detail-list">${detailRows.join("")}</div>` : ""}
    </div>
  `;
}

function renderPrimaryFullText(primary, queryType) {
  if (!primary || queryType !== "section_lookup") {
    return "";
  }

  const fullText = cleanDisplayText(primary.law_text || "");
  if (!fullText) {
    return "";
  }

  const blocks = fullText
    .split(/(?=Illustrations?:|Explanation|Exception)/i)
    .map((item) => item.trim())
    .filter(Boolean)
    .map((item) => `<p>${escapeHtml(item)}</p>`)
    .join("");

  return `<div class="answer-body section-full-text">${blocks}</div>`;
}

function renderPrimaryAnswer(data) {
  const sections = Array.isArray(data.sections) ? data.sections : [];
  const primary = sections[0];
  const parsed = parseAnswer(data.answer || "");
  const queryType = detectClientQuestionType(data);
  const heading = buildAnswerHeading(data, primary, queryType);
  const body = buildHumanAnswer(data, primary, parsed, queryType);
  const chapterChip = primary.chapter
    ? `<div class="chip-row"><span class="chip">${escapeHtml(cleanDisplayText(primary.chapter))}</span></div>`
    : "";
  const primarySection = renderPrimarySectionNote(primary && primary.section);
  const metadata = renderMetadataFacts(primary, queryType);
  const fullText = renderPrimaryFullText(primary, queryType);
  const lead = queryType === "section_lookup" && fullText
    ? ""
    : `<div class="answer-body answer-lead">${escapeHtml(cleanDisplayText(body))}</div>`;

  return `
    <section class="answer-panel">
      <div class="answer-header">
        <span class="eyebrow">LEGAL RESPONSE</span>
        <h2>${escapeHtml(cleanDisplayText(heading))}</h2>
      </div>
      ${chapterChip}
      ${primarySection}
      ${lead}
      ${metadata}
      ${fullText}
    </section>
  `;
}

function renderGeneralAnswer(data) {
  const title = data.general_title || "General IPC Answer";
  const answer = data.answer || "";
  const sections = Array.isArray(data.sections) ? data.sections : [];
  const showExplainer = data.show_explainer === true;
  const primary = sections[0] || null;

  let html = `
    <section class="answer-panel">
      <div class="answer-header">
        <h2>${escapeHtml(cleanDisplayText(title))}</h2>
      </div>
      ${renderPrimarySectionNote(primary && primary.section)}
      <div class="answer-body">${escapeHtml(cleanDisplayText(answer))}</div>
    </section>
  `;

  if (sections.length) {
    if (showExplainer) {
      html += renderExplainer(primary, {
        queryType: "general",
        answerMode: "general",
        generalTitle: title,
        query: data.query || "",
      });
    }
    if (sections.length > 1) {
      html += renderSourceCards(sections, data);
    }
  }

  results.innerHTML = html;
}

function renderComparisonAnswer(data) {
  const title = data.general_title || "IPC Comparison";
  const answer = data.answer || "";
  const entries = Array.isArray(data.comparison) ? data.comparison : [];

  const cards = entries
    .map(
      (item) => `
        <article class="comparison-card">
          <div class="comparison-top">
            <span class="chip">Section ${escapeHtml(item.section)} IPC</span>
            ${item.chapter ? `<span class="chip chip-muted">${escapeHtml(item.chapter)}</span>` : ""}
          </div>
          <h4>${escapeHtml(cleanDisplayText(item.title))}</h4>
          <p>${escapeHtml(cleanDisplayText(item.plain_english || ""))}</p>
          <div class="comparison-facts">
            ${item.punishment_summary ? `<div><strong>Punishment:</strong> ${escapeHtml(cleanDisplayText(item.punishment_summary))}</div>` : ""}
            ${item.bailable_status ? `<div><strong>Bail:</strong> ${escapeHtml(cleanDisplayText(item.bailable_status))}</div>` : ""}
            ${item.cognizable_status ? `<div><strong>Cognizable:</strong> ${escapeHtml(cleanDisplayText(item.cognizable_status))}</div>` : ""}
            ${item.triable_by ? `<div><strong>Tried By:</strong> ${escapeHtml(cleanDisplayText(item.triable_by))}</div>` : ""}
          </div>
        </article>
      `
    )
    .join("");

  results.innerHTML = `
    <section class="answer-panel">
      <div class="answer-header">
        <span class="eyebrow">LEGAL RESPONSE</span>
        <h2>${escapeHtml(cleanDisplayText(title))}</h2>
      </div>
      <div class="answer-body">${escapeHtml(cleanDisplayText(answer))}</div>
    </section>
    <section class="sources-panel">
      <div class="sources-header">
        <span class="eyebrow">COMPARISON</span>
        <h3>Side-by-Side View</h3>
      </div>
      <div class="comparison-grid">${cards}</div>
    </section>
  `;
}

function normalizeScenarioText(text) {
  return cleanDisplayText(text).replace(/^example\s*:\s*/i, "").trim();
}

function shouldShowResultExplainer(primary, queryType, answerMode) {
  if (!primary) {
    return false;
  }

  const hasCustom = Boolean(
    String(primary.explainer_steps || "").trim() ||
    String(primary.example_scenario || "").trim()
  );
  const isPunishmentTitle = /^punishment for/i.test(String(primary.title || "").trim());

  if (answerMode === "general") {
    return false;
  }

  if (queryType === "punishment") {
    return true;
  }

  if (queryType === "section_lookup") {
    if (isDefinitionLikeSection(primary)) {
      return false;
    }
    return hasCustom || isPunishmentTitle;
  }

  return false;
}

function renderExplainer(primary, context = {}) {
  const explainer = datasetExplainer(primary, context) || genericExplainer(primary, context);
  const scenarioText = normalizeScenarioText(explainer.scenario || "");

  const steps = explainer.steps
    .map(
      (step, index) => `
        <div class="explainer-step">
          <span class="explainer-index">${index + 1}</span>
          <span class="explainer-text">${escapeHtml(cleanDisplayText(step))}</span>
        </div>
      `
    )
    .join(`<div class="explainer-arrow" aria-hidden="true">&rarr;</div>`);

  return `
    <section class="explainer-panel">
      <div class="sources-header">
        <span class="eyebrow">${escapeHtml(explainer.label)}</span>
        <h3>${escapeHtml(explainer.title)}</h3>
      </div>
      <div class="explainer-flow">${steps}</div>
      ${scenarioText ? `
      <div class="explainer-scenario">
        <strong>Example Scenario:</strong>
        <span>${escapeHtml(scenarioText)}</span>
      </div>
      ` : ""}
    </section>
  `;
}

function buildRelatedPreview(section, queryType) {
  if (queryType === "punishment" && section.punishment_summary) {
    return section.punishment_summary;
  }
  if (queryType === "section_lookup" && section.plain_english) {
    return section.plain_english;
  }
  if (section.plain_english) {
    return section.plain_english;
  }
  if (section.punishment_summary) {
    return section.punishment_summary;
  }
  return `Open Section ${section.section} to read the full statutory text.`;
}

function renderSourceCards(sections, data) {
  const relatedSections = sections.slice(1, 4);
  if (!relatedSections.length) {
    return "";
  }

  const queryType = detectClientQuestionType(data);

  const cards = relatedSections
    .map((section) => {
      const chapter = section.chapter
        ? `<div class="chip-row"><span class="chip">${escapeHtml(section.chapter)}</span></div>`
        : "";

      const preview = cleanDisplayText(buildRelatedPreview(section, queryType));

      return `
        <article class="result-card" onclick="openSection('${escapeHtml(section.section)}')">
          <div class="result-top">
            <span class="result-section">Section ${escapeHtml(section.section)}</span>
            <span class="result-action">Related section</span>
          </div>
          <h4>${escapeHtml(cleanDisplayText(section.title))}</h4>
          ${chapter}
          <p>${escapeHtml(preview)}</p>
        </article>
      `;
    })
    .join("");

  return `
    <section class="sources-panel">
      <div class="sources-header">
        <span class="eyebrow">RELATED</span>
        <h3>Other Relevant Sections</h3>
      </div>
      <div class="result-grid">${cards}</div>
    </section>
  `;
}

function renderResults(data) {
  if (!data || data.error) {
    renderError();
    return;
  }

  const sections = Array.isArray(data.sections) ? data.sections : [];
  const answer = data.answer || "";
  const answerMode = data.answer_mode || "section";
  const queryType = detectClientQuestionType(data);

  if (answerMode === "general") {
    renderGeneralAnswer(data);
    return;
  }

  if (answerMode === "comparison") {
    renderComparisonAnswer(data);
    return;
  }

  if (!sections.length && !answer) {
    renderEmpty("Try a section number like 420 or a query like punishment for theft.");
    return;
  }

  if (!sections.length) {
    renderEmpty(answer || "No reliable IPC answer was found.");
    return;
  }

  const showExplainer = shouldShowResultExplainer(sections[0], queryType, answerMode);
  const showRelated = ["definition", "general", "punishment", "section_lookup"].includes(queryType) && sections.length > 1;

  results.innerHTML =
    renderPrimaryAnswer(data) +
    (showExplainer ? renderExplainer(sections[0], {
      queryType,
      answerMode,
      query: data.query || "",
      generalTitle: data.general_title || "",
    }) : "") +
    (showRelated ? renderSourceCards(sections, data) : "");
}

window.openSection = function (sectionId) {
  window.location.href = `/section/${encodeURIComponent(sectionId)}`;
};

window.loadSuggestion = function (queryText) {
  input.value = queryText;
  askAI();
};

window.loadSection = function (sectionId) {
  input.value = `section ${sectionId}`;
  askAI();
};

window.askAI = async function () {
  const query = input.value.trim();
  if (!query) {
    renderEmpty("Type a section number or a legal question.");
    return;
  }

  suggestions.style.display = "none";
  renderLoading();

  const data = await safeFetch("/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  renderResults(data);
  window.history.pushState({}, "", `/?q=${encodeURIComponent(query)}`);
};

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    askAI();
  }
});

input.addEventListener("input", async () => {
  const query = input.value.trim();
  if (query.length < 2) {
    suggestions.style.display = "none";
    suggestions.innerHTML = "";
    return;
  }

  const data = await safeFetch(`/autocomplete?q=${encodeURIComponent(query)}`);
  if (!Array.isArray(data)) {
    suggestions.style.display = "none";
    return;
  }

  suggestions.innerHTML = data
    .map(
      (item) => `
        <button class="suggestion" type="button" onclick="loadSuggestion('${escapeHtml(item.query || `section ${item.section}`)}')">
          <span class="suggestion-section">${escapeHtml(item.kind === "guided" ? "Try asking" : `Section ${item.section}`)}</span>
          <span class="suggestion-title">${escapeHtml(item.title)}</span>
        </button>
      `
    )
    .join("");

  suggestions.style.display = data.length ? "block" : "none";
});

document.addEventListener("click", (event) => {
  if (!suggestions.contains(event.target) && event.target !== input) {
    suggestions.style.display = "none";
  }
});

window.addEventListener("DOMContentLoaded", () => {
  const params = new URLSearchParams(window.location.search);
  const query = params.get("q");
  if (query) {
    input.value = query;
    askAI();
  }
});
