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

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from a PDF file."""
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text

    def split_into_questions(self, text: str) -> List[str]:
        """Split text into individual questions."""
        # Based on analysis, questions follow these patterns:
        # - "Question 1 (25 marks)" or "Question 1  (30 marks)"
        # - "1. (a)" or "2. (a)" for main questions
        # - Sometimes just "1." followed by content

        # First, try to split by "Question X" pattern (newer papers)
        question_pattern = r"(?=Question\s+\d+\s*\([^)]+\))"
        questions = re.split(question_pattern, text, flags=re.IGNORECASE)

        # If that doesn't work well, try the older pattern
        if len(questions) < 3:  # If we don't get enough questions
            # Split by numbered questions like "1. (a)" or "2. (a)"
            question_pattern = r"(?=^\d+\.\s*\([a-z]\)|\n\d+\.\s*\([a-z]\))"
            questions = re.split(question_pattern, text, flags=re.MULTILINE)

        # If still not enough, try even simpler pattern
        if len(questions) < 3:
            # Split by just numbers followed by period and content
            question_pattern = r"(?=^\d+\.\s+[A-Z]|\n\d+\.\s+[A-Z])"
            questions = re.split(question_pattern, text, flags=re.MULTILINE)

        # Clean up questions
        cleaned_questions = []
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
                    cleaned_questions.append(cleaned_q)

        return cleaned_questions

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
                text = self.extract_text_from_pdf(pdf_path)
                questions = self.split_into_questions(text)

                for q_idx, question in enumerate(questions, 1):
                    all_questions.append(question)
                    all_metadata.append(
                        {
                            "year": year,
                            "paper": paper_num,
                            "question_number": q_idx,
                            "filename": filename,
                        }
                    )

        print(f"Found {len(all_questions)} questions across all papers.")

        # Create embeddings
        print("Creating embeddings...")
        self.embeddings = self.model.encode(all_questions)
        self.questions = all_questions
        self.metadata = all_metadata

    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar questions using natural language query."""
        if self.embeddings is None:
            raise ValueError("Please process papers first using process_papers()")

        # Encode query
        query_embedding = self.model.encode([query])

        # Calculate similarities
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]

        # Get top k results
        top_k_indices = np.argsort(similarities)[-k:][::-1]

        # Prepare results
        results = []
        for idx in top_k_indices:
            results.append(
                {
                    "question": self.questions[idx],
                    "metadata": self.metadata[idx],
                    "similarity_score": float(similarities[idx]),
                }
            )

        return results


# Example usage
if __name__ == "__main__":
    searcher = MathPaperSearcher()
    print("Processing papers...")
    searcher.process_papers()

    # Example search
    query = "Find questions about calculus and derivatives"
    results = searcher.search(query)

    print(f"\nResults for query: '{query}'\n")
    for i, result in enumerate(results, 1):
        print(f"Result {i}:")
        print(f"Year: {result['metadata']['year']}")
        print(f"Paper: {result['metadata']['paper']}")
        print(f"Question: {result['question'][:200]}...")  # Print first 200 chars
        print(f"Similarity Score: {result['similarity_score']:.2f}")
        print("-" * 80)
