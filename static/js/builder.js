/* QuizeTalk — Visual Quiz Studio behaviour */
(() => {
  "use strict";

  const form = document.getElementById("quiz-form");
  if (!form) return;

  const list = document.getElementById("questions-list");
  const template = document.getElementById("question-template");
  const emptyState = document.getElementById("builder-empty");
  const countEl = document.getElementById("question-count");
  const addBtn = document.getElementById("add-question");
  const messageEl = document.getElementById("form-message");
  const importPanel = document.getElementById("import-panel");
  const importJson = document.getElementById("import-json");
  let uid = 0;
  const MAX = 30;

  /* ---------- helpers ---------- */
  function showMessage(text, type = "error") {
    messageEl.textContent = text;
    messageEl.className = `form-message form-message--${type}`;
    messageEl.hidden = !text;
  }

  function cardValue(card, role) {
    return (card.querySelector(`[data-role="${role}"]`)?.value || "").trim();
  }

  function updateUI() {
    const cards = [...list.querySelectorAll(".question-card")];
    cards.forEach((card, index) => {
      card.querySelector(".question-card__index").textContent = `Q${index + 1}`;
    });
    countEl.textContent = String(cards.length);
    emptyState.hidden = cards.length > 0;
    addBtn.disabled = cards.length >= MAX;
    addBtn.textContent = cards.length >= MAX ? "Maximum 30 questions" : "＋ Add Question";
  }

  function addQuestion(focus = true) {
    if (list.querySelectorAll(".question-card").length >= MAX) return;
    const card = template.content.firstElementChild.cloneNode(true);
    uid += 1;
    // Radio buttons must be unique per question, otherwise all cards share one answer.
    card.querySelectorAll('[data-role="correct"]').forEach((radio) => {
      radio.name = `correct_q${uid}`;
    });
    list.appendChild(card);
    updateUI();
    if (focus) card.querySelector('[data-role="text"]').focus();
  }

  function collectQuestions() {
    return [...list.querySelectorAll(".question-card")].map((card) => ({
      text: cardValue(card, "text"),
      option_a: cardValue(card, "option-a"),
      option_b: cardValue(card, "option-b"),
      option_c: cardValue(card, "option-c"),
      option_d: cardValue(card, "option-d"),
      correct: card.querySelector('[data-role="correct"]:checked')?.value || "",
      explanation: cardValue(card, "explanation"),
    }));
  }

  function collectQuiz() {
    return {
      title: document.getElementById("quiz-title").value.trim(),
      category: document.getElementById("quiz-category").value,
      description: document.getElementById("quiz-description").value.trim(),
      time_per_question: Number(document.getElementById("quiz-time").value),
      questions: collectQuestions(),
    };
  }

  async function postJSON(url, body) {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(body),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok || !data.ok) throw new Error(data.error || "Something went wrong. Please try again.");
    return data;
  }

  /* ---------- events ---------- */
  addBtn.addEventListener("click", () => addQuestion());

  list.addEventListener("click", (event) => {
    const removeBtn = event.target.closest(".question-card__remove");
    if (!removeBtn) return;
    removeBtn.closest(".question-card").remove();
    updateUI();
    showMessage("");
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    showMessage("Publishing your quiz…", "ok");
    try {
      const data = await postJSON("/api/quizzes", collectQuiz());
      showMessage(data.message || "Published!", "ok");
      window.location.assign(data.url);
    } catch (error) {
      showMessage(error.message);
    }
  });

  document.getElementById("toggle-import").addEventListener("click", () => {
    importPanel.hidden = !importPanel.hidden;
    if (!importPanel.hidden) importJson.focus();
  });
  document.getElementById("close-import").addEventListener("click", () => {
    importPanel.hidden = true;
  });
  document.getElementById("sample-json").addEventListener("click", () => {
    importJson.value = JSON.stringify(
      {
        title: "Quick Science Round",
        category: "Science",
        description: "Imported from JSON — edit anything after publishing.",
        time_per_question: 15,
        questions: [
          {
            text: "What is the chemical symbol for water?",
            options: ["Wa", "H2O", "W", "O2"],
            correct: "B",
            explanation: "Two hydrogen atoms and one oxygen atom.",
          },
        ],
      },
      null,
      2
    );
  });
  document.getElementById("import-btn").addEventListener("click", async () => {
    showMessage("");
    let parsed;
    try {
      parsed = JSON.parse(importJson.value);
    } catch (error) {
      showMessage("That isn't valid JSON. Check the brackets and quotes.");
      return;
    }
    try {
      const data = await postJSON("/api/quizzes/import", parsed);
      showMessage(data.message || "Imported!", "ok");
      window.location.assign(data.url);
    } catch (error) {
      showMessage(error.message);
    }
  });

  updateUI();
})();
