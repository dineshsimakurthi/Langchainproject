# 🗄️ Natural Language to SQL Generator

A Streamlit web application that converts natural language questions into SQL queries using Google's Gemini LLM via LangChain, with observability powered by Langfuse.

---

## Features

- **Natural Language to SQL** — Describe what data you want in plain English and get a valid SQL query instantly
- **Custom Schema Support** — Paste your own database schema so the model generates accurate, context-aware queries
- **Conversation History** — Tracks previous queries and generated SQL within the session
- **Langfuse Observability** — Every LLM call is traced and logged via Langfuse for monitoring and debugging
- **Observability Panel** — Toggle an in-app panel to inspect schema, query details, and chat history stats

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | [Streamlit](https://streamlit.io/) |
| LLM | [Google Gemini 2.5 Flash Lite](https://ai.google.dev/) |
| Orchestration | [LangChain](https://www.langchain.com/) |
| Observability | [Langfuse](https://langfuse.com/) |
| Environment | Python + `python-dotenv` |

---

## Project Structure

```
.
├── app.py               # Main Streamlit application
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables (not committed)
```

---

## Getting Started

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key_here

# Langfuse (optional but recommended)
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
```

- Get a **Google API key** from [Google AI Studio](https://aistudio.google.com/app/apikey)
- Get **Langfuse keys** from [Langfuse Cloud](https://cloud.langfuse.com) (free tier available)

### 5. Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## Usage

1. **Paste your database schema** in the schema text area (tables, columns, and types)
2. **Enter your requirement** in plain English (e.g., *"Show all employees with salary greater than 50000"*)
3. Click **Generate SQL** — the query appears as formatted SQL code
4. Toggle **Show observability details** to inspect session stats
5. Scroll down to view **Conversation History** for all queries in the current session

### Example

**Schema:**
```sql
Table employees(id INTEGER, name TEXT, salary INTEGER, department_id INTEGER)
Table departments(id INTEGER, name TEXT)
```

**Input:** `List all employees in the Engineering department`

**Output:**
```sql
SELECT e.name FROM employees e
JOIN departments d ON e.department_id = d.id
WHERE d.name = 'Engineering';
```

---

## Observability with Langfuse

All LLM calls are automatically traced via the `CallbackHandler` from `langfuse.langchain`. You can view traces, latency, token usage, and more in your [Langfuse dashboard](https://cloud.langfuse.com).

---

## Notes

- The model is configured with `temperature=0.7`. Lower this (e.g., `0.0`) for more deterministic SQL output.
- Conversation history is stored **in-session only** — it resets on page refresh.
- The app does not execute SQL queries; it only generates them.
