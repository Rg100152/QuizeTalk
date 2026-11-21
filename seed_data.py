"""Seed QuizeTalk with four ready-to-play quizzes and sample discussions.

Usage:
    python seed_data.py            # seeds only when the database is empty
    python seed_data.py --force    # wipes demo content and seeds again
    python seed_data.py --path /tmp/demo.db --force
"""
from __future__ import annotations

import argparse

from database import DB_PATH, connect_db, init_db

SEED = [
    {
        "title": "Python Mastery",
        "category": "Coding",
        "description": "A quick-fire round on Python basics, data types and handy built-ins.",
        "time_per_question": 15,
        "questions": [
            {
                "text": "Which keyword defines a function in Python?",
                "options": ["def", "func", "function", "lambda"],
                "correct": "A",
                "explanation": "`def` declares a named function. `lambda` only creates a small anonymous one.",
            },
            {
                "text": "What does len([1, 2, 3]) return?",
                "options": ["2", "3", "4", "Error"],
                "correct": "B",
                "explanation": "len() counts the items in a container — this list has three items.",
            },
            {
                "text": "Which built-in type stores key-value pairs?",
                "options": ["List", "Tuple", "Dictionary", "Set"],
                "correct": "C",
                "explanation": "Dictionaries map keys to values: {'name': 'Ada'}.",
            },
            {
                "text": "What is the value of 2 ** 3 in Python?",
                "options": ["6", "16", "8", "9"],
                "correct": "C",
                "explanation": "The ** operator is exponentiation: 2 to the power of 3 = 8.",
            },
            {
                "text": "Which exception is raised when you divide by zero?",
                "options": ["ValueError", "TypeError", "IndexError", "ZeroDivisionError"],
                "correct": "D",
                "explanation": "Python raises ZeroDivisionError; catch it with a try/except block.",
            },
        ],
        "talks": [
            {
                "player_name": "Aarav",
                "score_text": "5/5",
                "message": "Tip: remember ** is power, not multiply. Easy mark once that clicks!",
            },
            {
                "player_name": "Meera",
                "score_text": "4/5",
                "message": "Missed the len() one — I always forget it counts items, not indexes. 😅",
            },
        ],
    },
    {
        "title": "Cyber Security Basics",
        "category": "General",
        "description": "Password smarts, phishing traps and the everyday habits that keep you safe.",
        "time_per_question": 20,
        "questions": [
            {
                "text": "What does HTTPS add to a normal HTTP connection?",
                "options": [
                    "Faster loading only",
                    "Encryption through TLS",
                    "A different port number",
                    "Free Wi-Fi",
                ],
                "correct": "B",
                "explanation": "HTTPS wraps HTTP in TLS so data between you and the site is encrypted.",
            },
            {
                "text": "Which of these is the strongest password?",
                "options": [
                    "password123",
                    "qwertyuiop",
                    "C0rrect-H0rse-Battery!",
                    "12345678",
                ],
                "correct": "C",
                "explanation": "Long, unique passphrases with mixed characters are much harder to crack.",
            },
            {
                "text": "What is phishing?",
                "options": [
                    "A firewall rule",
                    "A fake message tricking you into sharing secrets",
                    "A type of malware that encrypts files",
                    "A password manager feature",
                ],
                "correct": "B",
                "explanation": "Phishing uses convincing fake emails or sites to steal credentials.",
            },
            {
                "text": "Which of these is 'something you have' in authentication?",
                "options": ["A password", "A fingerprint", "A phone receiving an OTP", "A PIN"],
                "correct": "C",
                "explanation": "Factors are: something you know, something you have, something you are.",
            },
            {
                "text": "What does a firewall mainly do?",
                "options": [
                    "Stores backups",
                    "Speeds up downloads",
                    "Filters incoming and outgoing network traffic",
                    "Writes your passwords",
                ],
                "correct": "C",
                "explanation": "Firewalls apply rules to network traffic to block suspicious connections.",
            },
        ],
        "talks": [
            {
                "player_name": "Riya",
                "score_text": "5/5",
                "message": "My trick: never tap links in messages. Open the app or type the URL yourself.",
            },
            {
                "player_name": "Kabir",
                "score_text": "3/5",
                "message": "Got the MFA factor question wrong. Remember: phone = have, fingerprint = are.",
            },
            {
                "player_name": "Nisha",
                "score_text": "4/5",
                "message": "A password manager changed my life. Unique passwords everywhere!",
            },
        ],
    },
    {
        "title": "World Wildlife & Snakes",
        "category": "Science",
        "description": "Slithery facts, record holders and creatures of the wild.",
        "time_per_question": 15,
        "questions": [
            {
                "text": "Which snake is the longest by total length?",
                "options": [
                    "Reticulated python",
                    "Green anaconda",
                    "King cobra",
                    "Black mamba",
                ],
                "correct": "A",
                "explanation": "The reticulated python is longest; the green anaconda is the heaviest.",
            },
            {
                "text": "Which snake warns predators with a rattle on its tail?",
                "options": ["Cobra", "Rattlesnake", "Python", "Viper"],
                "correct": "B",
                "explanation": "Rattlesnakes shake modified tail scales to make their famous buzzing sound.",
            },
            {
                "text": "What do we call animals most active at dawn and dusk?",
                "options": ["Nocturnal", "Diurnal", "Crepuscular", "Hibernating"],
                "correct": "C",
                "explanation": "Crepuscular animals are most active during twilight hours.",
            },
            {
                "text": "Which is the largest land animal?",
                "options": [
                    "White rhinoceros",
                    "Giraffe",
                    "Hippopotamus",
                    "African bush elephant",
                ],
                "correct": "D",
                "explanation": "African bush elephants can weigh over 6 tonnes.",
            },
            {
                "text": "Which big cat is native to the Americas?",
                "options": ["Lion", "Jaguar", "Leopard", "Tiger"],
                "correct": "B",
                "explanation": "Jaguars roam from Mexico down to Argentina — the only Panthera cat there.",
            },
        ],
        "talks": [
            {
                "player_name": "Dev",
                "score_text": "4/5",
                "message": "Longest vs heaviest got me! Python = longest, anaconda = heaviest.",
            },
            {
                "player_name": "Sanya",
                "score_text": "5/5",
                "message": "Crepuscular is such a fun word. Now I can sound fancy at sunrise. 🐍",
            },
        ],
    },
    {
        "title": "General Knowledge",
        "category": "General",
        "description": "A little bit of everything: planets, elements, books and oceans.",
        "time_per_question": 12,
        "questions": [
            {
                "text": "How many continents are there on Earth?",
                "options": ["5", "6", "7", "8"],
                "correct": "C",
                "explanation": "The seven continents are Africa, Antarctica, Asia, Australia, Europe, North and South America.",
            },
            {
                "text": "Which planet is known as the Red Planet?",
                "options": ["Venus", "Mars", "Jupiter", "Mercury"],
                "correct": "B",
                "explanation": "Iron oxide dust gives Mars its rusty red colour.",
            },
            {
                "text": "What is the chemical symbol for gold?",
                "options": ["Go", "Gd", "Ag", "Au"],
                "correct": "D",
                "explanation": "Au comes from the Latin word 'aurum'. Ag is silver.",
            },
            {
                "text": "Who wrote 'The Discovery of India'?",
                "options": [
                    "Jawaharlal Nehru",
                    "Mahatma Gandhi",
                    "Rabindranath Tagore",
                    "Amartya Sen",
                ],
                "correct": "A",
                "explanation": "Nehru wrote it while imprisoned during the Quit India movement.",
            },
            {
                "text": "Which is the largest ocean on Earth?",
                "options": ["Atlantic", "Indian", "Pacific", "Arctic"],
                "correct": "C",
                "explanation": "The Pacific covers more area than all Earth's landmasses combined.",
            },
        ],
        "talks": [
            {
                "player_name": "Tara",
                "score_text": "5/5",
                "message": "Au = aurum, Ag = argentum. Latin roots make element symbols so much easier!",
            },
            {
                "player_name": "Arjun",
                "score_text": "4/5",
                "message": "Fast round! 12 seconds makes the GK quiz genuinely thrilling.",
            },
        ],
    },
]


