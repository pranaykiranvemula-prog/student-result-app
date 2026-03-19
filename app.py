from flask import Flask, render_template, request, redirect, url_for, send_file
import json
import os
import csv
import io

app = Flask(__name__)
DATA_FILE = "students.json"


# ── Helpers ──────────────────────────────────────────────────────────

def load_students():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_students(students):
    with open(DATA_FILE, "w") as f:
        json.dump(students, f, indent=2)

def calculate_grade(percentage):
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    else:
        return "FAIL"

def calculate_student(student):
    marks = [
        student["maths"],
        student["science"],
        student["english"],
        student["telugu"],
        student["hindi"]
    ]
    total      = sum(marks)
    maximum    = len(marks) * 100
    percentage = round((total / maximum) * 100, 2)
    grade      = calculate_grade(percentage)
    return total, maximum, percentage, grade


# ── Routes ───────────────────────────────────────────────────────────

@app.route("/")
def index():
    students  = load_students()
    results   = []
    passed    = 0
    failed    = 0
    class_avg = 0

    for s in students:
        total, maximum, percentage, grade = calculate_student(s)
        results.append({
            "id":         s["id"],
            "name":       s["name"],
            "maths":      s["maths"],
            "science":    s["science"],
            "english":    s["english"],
            "telugu":     s["telugu"],
            "hindi":      s["hindi"],
            "total":      total,
            "maximum":    maximum,
            "percentage": percentage,
            "grade":      grade,
        })
        if grade == "FAIL":
            failed += 1
        else:
            passed += 1

    if results:
        class_avg = round(
            sum(r["percentage"] for r in results) / len(results), 2
        )

    return render_template(
        "index.html",
        results=results,
        passed=passed,
        failed=failed,
        class_avg=class_avg,
        total_students=len(results),
    )


@app.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        students = load_students()
        new_id   = max([s["id"] for s in students], default=0) + 1
        try:
            student = {
                "id":      new_id,
                "name":    request.form["name"].strip(),
                "maths":   int(request.form["maths"]),
                "science": int(request.form["science"]),
                "english": int(request.form["english"]),
                "telugu":  int(request.form["telugu"]),
                "hindi":   int(request.form["hindi"]),
            }
            students.append(student)
            save_students(students)
            return redirect(url_for("index"))
        except (ValueError, KeyError):
            error = "Please fill all fields with valid numbers (0-100)."
            return render_template("add.html", error=error)

    return render_template("add.html", error=None)


@app.route("/delete/<int:student_id>")
def delete_student(student_id):
    students = load_students()
    students = [s for s in students if s["id"] != student_id]
    save_students(students)
    return redirect(url_for("index"))


@app.route("/download")
def download_csv():
    students = load_students()
    output   = io.StringIO()
    writer   = csv.writer(output)
    writer.writerow(["Name","Maths","Science","English","Telugu","Hindi",
                     "Total","Maximum","Percentage","Grade"])
    for s in students:
        total, maximum, percentage, grade = calculate_student(s)
        writer.writerow([s["name"], s["maths"], s["science"],
                         s["english"], s["telugu"], s["hindi"],
                         total, maximum, percentage, grade])
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="results.csv",
    )


if __name__ == "__main__":
    app.run(debug=True)