from flask import Flask, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "student_id_card_secret"


# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect("student_id_card.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            register_no TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            register_no TEXT NOT NULL,
            application_type TEXT NOT NULL,
            reason TEXT NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
    """)

    conn.commit()
    conn.close()


# ---------- HOME ----------
@app.route("/")
def home():
    return """
    <html>
    <head>
        <title>Student ID Card Management System</title>
        <style>
            body {
                font-family: Arial;
                background: #f2f6fc;
                text-align: center;
                padding: 60px;
            }
            .box {
                background: white;
                padding: 40px;
                max-width: 600px;
                margin: auto;
                border-radius: 15px;
                box-shadow: 0 0 15px #ccc;
            }
            h1 {
                color: #1d4ed8;
            }
            a, button {
                display: inline-block;
                padding: 12px 25px;
                margin: 10px;
                background: #1d4ed8;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                border: none;
                cursor: pointer;
            }
        </style>
    </head>

    <body>
        <div class="box">
            <h1>Student ID Card Management System</h1>
            <p>Apply for a new ID card or request a replacement.</p>

            <a href="/register">Student Registration</a>
            <a href="/login">Student Login</a>
        </div>
    </body>
    </html>
    """


# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        name = request.form["name"]
        register_no = request.form["register_no"]
        department = request.form["department"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()

        try:
            conn.execute("""
                INSERT INTO students
                (name, register_no, department, email, password)
                VALUES (?, ?, ?, ?, ?)
            """, (name, register_no, department, email, password))

            conn.commit()
            conn.close()

            return redirect("/login")

        except sqlite3.IntegrityError:
            conn.close()
            return "Register number already exists. <a href='/register'>Go Back</a>"

    return """
    <html>
    <head>
        <title>Student Registration</title>
        <style>
            body {
                font-family: Arial;
                background: #eef4ff;
                text-align: center;
                padding: 30px;
            }
            form {
                background: white;
                padding: 30px;
                max-width: 400px;
                margin: auto;
                border-radius: 12px;
                box-shadow: 0 0 10px #ccc;
            }
            input {
                width: 90%;
                padding: 10px;
                margin: 8px;
            }
            button {
                padding: 12px 30px;
                background: #1d4ed8;
                color: white;
                border: none;
                border-radius: 6px;
            }
        </style>
    </head>

    <body>
        <h1>Student Registration</h1>

        <form method="POST">

            <input name="name" placeholder="Student Name" required>

            <input name="register_no" placeholder="Register Number" required>

            <input name="department" placeholder="Department" required>

            <input name="email" type="email" placeholder="Email" required>

            <input name="password" type="password" placeholder="Password" required>

            <button type="submit">Register</button>

        </form>

        <p><a href="/">Home</a></p>
    </body>
    </html>
    """


# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        register_no = request.form["register_no"]
        password = request.form["password"]

        conn = get_db()

        student = conn.execute("""
            SELECT * FROM students
            WHERE register_no = ? AND password = ?
        """, (register_no, password)).fetchone()

        conn.close()

        if student:
            session["register_no"] = register_no
            return redirect("/dashboard")

        return "Invalid login details. <a href='/login'>Try Again</a>"

    return """
    <html>
    <head>
        <title>Student Login</title>
        <style>
            body {
                font-family: Arial;
                background: #eef4ff;
                text-align: center;
                padding: 50px;
            }
            form {
                background: white;
                padding: 30px;
                max-width: 350px;
                margin: auto;
                border-radius: 12px;
                box-shadow: 0 0 10px #ccc;
            }
            input {
                width: 90%;
                padding: 10px;
                margin: 10px;
            }
            button {
                padding: 12px 30px;
                background: #1d4ed8;
                color: white;
                border: none;
                border-radius: 6px;
            }
        </style>
    </head>

    <body>

        <h1>Student Login</h1>

        <form method="POST">

            <input name="register_no"
                   placeholder="Register Number"
                   required>

            <input name="password"
                   type="password"
                   placeholder="Password"
                   required>

            <button type="submit">Login</button>

        </form>

        <p><a href="/">Home</a></p>

    </body>
    </html>
    """


# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():

    if "register_no" not in session:
        return redirect("/login")

    register_no = session["register_no"]

    conn = get_db()

    student = conn.execute("""
        SELECT * FROM students
        WHERE register_no = ?
    """, (register_no,)).fetchone()

    applications = conn.execute("""
        SELECT * FROM applications
        WHERE register_no = ?
    """, (register_no,)).fetchall()

    conn.close()

    application_rows = ""

    for application in applications:
        application_rows += f"""
        <tr>
            <td>{application['id']}</td>
            <td>{application['application_type']}</td>
            <td>{application['reason']}</td>
            <td>{application['status']}</td>
        </tr>
        """

    return f"""
    <html>
    <head>
        <title>Student Dashboard</title>
        <style>
            body {{
                font-family: Arial;
                background: #f2f6fc;
                padding: 30px;
                text-align: center;
            }}

            .box {{
                background: white;
                padding: 30px;
                max-width: 800px;
                margin: auto;
                border-radius: 12px;
                box-shadow: 0 0 10px #ccc;
            }}

            a {{
                display: inline-block;
                padding: 12px 20px;
                margin: 10px;
                background: #1d4ed8;
                color: white;
                text-decoration: none;
                border-radius: 6px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 25px;
            }}

            th, td {{
                padding: 10px;
                border: 1px solid #ccc;
            }}

            th {{
                background: #1d4ed8;
                color: white;
            }}
        </style>
    </head>

    <body>

        <div class="box">

            <h1>Student Dashboard</h1>

            <h2>Welcome, {student['name']}</h2>

            <p>
                Register Number: {student['register_no']}
            </p>

            <p>
                Department: {student['department']}
            </p>

            <a href="/apply">Apply / Replacement ID Card</a>

            <a href="/logout">Logout</a>

            <h2>Application Status</h2>

            <table>

                <tr>
                    <th>ID</th>
                    <th>Type</th>
                    <th>Reason</th>
                    <th>Status</th>
                </tr>

                {application_rows}

            </table>

        </div>

    </body>
    </html>
    """


# ---------- APPLY ----------
@app.route("/apply", methods=["GET", "POST"])
def apply():

    if "register_no" not in session:
        return redirect("/login")

    if request.method == "POST":

        application_type = request.form["application_type"]
        reason = request.form["reason"]

        conn = get_db()

        conn.execute("""
            INSERT INTO applications
            (register_no, application_type, reason)
            VALUES (?, ?, ?)
        """, (
            session["register_no"],
            application_type,
            reason
        ))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return """
    <html>
    <head>
        <title>ID Card Application</title>
        <style>
            body {
                font-family: Arial;
                background: #eef4ff;
                text-align: center;
                padding: 40px;
            }

            form {
                background: white;
                padding: 30px;
                max-width: 450px;
                margin: auto;
                border-radius: 12px;
                box-shadow: 0 0 10px #ccc;
            }

            select, textarea, button {
                width: 90%;
                padding: 12px;
                margin: 10px;
            }

            button {
                background: #1d4ed8;
                color: white;
                border: none;
                border-radius: 6px;
            }
        </style>
    </head>

    <body>

        <h1>ID Card Application</h1>

        <form method="POST">

            <select name="application_type">

                <option value="New ID Card">
                    New ID Card
                </option>

                <option value="Replacement">
                    Replacement
                </option>

            </select>

            <textarea name="reason"
                      placeholder="Enter reason"
                      required></textarea>

            <button type="submit">
                Submit Application
            </button>

        </form>

        <p>
            <a href="/dashboard">Back to Dashboard</a>
        </p>

    </body>
    </html>
    """


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ---------- START APPLICATION ----------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)