# Database Management (DBMS)

PostgreSQL database configuration with `pgvector` vector similarity search support.

## Credentials (.env)
- Database: `team_builder`
- User: `admin`
- Password: `admin123`
- Port: `5432`

## Extensions
- `vector`: pgvector extension enabled in `init.sql` for storing 384-dimensional resume chunk embeddings and cosine distance queries (`<=>`).
