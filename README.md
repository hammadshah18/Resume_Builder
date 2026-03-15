# AI Resume Builder API

An intelligent FastAPI-based application that generates and builds professional resumes using Google's Generative AI (Gemini).

## Features

- **AI-Powered Resume Generation** - Uses Gemini 2.5 Flash LLM to create professional resumes
- **RESTful API** - Built with FastAPI for easy integration
- **Flexible Input** - Supports personal info, work experience, education, projects, and skills
- **Customizable Output** - Generates resumes tailored to different job descriptions

## Tech Stack

- **Framework**: FastAPI
- **LLM**: Google Generative AI (Gemini 2.5 Flash)
- **Data Validation**: Pydantic
- **Language**: Python 3.10

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Resume_build
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory:
```
GOOGLE_API_KEY=your_google_api_key_here
```

## Usage

Run the application:
```bash
python main.py
```

or with uvicorn:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

View the interactive API documentation at `http://localhost:8000/docs`

## API Endpoints

- `POST /resume/generate` - Generate a resume from user data
- `GET /docs` - Interactive API documentation

## Environment Variables

- `GOOGLE_API_KEY` - Your Google Generative AI API key (required)

## License

MIT
