from flask import Flask, render_template, request, g, make_response
import sqlite3
import os

app = Flask(__name__)

DATABASE = os.path.join(app.root_path, 'flsite.db')
app.config.from_object(__name__)

class QuizApp:
    def __init__(self):
        self.db = None

    def connect_db(self):
        conn = sqlite3.connect(app.config['DATABASE'])
        conn.row_factory = sqlite3.Row
        return conn

    def get_db(self):
        if not hasattr(g, 'link_db'):
            g.link_db = self.connect_db()
        return g.link_db

    def close_db(self, error):
        if hasattr(g, 'link_db'):
            g.link_db.close()

    def create_db(self):
        db = self.connect_db()
        with app.open_resource('db.sql', 'r') as f:
            db.cursor().executescript(f.read())
        db.commit()
        db.close()

quiz_app = QuizApp()

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/Mockups/Quiz", methods=["POST", "GET"])
def addvalue():
    new_id = None
    if request.method == "POST":
        answer = request.form.get('answer')
        example = request.form.get('example')[:-1]
        db = quiz_app.get_db()
        if answer.isdigit():
            db.cursor().execute("""INSERT INTO quiz(id, example, answer, correct) VALUES (?, ?, ?, ?)""",
                            (request.cookies.get('id'), example, answer, eval(example) == int(answer)))
            db.commit()
            new_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

        if request.form.get('check') == '1':
            resp = make_response(render_template("./result.html",
                                                 answers=db.cursor().execute(
                                                     """SELECT example,answer FROM quiz WHERE id=?""",
                                                     (request.cookies.get('id'),)).fetchall(),
                                                 right_answers=db.cursor().execute(
                                                     """SELECT sum(correct) FROM quiz WHERE id=?""",
                                                     (request.cookies.get('id'),)).fetchone(),
                                                 all_answers=db.cursor().execute(
                                                     """SELECT count(correct) FROM quiz WHERE id=?""",
                                                     (request.cookies.get('id'),)).fetchone()))
            return resp

        return render_template('./quiz.html')

    if request.method == "GET":
        if request.cookies.get('id') is None:
            db = quiz_app.get_db()
            resp = make_response(render_template('/index.html'))
            resp.set_cookie('id', f"{new_id if new_id is not None else 1}")
            return resp

        if request.args.get('type') == 'Quiz':
            db = quiz_app.get_db()
            resp = make_response(render_template("./quiz.html"))
            resp.set_cookie('id', f"{new_id if new_id is not None else 1}")
            return resp

        else:
            db = quiz_app.get_db()
            resp = make_response(render_template("./result.html",
                                                 answers=db.cursor().execute(
                                                     """SELECT example,answer FROM quiz WHERE id=?""",
                                                     (request.cookies.get('id'),)).fetchall(),
                                                 right_answers=db.cursor().execute(
                                                     """SELECT sum(correct) FROM quiz WHERE id=?""",
                                                     (request.cookies.get('id'),)).fetchone(),
                                                 all_answers=db.cursor().execute(
                                                     """SELECT count(correct) FROM quiz WHERE id=?""",
                                                     (request.cookies.get('id'),)).fetchone()))

            return resp

if __name__ == "__main__":
    quiz_app.create_db()
    app.run(debug=True)