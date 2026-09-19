# seed.py
"""
Seed script to populate PostgreSQL with 18 realistic fictional employees,
their verified skills, project histories, and pgvector embeddings.
Enables immediate testing of the Demo Scenario without manual uploads.
"""

import sys
from pathlib import Path

# Add backend directory to sys.path so app modules import properly
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db.database import SessionLocal, Base, engine
from app.db.models import Employee
from app.rag.ingestion import ingest_employee

SEED_EMPLOYEES = [
    {
        "name": "Priya Sharma",
        "role": "Technical Lead",
        "department": "Engineering",
        "years_experience": 8.0,
        "skills": [
            {"name": "Python", "proficiency": "expert", "years": 8.0},
            {"name": "FastAPI", "proficiency": "advanced", "years": 5.0},
            {"name": "PostgreSQL", "proficiency": "expert", "years": 7.0},
            {"name": "AWS", "proficiency": "advanced", "years": 6.0},
            {"name": "React", "proficiency": "intermediate", "years": 4.0},
            {"name": "Docker", "proficiency": "advanced", "years": 5.0},
        ],
        "projects": [
            {
                "name": "OmniChannel E-Commerce Architecture",
                "domain": "E-Commerce",
                "description": "Architected resilient distributed backend handling 20,000 req/sec on AWS using FastAPI and PostgreSQL.",
                "technologies": ["Python", "FastAPI", "PostgreSQL", "AWS"]
            },
            {
                "name": "Customer Support Portal Redesign",
                "domain": "Customer Support",
                "description": "Led cross-functional team of 7 engineers delivering real-time support platform integration.",
                "technologies": ["React", "FastAPI", "Docker"]
            }
        ],
        "resume_text": (
            "Priya Sharma - Technical Lead / Senior Architect (8 years experience).\n"
            "Seasoned engineering leader with deep expertise designing cloud-native architectures on AWS with Python, FastAPI, and PostgreSQL.\n"
            "Proven track record leading engineering squads in e-commerce and customer support domains.\n"
            "Led OmniChannel E-Commerce Architecture: designed scalable FastAPI microservices with PostgreSQL connection pooling and AWS ECS deployment.\n"
            "Led Customer Support Portal Redesign coordinating frontend React teams and backend API squads."
        )
    },
    {
        "name": "Alex Rivera",
        "role": "Senior Backend Engineer",
        "department": "Engineering",
        "years_experience": 6.0,
        "skills": [
            {"name": "Python", "proficiency": "expert", "years": 6.0},
            {"name": "FastAPI", "proficiency": "expert", "years": 5.0},
            {"name": "PostgreSQL", "proficiency": "advanced", "years": 5.0},
            {"name": "AWS", "proficiency": "advanced", "years": 4.0},
            {"name": "Redis", "proficiency": "intermediate", "years": 3.0},
            {"name": "Docker", "proficiency": "advanced", "years": 4.0},
        ],
        "projects": [
            {
                "name": "Payment Gateway Microservices",
                "domain": "Financial Services",
                "description": "Engineered high-concurrency payment APIs using FastAPI and PostgreSQL on AWS with 99.99% uptime.",
                "technologies": ["Python", "FastAPI", "PostgreSQL", "AWS"]
            },
            {
                "name": "E-Commerce Order Pipeline",
                "domain": "E-Commerce",
                "description": "Built event-driven backend service for real-time checkout and inventory reconciliation.",
                "technologies": ["FastAPI", "PostgreSQL", "Redis"]
            }
        ],
        "resume_text": (
            "Alex Rivera - Senior Backend Engineer (6 years experience).\n"
            "Core focus on Python, FastAPI, PostgreSQL, and AWS cloud infrastructure.\n"
            "Architected Payment Gateway Microservices on AWS handling payment transactions with PostgreSQL and Redis caching.\n"
            "Engineered high-throughput E-Commerce Order Pipeline with automated testing and Docker containerization."
        )
    },
    {
        "name": "Elena Rostova",
        "role": "Backend Engineer",
        "department": "Engineering",
        "years_experience": 4.0,
        "skills": [
            {"name": "Python", "proficiency": "advanced", "years": 4.0},
            {"name": "FastAPI", "proficiency": "advanced", "years": 3.0},
            {"name": "PostgreSQL", "proficiency": "advanced", "years": 4.0},
            {"name": "AWS", "proficiency": "intermediate", "years": 2.0},
            {"name": "Django", "proficiency": "intermediate", "years": 2.0},
        ],
        "projects": [
            {
                "name": "Support Ticket Routing API",
                "domain": "Customer Support",
                "description": "Developed automated ticket routing service using Python and FastAPI integrated with PostgreSQL.",
                "technologies": ["Python", "FastAPI", "PostgreSQL"]
            },
            {
                "name": "E-Commerce Catalog Sync",
                "domain": "E-Commerce",
                "description": "Created high-speed product catalog ingestion pipeline deployed to AWS S3 and RDS PostgreSQL.",
                "technologies": ["FastAPI", "PostgreSQL", "AWS"]
            }
        ],
        "resume_text": (
            "Elena Rostova - Backend Engineer with 4 years experience specializing in Python and FastAPI.\n"
            "Strong database background with PostgreSQL query optimization and cloud deployment on AWS.\n"
            "Built Support Ticket Routing API for automated customer service escalation.\n"
            "Developed E-Commerce Catalog Sync pipelines integrated with AWS cloud services."
        )
    },
    {
        "name": "Marcus Chen",
        "role": "Senior Frontend Engineer",
        "department": "Frontend",
        "years_experience": 5.0,
        "skills": [
            {"name": "React", "proficiency": "expert", "years": 5.0},
            {"name": "TypeScript", "proficiency": "expert", "years": 4.0},
            {"name": "Next.js", "proficiency": "advanced", "years": 3.0},
            {"name": "Tailwind CSS", "proficiency": "advanced", "years": 4.0},
            {"name": "JavaScript", "proficiency": "expert", "years": 5.0},
        ],
        "projects": [
            {
                "name": "E-Commerce Customer Portal",
                "domain": "E-Commerce",
                "description": "Constructed responsive customer portal in React and Next.js with sub-second page loads and accessible UI.",
                "technologies": ["React", "TypeScript", "Next.js", "Tailwind CSS"]
            },
            {
                "name": "Live Support Agent Dashboard",
                "domain": "Customer Support",
                "description": "Built real-time agent dashboard using React and WebSockets for chat and ticket triage.",
                "technologies": ["React", "TypeScript", "Tailwind CSS"]
            }
        ],
        "resume_text": (
            "Marcus Chen - Senior Frontend Engineer (5 years experience).\n"
            "Mastery of React, Next.js, TypeScript, and modern web UI component architecture.\n"
            "Developed E-Commerce Customer Portal serving over 500k monthly active users with React and Tailwind CSS.\n"
            "Created Live Support Agent Dashboard featuring real-time state management and accessible components."
        )
    },
    {
        "name": "Maya Patel",
        "role": "ML Engineer",
        "department": "AI Research",
        "years_experience": 4.0,
        "skills": [
            {"name": "Python", "proficiency": "expert", "years": 4.0},
            {"name": "LLM", "proficiency": "expert", "years": 3.0},
            {"name": "RAG", "proficiency": "expert", "years": 3.0},
            {"name": "PyTorch", "proficiency": "advanced", "years": 3.0},
            {"name": "FastAPI", "proficiency": "intermediate", "years": 2.0},
            {"name": "AWS", "proficiency": "intermediate", "years": 2.0},
        ],
        "projects": [
            {
                "name": "AI Customer Support Agent with RAG",
                "domain": "Customer Support",
                "description": "Created generative AI customer support assistant using LLMs and RAG vector search over internal knowledge base.",
                "technologies": ["Python", "LLM", "RAG", "PyTorch", "FastAPI"]
            },
            {
                "name": "E-Commerce Product Q&A Bot",
                "domain": "E-Commerce",
                "description": "Implemented RAG pipeline for automated product question answering with 94% customer resolution rate.",
                "technologies": ["Python", "LLM", "RAG", "AWS"]
            }
        ],
        "resume_text": (
            "Maya Patel - Machine Learning / AI Engineer (4 years experience).\n"
            "Specialist in LLM applications, Retrieval-Augmented Generation (RAG), vector similarity search, and conversational AI.\n"
            "Engineered AI Customer Support Agent with RAG that cut tier-1 support response times by 70%.\n"
            "Implemented E-Commerce Product Q&A Bot with hybrid search retrieval deployed via FastAPI and AWS."
        )
    },
    {
        "name": "Sarah Jenkins",
        "role": "QA Lead",
        "department": "Quality Assurance",
        "years_experience": 5.0,
        "skills": [
            {"name": "Playwright", "proficiency": "expert", "years": 4.0},
            {"name": "PyTest", "proficiency": "expert", "years": 5.0},
            {"name": "Selenium", "proficiency": "advanced", "years": 5.0},
            {"name": "API Testing", "proficiency": "expert", "years": 5.0},
            {"name": "CI/CD", "proficiency": "advanced", "years": 4.0},
            {"name": "Python", "proficiency": "advanced", "years": 4.0},
        ],
        "projects": [
            {
                "name": "Automated E-Commerce End-to-End Suite",
                "domain": "E-Commerce",
                "description": "Built automated Playwright & PyTest test pipeline running against staging and production e-commerce checkouts.",
                "technologies": ["Playwright", "PyTest", "Python", "CI/CD"]
            },
            {
                "name": "AI Chatbot Regression Test Framework",
                "domain": "Customer Support",
                "description": "Created comprehensive API testing framework to evaluate conversational AI response accuracy and latency.",
                "technologies": ["PyTest", "API Testing", "Python"]
            }
        ],
        "resume_text": (
            "Sarah Jenkins - QA Lead / Test Automation Engineer (5 years experience).\n"
            "Extensive experience designing robust test automation frameworks with Playwright, Selenium, PyTest, and API testing.\n"
            "Built Automated E-Commerce End-to-End Suite ensuring zero defects in critical checkout flows.\n"
            "Designed AI Chatbot Regression Test Framework for validating customer support conversational agents."
        )
    },
    {
        "name": "David Kim",
        "role": "DevOps Engineer",
        "department": "Infrastructure",
        "years_experience": 6.0,
        "skills": [
            {"name": "AWS", "proficiency": "expert", "years": 6.0},
            {"name": "Docker", "proficiency": "expert", "years": 5.0},
            {"name": "Kubernetes", "proficiency": "advanced", "years": 4.0},
            {"name": "Terraform", "proficiency": "advanced", "years": 4.0},
            {"name": "CI/CD", "proficiency": "expert", "years": 5.0},
            {"name": "PostgreSQL", "proficiency": "intermediate", "years": 3.0},
        ],
        "projects": [
            {
                "name": "E-Commerce Cloud Infrastructure on AWS",
                "domain": "E-Commerce",
                "description": "Provisioned multi-AZ AWS infrastructure with Terraform, ECS, RDS PostgreSQL, and CloudFront.",
                "technologies": ["AWS", "Terraform", "Docker", "PostgreSQL"]
            }
        ],
        "resume_text": (
            "David Kim - DevOps / Cloud Infrastructure Engineer (6 years experience).\n"
            "Expert in AWS architectures (ECS, RDS, S3, IAM), Docker containerization, Kubernetes, and automated CI/CD pipelines.\n"
            "Designed E-Commerce Cloud Infrastructure on AWS with zero downtime rolling deployments."
        )
    },
    {
        "name": "Sophia Martinez",
        "role": "Frontend Developer",
        "department": "Frontend",
        "years_experience": 3.0,
        "skills": [
            {"name": "React", "proficiency": "advanced", "years": 3.0},
            {"name": "JavaScript", "proficiency": "advanced", "years": 3.0},
            {"name": "TypeScript", "proficiency": "intermediate", "years": 2.0},
            {"name": "Tailwind CSS", "proficiency": "advanced", "years": 3.0},
        ],
        "projects": [
            {
                "name": "Customer Self-Service FAQ",
                "domain": "Customer Support",
                "description": "Built interactive React knowledge base with responsive search and dynamic help widget.",
                "technologies": ["React", "TypeScript", "Tailwind CSS"]
            }
        ],
        "resume_text": (
            "Sophia Martinez - Frontend Developer (3 years experience) focused on React and modern UI/UX design.\n"
            "Built Customer Self-Service FAQ and responsive customer support interfaces with React and Tailwind CSS."
        )
    },
    {
        "name": "Aisha Bello",
        "role": "ML Engineer",
        "department": "AI Research",
        "years_experience": 3.5,
        "skills": [
            {"name": "Python", "proficiency": "advanced", "years": 3.5},
            {"name": "LLM", "proficiency": "advanced", "years": 2.5},
            {"name": "NLP", "proficiency": "advanced", "years": 3.5},
            {"name": "PyTorch", "proficiency": "advanced", "years": 3.0},
            {"name": "RAG", "proficiency": "intermediate", "years": 2.0},
        ],
        "projects": [
            {
                "name": "Customer Support Intent Classifier",
                "domain": "Customer Support",
                "description": "Trained transformer NLP models to classify and route customer support inquiries automatically.",
                "technologies": ["Python", "NLP", "LLM", "PyTorch"]
            }
        ],
        "resume_text": (
            "Aisha Bello - ML & NLP Specialist with 3.5 years experience in PyTorch, LLMs, and conversational AI.\n"
            "Built Customer Support Intent Classifier with 92% categorization accuracy for incoming support tickets."
        )
    },
    {
        "name": "Carlos Mendez",
        "role": "QA Engineer",
        "department": "Quality Assurance",
        "years_experience": 3.0,
        "skills": [
            {"name": "Playwright", "proficiency": "intermediate", "years": 2.0},
            {"name": "Selenium", "proficiency": "advanced", "years": 3.0},
            {"name": "API Testing", "proficiency": "advanced", "years": 3.0},
            {"name": "PyTest", "proficiency": "intermediate", "years": 2.0},
            {"name": "Python", "proficiency": "intermediate", "years": 2.0},
        ],
        "projects": [
            {
                "name": "Support Ticket API Validation",
                "domain": "Customer Support",
                "description": "Automated regression testing for customer support ticketing APIs.",
                "technologies": ["API Testing", "Python", "Selenium"]
            }
        ],
        "resume_text": (
            "Carlos Mendez - QA Engineer with 3 years experience testing enterprise web applications and REST APIs.\n"
            "Hands-on expertise in Selenium, Playwright, and Postman test automation."
        )
    },
    {
        "name": "Emily Zhao",
        "role": "Full Stack Engineer",
        "department": "Engineering",
        "years_experience": 4.0,
        "skills": [
            {"name": "React", "proficiency": "advanced", "years": 4.0},
            {"name": "FastAPI", "proficiency": "intermediate", "years": 3.0},
            {"name": "Python", "proficiency": "advanced", "years": 4.0},
            {"name": "PostgreSQL", "proficiency": "intermediate", "years": 3.0},
            {"name": "TypeScript", "proficiency": "advanced", "years": 3.0},
        ],
        "projects": [
            {
                "name": "Customer CRM Workspace",
                "domain": "Customer Support",
                "description": "Full-stack web application connecting customer records with live support tickets.",
                "technologies": ["React", "FastAPI", "PostgreSQL", "TypeScript"]
            }
        ],
        "resume_text": (
            "Emily Zhao - Full Stack Engineer (4 years experience) proficient in React, FastAPI, and PostgreSQL.\n"
            "Developed Customer CRM Workspace bridging frontend UI and backend relational databases."
        )
    },
    {
        "name": "Liam O'Connor",
        "role": "Technical Lead",
        "department": "Engineering",
        "years_experience": 9.0,
        "skills": [
            {"name": "Go", "proficiency": "expert", "years": 7.0},
            {"name": "Python", "proficiency": "advanced", "years": 6.0},
            {"name": "AWS", "proficiency": "expert", "years": 7.0},
            {"name": "PostgreSQL", "proficiency": "advanced", "years": 6.0},
            {"name": "Kubernetes", "proficiency": "expert", "years": 5.0},
        ],
        "projects": [
            {
                "name": "High-Throughput Streaming Engine",
                "domain": "Financial Services",
                "description": "Architected low-latency distributed event engine on AWS with Kubernetes.",
                "technologies": ["Go", "AWS", "PostgreSQL", "Kubernetes"]
            }
        ],
        "resume_text": (
            "Liam O'Connor - Principal Technical Lead (9 years experience) with deep systems architecture knowledge.\n"
            "Built distributed systems on AWS handling millions of concurrent events."
        )
    },
    {
        "name": "James Wilson",
        "role": "Backend Developer",
        "department": "Engineering",
        "years_experience": 2.5,
        "skills": [
            {"name": "Python", "proficiency": "intermediate", "years": 2.5},
            {"name": "FastAPI", "proficiency": "intermediate", "years": 2.0},
            {"name": "PostgreSQL", "proficiency": "intermediate", "years": 2.0},
            {"name": "Docker", "proficiency": "intermediate", "years": 1.5},
        ],
        "projects": [
            {
                "name": "Internal Notifications Microservice",
                "domain": "Internal Operations",
                "description": "Built email and SMS notification dispatcher using FastAPI and PostgreSQL.",
                "technologies": ["Python", "FastAPI", "PostgreSQL"]
            }
        ],
        "resume_text": (
            "James Wilson - Junior Backend Developer (2.5 years experience).\n"
            "Strong fundamentals in Python, FastAPI microservices, and PostgreSQL query construction."
        )
    },
    {
        "name": "Vikram Malhotra",
        "role": "Senior Frontend Engineer",
        "department": "Frontend",
        "years_experience": 6.0,
        "skills": [
            {"name": "React", "proficiency": "expert", "years": 6.0},
            {"name": "TypeScript", "proficiency": "expert", "years": 5.0},
            {"name": "Next.js", "proficiency": "advanced", "years": 4.0},
            {"name": "GraphQL", "proficiency": "intermediate", "years": 3.0},
        ],
        "projects": [
            {
                "name": "E-Commerce Checkout Flow",
                "domain": "E-Commerce",
                "description": "Streamlined multi-step checkout flow cutting drop-off rates by 18%.",
                "technologies": ["React", "Next.js", "TypeScript"]
            }
        ],
        "resume_text": (
            "Vikram Malhotra - Senior Frontend Engineer (6 years experience).\n"
            "Specialized in React, Next.js, and TypeScript frontend performance optimization."
        )
    },
    {
        "name": "Tariq Al-Mansoor",
        "role": "Data Engineer",
        "department": "Data",
        "years_experience": 5.0,
        "skills": [
            {"name": "Python", "proficiency": "expert", "years": 5.0},
            {"name": "PostgreSQL", "proficiency": "expert", "years": 5.0},
            {"name": "SQL", "proficiency": "expert", "years": 5.0},
            {"name": "AWS", "proficiency": "intermediate", "years": 3.0},
        ],
        "projects": [
            {
                "name": "Customer Analytics Data Warehouse",
                "domain": "Data Analytics",
                "description": "Built ELT pipeline syncing customer support metrics into PostgreSQL warehouse.",
                "technologies": ["Python", "PostgreSQL", "SQL", "AWS"]
            }
        ],
        "resume_text": (
            "Tariq Al-Mansoor - Data Engineer with 5 years experience in PostgreSQL data modeling and Python ETL."
        )
    },
    {
        "name": "Rachel Green",
        "role": "Junior QA Engineer",
        "department": "Quality Assurance",
        "years_experience": 2.0,
        "skills": [
            {"name": "API Testing", "proficiency": "intermediate", "years": 2.0},
            {"name": "Postman", "proficiency": "intermediate", "years": 2.0},
            {"name": "Selenium", "proficiency": "intermediate", "years": 1.5},
        ],
        "projects": [
            {
                "name": "Mobile Web Smoke Tests",
                "domain": "E-Commerce",
                "description": "Conducted automated and exploratory smoke testing on mobile checkout.",
                "technologies": ["Selenium", "API Testing"]
            }
        ],
        "resume_text": (
            "Rachel Green - Junior QA Engineer (2 years experience) specialized in API validation and web test execution."
        )
    },
    {
        "name": "Benjamin Brooks",
        "role": "Backend Engineer",
        "department": "Engineering",
        "years_experience": 5.0,
        "skills": [
            {"name": "Java", "proficiency": "expert", "years": 5.0},
            {"name": "PostgreSQL", "proficiency": "advanced", "years": 4.0},
            {"name": "AWS", "proficiency": "intermediate", "years": 3.0},
        ],
        "projects": [
            {
                "name": "Banking Settlement Engine",
                "domain": "Financial Services",
                "description": "Implemented high-reliability transaction settlement engine.",
                "technologies": ["Java", "PostgreSQL", "AWS"]
            }
        ],
        "resume_text": (
            "Benjamin Brooks - Backend Engineer (5 years experience) specializing in enterprise services."
        )
    },
    {
        "name": "Ananya Iyer",
        "role": "ML Engineer",
        "department": "AI Research",
        "years_experience": 3.0,
        "skills": [
            {"name": "Python", "proficiency": "advanced", "years": 3.0},
            {"name": "TensorFlow", "proficiency": "advanced", "years": 3.0},
            {"name": "Docker", "proficiency": "intermediate", "years": 2.0},
        ],
        "projects": [
            {
                "name": "Product Image Tagging Engine",
                "domain": "E-Commerce",
                "description": "Computer vision model automatically tagging catalog merchandise.",
                "technologies": ["Python", "TensorFlow", "Docker"]
            }
        ],
        "resume_text": (
            "Ananya Iyer - ML Engineer with 3 years experience building predictive models and computer vision pipelines."
        )
    }
]

