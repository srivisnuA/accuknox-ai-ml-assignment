"""Local sample API for the student-score task. Run: python -m assignment_1.question_02.demo_api"""
from flask import Flask, jsonify
app = Flask(__name__)
STUDENTS = [
    {"student": "Asha", "subject": "Maths", "score": 88},
    {"student": "Bala", "subject": "Maths", "score": 76},
    {"student": "Charan", "subject": "Maths", "score": 92},
    {"student": "Divya", "subject": "Maths", "score": 81},
    {"student": "Eshan", "subject": "Maths", "score": 69},
]
@app.get("/health")
def health():
    return jsonify({"status": "ok"})
@app.get("/students")
def students():
    return jsonify({"students": STUDENTS})
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False)
