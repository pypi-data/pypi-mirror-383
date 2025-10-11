import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF

def generate_report(data: pd.DataFrame, method="topsis", filename="decision_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"{method.upper()} Decision Report", ln=True, align="C")
    pdf.ln(10)

    # Add table
    pdf.cell(200, 10, txt="Rankings Table:", ln=True)
    pdf.ln(5)
    for _, row in data.iterrows():
        row_str = " | ".join(str(x) for x in row)
        pdf.cell(200, 8, txt=row_str, ln=True)

    # Find numeric column for chart
    numeric_cols = data.select_dtypes(include=["number"]).columns
    if len(numeric_cols) >= 2:
        # Assume first numeric column is score for chart
        score_col = numeric_cols[-1]  # usually last column like "Topsis Score"
        plt.figure(figsize=(6,4))
        plt.barh(data.iloc[:, 0], data[score_col], color="skyblue")
        plt.xlabel(score_col)
        plt.title(f"{method.upper()} Ranking Scores")
        plt.tight_layout()
        plt.savefig("chart.png")
        plt.close()

        pdf.add_page()
        pdf.cell(200, 10, txt="Ranking Chart:", ln=True)
        pdf.image("chart.png", x=10, y=30, w=180)

    pdf.output(filename)
    print(f"✅ Report saved as {filename}")
