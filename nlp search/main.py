import json

# read data.json file
with open("J:/Projects/lc-maths-semantic-search/data.json", "r") as f:
    data = json.load(f)

maths_data = data["lc"]["Mathematics"]

# Store all HL maths papers with year data
hl_maths_by_year = {}

# Iterate through each year
for year, papers in maths_data.items():
    print(f"\nYear: {year}")
    print("-" * 50)

    # Group papers by type for this year
    papers_by_type = {}
    for paper in papers:
        paper_type = paper["type"]

        if paper_type not in papers_by_type:
            papers_by_type[paper_type] = []

        if (
            "Higher Level" in paper["details"]
            and paper["url"][::-1][0:6][::-1] == "EV.pdf"
        ):
            papers_by_type[paper_type].append(paper)

    # Print papers grouped by type and store for this year
    if papers_by_type:  # Only add year if there are HL papers
        hl_maths_by_year[year] = papers_by_type
        
        for paper_type, type_papers in papers_by_type.items():
            print(f"\n{paper_type}:")
            for paper in type_papers:
                print(f"  - {paper['details']} ({paper['url']})")

# Save all HL maths papers with year structure
with open("J:/Projects/lc-maths-semantic-search/hl-maths-data.json", "w") as f:
    json.dump(hl_maths_by_year, f, indent=2)
