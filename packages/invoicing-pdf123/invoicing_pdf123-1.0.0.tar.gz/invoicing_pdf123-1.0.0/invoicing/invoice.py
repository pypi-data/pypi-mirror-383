import os
import pandas as pd
import glob
from fpdf import FPDF
from pathlib import Path

def generate(invoices_path, pdfs_path, image_path, product_id, product_name,
             amount_purchased, price_per_unit, total_price):
    """
    Converts invoice Excel files into PDF invoices.

    :param invoices_path: Folder containing Excel invoice files
    :param pdfs_path: Folder to save generated PDF invoices
    :param image_path: Path to logo image
    :param product_id: Column name for product ID
    :param product_name: Column name for product name
    :param amount_purchased: Column name for amount purchased
    :param price_per_unit: Column name for price per unit
    :param total_price: Column name for total price
    """

    # Create output folder if it doesn't exist
    if not os.path.exists(pdfs_path):
        os.makedirs(pdfs_path)

    # Get list of Excel files in the invoices folder
    filepaths = glob.glob(f"{invoices_path}/*.xlsx")

    for filepath in filepaths:
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.add_page()

        # Extract invoice number and date from filename
        filename = Path(filepath).stem
        try:
            invoice_nr, date = filename.split("-")
        except ValueError:
            print(f"Filename format incorrect: {filename}. Skipping file.")
            continue

        # Invoice header
        pdf.set_font(family="Times", size=16, style="B")
        pdf.cell(w=50, h=8, txt=f"Invoice nr. {invoice_nr}", ln=1)
        pdf.cell(w=50, h=8, txt=f"Date: {date}", ln=1)

        # Read the Excel file
        try:
            df = pd.read_excel(filepath, sheet_name="Sheet 1")
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            continue

        # Ensure required columns exist
        required_columns = [product_id, product_name, amount_purchased, price_per_unit, total_price]
        if not all(col in df.columns for col in required_columns):
            print(f"Missing columns in {filename}. Skipping file.")
            continue

        # Format column headers
        columns = [product_id, product_name, amount_purchased, price_per_unit, total_price]
        formatted_columns = [col.replace("_", " ").title() for col in columns]

        # Add table header
        pdf.set_font(family="Times", size=10, style="B")
        pdf.set_text_color(80, 80, 80)
        widths = [30, 70, 30, 30, 30]

        for i, col in enumerate(formatted_columns):
            pdf.cell(w=widths[i], h=8, txt=col, border=1)
        pdf.ln()

        # Add rows from Excel
        pdf.set_font(family="Times", size=10)
        pdf.set_text_color(80, 80, 80)

        for index, row in df.iterrows():
            pdf.cell(w=30, h=8, txt=str(row[product_id]), border=1)
            pdf.cell(w=70, h=8, txt=str(row[product_name]), border=1)
            pdf.cell(w=30, h=8, txt=str(row[amount_purchased]), border=1)
            pdf.cell(w=30, h=8, txt=str(row[price_per_unit]), border=1)
            pdf.cell(w=30, h=8, txt=str(row[total_price]), border=1, ln=1)

        # Add total sum row
        total_sum = df[total_price].sum()
        pdf.cell(w=30 + 70 + 30 + 30, h=8, txt="Total", border=1)
        pdf.cell(w=30, h=8, txt=str(total_sum), border=1, ln=1)

        # Add total sum text
        pdf.set_font(family="Times", size=10, style="B")
        pdf.cell(w=0, h=10, txt=f"The total price is {total_sum}", ln=1)

        # Add company name and logo
        pdf.set_font(family="Times", size=14, style="B")
        pdf.cell(w=0, h=10, txt="PythonHow", ln=1)

        if os.path.exists(image_path):
            pdf.image(image_path, w=10)
        else:
            print(f"Image not found at: {image_path}")

        # Save PDF
        output_filepath = f"{pdfs_path}/{filename}.pdf"
        pdf.output(output_filepath)
        print(f"Created: {output_filepath}")
