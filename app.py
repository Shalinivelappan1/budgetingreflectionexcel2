import streamlit as st
import pandas as pd
from io import BytesIO

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Smart Budget & Expense Tracker",
    page_icon="💰",
    layout="centered"
)

st.title("💰 Smart Budget & Expense Tracker")
st.caption("Developed by Prof. Shalini Velappan, IIM Trichy")

# --------------------------------------------------
# Scoring Functions
# --------------------------------------------------
def calculate_financial_health_score(savings_rate, expense_ratio, needs_pct, wants_pct):
    score = 0
    savings_rate = max(savings_rate, 0)

    # Savings (40)
    score += min((savings_rate / 20) * 40, 40)

    # Expense ratio (30)
    if expense_ratio <= 70:
        score += 30
    elif expense_ratio <= 85:
        score += 15
    else:
        score += 5

    # 30–30–20 adherence (30)
    score += 10 if needs_pct <= 30 else 0
    score += 10 if wants_pct <= 30 else 0
    score += 10 if savings_rate >= 20 else 0

    return min(round(score), 100)


def calculate_alignment_score(spendable_income, essential_expenses):
    if spendable_income <= 0:
        return 0

    ratio = essential_expenses / spendable_income

    if ratio <= 0.5:
        return 100
    elif ratio <= 0.7:
        return 80
    elif ratio <= 0.9:
        return 50
    else:
        return 20

# --------------------------------------------------
# Excel Generator (unchanged)
# --------------------------------------------------
def generate_excel_file(
    period, income, total_expenses, savings,
    savings_rate, expense_ratio, health_score,
    df, needs_pct, wants_pct,
    student_name, course,
    confidence_before, confidence_after,
    reflections,
    basic, hra, special, variable,
    employer_pf, employee_pf, tax,
    take_home, spendable_income,
    essential_expenses, alignment_score
):
    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:

        pd.DataFrame({
            "Metric": [
                "Period", "Income", "Total Expenses", "Savings",
                "Savings Rate (%)", "Expense–Income Ratio (%)",
                "Financial Health Score", "CTC–Budget Alignment Score"
            ],
            "Value": [
                period, income, total_expenses, savings,
                round(max(savings_rate, 0), 2),
                round(expense_ratio, 2),
                health_score,
                alignment_score
            ]
        }).to_excel(writer, sheet_name="Budget_Summary", index=False)

        expense_df = df.copy()
        expense_df["% of Income"] = expense_df["Amount (₹)"].apply(
            lambda x: round((x / income) * 100, 2) if income > 0 else 0
        )
        expense_df.to_excel(writer, sheet_name="Expense_Details", index=False)

        pd.DataFrame({
            "Component": ["Needs", "Wants", "Savings"],
            "Actual %": [needs_pct, wants_pct, savings_rate],
            "Benchmark": ["≤ 30%", "≤ 30%", "≥ 20%"]
        }).to_excel(writer, sheet_name="30-30-20_Check", index=False)

        pd.DataFrame({
            "Component": [
                "Basic Pay", "HRA", "Special Allowance",
                "Variable Pay", "Employer PF",
                "Employee PF", "Tax",
                "Take-Home Pay",
                "Spendable Income",
                "Essential Expenses",
                "CTC–Budget Alignment Score"
            ],
            "Amount (₹)": [
                basic, hra, special,
                variable, employer_pf,
                employee_pf, tax,
                take_home,
                spendable_income,
                essential_expenses,
                alignment_score
            ]
        }).to_excel(writer, sheet_name="CTC_Alignment", index=False)

        pd.DataFrame({
            "Field": [
                "Student Name", "Course",
                "Confidence (Before)", "Confidence (After)",
                "Q1", "Q2", "Q3", "Q4", "Q5"
            ],
            "Response": [
                student_name, course,
                confidence_before, confidence_after,
                reflections[0], reflections[1],
                reflections[2], reflections[3], reflections[4]
            ]
        }).to_excel(writer, sheet_name="Reflection", index=False)

    output.seek(0)
    return output

# --------------------------------------------------
# Tabs
# --------------------------------------------------
tab1, tab2 = st.tabs(["📊 Budget Dashboard", "🧠 Reflection & Submission"])

