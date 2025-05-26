from nlp import MathPaperSearcher


def main():
    # Initialize the searcher
    searcher = MathPaperSearcher()

    print("Processing papers...")
    searcher.process_papers()

    while True:
        # Get search query from user
        query = input("\nEnter your search query (or 'quit' to exit): ")
        if query.lower() == "quit":
            break

        # Search for questions
        results = searcher.search(query)

        # Display results in descending order of similarity score
        print(f"\nResults for query: '{query}'\n")
        for i, result in enumerate(reversed(results), 1):
            print(f"Result {i}:")
            print(f"Year: {result['metadata']['year']}")
            print(f"Paper: {result['metadata']['paper']}")
            print(f"Question: {result['question'][:200]}...")  # Print first 200 chars
            print(f"Similarity Score: {result['similarity_score']:.2f}")
            print("-" * 80)


if __name__ == "__main__":
    main()
