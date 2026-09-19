# rag/normalization.py
import re

SKILL_ALIASES = {
    # React variations
    "reactjs": "React",
    "react.js": "React",
    "react js": "React",
    "react native": "React Native",
    
    # Next.js
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "next js": "Next.js",
    
    # Vue
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    
    # Python & Frameworks
    "py": "Python",
    "python3": "Python",
    "fastapi": "FastAPI",
    "fast api": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    
    # Databases
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "postgresql db": "PostgreSQL",
    "psql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "redis": "Redis",
    
    # Cloud & DevOps
    "aws": "AWS",
    "aws cloud": "AWS",
    "amazon web services": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "azure": "Azure",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "docker": "Docker",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "terraform": "Terraform",
    
    # AI / ML
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "llm": "LLM",
    "llms": "LLM",
    "large language models": "LLM",
    "rag": "RAG",
    "retrieval augmented generation": "RAG",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "langchain": "LangChain",
    "langgraph": "LangGraph",
    
    # QA / Testing
    "playwright": "Playwright",
    "selenium": "Selenium",
    "pytest": "PyTest",
    "jest": "Jest",
    "cypress": "Cypress",
    "qa": "QA",
    "quality assurance": "QA",
    "api testing": "API Testing",
    
    # Language
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "golang": "Go",
    "go": "Go",
}

def normalize_skill(skill_name: str) -> str:
    """Normalize a skill name using alias dictionary."""
    if not skill_name:
        return ""
    clean = skill_name.strip()
    lower = clean.lower()
    return SKILL_ALIASES.get(lower, clean)

def normalize_role(role_name: str) -> str:
    """Normalize role string to a standard role category."""
    if not role_name:
        return "Software Engineer"
    lower = role_name.lower().replace("-", " ").replace("_", " ")
    if "lead" in lower or "architect" in lower or "manager" in lower:
        return "Technical Lead"
    elif "backend" in lower or "back end" in lower or "api" in lower:
        return "Backend Engineer"
    elif "frontend" in lower or "front end" in lower or "ui" in lower:
        return "Frontend Engineer"
    elif "full" in lower and "stack" in lower:
        return "Full Stack Engineer"
    elif "ml" in lower or "machine learning" in lower or "ai" in lower or "nlp" in lower:
        return "ML Engineer"
    elif "qa" in lower or "test" in lower or "quality" in lower:
        return "QA Engineer"
    elif "devops" in lower or "cloud" in lower or "infra" in lower or "sre" in lower:
        return "DevOps Engineer"
    elif "data" in lower and ("engineer" in lower or "analytics" in lower):
        return "Data Engineer"
    return role_name.strip().title()
