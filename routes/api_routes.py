"""JSON endpoints used by the builder, the player and the discussion board."""
from __future__ import annotations

from flask import Blueprint, jsonify, request, url_for

from database import get_db

api_bp = Blueprint("api", __name__, url_prefix="/api")

LETTERS = ("A", "B", "C", "D")
MAX_QUESTIONS = 30


def _error(message: str, status: int = 400):
    return jsonify(ok=False, error=message), status


def _payload() -> dict:
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def _normalise_questions(raw) -> list[dict]:
    """Accept both builder shape (option_a..d) and JSON-import shape (options[])."""
    if not isinstance(raw, list) or not raw:
        raise ValueError("Add at least one question.")
    if len(raw) > MAX_QUESTIONS:
        raise ValueError(f"A quiz can have at most {MAX_QUESTIONS} questions.")

    cleaned = []
    for index, item in enumerate(raw, 1):
        if not isinstance(item, dict):
            raise ValueError(f"Question {index} is malformed.")

        text = str(item.get("text") or item.get("question") or "").strip()
        if not text:
            raise ValueError(f"Question {index} needs a question text.")

        options = item.get("options")
        if isinstance(options, list) and len(options) == 4:
            values = [str(option or "").strip() for option in options]
        else:
            values = [
                str(item.get(f"option_{letter.lower()}") or "").strip()
                for letter in LETTERS
            ]
        if any(not value for value in values):
            raise ValueError(f"Question {index} needs all four options.")

        raw_correct = item.get("correct")
        if raw_correct is None:
            raw_correct = item.get("correct_option")
        if isinstance(raw_correct, bool):
            raw_correct = None
        if isinstance(raw_correct, int):
            correct = LETTERS[raw_correct] if 0 <= raw_correct < 4 else None
        else:
            correct = str(raw_correct or "").strip().upper()[:1]
            if correct in ("1", "2", "3", "4"):
                correct = LETTERS[int(correct) - 1]
        if correct not in LETTERS:
            raise ValueError(f"Question {index} needs a valid correct answer (A-D).")

        cleaned.append(
            {
                "text": text,
                "option_a": values[0],
                "option_b": values[1],
                "option_c": values[2],
                "option_d": values[3],
                "correct": correct,
                "explanation": str(item.get("explanation") or "").strip(),
            }
        )
    return cleaned


