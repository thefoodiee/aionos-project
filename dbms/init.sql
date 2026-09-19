-- Initialize pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Employees Table
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    role VARCHAR(255) NOT NULL,
    department VARCHAR(255),
    years_experience NUMERIC(4, 1) DEFAULT 0,
    resume_filename VARCHAR(255),
    resume_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Skills Table
CREATE TABLE IF NOT EXISTS skills (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- Employee Skills Link Table
CREATE TABLE IF NOT EXISTS employee_skills (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    proficiency VARCHAR(50) DEFAULT 'intermediate',
    years_experience NUMERIC(4, 1) DEFAULT 1,
    CONSTRAINT uq_employee_skill UNIQUE (employee_id, skill_id)
);

-- Projects Table
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    domain VARCHAR(255)
);

-- Employee Projects Link Table
CREATE TABLE IF NOT EXISTS employee_projects (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    role VARCHAR(255),
    description TEXT,
    CONSTRAINT uq_employee_project UNIQUE (employee_id, project_id)
);

-- Document Chunks for RAG (384-dimensional dense vectors)
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding vector(384),
    metadata_json JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_doc_chunks_employee_id ON document_chunks(employee_id);
