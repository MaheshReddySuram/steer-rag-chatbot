const policies = [
  {
    title: "Refund Policy",
    source: "refund_policy.md#chunk-1",
    text:
      "Customers may request a refund within 30 days of purchase when the product or service was not used beyond the trial limit. Refund requests must include the order ID, customer email, purchase date, and reason for the request.",
  },
  {
    title: "Refund Policy",
    source: "refund_policy.md#chunk-2",
    text:
      "Refunds should be approved when the customer was charged incorrectly, cancelled within the eligible window, or experienced a duplicate payment. Refunds should be denied when the request is outside the eligibility period or the account shows heavy usage after purchase.",
  },
  {
    title: "Refund Policy",
    source: "refund_policy.md#chunk-3",
    text:
      "All refund decisions must be documented in the support case notes. If the refund amount is greater than 500 dollars, the case should be reviewed by a support lead before approval.",
  },
  {
    title: "Support Escalation Policy",
    source: "escalation_policy.md#chunk-1",
    text:
      "A customer support case should be escalated when the issue involves security risk, legal concern, repeated failed resolution, billing impact above 500 dollars, or a high-priority customer account.",
  },
  {
    title: "Support Escalation Policy",
    source: "escalation_policy.md#chunk-2",
    text:
      "Before escalating a case, the support analyst should summarize the customer issue, include troubleshooting steps already completed, attach relevant screenshots or logs, and identify the requested outcome.",
  },
  {
    title: "Account Change Policy",
    source: "account_change_policy.md#chunk-1",
    text:
      "Account changes include email updates, ownership transfers, billing contact updates, and permission changes. Analysts must verify the requestor identity before making any account change.",
  },
  {
    title: "Account Change Policy",
    source: "account_change_policy.md#chunk-2",
    text:
      "For standard changes, verification can include a signed-in request, matching account email, and recent billing confirmation. For ownership transfers or administrator permission changes, the analyst must collect written approval from the current account owner.",
  },
  {
    title: "Privacy Request Policy",
    source: "privacy_policy.md#chunk-1",
    text:
      "Customers may request access, correction, export, or deletion of their personal data. Privacy requests must be logged with request type, customer identifier, received date, and due date.",
  },
  {
    title: "Privacy Request Policy",
    source: "privacy_policy.md#chunk-2",
    text:
      "The support team should verify identity before processing a privacy request. Deletion requests must be reviewed for legal retention requirements before any data is removed.",
  },
];

const stopWords = new Set([
  "a",
  "an",
  "and",
  "are",
  "be",
  "being",
  "for",
  "from",
  "how",
  "i",
  "in",
  "is",
  "it",
  "of",
  "on",
  "or",
  "the",
  "to",
  "what",
  "when",
  "with",
]);

const messages = document.querySelector("#messages");
const form = document.querySelector("#chat-form");
const input = document.querySelector("#question");

function tokenize(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .split(/\s+/)
    .filter((word) => word.length > 2 && !stopWords.has(word));
}

function scorePolicy(question, policy) {
  const queryTokens = tokenize(question);
  const documentTokens = new Set(tokenize(`${policy.title} ${policy.text}`));
  const matches = queryTokens.filter((token) => documentTokens.has(token));
  const titleBoost = queryTokens.some((token) => policy.title.toLowerCase().includes(token)) ? 1.5 : 0;
  return matches.length + titleBoost;
}

function retrieve(question, topK = 3) {
  return policies
    .map((policy) => ({ ...policy, score: scorePolicy(question, policy) }))
    .filter((policy) => policy.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, topK);
}

function nextStep(title) {
  const steps = {
    "Refund Policy":
      "Confirm the order ID, customer email, purchase date, refund reason, and whether the refund is within the eligible window. If the amount is above 500 dollars, route it to a support lead.",
    "Support Escalation Policy":
      "Summarize the customer issue, include completed troubleshooting steps, attach relevant evidence, and route the case to the correct owner.",
    "Account Change Policy":
      "Verify the requestor identity before making the change. For ownership or administrator changes, collect written approval from the current account owner.",
    "Privacy Request Policy":
      "Verify identity, log the request type and due date, and check legal retention requirements before completing the request.",
  };
  return steps[title] || "Review the cited policy passage and route the case to the correct support owner.";
}

function followUps(title) {
  const questions = {
    "Refund Policy": [
      "What details are required to validate a refund request?",
      "When should a refund case be escalated?",
      "What makes a refund request ineligible?",
    ],
    "Support Escalation Policy": [
      "Which team should own this escalated case?",
      "What details should be included before escalation?",
      "When is a case considered high priority?",
    ],
    "Account Change Policy": [
      "What identity checks are needed for account changes?",
      "When is written owner approval required?",
      "What should happen if an account change looks suspicious?",
    ],
    "Privacy Request Policy": [
      "What types of privacy requests can customers make?",
      "What needs to be logged for a privacy request?",
      "When should a privacy request be escalated?",
    ],
  };
  return (
    questions[title] || [
      "What policy should I check first?",
      "When should this case be escalated?",
      "What information should I collect from the customer?",
    ]
  );
}

function answerQuestion(question) {
  const results = retrieve(question);
  if (results.length === 0) {
    return {
      answer:
        "I could not find a strong match in the available policy documents. Try asking about refunds, escalation, account changes, or privacy requests.",
      nextStep: "Rephrase the question with the policy area or customer issue you want to check.",
      followUps: followUps(""),
      sources: [],
    };
  }

  const top = results[0];
  return {
    answer: top.text,
    nextStep: nextStep(top.title),
    followUps: followUps(top.title),
    sources: results,
  };
}

function appendUserMessage(text) {
  const article = document.createElement("article");
  article.className = "message user";
  article.textContent = text;
  messages.appendChild(article);
}

function appendAssistantMessage(response) {
  const article = document.createElement("article");
  article.className = "message assistant";
  article.innerHTML = `
    <span class="label">Steer answer</span>
    <h2>Answer</h2>
    <p>${escapeHtml(response.answer)}</p>
    <h2>Recommended next step</h2>
    <p>${escapeHtml(response.nextStep)}</p>
    <h2>Suggested follow-up questions</h2>
    <ul>${response.followUps.map((question) => `<li>${escapeHtml(question)}</li>`).join("")}</ul>
    ${renderSources(response.sources)}
  `;
  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;
}

function renderSources(sources) {
  if (sources.length === 0) {
    return "";
  }

  return `
    <div class="sources">
      <h2>Sources</h2>
      ${sources
        .map(
          (source) => `
            <details>
              <summary>${escapeHtml(source.title)} - ${escapeHtml(source.source)}</summary>
              <p>${escapeHtml(source.text)}<span class="score">Retrieval score: ${source.score.toFixed(1)}</span></p>
            </details>
          `
        )
        .join("")}
    </div>
  `;
}

function escapeHtml(value) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function submitQuestion(question) {
  const cleanQuestion = question.trim();
  if (!cleanQuestion) {
    return;
  }

  appendUserMessage(cleanQuestion);
  appendAssistantMessage(answerQuestion(cleanQuestion));
  input.value = "";
  input.focus();
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  submitQuestion(input.value);
});

document.querySelectorAll("[data-question]").forEach((button) => {
  button.addEventListener("click", () => submitQuestion(button.dataset.question));
});

appendAssistantMessage({
  answer: "Ask me about refunds, support escalation, account changes, or privacy requests.",
  nextStep: "Choose an example question or type your own policy question.",
  followUps: [
    "What is the refund policy?",
    "When should a support case be escalated?",
    "How do account ownership changes work?",
  ],
  sources: [],
});