def _insert_quiz(data: dict) -> int:
    title = str(data.get("title") or "").strip()
    if not title or len(title) > 120:
        raise ValueError("Give your quiz a title (up to 120 characters).")

    category = str(data.get("category") or "General").strip() or "General"
    description = str(data.get("description") or "").strip()
    raw_time = data.get("time_per_question", 15)
    try:
        time_limit = int(raw_time)
    except (TypeError, ValueError):
        raise ValueError("Time per question must be a number.") from None
    if not 5 <= time_limit <= 120:
        raise ValueError("Time per question must be between 5 and 120 seconds.")

    questions = _normalise_questions(data.get("questions"))

    db = get_db()
    cursor = db.execute(
        """INSERT INTO quizzes (title, category, description, time_per_question)
           VALUES (?, ?, ?, ?)""",
        (title[:120], category[:40], description[:300], time_limit),
    )
    quiz_id = cursor.lastrowid

    for position, question in enumerate(questions, 1):
        db.execute(
            """INSERT INTO questions
               (quiz_id, question_text, option_a, option_b, option_c, option_d,
                correct_option, explanation, position)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                quiz_id,
                question["text"],
                question["option_a"],
                question["option_b"],
                question["option_c"],
                question["option_d"],
                question["correct"],
                question["explanation"],
                position,
            ),
        )
    db.commit()
    return quiz_id


@api_bp.post("/quizzes")
def create_quiz():
    try:
        quiz_id = _insert_quiz(_payload())
    except ValueError as exc:
        return _error(str(exc))
    return (
        jsonify(
            ok=True,
            id=quiz_id,
            url=url_for("main.play", quiz_id=quiz_id),
            message="Quiz published! 🎉",
        ),
        201,
    )


@api_bp.post("/quizzes/import")
def import_quiz():
    payload = _payload()
    data = payload.get("quiz") if isinstance(payload.get("quiz"), dict) else payload
    try:
        quiz_id = _insert_quiz(data)
    except ValueError as exc:
        return _error(str(exc))
    return (
        jsonify(
            ok=True,
            id=quiz_id,
            url=url_for("main.play", quiz_id=quiz_id),
            message="Quiz imported successfully!",
        ),
        201,
    )


@api_bp.get("/quizzes/<int:quiz_id>/export")
def export_quiz(quiz_id: int):
    db = get_db()
    quiz = db.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
    if quiz is None:
        return _error("Quiz not found.", 404)

    rows = db.execute(
        "SELECT * FROM questions WHERE quiz_id = ? ORDER BY position, id", (quiz_id,)
    ).fetchall()
    return jsonify(
        ok=True,
        quiz={
            "title": quiz["title"],
            "category": quiz["category"],
            "description": quiz["description"],
            "time_per_question": quiz["time_per_question"],
            "questions": [
                {
                    "text": row["question_text"],
                    "options": [
                        row["option_a"],
                        row["option_b"],
                        row["option_c"],
                        row["option_d"],
                    ],
                    "correct": row["correct_option"],
                    "explanation": row["explanation"],
                }
                for row in rows
            ],
        },
    )


@api_bp.post("/quizzes/<int:quiz_id>/submit")
def submit_quiz(quiz_id: int):
    db = get_db()
    quiz = db.execute("SELECT id FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
    if quiz is None:
        return _error("Quiz not found.", 404)

    payload = _payload()
    raw_answers = payload.get("answers") or {}
    answers = raw_answers if isinstance(raw_answers, dict) else {}
    player_name = str(payload.get("player_name") or "Player").strip()[:40] or "Player"

    questions = db.execute(
        "SELECT * FROM questions WHERE quiz_id = ? ORDER BY position, id", (quiz_id,)
    ).fetchall()

    score = 0
    breakdown = []
    for question in questions:
        given = str(answers.get(str(question["id"]), "") or "").strip().upper()[:1]
        if given not in LETTERS:
            given = ""
        is_correct = given == question["correct_option"]
        if is_correct:
            score += 1
        breakdown.append(
            {
                "id": question["id"],
                "question": question["question_text"],
                "given": given,
                "correct": question["correct_option"],
                "is_correct": is_correct,
                "explanation": question["explanation"],
            }
        )

    total = len(questions)
    accuracy = round(score / total * 100) if total else 0
    db.execute(
        """INSERT INTO scores (quiz_id, player_name, score, total, accuracy)
           VALUES (?, ?, ?, ?, ?)""",
        (quiz_id, player_name, score, total, accuracy),
    )
    db.commit()

    return jsonify(
        ok=True,
        player_name=player_name,
        score=score,
        total=total,
        accuracy=accuracy,
        breakdown=breakdown,
        score_text=f"{score}/{total}",
    )


@api_bp.get("/quizzes/<int:quiz_id>/talks")
def get_talks(quiz_id: int):
    db = get_db()
    rows = db.execute(
        "SELECT * FROM talks WHERE quiz_id = ? ORDER BY created_at DESC, id DESC",
        (quiz_id,),
    ).fetchall()
    return jsonify(
        ok=True,
        talks=[
            {
                "id": row["id"],
                "player_name": row["player_name"],
                "score_text": row["score_text"],
                "message": row["message"],
                "created_at": row["created_at"],
            }
            for row in rows
        ],
    )


@api_bp.post("/quizzes/<int:quiz_id>/talks")
def post_talk(quiz_id: int):
    db = get_db()
    quiz = db.execute("SELECT id FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
    if quiz is None:
        return _error("Quiz not found.", 404)

    payload = _payload()
    message = str(payload.get("message") or "").strip()
    if not message:
        return _error("Write a tip or comment first.")
    if len(message) > 500:
        return _error("Keep your comment under 500 characters.")

    player_name = str(payload.get("player_name") or "Player").strip()[:40] or "Player"
    score_text = str(payload.get("score_text") or "").strip()[:20]

    cursor = db.execute(
        """INSERT INTO talks (quiz_id, player_name, score_text, message)
           VALUES (?, ?, ?, ?)""",
        (quiz_id, player_name, score_text, message),
    )
    db.commit()

    return (
        jsonify(
            ok=True,
            talk={
                "id": cursor.lastrowid,
                "player_name": player_name,
                "score_text": score_text,
                "message": message,
                "created_at": "just now",
            },
        ),
        201,
    )
