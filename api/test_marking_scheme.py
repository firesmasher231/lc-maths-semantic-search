import PyPDF2
import os


def test_marking_scheme_patterns():
    pdf_path = os.path.join("data", "markingscheme", "2023-markingscheme.pdf")

    if not os.path.exists(pdf_path):
        print("2023 marking scheme not found")
        return

    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        print(f"Total pages: {len(reader.pages)}")

        # Let's examine the first few pages to understand the structure
        for page_num in range(min(10, len(reader.pages))):
            page = reader.pages[page_num]
            text = page.extract_text()
            lines = text.split("\n")

            print(f"\n--- Page {page_num + 1} (first 15 lines) ---")
            for i, line in enumerate(lines[:15]):
                line_clean = line.strip()
                if line_clean:  # Only show non-empty lines
                    print(f"{i:2d}: {line_clean}")

            # Look specifically for any mention of "3" or "Q3" or similar
            relevant_lines = []
            for i, line in enumerate(lines):
                line_clean = line.strip().lower()
                if "3" in line_clean and any(
                    keyword in line_clean
                    for keyword in ["q", "question", "marks", "model", "solution"]
                ):
                    relevant_lines.append((i, line.strip()))

            if relevant_lines:
                print(f"\n*** Relevant lines on page {page_num + 1} ***")
                for line_num, line_text in relevant_lines:
                    print(f"  {line_num}: {line_text}")


if __name__ == "__main__":
    test_marking_scheme_patterns()
