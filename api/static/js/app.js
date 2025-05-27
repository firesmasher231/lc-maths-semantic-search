class MathSearchApp {
	constructor() {
		this.statusBar = document.getElementById("statusBar");
		this.statusIcon = document.getElementById("statusIcon");
		this.statusText = document.getElementById("statusText");
		this.searchSection = document.getElementById("searchSection");
		this.searchInput = document.getElementById("searchInput");
		this.searchBtn = document.getElementById("searchBtn");
		this.numResults = document.getElementById("numResults");
		this.resultsSection = document.getElementById("resultsSection");
		this.resultsHeader = document.getElementById("resultsHeader");
		this.resultsCount = document.getElementById("resultsCount");
		this.resultsContainer = document.getElementById("resultsContainer");
		this.papersGrid = document.getElementById("papersGrid");
		this.pdfModal = document.getElementById("pdfModal");
		this.pdfViewer = document.getElementById("pdfViewer");
		this.modalTitle = document.getElementById("modalTitle");
		this.closeModal = document.getElementById("closeModal");

		this.isReady = false;
		this.currentQuery = "";
		this.debugMode = false; // Set to true to show score breakdown

		// Context for current viewing session
		this.currentContext = {
			type: null, // 'question' or 'marking_scheme' or 'paper'
			year: null,
			paper: null,
			questionNumber: null,
			page: null,
		};

		this.init();
	}

	init() {
		this.setupEventListeners();
		this.checkStatus();
		this.loadAvailablePapers();

		// Initialize new modal elements
		this.modalSubtitle = document.getElementById("modalSubtitle");
		this.viewMarkingSchemeBtn = document.getElementById("viewMarkingSchemeBtn");
		this.backToQuestionBtn = document.getElementById("backToQuestionBtn");

		// Check status every 2 seconds until ready
		this.statusInterval = setInterval(() => {
			if (!this.isReady) {
				this.checkStatus();
			} else {
				clearInterval(this.statusInterval);
			}
		}, 2000);

		// Enable debug mode with Ctrl+Shift+D
		document.addEventListener("keydown", (e) => {
			if (e.ctrlKey && e.shiftKey && e.key === "D") {
				this.debugMode = !this.debugMode;
				console.log("Debug mode:", this.debugMode ? "ON" : "OFF");
				// Re-render results if they exist
				if (this.lastResults) {
					this.displayResults(this.lastResults);
				}
			}
		});

		// Escape key to close modal
		document.addEventListener("keydown", (e) => {
			if (e.key === "Escape" && this.pdfModal.style.display === "block") {
				this.closePdfModal();
			}
		});

		// New modal action buttons (added after elements are initialized)
		setTimeout(() => {
			if (this.viewMarkingSchemeBtn) {
				this.viewMarkingSchemeBtn.addEventListener("click", () =>
					this.openMarkingSchemeFromModal()
				);
			}
			if (this.backToQuestionBtn) {
				this.backToQuestionBtn.addEventListener("click", () =>
					this.backToQuestion()
				);
			}
		}, 100);
	}

	setupEventListeners() {
		// Search functionality
		this.searchBtn.addEventListener("click", () => this.performSearch());
		this.searchInput.addEventListener("keypress", (e) => {
			if (e.key === "Enter") {
				this.performSearch();
			}
		});

		// Modal functionality
		this.closeModal.addEventListener("click", () => this.closePdfModal());
		this.pdfModal.addEventListener("click", (e) => {
			if (e.target === this.pdfModal) {
				this.closePdfModal();
			}
		});
	}

	async checkStatus() {
		try {
			const response = await fetch("/api/status");
			const data = await response.json();

			this.updateStatusBar(data);

			if (data.ready && !this.isReady) {
				this.isReady = true;
				this.enableSearch();
			}
		} catch (error) {
			console.error("Error checking status:", error);
			this.updateStatusBar({
				is_processing: false,
				status: "Error connecting to server",
				ready: false,
			});
		}
	}

	updateStatusBar(data) {
		this.statusText.textContent = data.status;

		// Remove existing classes
		this.statusBar.classList.remove("ready", "error");

		if (data.ready) {
			this.statusIcon.className = "fas fa-check-circle";
			this.statusBar.classList.add("ready");
		} else if (data.status.includes("Error")) {
			this.statusIcon.className = "fas fa-exclamation-triangle";
			this.statusBar.classList.add("error");
		} else {
			this.statusIcon.className = "fas fa-spinner fa-spin";
		}
	}

	enableSearch() {
		this.searchSection.style.display = "block";
		this.searchBtn.disabled = false;
		this.searchInput.disabled = false;
	}

	async performSearch() {
		const query = this.searchInput.value.trim();
		if (!query) {
			alert("Please enter a search query");
			return;
		}

		this.currentQuery = query;
		this.searchBtn.disabled = true;
		this.searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

		try {
			const response = await fetch("/api/search", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({
					query: query,
					num_results: parseInt(this.numResults.value),
				}),
			});

			const data = await response.json();

			if (response.ok) {
				this.lastResults = data; // Store for debug mode
				this.displayResults(data);
			} else {
				this.showError(data.error || "Search failed");
			}
		} catch (error) {
			console.error("Search error:", error);
			this.showError("Network error occurred");
		} finally {
			this.searchBtn.disabled = false;
			this.searchBtn.innerHTML = '<i class="fas fa-search"></i>';
		}
	}

	displayResults(data) {
		this.resultsHeader.style.display = "block";
		this.resultsCount.textContent = `Found ${data.total_found} results for "${data.query}"`;

		if (data.results.length === 0) {
			this.resultsContainer.innerHTML =
				'<div class="no-results">No results found. Try a different search query.</div>';
			return;
		}

		this.resultsContainer.innerHTML = "";

		data.results.forEach((result, index) => {
			const resultElement = this.createResultElement(result, index + 1);
			this.resultsContainer.appendChild(resultElement);
		});

		// Scroll to results
		this.resultsSection.scrollIntoView({ behavior: "smooth" });
	}

	createResultElement(result, index) {
		const div = document.createElement("div");
		div.className = "result-item";

		const similarityPercentage = (result.similarity_score * 100).toFixed(1);
		const pageNumber = result.metadata.page_number || 1;

		// Create score display
		let scoreDisplay = `<i class="fas fa-percentage"></i> ${similarityPercentage}% match`;

		if (
			this.debugMode &&
			result.semantic_score !== undefined &&
			result.keyword_score !== undefined
		) {
			const semanticPercentage = (result.semantic_score * 100).toFixed(1);
			const keywordPercentage = (result.keyword_score * 100).toFixed(1);
			scoreDisplay = `
				<div style="font-size: 0.8rem;">
					<div><i class="fas fa-percentage"></i> ${similarityPercentage}% total</div>
					<div style="color: #666;">Semantic: ${semanticPercentage}%</div>
					<div style="color: #666;">Keyword: ${keywordPercentage}%</div>
				</div>
			`;
		}

		div.innerHTML = `
            <div class="result-header">
                <div class="result-meta">
                    <span class="meta-item">
                        <i class="fas fa-calendar"></i> ${result.metadata.year}
                    </span>
                    <span class="meta-item">
                        <i class="fas fa-file"></i> Paper ${
													result.metadata.paper
												}
                    </span>
                    <span class="meta-item">
                        <i class="fas fa-question-circle"></i> Question ${
													result.metadata.question_number
												}
                    </span>
                    <span class="meta-item">
                        <i class="fas fa-file-pdf"></i> Page ${pageNumber}
                    </span>
                </div>
                <span class="similarity-score">
                    ${scoreDisplay}
                </span>
            </div>
            <div class="result-content">
                <div class="result-question">${this.formatQuestion(
									result.question
								)}</div>
            </div>
            <button class="view-pdf-btn" onclick="app.openPdfWithQuestion('${
							result.metadata.year
						}', '${result.metadata.paper}', ${pageNumber}, ${
			result.metadata.question_number
		})">
                <i class="fas fa-external-link-alt"></i>
                Jump to Question (Page ${pageNumber})
            </button>
            <button class="view-marking-scheme-btn" onclick="app.openMarkingScheme('${
							result.metadata.year
						}', ${result.metadata.question_number})">
                <i class="fas fa-check-circle"></i>
                View Marking Scheme
            </button>
        `;

		return div;
	}

	formatQuestion(question) {
		// Basic formatting to make questions more readable
		return (
			question
				.replace(/\n\s*\n/g, "\n\n") // Normalize line breaks
				.replace(/^\s+|\s+$/g, "") // Trim whitespace
				.substring(0, 800) + (question.length > 800 ? "..." : "")
		); // Limit length
	}

	showError(message) {
		this.resultsHeader.style.display = "block";
		this.resultsCount.textContent = "Search Error";
		this.resultsContainer.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                ${message}
            </div>
        `;
	}

	async loadAvailablePapers() {
		try {
			const response = await fetch("/api/papers");
			const papers = await response.json();

			this.displayPapers(papers);
		} catch (error) {
			console.error("Error loading papers:", error);
			this.papersGrid.innerHTML =
				'<div class="error-message">Failed to load papers</div>';
		}
	}

	displayPapers(yearGroups) {
		if (yearGroups.length === 0) {
			this.papersGrid.innerHTML =
				'<div class="no-results">No papers available</div>';
			return;
		}

		this.papersGrid.innerHTML = "";

		yearGroups.forEach((yearData) => {
			const yearCard = document.createElement("div");
			yearCard.className = "year-card";

			// Create papers list
			const papersHtml = yearData.papers
				.map(
					(paper) =>
						`<div class="paper-item" onclick="app.openPdf('${yearData.year}', '${paper.paper}')">
					<i class="fas fa-file-pdf"></i>
					Paper ${paper.paper}
				</div>`
				)
				.join("");

			// Create marking scheme section if available
			const markingSchemeHtml = yearData.has_marking_scheme
				? `<div class="marking-scheme-item" onclick="app.openMarkingScheme('${yearData.year}')">
					<i class="fas fa-check-circle"></i>
					Marking Scheme
				</div>`
				: "";

			yearCard.innerHTML = `
				<div class="year-header">
					<div class="year-number">${yearData.year}</div>
				</div>
				<div class="year-content">
					${papersHtml}
					${markingSchemeHtml}
				</div>
			`;

			this.papersGrid.appendChild(yearCard);
		});
	}

	openPdf(year, paper, page = null) {
		let pdfUrl = `/api/pdf/${year}/${paper}`;
		let titleText = `${year} - Paper ${paper}`;

		if (page) {
			pdfUrl += `/${page}`;
			titleText += ` (Page ${page})`;
			// Add page fragment to URL for PDF viewer
			pdfUrl += "#page=" + page;
		}

		this.pdfViewer.src = pdfUrl;
		this.modalTitle.textContent = titleText;
		this.modalSubtitle.textContent = "";
		this.pdfModal.style.display = "block";
		document.body.style.overflow = "hidden"; // Prevent background scrolling

		// Hide action buttons for normal paper viewing
		this.viewMarkingSchemeBtn.style.display = "none";
		this.backToQuestionBtn.style.display = "none";

		// If page is specified, try to navigate to that page after a short delay
		if (page) {
			setTimeout(() => {
				// Try to scroll to the specific page using PDF.js viewer commands
				try {
					const iframe = this.pdfViewer;
					if (
						iframe.contentWindow &&
						iframe.contentWindow.PDFViewerApplication
					) {
						iframe.contentWindow.PDFViewerApplication.page = page;
					}
				} catch (e) {
					console.log("Could not navigate to specific page automatically");
				}
			}, 1000);
		}
	}

	openPdfWithQuestion(year, paper, page, questionNumber) {
		// Update context
		this.currentContext = {
			type: "question",
			year: year,
			paper: paper,
			questionNumber: questionNumber,
			page: page,
		};

		// Open the PDF
		this.openPdf(year, paper, page);

		// Update modal with question context
		this.modalTitle.textContent = `${year} - Paper ${paper}`;
		this.modalSubtitle.textContent = `Question ${questionNumber} (Page ${page})`;

		// Show marking scheme button
		this.viewMarkingSchemeBtn.style.display = "inline-flex";
		this.backToQuestionBtn.style.display = "none";
	}

	async openMarkingScheme(year, questionNumber = null) {
		// Update context for marking scheme viewing
		const previousContext = { ...this.currentContext };
		this.currentContext = {
			type: "marking_scheme",
			year: year,
			paper: previousContext.paper,
			questionNumber: questionNumber,
			page: null,
			previousContext: previousContext,
		};

		let titleText = `${year} - Marking Scheme`;
		let subtitleText = "";
		let pdfUrl = `/api/markingscheme/${year}`;

		// If we have a question number, try to find the specific page
		if (questionNumber) {
			subtitleText = `Finding solution for Question ${questionNumber}...`;
			this.modalTitle.textContent = titleText;
			this.modalSubtitle.textContent = subtitleText;
			this.modalSubtitle.classList.add("loading");
			this.pdfModal.style.display = "block";
			document.body.style.overflow = "hidden";

			try {
				const response = await fetch(
					`/api/markingscheme/${year}/question/${questionNumber}`
				);
				const data = await response.json();

				if (response.ok && data.found) {
					// Found the question, navigate to the specific page
					pdfUrl = `/api/markingscheme/${year}/${data.page}#page=${data.page}`;
					subtitleText = `Solution for Question ${questionNumber} (Page ${data.page})`;
					this.currentContext.page = data.page;
				} else {
					// Question not found, show message but still open marking scheme
					subtitleText =
						data.message ||
						`Question ${questionNumber} not found, showing full marking scheme`;
				}
			} catch (error) {
				console.error("Error finding question in marking scheme:", error);
				subtitleText = `Error finding Question ${questionNumber}, showing full marking scheme`;
			}

			// Remove loading state
			this.modalSubtitle.classList.remove("loading");
		}

		// Load the PDF
		this.pdfViewer.src = pdfUrl;
		this.modalTitle.textContent = titleText;
		this.modalSubtitle.textContent = subtitleText;
		this.pdfModal.style.display = "block";
		document.body.style.overflow = "hidden";

		// Show back button if we came from a question
		if (questionNumber && previousContext.type === "question") {
			this.backToQuestionBtn.style.display = "inline-flex";
			this.viewMarkingSchemeBtn.style.display = "none";
		} else {
			this.backToQuestionBtn.style.display = "none";
			this.viewMarkingSchemeBtn.style.display = "none";
		}

		// Try to navigate to the specific page after PDF loads
		if (questionNumber && this.currentContext.page) {
			setTimeout(() => {
				try {
					const iframe = this.pdfViewer;
					if (
						iframe.contentWindow &&
						iframe.contentWindow.PDFViewerApplication
					) {
						iframe.contentWindow.PDFViewerApplication.page =
							this.currentContext.page;
					}
				} catch (e) {
					console.log("Could not navigate to specific page automatically");
				}
			}, 1500); // Give more time for marking scheme to load
		}
	}

	openMarkingSchemeFromModal() {
		if (this.currentContext.type === "question") {
			this.openMarkingScheme(
				this.currentContext.year,
				this.currentContext.questionNumber
			);
		}
	}

	backToQuestion() {
		if (
			this.currentContext.previousContext &&
			this.currentContext.previousContext.type === "question"
		) {
			const prev = this.currentContext.previousContext;
			this.openPdfWithQuestion(
				prev.year,
				prev.paper,
				prev.page,
				prev.questionNumber
			);
		}
	}

	closePdfModal() {
		this.pdfModal.style.display = "none";
		this.pdfViewer.src = "";
		document.body.style.overflow = "auto"; // Restore scrolling

		// Reset context
		this.currentContext = {
			type: null,
			year: null,
			paper: null,
			questionNumber: null,
			page: null,
		};
	}
}

// Initialize the app when the page loads
let app;
document.addEventListener("DOMContentLoaded", () => {
	app = new MathSearchApp();
});

// Make app globally available for onclick handlers
window.app = app;
