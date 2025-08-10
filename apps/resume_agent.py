"""
LLM-powered Resume Agent
Backend function: resume_agent_backend
"""

from typing import Dict
from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3.2")

def extract_skills(job_desc: str) -> str:
    prompt = f"Extract the top 8 skills from this job description:\n{job_desc}"
    return llm.invoke(prompt)

def generate_resume(job_desc: str, skills: str) -> str:
    prompt = f"""
Create a short tailored resume summary for a candidate applying to this job:

Job Description:
{job_desc}

Candidate Skills:
{skills}

Resume Summary:"""
    return llm.invoke(prompt)

def resume_agent_backend(request) -> Dict:
    context = {}
    if request.method == "POST":
        job_desc = request.form.get("job_desc", "").strip()
        if not job_desc:
            context["resume"] = "Please provide a job description."
            return context

        # Skills extraction phase
        skills = extract_skills(job_desc)
        # Resume generation phase
        resume_summary = generate_resume(job_desc, skills)

        context["resume"] = f"**Extracted Skills:**\n{skills}\n\n**Generated Resume:**\n{resume_summary}"

    return context