import PyPDF2
import os


def find_question_3():
    pdf_path = os.path.join("api", "data", "markingscheme", "2023-markingscheme.pdf")

    if not os.path.exists(pdf_path):
        print("2023 marking scheme not found")
        return

    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        print(f"Total pages: {len(reader.pages)}")

        # Search for Q3 Model Solution pattern
        for page_num, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            lines = text.split("\n")

            for line_idx, line in enumerate(lines):
                line_clean = line.strip()
                line_lower = line_clean.lower()

                # Look for the specific pattern we saw: "Q3 Model Solution"
                if "q3 model solution" in line_lower:
                    print(f"\n*** FOUND Q3 on Page {page_num} ***")
                    print(f"Line {line_idx}: {line_clean}")

                    # Show some context around this line
                    print("\nContext:")
                    start_idx = max(0, line_idx - 2)
                    end_idx = min(len(lines), line_idx + 3)
                    for i in range(start_idx, end_idx):
                        marker = ">>> " if i == line_idx else "    "
                        print(f"{marker}{i:2d}: {lines[i].strip()}")

                    return page_num

        print("Q3 Model Solution not found")
        return None


if __name__ == "__main__":
    find_question_3()
