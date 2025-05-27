import os
import PyPDF2
from typing import List


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file."""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text


def analyze_paper_format(years: List[str]):
    """Analyze the format of papers from different years."""
    papers_dir = "data/papers"

    for year in years:
        paper1_file = f"{year}-paper1.pdf"
        paper_path = os.path.join(papers_dir, paper1_file)

        if os.path.exists(paper_path):
            print(f"\n{'='*50}")
            print(f"ANALYZING {year} PAPER 1")
            print(f"{'='*50}")

            text = extract_text_from_pdf(paper_path)

            # Show first 2000 characters to see the structure
            print("First 2000 characters:")
            print(text[:2000])
            print("\n" + "-" * 30)

            # Look for question patterns
            lines = text.split("\n")
            question_lines = []
            for i, line in enumerate(lines[:100]):  # Check first 100 lines
                line = line.strip()
                if line and any(
                    char.isdigit() for char in line[:10]
                ):  # Lines starting with numbers
                    question_lines.append(f"Line {i}: {line}")

            print("Lines that might be questions (first 20):")
            for line in question_lines[:20]:
                print(line)
        else:
            print(f"File not found: {paper1_file}")


if __name__ == "__main__":
    # Analyze papers from every 3 years
    years_to_analyze = [
        "2024",
        "2021",
        "2018",
        "2015",
        "2012",
        "2009",
        "2006",
        "2003",
        "2000",
    ]
    analyze_paper_format(years_to_analyze)
