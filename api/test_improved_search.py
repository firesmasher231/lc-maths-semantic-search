import PyPDF2
import os
import json
import requests


def test_improved_search(year, question_number):
    """Test the improved marking scheme search function."""
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
                    # Model solution patterns (newer format)
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

                    # Skip very short lines
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

                            # For newer format: Look for "Q3" at start of line or in table format
                            elif f"q{question_number}" in line_lower:
                                if (
                                    line_lower.startswith(f"q{question_number}")
                                    or line_lower.startswith(f"q.{question_number}")
                                    or line_lower.startswith(f"q {question_number}")
                                ):
                                    is_valid_match = True
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
                                if (
                                    line_lower.startswith(f"{question_number}.")
                                    or f" {question_number}." in line_lower
                                    or f"\t{question_number}." in line_lower
                                ):
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
                                # ENHANCED: Check if this is likely an instructions/summary page
                                full_text_lower = text.lower()

                                # Check if this looks like an instructions/summary page
                                is_instructions_page = any(
                                    keyword in full_text_lower
                                    for keyword in [
                                        "instructions",
                                        "answer questions as follows",
                                        "section a",
                                        "section b",
                                        "answer all",
                                        "answer both",
                                        "answer any",
                                        "there are three sections",
                                        "write your answers in the spaces provided",
                                    ]
                                )

                                # Check if this looks like actual solution content
                                has_solution_content = any(
                                    keyword in full_text_lower
                                    for keyword in [
                                        "method",
                                        "scale",
                                        "partial credit",
                                        "correct",
                                        "incorrect",
                                        "low partial credit",
                                        "high partial credit",
                                        "marking notes",
                                    ]
                                )

                                # Count mathematical symbols and solution indicators
                                math_symbols = sum(
                                    1 for char in text if char in "=+-×÷∫∑√"
                                )
                                solution_words = sum(
                                    1
                                    for word in [
                                        "method",
                                        "scale",
                                        "marks",
                                        "credit",
                                        "solution",
                                    ]
                                    if word in full_text_lower
                                )

                                print(
                                    f"Page {page_num}: Found '{pattern}' in line: {line_clean}"
                                )
                                print(f"  Instructions page: {is_instructions_page}")
                                print(f"  Has solution content: {has_solution_content}")
                                print(f"  Math symbols: {math_symbols}")
                                print(f"  Solution words: {solution_words}")

                                # Prioritize actual solution pages over instruction pages
                                if (
                                    is_instructions_page
                                    and not has_solution_content
                                    and math_symbols < 5
                                ):
                                    print(f"  -> Skipping instructions page")
                                    continue

                                print(f"  -> MATCH! Using page {page_num}")
                                return {
                                    "page": page_num,
                                    "found": True,
                                    "year": year,
                                    "question_number": question_number,
                                    "matched_text": line_clean[:100],
                                    "content_type": (
                                        "solution"
                                        if has_solution_content
                                        else "summary"
                                    ),
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


def test_improved_marking_scheme_logic():
    """Test the improved marking scheme finding logic"""

    # Test cases - these should now find the actual solution pages
    test_cases = [
        {
            "year": "2023",
            "question": 3,
            "expected_page_range": (10, 15),
        },  # Should find page 12
        {
            "year": "2023",
            "question": 1,
            "expected_page_range": (6, 10),
        },  # Should find around page 7
        {
            "year": "2023",
            "question": 2,
            "expected_page_range": (9, 12),
        },  # Should find around page 10
        {
            "year": "2022",
            "question": 3,
            "expected_page_range": (8, 15),
        },  # Test another year
        {
            "year": "2000",
            "question": 1,
            "should_fail": True,
        },  # Should fail for year 2000
    ]

    base_url = "http://localhost:5000"

    print("Testing improved marking scheme logic...")
    print("=" * 60)

    for i, test_case in enumerate(test_cases, 1):
        year = test_case["year"]
        question = test_case["question"]

        print(f"\nTest {i}: Year {year}, Question {question}")
        print("-" * 40)

        try:
            url = f"{base_url}/api/markingscheme/{year}/question/{question}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                page = data.get("page")
                found = data.get("found")
                content_type = data.get("content_type", "unknown")
                matched_text = data.get("matched_text", "")

                print(f"✓ Found: {found}")
                print(f"✓ Page: {page}")
                print(f"✓ Content Type: {content_type}")
                print(f"✓ Matched Text: {matched_text[:80]}...")

                # Check if it's in expected range
                if "expected_page_range" in test_case:
                    min_page, max_page = test_case["expected_page_range"]
                    if min_page <= page <= max_page:
                        print(
                            f"✓ Page {page} is in expected range ({min_page}-{max_page})"
                        )
                    else:
                        print(
                            f"⚠ Page {page} is outside expected range ({min_page}-{max_page})"
                        )

                # Check content type
                if content_type == "solution":
                    print("✓ Correctly identified as solution page")
                elif content_type == "summary":
                    print("⚠ Found summary page instead of solution")

            elif response.status_code == 404:
                data = response.json()
                error = data.get("error", "")

                if "should_fail" in test_case and test_case["should_fail"]:
                    print(f"✓ Expected failure: {error}")
                else:
                    print(f"✗ Unexpected 404: {error}")

            else:
                print(f"✗ HTTP {response.status_code}: {response.text}")

        except requests.exceptions.ConnectionError:
            print("✗ Connection failed - is the server running?")
            print("  Start server with: python start.py")
            break
        except Exception as e:
            print(f"✗ Error: {e}")

    print("\n" + "=" * 60)
    print("Test completed!")
    print("\nTo start the server if not running:")
    print("  python start.py")


if __name__ == "__main__":
    # Test with both 2023 (new format) and 2011 (old format)
    print("=== Testing 2023 Question 3 ===")
    result_2023 = test_improved_search("2023", 3)
    print("Result:", json.dumps(result_2023, indent=2))

    print("\n=== Testing 2011 Question 6 ===")
    result_2011 = test_improved_search("2011", 6)
    print("Result:", json.dumps(result_2011, indent=2))

    test_improved_marking_scheme_logic()