# ================= TAB 1 =================
with tab1:
    period = st.radio("Select Budget Period", ["Monthly", "Yearly"], horizontal=True)
    income = st.number_input(f"{period} Income (₹)", min_value=0, step=1000)

    savings_goal = st.number_input(f"{period} Savings Goal (₹)", min_value=0, step=1000)

    categories = [
        "Housing (Rent / EMI)", "Food", "Transport",
        "Utilities", "Lifestyle & Entertainment", "Others"
    ]

    expenses = {c: st.number_input(f"{c} (₹)", min_value=0, step=500) for c in categories}

    df = pd.DataFrame({
        "Category": expenses.keys(),
        "Amount (₹)": expenses.values()
    })

    total_expenses = df["Amount (₹)"].sum()
    savings = income - total_expenses
    savings_rate = (savings / income * 100) if income else 0
    expense_ratio = (total_expenses / income * 100) if income else 0

    # -------- Budget Summary Tiles --------
    st.subheader("📊 Budget Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Income", f"₹{income:,.0f}")
    c2.metric("Expenses", f"₹{total_expenses:,.0f}")
    c3.metric("Savings", f"₹{savings:,.0f}")

    # -------- Expense Ratio Bar --------
    st.subheader("📉 Expense-to-Income Ratio")
    st.progress(min(expense_ratio / 100, 1.0))

    if expense_ratio <= 70:
        st.success(f"✅ Spending {expense_ratio:.1f}% — healthy")
    elif expense_ratio <= 85:
        st.warning(f"⚠️ Spending {expense_ratio:.1f}% — monitor closely")
    else:
        st.error(f"🚨 Spending {expense_ratio:.1f}% — high risk")

    # -------- Savings Goal Tracker --------
    st.subheader("🎯 Savings Goal Tracker")
    if savings_goal > 0:
        progress = max(min(savings / savings_goal, 1.0), 0.0)
        st.progress(progress)
        if progress >= 1:
            st.success("🎉 Savings goal achieved!")
        elif progress >= 0.5:
            st.warning("⚠️ Halfway to savings goal")
        else:
            st.error("🚨 Savings behind target")
    else:
        st.info("Set a savings goal to track progress.")

    # -------- 30–30–20 Rule --------
    needs = df[df["Category"].isin(["Housing (Rent / EMI)", "Food", "Utilities"])]["Amount (₹)"].sum()
    wants = df[df["Category"] == "Lifestyle & Entertainment"]["Amount (₹)"].sum()

    needs_pct = (needs / income * 100) if income else 0
    wants_pct = (wants / income * 100) if income else 0

    st.subheader("🇮🇳 30–30–20 Rule Check (India)")
    st.write(f"Needs: {needs_pct:.1f}% | Wants: {wants_pct:.1f}% | Savings: {savings_rate:.1f}%")

    # -------- Smart Insights --------
    st.subheader("🧠 Smart Budget Insights")
    insights = []

    if expense_ratio > 85:
        insights.append("High expense-to-income ratio increases financial stress.")
    if savings_rate < 20:
        insights.append("Savings are below the recommended 20%.")
    if wants_pct > 30:
        insights.append("Lifestyle spending exceeds the 30% guideline.")
    if needs_pct > 30:
        insights.append("Essential expenses are high; housing or utilities may need review.")

    if not insights:
        insights.append("Your budget is well-balanced and aligned with benchmarks.")

    for i in insights:
        st.write("•", i)

    # -------- CTC Section (unchanged) --------
    st.subheader("💼 CTC Structure (Monthly)")
    c1, c2 = st.columns(2)

    with c1:
        basic = st.number_input("Basic Pay (₹)", min_value=0, step=1000)
        hra = st.number_input("HRA (₹)", min_value=0, step=1000)
        special = st.number_input("Special Allowance (₹)", min_value=0, step=1000)

    with c2:
        variable = st.number_input("Variable Pay (₹)", min_value=0, step=1000)
        employer_pf = st.number_input("Employer PF / NPS (₹)", min_value=0, step=500)
        employee_pf = st.number_input("Employee PF (₹)", min_value=0, step=500)
        tax = st.number_input("Tax (₹)", min_value=0, step=500)

    gross_ctc = basic + hra + special + variable + employer_pf
    take_home = basic + hra + special + variable - employee_pf - tax
    spendable_income = basic + hra + special - employee_pf - tax

    st.subheader("🔄 CTC → Reality Check")
    m1, m2, m3 = st.columns(3)
    m1.metric("Gross CTC", f"₹{gross_ctc:,.0f}")
    m2.metric("Take-Home Pay", f"₹{take_home:,.0f}")
    m3.metric("Spendable Income", f"₹{spendable_income:,.0f}")

    # -------- Scores --------
    health_score = calculate_financial_health_score(
        savings_rate, expense_ratio, needs_pct, wants_pct
    )

    alignment_score = calculate_alignment_score(spendable_income, needs)

    st.subheader("❤️ Financial Health Score")
    st.metric("Score (0–100)", health_score)

    st.subheader("🧩 CTC–Budget Alignment Score")
    st.metric("Alignment Score (0–100)", alignment_score)

# ================= TAB 2 =================
with tab2:
    confidence_before = st.slider("Confidence Before", 0, 10, 5)
    confidence_after = st.slider("Confidence After", 0, 10, confidence_before)

    reflections = [
        st.text_area("Q1: What surprised you most about your spending?"),
        st.text_area("Q2: One expense you would reduce next month"),
        st.text_area("Q3: Reflection on 30–30–20 rule"),
        st.text_area("Q4: One financial habit you want to change"),
        st.text_area("Q5: One-line insight from this exercise")
    ]

    student_name = st.text_input("Student Name")
    course = st.text_input("Course / Section")

    if st.button("⬇️ Download Excel Submission") and student_name:
        excel = generate_excel_file(
            period, income, total_expenses, savings,
            savings_rate, expense_ratio, health_score,
            df, needs_pct, wants_pct,
            student_name, course,
            confidence_before, confidence_after,
            reflections,
            basic, hra, special, variable,
            employer_pf, employee_pf, tax,
            take_home, spendable_income,
            needs, alignment_score
        )

        st.download_button(
            "📥 Download Excel File",
            excel,
            file_name=f"{student_name.replace(' ', '_')}_Budget_Submission.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
