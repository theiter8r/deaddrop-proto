# DeadDrop Proto — Static Scanner: Task Ledger

## Sprint: Layer 1 — Static Scanner Backend

- [x] **Card 1: FastAPI Setup & Data Models** ✅ DONE
  - Initialize Python project structure (`backend/`)
  - Generate `requirements.txt` with all dependencies
  - Define core Pydantic schemas (`endpoint_path`, `http_method`, `source_file`, `is_deprecated`)
  - Set up SQLAlchemy models + async DB connection (asyncpg)
  - Create `Dockerfile` for the backend (linux/amd64)

- [x] **Card 2: Repo Auth & Discovery Logic** ✅ DONE
  - Implement GitHub/GitLab token-based auth via `httpx`
  - Build async repo file tree walker to find target files (`swagger.json`, `openapi.yaml`, `*.postman_collection.json`)
  - Return a normalized list of matching file paths + raw content

- [ ] **Card 3: Build File Parsing Engine** 🔄 IN PROGRESS
  - Parse OpenAPI/Swagger JSON & YAML → extract endpoints
  - Parse Postman Collection JSON → extract endpoints
  - Normalize all outputs to unified schema
  - Handle `deprecated` fields from OpenAPI spec → `is_deprecated`

- [ ] **Card 4: Create Scanner Endpoints**
  - `POST /scan` — accepts repo URL + token, triggers full scan, persists to DB
  - `GET /endpoints` — returns all discovered endpoints from DB
  - Wire parsing engine into scan flow end-to-end

- [ ] **Card 5: End-to-End Mock Testing**
  - Write pytest tests using `httpx.AsyncClient` against a test DB
  - Test scan flow with fixture files (mock swagger/openapi/postman)
  - Validate DB persistence and API response schema
