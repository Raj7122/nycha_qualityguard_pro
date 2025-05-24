# NYCHA QualityGuard Pro (or Your Chosen App Name)

## 🚀 Project Summary

NYCHA QualityGuard Pro is an AI-native application designed to empower NYCHA (New York City Housing Authority) Superintendents. It provides intelligent insights into maintenance operations, helping them move beyond purely reactive, numbers-driven work towards proactive, quality-focused building stewardship. The application aims to assist superintendents in identifying urgent resident-reported issues, predicting potential rework for completed jobs, and accessing relevant contextual information to make more informed decisions, ultimately improving resident living conditions and operational efficiency.

## ✨ Core Features (MVP & Vision)

*   **AI-Powered Daily Quality Briefing:** A `smolagent` (`CodeAgent` powered by Google Gemini) generates a concise daily briefing highlighting:
    *   Newly flagged urgent 311 complaints based on NLP analysis.
    *   (Simulated) Recently closed work orders with a high predicted rework risk.
    *   (Stretch Goal) Contextual information from a knowledge base (e.g., NYCHA SOPs) related to flagged items using Agentic RAG principles.
*   **Urgent Complaint Identification:** Leverages Natural Language Processing (NLP) on NYC 311 data to automatically detect and flag complaints indicating potential safety, health, or critical service issues.
*   **Rework Risk Prediction (Conceptual Demo):** Utilizes a rule-based engine (or simple ML on synthetic data) to assess the likelihood of a (simulated) completed work order requiring rework, based on factors like asset age, resolution type, and contractor history.
*   **Interactive Superintendent Dashboard:** A modern web interface (built with Bolt.new) for superintendents to view the daily briefing, explore lists of urgent complaints with AI-derived insights, and analyze rework risk assessments.
*   **MCP-Inspired Tool Server:** Core AI capabilities (Urgency Flagging, Rework Risk Assessment, Knowledge Base Access) are exposed as well-defined tools via an internal server (using `mcp.server.fastmcp`), enabling interoperability and use by the `smolagent`.

## 🛠️ Tech Stack & Architecture

The project employs a modern, AI-native tech stack:

**Frontend:**

*   **UI Framework:** [Bolt.new](https://bolt.new/) (for the main dynamic web application)
*   **Language:** Likely TypeScript/JavaScript (as per Bolt.new's typical stack)
*   **Styling:** Tailwind CSS (or as configured by Bolt.new)
*   **Icons:** Lucide React (or similar)
*   **(Optional Prototyping):** Gradio (for rapid interactive demos of individual AI components or simple agent interactions)

**Backend:**

*   **Language:** Python
*   **Web Framework:** Flask (using a factory pattern and Blueprints for organization)
*   **AI/ML & Data Processing:**
    *   `pandas`, `numpy`: For data manipulation.
    *   `nltk`, `spaCy`, `scikit-learn`: For Natural Language Processing (keyword spotting, text classification) and basic Machine Learning.
*   **Agent Framework:**
    *   `smolagents`: Specifically `CodeAgent` for orchestrating tasks and using tools.
*   **LLM Integration:**
    *   Google Gemini (e.g., `gemini-1.0-pro` or `gemini-1.5-flash`) via its OpenAI-compatible API endpoint, integrated using `smolagents.OpenAIServerModel`.
*   **MCP (Model-Context Protocol) Implementation:**
    *   `mcp` library: Using `mcp.server.fastmcp` to create an internal server exposing backend AI services as callable "tools" for the `smolagent`.
*   **API Communication:**
    *   `requests`: For calling external APIs (e.g., NYC OpenData).
    *   RESTful APIs built with Flask to connect backend services to the Bolt.new frontend.
*   **Database:**
    *   PostgreSQL (primary choice for structured data) or SQLite (for simpler MVP needs).
    *   (Stretch Goal) Vector Database (e.g., Chroma, FAISS) for Agentic RAG knowledge base.
*   **Environment Management:** `python-dotenv`

**Development & Operations Tools:**

*   **IDE:** Cursor (AI-assisted code editor)
*   **Version Control:** Git & GitHub
*   **Virtual Environments:** `venv` or `conda`
*   **Code Quality:** Black (formatter), Flake8 (linter) (as per initial setup)
*   **Testing:** Pytest (as per initial setup)
*   **Security (for Agent Execution - Planned):** Docker / E2B for sandboxing `CodeAgent` execution.
*   **Debugging & Monitoring (Planned):** Langfuse (for agent tracing), MCP Inspector Tool.

## 🏁 Project Status

Currently in Phase 2 of MVP development, focusing on implementing the `smolagent`-driven Daily Briefing and integrating the Rework Risk Prediction service. Phase 1 (311 Data Ingestion, NLP Urgency Flagging, and initial Frontend Dashboard) is largely complete.

*(Adjust the "Project Status" as you progress!)*
