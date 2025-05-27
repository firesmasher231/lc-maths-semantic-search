from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import sys

# Add the current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from backend.nlp import MathPaperSearcher
import threading
import time

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # python-dotenv not installed, continue without it
    pass

app = Flask(__name__)
CORS(app)

# Global searcher instance
searcher = None
is_processing = False
processing_status = "Not started"


def initialize_searcher():
    """Initialize the searcher in a background thread."""
    global searcher, is_processing, processing_status

    is_processing = True
    processing_status = "Initializing model..."

    try:
        searcher = MathPaperSearcher()
        processing_status = "Processing papers..."
        searcher.process_papers()
        processing_status = "Ready"
        is_processing = False
        print("Searcher initialized successfully!")
    except Exception as e:
        processing_status = f"Error: {str(e)}"
        is_processing = False
        print(f"Error initializing searcher: {e}")


@app.route("/")
def index():
    """Serve the main page."""
    return render_template("index.html")


@app.route("/api/status")
def get_status():
    """Get the current processing status."""
    return jsonify(
        {
            "is_processing": is_processing,
            "status": processing_status,
            "ready": searcher is not None and not is_processing,
        }
    )


@app.route("/api/search", methods=["POST"])
def search():
    """Search for math questions."""
    global searcher

    if searcher is None or is_processing:
        return (
            jsonify(
                {
                    "error": "Searcher not ready yet. Please wait for initialization to complete.",
                    "status": processing_status,
                }
            ),
            503,
        )

    data = request.get_json()
    query = data.get("query", "")
    num_results = data.get("num_results", 5)

    if not query:
        return jsonify({"error": "Query is required"}), 400

    try:
        results = searcher.search(query, k=num_results)
        return jsonify(
            {"query": query, "results": results, "total_found": len(results)}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/pdf/<year>/<paper>")
@app.route("/api/pdf/<year>/<paper>/<int:page>")
def get_pdf(year, paper, page=None):
    """Serve PDF files with optional page parameter."""
    filename = f"{year}-paper{paper}.pdf"
    pdf_path = os.path.join("data", "papers", filename)

    if os.path.exists(pdf_path):
        # If page is specified, add it as a URL fragment
        response = send_file(pdf_path, as_attachment=False, mimetype="application/pdf")
        if page:
            # Add page information to response headers for frontend to use
            response.headers["X-PDF-Page"] = str(page)
        return response
    else:
        return jsonify({"error": "PDF not found"}), 404


@app.route("/api/markingscheme/<year>")
@app.route("/api/markingscheme/<year>/<int:page>")
def get_marking_scheme(year, page=None):
    """Serve marking scheme PDF files with optional page parameter."""
    filename = f"{year}-markingscheme.pdf"
    pdf_path = os.path.join("data", "markingscheme", filename)

    if os.path.exists(pdf_path):
        # If page is specified, add it as a URL fragment
        response = send_file(pdf_path, as_attachment=False, mimetype="application/pdf")
        if page:
            # Add page information to response headers for frontend to use
            response.headers["X-PDF-Page"] = str(page)
        return response
    else:
        return jsonify({"error": "Marking scheme not found"}), 404


@app.route("/api/markingscheme/<year>/question/<int:question_number>")
def find_marking_scheme_page(year, question_number):
    """Find the page number for a specific question in the marking scheme."""
    filename = f"{year}-markingscheme.pdf"
    pdf_path = os.path.join("data", "markingscheme", filename)

    if not os.path.exists(pdf_path):
        return jsonify({"error": "Marking scheme not found"}), 404

    try:
        # Import PyPDF2 for PDF processing
        import PyPDF2

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

                                # Prioritize actual solution pages over instruction pages
                                if (
                                    is_instructions_page
                                    and not has_solution_content
                                    and math_symbols < 5
                                ):
                                    # This looks like an instructions page, continue searching
                                    continue

                                return jsonify(
                                    {
                                        "page": page_num,
                                        "found": True,
                                        "year": year,
                                        "question_number": question_number,
                                        "matched_text": line_clean[
                                            :100
                                        ],  # For debugging
                                        "content_type": (
                                            "solution"
                                            if has_solution_content
                                            else "summary"
                                        ),
                                    }
                                )

        # If not found, return the first page as fallback
        return jsonify(
            {
                "page": 1,
                "found": False,
                "year": year,
                "question_number": question_number,
                "message": f"Question {question_number} not found, showing first page",
            }
        )

    except Exception as e:
        return jsonify({"error": f"Error processing marking scheme: {str(e)}"}), 500


@app.route("/api/papers")
def get_available_papers():
    """Get list of available papers grouped by year with marking scheme info."""
    papers_dir = os.path.join("data", "papers")
    markingscheme_dir = os.path.join("data", "markingscheme")

    papers_by_year = {}

    # Get all papers
    if os.path.exists(papers_dir):
        for filename in os.listdir(papers_dir):
            if filename.endswith(".pdf"):
                year = filename[:4]
                paper = filename.split("-paper")[1].split(".")[0]

                if year not in papers_by_year:
                    papers_by_year[year] = {
                        "year": year,
                        "papers": [],
                        "has_marking_scheme": False,
                    }

                papers_by_year[year]["papers"].append(
                    {"paper": paper, "filename": filename}
                )

    # Check for marking schemes
    if os.path.exists(markingscheme_dir):
        for filename in os.listdir(markingscheme_dir):
            if filename.endswith(".pdf") and "markingscheme" in filename:
                year = filename[:4]
                if year in papers_by_year:
                    papers_by_year[year]["has_marking_scheme"] = True

    # Convert to list and sort
    result = list(papers_by_year.values())

    # Sort papers within each year
    for year_data in result:
        year_data["papers"].sort(key=lambda x: int(x["paper"]))

    # Sort years (most recent first)
    result.sort(key=lambda x: int(x["year"]), reverse=True)

    return jsonify(result)


@app.route("/api/debug")
def debug_info():
    """Debug information for deployment troubleshooting."""
    import sys

    return jsonify(
        {
            "current_working_directory": os.getcwd(),
            "python_path": sys.path,
            "backend_module_location": getattr(
                __import__("backend.nlp", fromlist=["MathPaperSearcher"]),
                "__file__",
                "Not found",
            ),
            "data_directory_exists": os.path.exists("data"),
            "papers_directory_exists": os.path.exists("data/papers"),
            "backend_directory_exists": os.path.exists("backend"),
        }
    )


if __name__ == "__main__":
    # Start initialization in background
    init_thread = threading.Thread(target=initialize_searcher)
    init_thread.daemon = True
    init_thread.start()

    # Get configuration from environment variables
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"

    print(f"🚀 Starting LC Mathematics Search on {host}:{port}")
    print(f"📊 Debug mode: {debug}")
    print(f"📁 Papers directory: {os.path.join('data', 'papers')}")

    # Run the Flask app
    app.run(debug=debug, host=host, port=port)
