# 🎤 QuizeTalk

> Create custom quizzes, play them in a live gamified arena, and talk about them afterwards.

QuizeTalk is a full-stack Python web app built with **Flask + SQLite3** on the backend and **HTML5, CSS3 & vanilla JavaScript** on the frontend. No build tools, no npm, no frameworks — just clone, seed and play.

---

## ✨ Features

| Area | What you get |
| --- | --- |
| **Home Hub** | Gradient hero, category filters (All / Coding / Science / General), quiz cards with question count, player count and discussion count. |
| **Visual Quiz Studio** (`/create`) | Split-card builder with title, category, timer and live question cards. Add/remove MCQs, pick the correct answer, add explanations, and even import a quiz from JSON. |
| **Live Quiz Stage** (`/play/<id>`) | Smooth progress bar, animated SVG circular countdown, 2×2 colour-coded option tiles, `A/B/C/D` keyboard shortcuts, instant green/red feedback, sound effects and confetti. |
| **Scorecard** | Accuracy percentage, per-question breakdown with explanations, one-click share link and a replay button. |
| **QuizeTalk Corner** | Discussion board under every scorecard — post your score and a tip; comments are stored in SQLite and shown live. |
| **Extras** | JSON export/import endpoint, seeded demo content, friendly 404 page, responsive layout and reduced-motion support. |

---

## 📁 Project structure

```
quizetalk-app/
├── app.py                      # Flask app factory, blueprints, error handlers
├── seed_data.py                # 4 sample quizzes × 5 questions + discussions
├── requirements.txt
├── README.md
├── .gitignore
├── database/
│   ├── __init__.py             # schema + shared SQLite helpers
│   └── quizetalk.db            # created automatically (git-ignored)
├── routes/
│   ├── main_routes.py          # /, /create, /play/<id>
│   └── api_routes.py           # /api/... JSON endpoints
├── templates/
│   ├── base.html               # navbar + SVG logo + CTA
│   ├── index.html              # Home Hub
│   ├── create.html             # Visual Quiz Studio
│   └── play.html               # Live Quiz Stage + scorecard + talks
└── static/
    ├── css/quizetalk.css       # full gamified design system
    ├── js/
    │   ├── builder.js          # dynamic question cards + publish/import
    │   └── player.js           # timer ring, feedback, confetti, talks
    └── assets/logo-quizetalk.svg
```

---

## 🚀 Run locally

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python seed_data.py               # optional: app auto-seeds an empty DB
python app.py
```

Open <http://127.0.0.1:5000>.

Reset the demo data any time with:

```bash
python seed_data.py --force
```

---

## 🔌 API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/api/quizzes` | Publish a new quiz with its questions. |
| `POST` | `/api/quizzes/import` | Import a quiz from exported JSON. |
| `GET` | `/api/quizzes/<id>/export` | Download a quiz as portable JSON. |
| `POST` | `/api/quizzes/<id>/submit` | Grade answers, save the score, return a breakdown. |
| `GET` | `/api/quizzes/<id>/talks` | List discussion posts. |
| `POST` | `/api/quizzes/<id>/talks` | Add a discussion post. |

Example import payload:

```json
{
  "title": "My Quiz",
  "category": "Science",
  "time_per_question": 15,
  "questions": [
    {
      "text": "What is H2O?",
      "options": ["Oxygen", "Water", "Salt", "Hydrogen"],
      "correct": "B",
      "explanation": "Two hydrogen atoms plus one oxygen atom."
    }
  ]
}
```

The builder accepts either `options[]` + `correct`, or `option_a` … `option_d` + `correct_option`.

---

## 🗃️ Database

SQLite tables: `quizzes`, `questions`, `scores`, `talks`. Foreign keys cascade deletes, and frequently queried columns are indexed. The database file lives at `database/quizetalk.db` and is ignored by Git.

---

## 🎨 Design tokens

| Token | Colour |
| --- | --- |
| Background | `#F4F3FF` soft lavender-white |
| Brand | `#6D28D9` → `#8B5CF6` violet gradient |
| Ink | `#1E1B4B` |
| Options A / B / C / D | `#0EA5E9` / `#10B981` / `#F59E0B` / `#F43F5E` |
| Card radius | `18px` |

---

## 📤 Push to GitHub

```bash
git init
git add .
git commit -m "feat: QuizeTalk full-stack quiz generator and discussion platform"
git branch -M main
git remote add origin https://github.com/Rg100152/QuizeTalk.git
git push -u origin main
```

---

Made with 💜 for curious people who like to talk about what they learned.
