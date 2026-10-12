
from flask import Flask, request, redirect, render_template_string
from datetime import date, datetime, timedelta
import json
import os

app = Flask(__name__)

DATA_FILE = "cases.json"

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Law Firm Management System</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f3f5f8;
               margin: 0; color: #222; }
        header { background: #17324d; color: white; padding: 22px; }
        main { max-width: 1100px; margin: 25px auto; padding: 0 16px; }
        .cards { display: flex; flex-wrap: wrap; gap: 12px; }
        .card { background: white; padding: 18px; border-radius: 8px;
                flex: 1; min-width: 140px; box-shadow: 0 1px 5px #ddd; }
        form, .panel { background: white; padding: 20px; margin: 20px 0;
                       border-radius: 8px; }
        input, select, button { box-sizing: border-box; padding: 10px;
                                margin: 6px 0; width: 100%; }
        button { background: #17324d; color: white; border: 0;
                 border-radius: 5px; cursor: pointer; }
        table { border-collapse: collapse; width: 100%; background: white; }
        th, td { padding: 10px; border-bottom: 1px solid #ddd;
                 text-align: left; }
        th { background: #e7edf3; }
        .table-wrap { overflow-x: auto; }
        .badge { font-weight: bold; }
        .Overdue { color: #b42318; }
        .Inactive { color: #9a6700; }
        .Active { color: #067647; }
        .Closed { color: #475467; }
        .hint { color: #555; font-size: 14px; }
    </style>
</head>
<body>
<header>
    <h1>Law Firm Management System</h1>
    <p>Manage cases and identify overdue or inactive matters.</p>
</header>
<main>
    <div class="cards">
        <div class="card"><h3>Total Cases</h3><strong>{{ cases|length }}</strong></div>
        <div class="card"><h3>Overdue</h3><strong>{{ overdue_count }}</strong></div>
        <div class="card"><h3>Inactive</h3><strong>{{ inactive_count }}</strong></div>
        <div class="card"><h3>Active</h3><strong>{{ active_count }}</strong></div>
    </div>

    <form method="POST" action="/add">
        <h2>Register a Case</h2>
        <label>Case Number</label>
        <input name="case_number" required placeholder="e.g. CASE-001">
        <label>Client Name (use fictional details for demos)</label>
        <input name="client_name" required placeholder="e.g. Alex Example">
        <label>Case Type</label>
        <select name="case_type">
            <option>Civil</option><option>Criminal</option>
            <option>Family</option><option>Commercial</option>
            <option>Other</option>
        </select>
        <label>Deadline</label>
        <input type="date" name="deadline" required>
        <label>Last Activity Date</label>
        <input type="date" name="last_activity" required>
        <label>Status</label>
        <select name="status">
            <option>Open</option><option>In Progress</option>
            <option>Closed</option>
        </select>
        <button type="submit">Add Case</button>
    </form>

    <section class="panel">
        <h2>Case Records</h2>
        <p class="hint">Overdue = open case past its deadline.
        Inactive = open case with no activity for at least 30 days.</p>
        <div class="table-wrap">
        <table>
            <thead><tr>
                <th>Case No.</th><th>Client</th><th>Type</th>
                <th>Deadline</th><th>Last Activity</th>
                <th>Status</th><th>Alert</th>
            </tr></thead>
            <tbody>
            {% for c in cases %}
                <tr>
                    <td>{{ c.case_number }}</td>
                    <td>{{ c.client_name }}</td>
                    <td>{{ c.case_type }}</td>
                    <td>{{ c.deadline }}</td>
                    <td>{{ c.last_activity }}</td>
                    <td>{{ c.status }}</td>
                    <td class="badge {{ c.alert }}">{{ c.alert }}</td>
                </tr>
            {% else %}
                <tr><td colspan="7">No cases registered yet.</td></tr>
            {% endfor %}
            </tbody>
        </table>
        </div>
    </section>
</main>
</body>
</html>
"""

def load_cases():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []

def save_cases(cases):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(cases, file, indent=4)

def get_alert(case):
    if case["status"] == "Closed":
        return "Closed"
    today = date.today()
    deadline = date.fromisoformat(case["deadline"])
    last_activity = date.fromisoformat(case["last_activity"])
    if deadline < today:
        return "Overdue"
    if (today - last_activity).days >= 30:
        return "Inactive"
    return "Active"

@app.route("/")
def home():
    cases = load_cases()
    for case in cases:
        case["alert"] = get_alert(case)
    return render_template_string(
        HTML,
        cases=cases,
        overdue_count=sum(c["alert"] == "Overdue" for c in cases),
        inactive_count=sum(c["alert"] == "Inactive" for c in cases),
        active_count=sum(c["alert"] == "Active" for c in cases)
    )

@app.route("/add", methods=["POST"])
def add_case():
    cases = load_cases()
    case_number = request.form["case_number"].strip()
    if any(c["case_number"].lower() == case_number.lower() for c in cases):
        return "That case number already exists. Go back and use a unique number.", 400

    deadline = request.form["deadline"]
    last_activity = request.form["last_activity"]
    try:
        date.fromisoformat(deadline)
        date.fromisoformat(last_activity)
    except ValueError:
        return "Please enter valid dates.", 400

    cases.append({
        "case_number": case_number,
        "client_name": request.form["client_name"].strip(),
        "case_type": request.form["case_type"],
        "deadline": deadline,
        "last_activity": last_activity,
        "status": request.form["status"]
    })
    save_cases(cases)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)