def seed_database(force: bool = False):
    print("Starting database seeding...")
    # Create tables if not present
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        count = db.query(Employee).count()
        if not force and count >= len(SEED_EMPLOYEES):
            print(f"Database already contains {count} employees. Skipping seed.")
            return {"status": "skipped", "count": count, "message": f"Database already contains {count} candidate profiles."}

        print(f"Ingesting {len(SEED_EMPLOYEES)} fictional employees with pgvector embeddings...")
        for emp_data in SEED_EMPLOYEES:
            override_data = {
                "name": emp_data["name"],
                "role": emp_data["role"],
                "department": emp_data.get("department", "Engineering"),
                "years_experience": emp_data["years_experience"],
                "skills": emp_data["skills"],
                "projects": emp_data["projects"]
            }
            emp = ingest_employee(
                db=db,
                raw_text=emp_data["resume_text"],
                filename=f"{emp_data['name'].lower().replace(' ', '_')}_resume.pdf",
                override_data=override_data
            )
            print(f"  ✓ Ingested {emp.name} ({emp.role}) - {len(emp_data['skills'])} skills, {len(emp_data['projects'])} projects")

        final_count = db.query(Employee).count()
        print(f"Seeding complete! Total employees in database: {final_count}")
        return {"status": "success", "count": final_count, "message": f"Successfully loaded {final_count} candidate profiles with vector embeddings."}
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
