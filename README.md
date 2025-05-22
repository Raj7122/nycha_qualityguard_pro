# NYCHA QualityGuard Pro

A professional-grade backend system for NYCHA complaint analysis and quality monitoring.

## Project Structure

```
Nychaguard/
├── backend/
│   ├── app.py                 # Main application entry point
│   ├── config/               # Configuration management
│   │   ├── __init__.py
│   │   └── development.py    # Development settings
│   ├── api/                  # API routes and controllers
│   │   ├── __init__.py
│   │   ├── routes/          # Route definitions
│   │   └── schemas/         # Request/Response schemas
│   ├── services/            # Business logic layer
│   │   ├── __init__.py
│   │   ├── ai/             # AI-related services
│   │   └── complaint/      # Complaint handling services
│   ├── agents/             # Agent definitions
│   │   └── __init__.py
│   ├── mcp/                # MCP tool definitions
│   │   ├── __init__.py
│   │   ├── tools/          # Tool implementations
│   │   └── schemas/        # Tool schemas
│   ├── utils/              # Utility functions
│   │   └── __init__.py
│   ├── models/             # Data models
│   │   └── __init__.py
│   └── tests/              # Test suite
│       ├── __init__.py
│       ├── test_api/       # API tests
│       ├── test_services/  # Service tests
│       └── test_agents/    # Agent tests
├── .env.example            # Example environment variables
├── .gitignore             # Git ignore file
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Nychaguard.git
cd Nychaguard
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the development server:
```bash
cd backend
python app.py
```

## API Endpoints

- `GET /`: Health check endpoint
- `GET /api/test`: Test endpoint

## Development

- The application uses Flask for the backend
- Configuration is managed through the `config` directory
- Environment variables are loaded from `.env` file

## Testing

Run tests using pytest:
```bash
pytest
```

## License

[Your chosen license] 