from flask import Flask, render_template, request, session, send_file
import matplotlib.pyplot as plt
import logging
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

app = Flask(_name_)
app.secret_key = 'supersecretkey'  # Required for session

# Configure logging
logging.basicConfig(level=logging.INFO)

def safe_float(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0

def calculate_emergency_fund(salary, expenses, months):
    total_monthly_expenses = sum(expenses.values())
    return round(total_monthly_expenses * months, 2)

def calculate_savings_ratio(salary, total_expenses):
    return round((salary - total_expenses) / salary * 100, 2) if salary > 0 else 0

def generate_cost_cutting_tips(salary, expenses):
    tips = []
    for category, amount in expenses.items():
        if salary > 0 and amount > 0.2 * salary:
            tips.append(f"Consider cutting down on {category}, it's a major part of your salary.")
    if not tips:
        tips.append("Your expenses look balanced. Good job!")
    return tips

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        salary = safe_float(request.form.get('salary'))

        expenses = {
            'Rent': safe_float(request.form.get('Rent')),
            'Utilities': safe_float(request.form.get('Utilities')),
            'Groceries': safe_float(request.form.get('Groceries')),
            'Transport': safe_float(request.form.get('Transport')),
            'Insurance': safe_float(request.form.get('Insurance')),
            'Other': safe_float(request.form.get('Other')),
        }
        months = int(request.form.get('months') or 1)

        total_monthly_expenses = sum(expenses.values())
        emergency_fund = calculate_emergency_fund(salary, expenses, months)
        savings_ratio = calculate_savings_ratio(salary, total_monthly_expenses)
        tips = generate_cost_cutting_tips(salary, expenses)

        labels = list(expenses.keys())
        values = list(expenses.values())

        logging.info(f"Salary: {salary}, Total Monthly Expenses: {total_monthly_expenses}, Emergency Fund: {emergency_fund}, Savings Ratio: {savings_ratio}")

        if 'history' not in session:
            session['history'] = []
        session['history'].append({
            'salary': salary,
            'expenses': expenses,
            'months': months,
            'emergency_fund': emergency_fund,
            'savings_ratio': savings_ratio
        })
        session.modified = True

        return render_template('result.html',
                               salary=salary,
                               total_monthly_expenses=total_monthly_expenses,
                               emergency_fund=emergency_fund,
                               savings_ratio=savings_ratio,
                               months=months,
                               expenses=expenses,
                               tips=tips,
                               labels=labels,
                               values=values)

    except Exception as e:
        logging.exception("An error occurred during calculation.")
        return f"Something went wrong: {e}"

@app.route('/download-pdf')
def download_pdf():
    try:
        if 'history' not in session or not session['history']:
            return "No data available for report generation."

        last_entry = session['history'][-1]

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica", 12)

        p.drawString(100, 750, "Emergency Fund Report")
        p.line(100, 747, 500, 747)

        y = 720
        p.drawString(100, y, f"Salary: ₹{last_entry['salary']}")
        y -= 20
        p.drawString(100, y, f"Months to Save: {last_entry['months']}")
        y -= 20
        p.drawString(100, y, f"Emergency Fund Required: ₹{last_entry['emergency_fund']}")
        y -= 20
        p.drawString(100, y, f"Savings Ratio: {last_entry['savings_ratio']}%")

        y -= 40
        p.drawString(100, y, "Expenses:")
        for category, amount in last_entry['expenses'].items():
            y -= 20
            p.drawString(120, y, f"{category}: ₹{amount}")

        p.showPage()
        p.save()

        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name='EmergencyFundReport.pdf', mimetype='application/pdf')

    except Exception as e:
        logging.exception("Failed to generate PDF.")
        return f"Error generating PDF: {e}"

@app.route('/history')
def view_history():
    return json.dumps(session.get('history', []), indent=4)

if _name_ == '_main_':
    app.run(debug=True)