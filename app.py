"""QuizeTalk -- create quizzes, play them live, and talk about them."""
from __future__ import annotations

from flask import Flask, jsonify, redirect, render_template_string, request

from database import close_db, db_path, init_db
from routes.api_routes import api_bp
from routes.main_routes import main_bp

NOT_FOUND_PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Page not found · QuizeTalk</title>
  <link rel="icon" href="/static/assets/logo-quizetalk.svg" type="image/svg+xml">
  <link rel="stylesheet" href="/static/css/quizetalk.css">
</head>
<body>
  <main class="page-shell not-found">
    <div class="empty-state">
      <div class="empty-state__emoji">🧭</div>
      <h1>That quiz wandered off</h1>
      <p>We couldn't find what you were looking for. Let's get you back to the fun.</p>
      <a class="btn btn--primary" href="/">Back to Home Hub</a>
    </div>
  </main>
</body>
</html>
"""


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="quizetalk-dev-secret-change-me",
        DATABASE=db_path(),
    )

    init_db(app.config["DATABASE"])
    app.teardown_appcontext(close_db)

    # First run is friendly: load the demo quizzes automatically. Running
    # `python seed_data.py` manually still works (and supports --force).
    from seed_data import seed_if_empty

    seed_if_empty(app.config["DATABASE"])

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    @app.errorhandler(404)
    def handle_404(error):
        if request.path.startswith("/api/"):
            return jsonify(ok=False, error="Resource not found."), 404
        return render_template_string(NOT_FOUND_PAGE), 404

    @app.get("/favicon.ico")
    def favicon():
        return redirect("/static/assets/logo-quizetalk.svg")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
