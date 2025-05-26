import os
import PyPDF2
import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
import re


class MathPaperSearcher:
    def __init__(self, papers_dir: str = "data/papers"):
        self.papers_dir = papers_dir
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.embeddings = None
        self.questions = []
        self.metadata = []

    def extract_text_with_pages(self, pdf_path: str) -> List[Tuple[str, int]]:
        """Extract text from a PDF file with page numbers."""
        pages_text = []
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                pages_text.append((text, page_num))
        return pages_text

    def split_into_questions_with_pages(
        self, pages_text: List[Tuple[str, int]]
    ) -> List[Tuple[str, int]]:
        """Split text into individual questions with their page numbers."""
        all_questions = []

        # Combine all text but keep track of page boundaries
        full_text = ""
        page_boundaries = []
        current_pos = 0

        for text, page_num in pages_text:
            full_text += text + "\n"
            current_pos += len(text) + 1
            page_boundaries.append((current_pos, page_num))

        # Based on analysis, questions follow these patterns:
        # - "Question 1 (25 marks)" or "Question 1  (30 marks)"
        # - "1. (a)" or "2. (a)" for main questions
        # - Sometimes just "1." followed by content

        # First, try to split by "Question X" pattern (newer papers)
        question_pattern = r"(?=Question\s+\d+\s*\([^)]+\))"
        questions = re.split(question_pattern, full_text, flags=re.IGNORECASE)

        # If that doesn't work well, try the older pattern
        if len(questions) < 3:  # If we don't get enough questions
            # Split by numbered questions like "1. (a)" or "2. (a)"
            question_pattern = r"(?=^\d+\.\s*\([a-z]\)|\n\d+\.\s*\([a-z]\))"
            questions = re.split(question_pattern, full_text, flags=re.MULTILINE)

        # If still not enough, try even simpler pattern
        if len(questions) < 3:
            # Split by just numbers followed by period and content
            question_pattern = r"(?=^\d+\.\s+[A-Z]|\n\d+\.\s+[A-Z])"
            questions = re.split(question_pattern, full_text, flags=re.MULTILINE)

        # Clean up questions and find their page numbers
        cleaned_questions = []
        current_pos = 0

        for q in questions:
            q = q.strip()
            # Remove very short segments (likely headers/footers)
            if len(q) > 50:  # Only keep substantial content
                # Remove common header/footer patterns
                lines = q.split("\n")
                filtered_lines = []
                for line in lines:
                    line = line.strip()
                    # Skip common header/footer patterns
                    if not any(
                        pattern in line.lower()
                        for pattern in [
                            "leaving certificate",
                            "mathematics",
                            "paper 1",
                            "higher level",
                            "page",
                            "marks",
                            "examination",
                            "state examinations commission",
                            "coimisiún na scrúduithe stáit",
                            "for examiner",
                        ]
                    ):
                        filtered_lines.append(line)

                cleaned_q = "\n".join(filtered_lines).strip()
                if len(cleaned_q) > 30:  # Final length check
                    # Find the page number for this question
                    question_start_pos = full_text.find(q, current_pos)
                    page_num = self.find_page_for_position(
                        question_start_pos, page_boundaries
                    )
                    cleaned_questions.append((cleaned_q, page_num))
                    current_pos = question_start_pos + len(q)

        return cleaned_questions

    def find_page_for_position(
        self, position: int, page_boundaries: List[Tuple[int, int]]
    ) -> int:
        """Find which page a text position belongs to."""
        for boundary_pos, page_num in page_boundaries:
            if position < boundary_pos:
                return page_num
        return page_boundaries[-1][1] if page_boundaries else 1

    def calculate_keyword_score(self, query: str, question: str) -> float:
        """Calculate keyword matching score between query and question."""
        # Normalize both query and question text
        query_lower = query.lower()
        question_lower = question.lower()

        # Remove common mathematical symbols and normalize
        def normalize_text(text):
            # Replace common variations
            text = re.sub(r"['\u2019]", "'", text)  # Normalize apostrophes
            text = re.sub(r"\s+", " ", text)  # Normalize whitespace
            text = re.sub(
                r"[^\w\s']", " ", text
            )  # Remove special chars except apostrophes
            return text.strip()

        query_normalized = normalize_text(query_lower)
        question_normalized = normalize_text(question_lower)

        # Extract meaningful terms from query (remove common words)
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "about",
            "find",
            "calculate",
            "solve",
            "show",
            "prove",
            "question",
            "questions",
            "problem",
            "problems",
        }

        query_terms = [
            term
            for term in query_normalized.split()
            if term not in stop_words and len(term) > 2
        ]

        if not query_terms:
            return 0.0

        # Calculate different types of matches
        exact_phrase_match = 0.0
        exact_term_matches = 0
        partial_matches = 0

        # Check for exact phrase match
        if query_normalized in question_normalized:
            exact_phrase_match = 1.0

        # Check for exact term matches and partial matches
        for term in query_terms:
            if term in question_normalized:
                exact_term_matches += 1
            elif any(term in word for word in question_normalized.split()):
                partial_matches += 1

        # Calculate weighted score
        phrase_weight = 0.5  # Exact phrase match gets highest weight
        exact_weight = 0.3  # Exact term matches
        partial_weight = 0.1  # Partial matches

        exact_term_score = (exact_term_matches / len(query_terms)) * exact_weight
        partial_score = (partial_matches / len(query_terms)) * partial_weight
        phrase_score = exact_phrase_match * phrase_weight

        total_score = phrase_score + exact_term_score + partial_score
        return min(total_score, 1.0)  # Cap at 1.0

    def process_papers(self):
        """Process all papers and create search index."""
        all_questions = []
        all_metadata = []

        for filename in os.listdir(self.papers_dir):
            if filename.endswith(".pdf"):
                year = filename[:4]
                paper_num = filename[::-1][4:5]  # Extract paper number (1 or 2)
                print(
                    f"Processing {filename}... with year {year} and paper number {paper_num}"
                )

                pdf_path = os.path.join(self.papers_dir, filename)
                print(f"Processing {filename}...")
                pages_text = self.extract_text_with_pages(pdf_path)
                questions_with_pages = self.split_into_questions_with_pages(pages_text)

                for q_idx, (question, page_num) in enumerate(questions_with_pages, 1):
                    all_questions.append(question)
                    all_metadata.append(
                        {
                            "year": year,
                            "paper": paper_num,
                            "question_number": q_idx,
                            "filename": filename,
                            "page_number": page_num,
                        }
                    )

        print(f"Found {len(all_questions)} questions across all papers.")

        # Create embeddings
        print("Creating embeddings...")
        self.embeddings = self.model.encode(all_questions)
        self.questions = all_questions
        self.metadata = all_metadata

    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar questions using natural language query with enhanced ranking."""
        if self.embeddings is None:
            raise ValueError("Please process papers first using process_papers()")

        # Encode query for semantic similarity
        query_embedding = self.model.encode([query])

        # Calculate semantic similarities
        semantic_similarities = cosine_similarity(query_embedding, self.embeddings)[0]

        # Calculate keyword scores for all questions
        keyword_scores = []
        for question in self.questions:
            keyword_score = self.calculate_keyword_score(query, question)
            keyword_scores.append(keyword_score)

        keyword_scores = np.array(keyword_scores)

        # Combine semantic and keyword scores
        # Give more weight to keyword matches for exact term queries
        semantic_weight = 0.7
        keyword_weight = 0.3

        # If query contains specific mathematical terms, increase keyword weight
        math_terms = [
            "theorem",
            "formula",
            "rule",
            "law",
            "principle",
            "identity",
            "equation",
            "inequality",
        ]
        if any(term in query.lower() for term in math_terms):
            semantic_weight = 0.6
            keyword_weight = 0.4

        combined_scores = (semantic_weight * semantic_similarities) + (
            keyword_weight * keyword_scores
        )

        # Get top k results
        top_k_indices = np.argsort(combined_scores)[-k:][::-1]

        # Prepare results
        results = []
        for idx in top_k_indices:
            results.append(
                {
                    "question": self.questions[idx],
                    "metadata": self.metadata[idx],
                    "similarity_score": float(combined_scores[idx]),
                    "semantic_score": float(semantic_similarities[idx]),
                    "keyword_score": float(keyword_scores[idx]),
                }
            )

        return results


# Example usage
if __name__ == "__main__":
    searcher = MathPaperSearcher()
    print("Processing papers...")
    searcher.process_papers()

    # Example search
    query = "de moivre's theorem"
    results = searcher.search(query)

    print(f"\nResults for query: '{query}'\n")
    for i, result in enumerate(results, 1):
        print(f"Result {i}:")
        print(f"Year: {result['metadata']['year']}")
        print(f"Paper: {result['metadata']['paper']}")
        print(f"Page: {result['metadata']['page_number']}")
        print(f"Combined Score: {result['similarity_score']:.3f}")
        print(f"Semantic Score: {result['semantic_score']:.3f}")
        print(f"Keyword Score: {result['keyword_score']:.3f}")
        print(f"Question: {result['question'][:200]}...")  # Print first 200 chars
        print("-" * 80)