def seed(path: str | None = None, force: bool = False) -> int:
    """Insert the demo content. Returns the number of quizzes created."""
    target = str(path or DB_PATH)
    init_db(target)
    connection = connect_db(target)
    try:
        existing = int(connection.execute("SELECT COUNT(*) FROM quizzes").fetchone()[0])
        if existing and not force:
            return 0

        if force:
            for table in ("talks", "scores", "questions", "quizzes"):
                connection.execute(f"DELETE FROM {table}")

        for quiz in SEED:
            cursor = connection.execute(
                """INSERT INTO quizzes (title, category, description, time_per_question)
                   VALUES (?, ?, ?, ?)""",
                (
                    quiz["title"],
                    quiz["category"],
                    quiz["description"],
                    quiz["time_per_question"],
                ),
            )
            quiz_id = cursor.lastrowid

            for position, question in enumerate(quiz["questions"], 1):
                connection.execute(
                    """INSERT INTO questions
                       (quiz_id, question_text, option_a, option_b, option_c,
                        option_d, correct_option, explanation, position)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        quiz_id,
                        question["text"],
                        *question["options"],
                        question["correct"],
                        question["explanation"],
                        position,
                    ),
                )

            for talk in quiz.get("talks", []):
                connection.execute(
                    """INSERT INTO talks (quiz_id, player_name, score_text, message)
                       VALUES (?, ?, ?, ?)""",
                    (quiz_id, talk["player_name"], talk["score_text"], talk["message"]),
                )

        connection.commit()
        return len(SEED)
    finally:
        connection.close()


def seed_if_empty(path: str | None = None) -> int:
    return seed(path, force=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed sample quizzes into QuizeTalk.")
    parser.add_argument("--force", action="store_true", help="replace existing quizzes")
    parser.add_argument("--path", default=None, help="path to a SQLite database file")
    args = parser.parse_args()

    created = seed(args.path, force=args.force)
    if created:
        print(f"✅ Seeded {created} quizzes with questions and discussions.")
    else:
        print("ℹ️  Database already has quizzes. Use --force to reseed.")
