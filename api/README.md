# LC Maths Question Search Web Application

A full-stack web application that allows you to search through Leaving Certificate Higher Level Mathematics papers using natural language queries. The application uses semantic search powered by sentence transformers to find relevant math questions and provides direct access to the original PDF papers.

## Features

- **Natural Language Search**: Search for math questions using plain English (e.g., "calculus and derivatives", "trigonometry problems")
- **Semantic Similarity**: Uses AI-powered sentence transformers to find contextually similar questions
- **PDF Viewer**: Click on search results to view the full paper in an embedded PDF viewer
- **Modern UI**: Clean, responsive design that works on desktop and mobile
- **Real-time Status**: Shows processing status as the system initializes
- **Paper Browser**: Browse all available papers by year

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Navigate to the application directory**:

   ```bash
   cd math-search-webapp
   ```

2. **Create a virtual environment** (recommended):

   ```bash
   python -m venv venv

   # On Windows:
   venv\Scripts\activate

   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Add PDF papers**:
   - Create a `data/papers` directory if it doesn't exist
   - Copy your PDF files to `data/papers/`
   - Files should be named in the format: `YYYY-paperN.pdf` (e.g., `2024-paper1.pdf`)

### Port Configuration

The application supports flexible port configuration through environment variables:

#### Method 1: Environment Variables (Recommended)

Set environment variables before running:

```bash
# Windows Command Prompt:
set FLASK_PORT=8080
set FLASK_HOST=0.0.0.0
set FLASK_DEBUG=False
python app.py

# Windows PowerShell:
$env:FLASK_PORT="8080"
$env:FLASK_HOST="0.0.0.0"
$env:FLASK_DEBUG="False"
python app.py

# macOS/Linux:
export FLASK_PORT=8080
export FLASK_HOST=0.0.0.0
export FLASK_DEBUG=False
python app.py
```

#### Method 2: Create a .env file

Create a `.env` file in the `math-search-webapp` directory:

```env
# Application Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=8080
FLASK_DEBUG=False

# For development:
# FLASK_DEBUG=True
# FLASK_PORT=3000
```

#### Available Configuration Options

- **FLASK_HOST**: Host to bind to (default: `0.0.0.0`)
- **FLASK_PORT**: Port to run on (default: `5000`)
- **FLASK_DEBUG**: Enable debug mode (default: `False`)

#### Common Port Configurations

```bash
# Default (port 5000):
python app.py

# Custom port 8080:
set FLASK_PORT=8080 && python app.py

# Development mode on port 3000:
set FLASK_PORT=3000 && set FLASK_DEBUG=True && python app.py

# Production on port 80 (requires admin privileges):
set FLASK_PORT=80 && python app.py
```

### Running the Application

1. **Start the Flask server**:

   ```bash
   python app.py
   ```

   Or with custom port:

   ```bash
   # Windows:
   set FLASK_PORT=8080 && python app.py

   # macOS/Linux:
   FLASK_PORT=8080 python app.py
   ```

2. **Open your web browser** and navigate to:

   ```
   http://localhost:5000
   ```

   (Or whatever port you configured)

3. **Wait for initialization**: The application will process all PDF papers and create search embeddings. This may take a few minutes on first run.

4. **Start searching**: Once ready, you can search for math questions using natural language!

## Alternative Startup Methods

### Using run.py

```bash
python run.py
```

### Using start.bat (Windows)

```bash
start.bat
```

### Using Docker

```bash
# Build and run with Docker Compose:
docker-compose up --build

# Run on custom port:
APP_PORT=8080 docker-compose up --build

# Background mode:
docker-compose up -d --build
```

## Usage

### Searching for Questions

1. Wait for the status bar to show "Ready"
2. Enter your search query in natural language, for example:

   - "calculus and derivatives"
   - "trigonometry problems"
   - "probability questions"
   - "integration by parts"
   - "complex numbers"

3. Select the number of results you want (5-20)
4. Click the search button or press Enter

### Viewing Papers

- Click "View Full Paper" on any search result to open the PDF
- Browse available papers in the "Available Papers" section
- Click on any paper card to view that paper directly

### Search Results

Each result shows:

- **Year and Paper**: Which exam paper the question is from
- **Question Number**: The question number within that paper
- **Similarity Score**: How closely the question matches your search (as a percentage)
- **Question Preview**: A preview of the question text
- **View Paper Button**: Opens the full PDF paper

## Technical Details

### Architecture

- **Backend**: Flask web server with REST API
- **Frontend**: Vanilla JavaScript with modern ES6+ features
- **Search Engine**: Sentence Transformers (all-MiniLM-L6-v2 model)
- **PDF Processing**: PyPDF2 for text extraction
- **Similarity**: Cosine similarity for semantic matching

### API Endpoints

- `GET /`: Main application page
- `GET /api/status`: Check processing status
- `POST /api/search`: Search for questions
- `GET /api/pdf/<year>/<paper>`: Serve PDF files
- `GET /api/papers`: List available papers

### File Structure

```
math-search-webapp/
├── app.py                 # Main Flask application
├── backend/
│   └── nlp.py            # NLP processing and search logic
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css     # Application styles
│   └── js/
│       └── app.js        # Frontend JavaScript
├── data/
│   └── papers/           # PDF files directory
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Docker configuration
├── Dockerfile           # Docker build instructions
└── README.md            # This file
```

## Troubleshooting

### Common Issues

1. **"Module not found" errors**: Make sure you've activated your virtual environment and installed all requirements

2. **PDF files not loading**: Ensure PDF files are in `data/papers/` and named correctly (`YYYY-paperN.pdf`)

3. **Search not working**: Wait for the status to show "Ready" - initial processing can take several minutes

4. **Port already in use**:

   ```bash
   # Try a different port:
   set FLASK_PORT=8080 && python app.py

   # Or check what's using the port:
   netstat -ano | findstr :5000
   ```

5. **Permission denied on port 80/443**: These ports require administrator privileges:
   ```bash
   # Run as administrator, then:
   set FLASK_PORT=80 && python app.py
   ```

### Performance Notes

- First startup takes longer as it processes all PDFs and creates embeddings
- Search performance improves after the initial processing
- More PDF files = longer initialization time
- The sentence transformer model downloads automatically on first use

### Environment Variables Reference

| Variable      | Default   | Description             |
| ------------- | --------- | ----------------------- |
| `FLASK_HOST`  | `0.0.0.0` | Host address to bind to |
| `FLASK_PORT`  | `5000`    | Port number to run on   |
| `FLASK_DEBUG` | `False`   | Enable Flask debug mode |

## Docker Deployment

For production deployment, see `DEPLOYMENT.md` for comprehensive Docker and auto-deployment instructions.

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is for educational purposes. Please ensure you have the right to use any PDF files you add to the system.
