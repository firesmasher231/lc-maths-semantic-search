import PyPDF2
import os


def analyze_2011_marking_scheme():
    pdf_path = os.path.join("data", "markingscheme", "2011-markingscheme.pdf")

    if not os.path.exists(pdf_path):
        print("2011 marking scheme not found")
        return

    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        print(f"Total pages: {len(reader.pages)}")

        question_number = 6

        # Search for Question 6 patterns and analyze context
        for page_num, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            lines = text.split("\n")

            found_q6 = False
            q6_lines = []

            for line_idx, line in enumerate(lines):
                line_clean = line.strip()
                line_lower = line_clean.lower()

                # Look for Question 6 mentions
                if any(
                    pattern in line_lower
                    for pattern in ["question 6", "q6", "q.6", "q 6"]
                ):
                    found_q6 = True
                    q6_lines.append((line_idx, line_clean))

            if found_q6:
                print(f"\n--- Page {page_num} ---")

                # Show context around Q6 mentions
                for line_idx, line_text in q6_lines:
                    print(f"Line {line_idx}: {line_text}")

                # Analyze the content type of this page
                full_text_lower = text.lower()

                # Check if this looks like an instructions/summary page
                is_instructions = any(
                    keyword in full_text_lower
                    for keyword in [
                        "instructions",
                        "answer questions as follows",
                        "section a",
                        "section b",
                        "answer all",
                        "answer both",
                        "answer any",
                    ]
                )

                # Check if this looks like actual solution content
                has_math_content = any(
                    keyword in full_text_lower
                    for keyword in [
                        "solution",
                        "method",
                        "scale",
                        "marks",
                        "partial credit",
                        "correct",
                        "incorrect",
                        "=",
                        "+",
                        "-",
                        "×",
                        "÷",
                    ]
                )

                # Count mathematical symbols and solution indicators
                math_symbols = sum(1 for char in text if char in "=+-×÷∫∑√")
                solution_words = sum(
                    1
                    for word in ["solution", "method", "scale", "marks", "credit"]
                    if word in full_text_lower
                )

                print(f"  Page type analysis:")
                print(f"    Instructions page: {is_instructions}")
                print(f"    Has math content: {has_math_content}")
                print(f"    Math symbols count: {math_symbols}")
                print(f"    Solution words count: {solution_words}")

                # Show first few lines to understand page structure
                print(f"  First 5 lines:")
                for i, line in enumerate(lines[:5]):
                    if line.strip():
                        print(f"    {i}: {line.strip()}")


if __name__ == "__main__":
    analyze_2011_marking_scheme()
