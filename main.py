import os
import json
import re
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

load_dotenv()

app = FastAPI(title="AI Resume Builder API")

# ================= LLM =================

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.6,
    api_key=os.getenv("GOOGLE_API_KEY")
)

# ================= DATA MODELS =================

class PersonalInfo(BaseModel):
    name: str
    email: str
    phone: str
    linkedin: Optional[str] = None
    github: Optional[str] = None

class Project(BaseModel):
    name: str
    description: str
    technologies: Optional[List[str]] = None
    link: Optional[str] = None

class Experience(BaseModel):
    company: str
    role: str
    duration: str
    description: str

class Education(BaseModel):
    institute: str
    degree: str
    year: str

class ResumeRequest(BaseModel):
    personal_info: PersonalInfo
    target_role: str
    skills: List[str]
    projects: List[Project]
    experience: List[Experience]
    education: List[Education]
    job_description: Optional[str] = None
    regenerate: Optional[bool] = False

class ImproveRequest(BaseModel):
    section: str
    content: str
    target_role: str
    job_description: Optional[str] = None

class KeywordRequest(BaseModel):
    job_description: str

# ================= JSON CLEANER =================

def clean_llm_json(output: str):
    """
    Remove markdown fences and parse JSON safely.
    """
    try:
        cleaned = re.sub(r"```json|```", "", output, flags=re.IGNORECASE).strip()
        return json.loads(cleaned)
    except Exception:
        return {"error": "Model returned non-JSON output", "raw_output": output}

# ================= PROMPTS =================

resume_prompt = PromptTemplate.from_template("""
You are an expert ATS resume writer.

Convert the user's raw information into a highly optimized ATS-friendly resume.

Rules:
- Use strong action verbs
- Use bullet points
- Focus on measurable impact
- Optimize for the target role
- Include relevant ATS keywords
- Avoid generic wording
- Make each bullet point unique

If regenerate=True, create a noticeably different and more optimized version.

Return ONLY valid JSON in this format:

{{
"summary": "",
"skills": [],
"experience": [
 {{ "role":"", "company":"", "points":[] }}
],
"projects":[
 {{ "name":"", "points":[] }}
],
"education":[]
}}

User Data + Keywords:
{data}
""")

improve_prompt = PromptTemplate.from_template("""
You are an ATS resume optimization expert.

Improve the following resume section to be more ATS optimized.

Rules:
- Use strong action verbs
- Increase impact
- Add relevant keywords
- Make bullet points concise
- Improve clarity

Target Role:
{role}

Job Description:
{job}

Original Content:
{content}

Return improved bullet points only.
""")

keyword_prompt = PromptTemplate.from_template("""
Extract the most important ATS keywords from this job description.

Rules:
- Extract technical skills
- Extract tools
- Extract frameworks
- Extract role-related keywords

Return JSON format:
{{ "keywords":[] }}

Job Description:
{job}
""")

# ================= LANDING =================

@app.get("/")
async def landing_page():
    return {
        "message": "Welcome to AI Resume Builder API",
        "description": "Generate ATS-optimized resume content using AI",
        "available_endpoints": {
            "health_check": "/health",
            "generate_resume": "/generate-resume",
            "improve_section": "/improve-section",
            "extract_keywords": "/extract-keywords"
        },
        "documentation": "/docs"
    }

# ================= HEALTH =================

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AI Resume Builder API",
        "version": "1.0",
        "llm_model": "gemini-2.5-flash"
    }

# ================= GENERATE RESUME =================

@app.post("/generate-resume")
async def generate_resume(data: ResumeRequest):
    keywords = []

    # STEP 1 — Extract keywords if job description exists
    if data.job_description:
        keyword_prompt_text = keyword_prompt.format(job=data.job_description)
        keyword_response = llm.invoke(keyword_prompt_text)
        keywords = clean_llm_json(keyword_response.content).get("keywords", [])

    # STEP 2 — Combine user data + keywords
    resume_data = {"user_data": data.dict(), "extracted_keywords": keywords}

    resume_prompt_text = resume_prompt.format(data=json.dumps(resume_data, indent=2))
    resume_response = llm.invoke(resume_prompt_text)

    parsed_resume = clean_llm_json(resume_response.content)

    return {
        "keywords_used": keywords,
        "resume_content": parsed_resume
    }

# ================= IMPROVE SECTION =================

@app.post("/improve-section")
async def improve_section(data: ImproveRequest):
    prompt_text = improve_prompt.format(
        role=data.target_role,
        job=data.job_description,
        content=data.content
    )
    response = llm.invoke(prompt_text)
    return {"improved_content": response.content}

# ================= EXTRACT KEYWORDS =================

@app.post("/extract-keywords")
async def extract_keywords(data: KeywordRequest):
    prompt_text = keyword_prompt.format(job=data.job_description)
    response = llm.invoke(prompt_text)
    parsed = clean_llm_json(response.content)
    return parsed