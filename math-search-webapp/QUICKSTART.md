# Quick Start Guide

Get the LC Mathematics Search application running in under 5 minutes!

## 🚀 Fastest Setup

1. **Install dependencies**:

   ```bash
   cd math-search-webapp
   pip install -r requirements.txt
   ```

2. **Add your PDF papers** to `data/papers/` (format: `YYYY-paperN.pdf`)

3. **Run the application**:

   ```bash
   python app.py
   ```

4. **Open** http://localhost:5000

## 🔧 Custom Port Setup

### Option 1: Quick Command Line

```bash
# Windows:
set FLASK_PORT=8080 && python app.py

# macOS/Linux:
FLASK_PORT=8080 python app.py
```

### Option 2: Interactive Configuration

```bash
python configure.py
```

Follow the prompts to set your preferred port and settings.

### Option 3: Manual .env File

Create a `.env` file:

```env
FLASK_PORT=8080
FLASK_HOST=0.0.0.0
FLASK_DEBUG=False
```

## 🐳 Docker (Production)

```bash
# Default (port 8080):
docker-compose up --build

# Custom port:
APP_PORT=3000 docker-compose up --build
```

## 🎯 Common Configurations

| Use Case        | Command                                 |
| --------------- | --------------------------------------- |
| **Default**     | `python app.py`                         |
| **Port 8080**   | `set FLASK_PORT=8080 && python app.py`  |
| **Development** | `set FLASK_DEBUG=True && python app.py` |
| **Production**  | `docker-compose up -d --build`          |

## 🔍 Troubleshooting

- **Port 5000 busy?** → Use `FLASK_PORT=8080`
- **Permission denied?** → Try a port > 1024
- **Module errors?** → Activate virtual environment
- **No PDFs found?** → Check `data/papers/` directory

## 📚 Next Steps

- See `README.md` for detailed documentation
- See `DEPLOYMENT.md` for production deployment
- Run `python configure.py --show` to check current settings
