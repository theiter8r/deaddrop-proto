# CLAUDE.md

# Project Context: Four Layer API Security System

## System Overview
We are building a prototype for an Automated API Security and Governance System. The current focus is on "Layer 1: Continuous Scanning & Discovery" (Static Scanner) and "Layer 4: The Dashboard" (Frontend UI). 

## Infrastructure & Hosting
* **Target Environment:** Railway
* **Database:** PostgreSQL (Railway provisioned)
* **Backend:** FastAPI (Python 3.10+), containerized via Docker.
* **Frontend:** React/Next.js (Static Export), served via Nginx, containerized via Docker.

## Backend Requirements (Static Scanner)
* **Goal:** Discover and normalize API definitions from code repositories.
* **Inputs:** `swagger.json`, `openapi.yaml`, `*.postman_collection.json` via GitHub/GitLab.
* **Data Model:** Standardize outputs into a unified schema: `endpoint_path`, `http_method`, `source_file`, `is_deprecated` (boolean).

## Frontend Requirements (Security Dashboard)
* **Goal:** Provide a live grid view of discovered APIs.
* **Features:** Data table mapping the backend's standardized schema. Visual tags for status (Active, Zombie, Shadow) and an action column for future "Decommission" webhook triggers.

---

## 🛑 Strict Constraints & Rules

### 1. Docker & Deployment Constraints
* **Architecture:** When building Docker images locally on Apple Silicon for deployment, explicitly use `--platform linux/amd64`. Railway expects x86_64; ARM64 images will fail to run.
* **Frontend Build:** The Next.js application MUST be configured for static export (`output: 'export'` in `next.config.js`). 
* **No Next.js SSR:** Because the frontend is served via an Nginx container, do not write any Next.js Server Components, Server Actions, or API Routes (`/app/api/...`). All data fetching must happen client-side via standard HTTP requests to the FastAPI backend container.

### 2. Backend Coding Constraints
* **Asynchronous I/O:** Use `async def` for all FastAPI endpoints. Use asynchronous HTTP clients (like `httpx`, not `requests`) for querying GitHub/GitLab APIs to prevent blocking the event loop.
* **Statelessness:** The FastAPI application must remain completely stateless. All parsed API data must be written to the Postgres database. Do not use in-memory dictionaries or local files to store the "Documented APIs List" between requests.

### 3. Frontend UI/UX Constraints
* **Styling:** Strictly use Tailwind CSS for all styling. Do not introduce styled-components or raw CSS modules unless absolutely necessary.
* **Simplicity:** This is a prototype. Favor native HTML tables styled with Tailwind over heavy, third-party data-grid libraries unless complex sorting/filtering is explicitly requested.

## 📋 Workflow & Task Management (The "Hook")
* **The Master Ledger:** You must treat `todo.md` as the absolute source of truth for project progress. 
* **Pre-Flight Check:** Before writing any code or executing a command, you MUST read `todo.md` to understand the current active task.
* **Post-Flight Update:** Upon completing a logical feature or Agile card, you MUST immediately update `todo.md` by checking off the completed item and moving the "IN PROGRESS" indicator to the next task.
* **Planning:** If asked to plan a new feature, draft the steps in `todo.md` first before writing the code.
