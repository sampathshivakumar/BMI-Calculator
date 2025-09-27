from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ensure table exists
conn = sqlite3.connect("bmi_data.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS bmi_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    gender TEXT,
    age INTEGER,
    height REAL,
    weight REAL,
    bmi REAL,
    status TEXT,
    diff_kg REAL
)
""")
conn.commit()

@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        gender = request.form["gender"]
        age = int(request.form["age"])
        height = float(request.form["height"])
        weight = float(request.form["weight"])
        height_m = height/100
        bmi = weight/(height_m**2)
        if bmi<18.5:
            status="Underweight"
            target=18.5*(height_m**2)
            diff=target-weight
            message=f"Your BMI is {bmi:.1f} ({status}). You need to gain {abs(diff):.1f} kg to reach a healthy weight."
        elif bmi<=24.9:
            status="Normal"
            diff=0
            message=f"Your BMI is {bmi:.1f}. You’re fit and within the healthy range!"
        else:
            status="Overweight"
            target=24.9*(height_m**2)
            diff=weight-target
            message=f"Your BMI is {bmi:.1f} ({status}). You need to lose {abs(diff):.1f} kg to reach a healthy weight."

        cursor.execute("""INSERT INTO bmi_records (name,gender,age,height,weight,bmi,status,diff_kg)
                          VALUES(?,?,?,?,?,?,?,?)""",
                          (name,gender,age,height,weight,bmi,status,diff))
        conn.commit()
        return render_template("index.html", message=message)
    return render_template("index.html")

@app.route("/past")
def past():
    cursor.execute("SELECT name,gender,age,height,weight,bmi,status,diff_kg FROM bmi_records")
    rows=cursor.fetchall()
    return render_template("past.html", rows=rows)

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000)
