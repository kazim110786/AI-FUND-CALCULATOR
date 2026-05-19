from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    salary = float(request.form.get("salary") or 0)
    months = int(request.form.get("months") or 1)

    rent = float(request.form.get("Rent") or 0)
    utilities = float(request.form.get("Utilities") or 0)
    groceries = float(request.form.get("Groceries") or 0)
    transport = float(request.form.get("Transport") or 0)
    insurance = float(request.form.get("Insurance") or 0)
    other = float(request.form.get("Other") or 0)

    total_expenses = rent + utilities + groceries + transport + insurance + other
    emergency_fund = total_expenses * months

    return render_template(
        "result.html",
        salary=salary,
        total_monthly_expenses=total_expenses,
        emergency_fund=emergency_fund,
        months=months
    )

if __name__ == "__main__":
    app.run()
