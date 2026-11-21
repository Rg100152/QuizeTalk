"""Page routes: Home Hub, Visual Quiz Studio and Live Quiz Stage."""
from __future__ import annotations

from flask import Blueprint, abort, render_template, request

from database import get_db

main_bp = Blueprint("main", __name__)

CATEGORIES = ("Coding", "Science", "General")

QUIZ_SUMMARY_SQL = """
    SELECT q.id, q.title, q.category, q.description, q.time_per_question,
           q.created_at,
           (SELECT COUNT(*) FROM questions qu WHERE qu.quiz_id = q.id) AS question_count,
           (SELECT COUNT(*) FROM scores s WHERE s.quiz_id = q.id) AS player_count,
           (SELECT COUNT(*) FROM talks t WHERE t.quiz_id = q.id) AS talk_count
    FROM quizzes q
"""


@main_bp.get("/")
def home():
    active = request.args.get("category", "All")
    if active not in ("All", *CATEGORIES):
        active = "All"

    db = get_db()
    if active == "All":
        quizzes = db.execute(
            QUIZ_SUMMARY_SQL + " ORDER BY q.created_at DESC, q.id DESC"
        ).fetchall()
    else:
        quizzes = db.execute(
            QUIZ_SUMMARY_SQL + " WHERE q.category = ? ORDER BY q.created_at DESC, q.id DESC",
            (active,),
        ).fetchall()

    totals = db.execute(
        """
        SELECT (SELECT COUNT(*) FROM quizzes)                  AS quizzes,
               (SELECT COUNT(*) FROM questions)                AS questions,
               (SELECT COUNT(*) FROM scores)                   AS plays,
               (SELECT COUNT(*) FROM talks)                    AS talks
        """
    ).fetchone()

    return render_template(
        "index.html",
        quizzes=quizzes,
        categories=CATEGORIES,
        active_category=active,
        totals=totals,
    )


@main_bp.get("/create")
def create():
    return render_template("create.html", categories=CATEGORIES)


@main_bp.get("/play/<int:quiz_id>")
def play(quiz_id: int):
    db = get_db()
    quiz = db.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
    if quiz is None:
        abort(404)

    questions = db.execute(
        "SELECT * FROM questions WHERE quiz_id = ? ORDER BY position ASC, id ASC",
        (quiz_id,),
    ).fetchall()
    if not questions:
        abort(404)

    talk_count = db.execute(
        "SELECT COUNT(*) FROM talks WHERE quiz_id = ?", (quiz_id,)
    ).fetchone()[0]

    return render_template(
        "play.html",
        quiz=dict(quiz),
        questions=[dict(question) for question in questions],
        talk_count=talk_count,
    )
