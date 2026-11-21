/* QuizeTalk — live quiz player: timer ring, feedback, confetti, score, talks */
(() => {
  "use strict";

  const quiz = window.QUIZ;
  const questions = window.QUESTIONS;
  const quizId = window.QUIZ_ID;
  if (!quiz || !Array.isArray(questions) || questions.length === 0) return;

  const $ = (id) => document.getElementById(id);
  const els = {
    arena: $("arena"),
    result: $("result"),
    playerName: $("player-name"),
    progressBar: $("progress-bar"),
    progressLabel: $("progress-label"),
    progressPercent: $("progress-percent"),
    progressTrack: $("progress-track"),
    timerValue: $("timer-value"),
    timerProgress: $("timer-progress"),
    questionNumber: $("question-number"),
    questionText: $("question-text"),
    explanation: $("explanation"),
    nextBtn: $("next-btn"),
    soundToggle: $("sound-toggle"),
    scoreValue: $("score-value"),
    accuracyValue: $("accuracy-value"),
    scoreProgress: $("score-progress"),
    resultTitle: $("result-title"),
    resultMessage: $("result-message"),
    breakdown: $("breakdown-list"),
    shareBtn: $("share-btn"),
    talkForm: $("talk-form"),
    talkName: $("talk-name"),
    talkScore: $("talk-score"),
    talkMessage: $("talk-message"),
    talkStatus: $("talk-message-status"),
    talkList: $("talk-list"),
    talkCount: $("talk-count"),
    confetti: $("confetti-canvas"),
  };
  const tiles = [...document.querySelectorAll(".option-tile")];

  const TIMER_CIRCUMFERENCE = 2 * Math.PI * 52;
  const SCORE_CIRCUMFERENCE = 2 * Math.PI * 54;
  els.timerProgress.style.strokeDasharray = String(TIMER_CIRCUMFERENCE);
  els.scoreProgress.style.strokeDasharray = String(SCORE_CIRCUMFERENCE);

  let current = 0;
  let locked = false;
  let answers = {};
  let deadline = 0;
  let ticker = null;
  let audioCtx = null;
  let muted = false;
  let lastResult = null;

  /* ---------------- sound ---------------- */
  function playTone(kind) {
    if (muted) return;
    try {
      const Ctx = window.AudioContext || window.webkitAudioContext;
      if (!Ctx) return;
      audioCtx = audioCtx || new Ctx();
      if (audioCtx.state === "suspended") audioCtx.resume();
      const notes = kind === "correct" ? [523.25, 659.25, 783.99] : [311.13, 233.08];
      notes.forEach((frequency, i) => {
        const oscillator = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        const start = audioCtx.currentTime + i * 0.09;
        oscillator.type = kind === "correct" ? "sine" : "triangle";
        oscillator.frequency.value = frequency;
        gain.gain.setValueAtTime(0.0001, start);
        gain.gain.exponentialRampToValueAtTime(0.11, start + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.0001, start + 0.17);
        oscillator.connect(gain);
        gain.connect(audioCtx.destination);
        oscillator.start(start);
        oscillator.stop(start + 0.19);
      });
    } catch (_) {
      /* audio is a bonus — never let it break the quiz */
    }
  }

  els.soundToggle.addEventListener("click", () => {
    muted = !muted;
    els.soundToggle.textContent = muted ? "🔇" : "🔊";
    els.soundToggle.title = muted ? "Sound off" : "Sound on";
  });

  /* ---------------- timer + question flow ---------------- */
  function setTimerDisplay(remaining, total) {
    els.timerValue.textContent = String(Math.ceil(remaining));
    const fraction = Math.max(0, Math.min(1, remaining / total));
    els.timerProgress.style.strokeDashoffset = String(TIMER_CIRCUMFERENCE * (1 - fraction));
    els.timerProgress.classList.toggle("is-low", remaining <= 5);
  }

  function startTimer() {
    clearInterval(ticker);
    const total = Number(quiz.time_per_question) || 15;
    deadline = Date.now() + total * 1000;
    setTimerDisplay(total, total);
    ticker = setInterval(() => {
      const remaining = Math.max(0, (deadline - Date.now()) / 1000);
      setTimerDisplay(remaining, total);
      if (remaining <= 0) {
        clearInterval(ticker);
        showFeedback("");
      }
    }, 80);
  }

  function renderQuestion() {
    const question = questions[current];
    locked = false;
    els.questionNumber.textContent = String(current + 1);
    els.questionText.textContent = question.question_text;
    els.explanation.hidden = true;
    els.explanation.textContent = "";
    els.explanation.className = "explanation";
    els.nextBtn.hidden = true;

    tiles.forEach((tile) => {
      const letter = tile.dataset.letter;
      tile.querySelector(".option-tile__text").textContent =
        question[`option_${letter.toLowerCase()}`] || "";
      tile.className = "option-tile";
      tile.disabled = false;
    });

    const percent = Math.round((current / questions.length) * 100);
    els.progressBar.style.width = `${percent}%`;
    els.progressLabel.textContent = `Question ${current + 1} of ${questions.length}`;
    els.progressPercent.textContent = `${percent}%`;
    els.progressTrack.setAttribute("aria-valuenow", String(percent));

    startTimer();
  }

  function showFeedback(given) {
    if (locked) return;
    locked = true;
    clearInterval(ticker);

    const question = questions[current];
    const correct = given === question.correct_option;
    tiles.forEach((tile) => {
      const letter = tile.dataset.letter;
      tile.disabled = true;
      if (letter === question.correct_option) tile.classList.add("is-correct");
      else if (letter === given) tile.classList.add("is-wrong");
      else tile.classList.add("is-dimmed");
    });

    let prefix;
    if (!given) prefix = `⏰ Time's up! Correct answer: ${question.correct_option}.`;
    else if (correct) prefix = "✅ Correct!";
    else prefix = `❌ Not quite — the answer was ${question.correct_option}.`;

    els.explanation.textContent = question.explanation
      ? `${prefix} ${question.explanation}`
      : prefix;
    els.explanation.className = `explanation ${correct ? "explanation--correct" : "explanation--wrong"}`;
    els.explanation.hidden = false;

    els.nextBtn.textContent = current === questions.length - 1 ? "See my score →" : "Next question →";
    els.nextBtn.hidden = false;
    playTone(correct ? "correct" : "wrong");
  }

  function selectAnswer(letter) {
    if (locked) return;
    answers[questions[current].id] = letter;
    showFeedback(letter);
  }

  function nextQuestion() {
    if (!locked) return;
    current += 1;
    if (current >= questions.length) finishQuiz();
    else renderQuestion();
  }

  tiles.forEach((tile) => {
    tile.addEventListener("click", () => selectAnswer(tile.dataset.letter));
  });
  els.nextBtn.addEventListener("click", nextQuestion);

  document.addEventListener("keydown", (event) => {
    if (els.arena.hidden || event.target.matches("input, textarea")) return;
    const key = event.key.toUpperCase();
    if (key.length === 1 && "ABCD".includes(key)) {
      event.preventDefault();
      selectAnswer(key);
    } else if (event.key === "Enter" && locked) {
      event.preventDefault();
      nextQuestion();
    }
  });

  /* ---------------- scorecard ---------------- */
  function headlineFor(accuracy) {
    if (accuracy >= 90) return ["Quiz legend! 🏆", "Almost flawless. The crown is yours."];
    if (accuracy >= 70) return ["Great job! 🎉", "You really know your stuff."];
    if (accuracy >= 40) return ["Nice try! 💪", "A solid round — check the tips below."];
    return ["Every round teaches you something 🌱", "Read the explanations, then go again!"];
  }

  function renderBreakdown(items) {
    els.breakdown.replaceChildren();
    items.forEach((item) => {
      const row = document.createElement("div");
      row.className = `breakdown__item ${item.is_correct ? "breakdown__item--ok" : "breakdown__item--no"}`;

      const badge = document.createElement("span");
      badge.className = "breakdown__badge";
      badge.textContent = item.is_correct ? "✓" : "✕";

      const body = document.createElement("div");
      body.className = "breakdown__body";

      const question = document.createElement("div");
      question.className = "breakdown__q";
      question.textContent = item.question;

      const answer = document.createElement("div");
      answer.className = "breakdown__answer";
      answer.textContent = `Your answer: ${item.given || "—"} · Correct: ${item.correct}`;

      body.append(question, answer);
      if (item.explanation) {
        const explanation = document.createElement("p");
        explanation.className = "breakdown__exp";
        explanation.textContent = item.explanation;
        body.appendChild(explanation);
      }
      row.append(badge, body);
      els.breakdown.appendChild(row);
    });
  }

  function renderResult(data) {
    lastResult = data;
    els.scoreValue.textContent = `${data.score}/${data.total}`;
    els.accuracyValue.textContent = `${data.accuracy}% accuracy`;
    const [title, message] = headlineFor(data.accuracy);
    els.resultTitle.textContent = title;
    els.resultMessage.textContent = message;
    renderBreakdown(data.breakdown);

    els.scoreProgress.style.strokeDashoffset = String(SCORE_CIRCUMFERENCE);
    requestAnimationFrame(() => {
      els.scoreProgress.style.strokeDashoffset = String(SCORE_CIRCUMFERENCE * (1 - data.accuracy / 100));
    });

    els.talkScore.value = data.score_text;
    if (!els.talkName.value.trim()) els.talkName.value = data.player_name;
    celebrate(data.accuracy);
  }

  async function finishQuiz() {
    clearInterval(ticker);
    const name = els.playerName.value.trim() || "Player";
    els.arena.hidden = true;
    els.result.hidden = false;

    try {
      const response = await fetch(`/api/quizzes/${quizId}/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ player_name: name, answers }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok || !data.ok) throw new Error(data.error || "Could not save your score.");
      renderResult(data);
      await loadTalks();
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (error) {
      els.resultTitle.textContent = "Score couldn't be saved";
      els.resultMessage.textContent = error.message;
    }
  }

  /* ---------------- confetti ---------------- */
  function celebrate(accuracy) {
    if (accuracy < 40 || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const canvas = els.confetti;
    const context = canvas.getContext("2d");
    if (!context) return;
    const dpr = window.devicePixelRatio || 1;
    const resize = () => {
      canvas.width = window.innerWidth * dpr;
      canvas.height = window.innerHeight * dpr;
      context.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();
    window.addEventListener("resize", resize, { once: true });

    const colours = ["#6D28D9", "#8B5CF6", "#EC4899", "#0EA5E9", "#10B981", "#F59E0B", "#FDE68A"];
    const particles = Array.from({ length: accuracy >= 90 ? 150 : 90 }, () => ({
      x: Math.random() * window.innerWidth,
      y: -20 - Math.random() * window.innerHeight * 0.5,
      vx: (Math.random() - 0.5) * 3.2,
      vy: 2 + Math.random() * 3.5,
      size: 6 + Math.random() * 7,
      rotation: Math.random() * Math.PI,
      spin: (Math.random() - 0.5) * 0.22,
      colour: colours[Math.floor(Math.random() * colours.length)],
    }));

    let frames = 0;
    function draw() {
      context.clearRect(0, 0, window.innerWidth, window.innerHeight);
      particles.forEach((p) => {
        p.vy += 0.09;
        p.x += p.vx;
        p.y += p.vy;
        p.rotation += p.spin;
        context.save();
        context.translate(p.x, p.y);
        context.rotate(p.rotation);
        context.fillStyle = p.colour;
        context.fillRect(-p.size / 2, -p.size / 3, p.size, p.size * 0.66);
        context.restore();
      });
      frames += 1;
      if (frames < 230) requestAnimationFrame(draw);
      else context.clearRect(0, 0, window.innerWidth, window.innerHeight);
    }
    requestAnimationFrame(draw);
  }

  /* ---------------- share link ---------------- */
  els.shareBtn.addEventListener("click", async () => {
    const suffix = lastResult ? `?score=${lastResult.score}-${lastResult.total}` : "";
    const link = `${window.location.origin}${window.location.pathname}${suffix}`;
    try {
      if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(link);
      else throw new Error("clipboard unavailable");
    } catch (_) {
      const helper = document.createElement("textarea");
      helper.value = link;
      document.body.appendChild(helper);
      helper.select();
      try { document.execCommand("copy"); } catch (_) { /* ignore */ }
      helper.remove();
    }
    els.shareBtn.textContent = "✅ Link copied!";
    window.setTimeout(() => { els.shareBtn.textContent = "🔗 Copy share link"; }, 2200);
  });

  /* ---------------- QuizeTalk discussion ---------------- */
  function formatTime(raw) {
    if (!raw || raw === "just now") return "just now";
    const parsed = new Date(raw.replace(" ", "T"));
    return Number.isNaN(parsed.getTime()) ? "just now" : parsed.toLocaleDateString();
  }

  function talkCard(talk) {
    const card = document.createElement("article");
    card.className = "talk-card";

    const head = document.createElement("div");
    head.className = "talk-card__head";

    const avatar = document.createElement("span");
    avatar.className = "avatar";
    avatar.textContent = (talk.player_name || "P").charAt(0).toUpperCase();

    const name = document.createElement("span");
    name.className = "talk-card__name";
    name.textContent = talk.player_name || "Player";
    head.appendChild(avatar);
    head.appendChild(name);

    if (talk.score_text) {
      const score = document.createElement("span");
      score.className = "talk-card__score";
      score.textContent = `🏅 ${talk.score_text}`;
      head.appendChild(score);
    }

    const time = document.createElement("span");
    time.className = "talk-card__time";
    time.textContent = formatTime(talk.created_at);
    head.appendChild(time);

    const message = document.createElement("p");
    message.className = "talk-card__message";
    message.textContent = talk.message;

    card.append(head, message);
    return card;
  }

  function setTalkCount(count) {
    els.talkCount.textContent = `${count} ${count === 1 ? "post" : "posts"}`;
  }

  async function loadTalks() {
    try {
      const response = await fetch(`/api/quizzes/${quizId}/talks`);
      const data = await response.json();
      if (!data.ok) return;
      els.talkList.replaceChildren(...data.talks.map(talkCard));
      setTalkCount(data.talks.length);
    } catch (_) {
      /* the quiz itself still works if comments can't load */
    }
  }

  els.talkForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = els.talkMessage.value.trim();
    if (!message) {
      els.talkStatus.textContent = "Write something first 🙂";
      els.talkStatus.className = "form-message form-message--error";
      els.talkStatus.hidden = false;
      return;
    }
    try {
      const response = await fetch(`/api/quizzes/${quizId}/talks`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({
          player_name: els.talkName.value.trim() || "Player",
          score_text: els.talkScore.value.trim(),
          message,
        }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok || !data.ok) throw new Error(data.error || "Could not post your comment.");
      els.talkList.prepend(talkCard(data.talk));
      setTalkCount(els.talkList.children.length);
      els.talkMessage.value = "";
      els.talkStatus.textContent = "Posted! Thanks for sharing 💜";
      els.talkStatus.className = "form-message form-message--ok";
      els.talkStatus.hidden = false;
    } catch (error) {
      els.talkStatus.textContent = error.message;
      els.talkStatus.className = "form-message form-message--error";
      els.talkStatus.hidden = false;
    }
  });

  /* ---------------- go! ---------------- */
  renderQuestion();
  loadTalks();
})();
