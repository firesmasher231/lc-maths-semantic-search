import PyPDF2
import os
import json


def test_find_marking_scheme_page(year, question_number):
    """Test the marking scheme search function directly."""
    filename = f"{year}-markingscheme.pdf"
    pdf_path = os.path.join("data", "markingscheme", filename)

    if not os.path.exists(pdf_path):
        return {"error": "Marking scheme not found"}

    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)

            # Search through pages for the question
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                text_lower = text.lower()

                # Enhanced patterns for both old and new marking scheme formats
                patterns_to_check = [
                    # Old format patterns
                    f"question {question_number}",
                    f"question{question_number}",
                    # New format patterns (like Q3, Q.3, etc.)
                    f"q{question_number}",
                    f"q.{question_number}",
                    f"q {question_number}",
                    # Standalone number patterns
                    f"{question_number}.",
                    f"({question_number})",
                    f"[{question_number}]",
                    # Model solution patterns (newer format) - UPDATED FOR NEW FORMAT
                    f"q{question_number} model solution",
                    f"q{question_number} model solution –",
                    f"q{question_number} model solution -",
                    f"model solution – {question_number}",
                    f"model solution - {question_number}",
                    f"solution {question_number}",
                ]

                # Check each line for question markers
                lines = text.split("\n")
                for line_idx, line in enumerate(lines):
                    line_clean = line.strip()
                    line_lower = line_clean.lower()

                    # Skip very short lines or lines that are clearly headers/footers
                    if len(line_clean) < 2:
                        continue

                    # Check for patterns
                    for pattern in patterns_to_check:
                        if pattern in line_lower:
                            # Additional validation based on context
                            is_valid_match = False

                            # For newer format: Look for "Q3 Model Solution" pattern
                            if f"q{question_number} model solution" in line_lower:
                                is_valid_match = True
                                print(
                                    f"Found pattern: 'q{question_number} model solution' in line: {line_clean}"
                                )

                            # For newer format: Look for "Q3" at start of line or in table format
                            elif f"q{question_number}" in line_lower:
                                if (
                                    line_lower.startswith(f"q{question_number}")
                                    or line_lower.startswith(f"q.{question_number}")
                                    or line_lower.startswith(f"q {question_number}")
                                ):
                                    is_valid_match = True
                                # Also check if it's in a table-like format (common in newer schemes)
                                elif any(
                                    word in line_lower
                                    for word in ["marks", "model", "solution", "scale"]
                                ):
                                    is_valid_match = True

                            # For older format: Look for "Question X" patterns
                            elif f"question {question_number}" in line_lower:
                                if (
                                    line_lower.startswith(f"question {question_number}")
                                    or f"question {question_number}" in line_lower
                                ):
                                    is_valid_match = True

                            # For standalone numbers: Be more careful
                            elif f"{question_number}." in line_lower:
                                # Make sure it's at the start of line or after whitespace
                                if (
                                    line_lower.startswith(f"{question_number}.")
                                    or f" {question_number}." in line_lower
                                    or f"\t{question_number}." in line_lower
                                ):
                                    # Additional check: make sure it's not just a page number or mark
                                    if not any(
                                        word in line_lower
                                        for word in ["page", "total", "marks only"]
                                    ):
                                        is_valid_match = True

                            # For model solution patterns
                            elif (
                                "model solution" in line_lower
                                and str(question_number) in line_lower
                            ):
                                is_valid_match = True

                            if is_valid_match:
                                return {
                                    "page": page_num,
                                    "found": True,
                                    "year": year,
                                    "question_number": question_number,
                                    "matched_text": line_clean[:100],  # For debugging
                                }

        # If not found, return the first page as fallback
        return {
            "page": 1,
            "found": False,
            "year": year,
            "question_number": question_number,
            "message": f"Question {question_number} not found, showing first page",
        }

    except Exception as e:
        return {"error": f"Error processing marking scheme: {str(e)}"}


if __name__ == "__main__":
    # Test with Question 3 from 2023
    result = test_find_marking_scheme_page("2023", 3)
    print("Result:", json.dumps(result, indent=2))
