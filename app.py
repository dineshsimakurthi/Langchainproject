import os
import streamlit as st
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

# =========================
# LANGFUSE IMPORTS (optional)
# =========================
try:
    from langfuse.langchain import CallbackHandler

    _HAS_LANGFUSE = True
except Exception:
    CallbackHandler = None
    _HAS_LANGFUSE = False

# =========================
# LOAD ENV
# =========================
load_dotenv()

# =========================
# LANGFUSE CALLBACK
# =========================
if _HAS_LANGFUSE and CallbackHandler is not None:
    langfuse_handler = CallbackHandler(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST"),
    )
else:
    langfuse_handler = None
    # If running in Streamlit, show an informational message about Langfuse not being available
    try:
        st = globals().get("st")
        if st is not None:
            st.info("Langfuse not installed or not configured — traces will not be sent.")
    except Exception:
        pass
# =========================
# STREAMLIT UI
# =========================
st.set_page_config(page_title="SQL Query Generator", page_icon="🗄️")
st.title("🗄️ Natural Language to SQL Generator")

# =========================
# MEMORY
# =========================
if "memory" not in st.session_state:
    st.session_state.memory = InMemoryChatMessageHistory()

memory = st.session_state.memory

# =========================
# DATABASE SCHEMA
# =========================
st.subheader("Database Schema")

database_schema = st.text_area(
    "Paste your database schema here",
    placeholder="""
Example:
Table employees(
    id INTEGER,
    name TEXT,
    salary INTEGER,
    department_id INTEGER
)

Table departments(
    id INTEGER,
    name TEXT
)
""",
    height=180,
)

# =========================
# PROMPT TEMPLATE
# =========================
prompt_template = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an SQL expert.

Use the following database schema to answer user requests:

{schema}

Convert the user's natural language request into a valid SQL query.

Only return the SQL query.
Do not explain anything.
"""
    ),
    ("human", "{input}")
])

# =========================
# MODEL
# =========================
google_api_key = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.7,
    google_api_key=google_api_key
)

output_parser = StrOutputParser()

# =========================
# CHAIN
# =========================
chain = prompt_template | llm | output_parser

# =========================
# FUNCTION
# =========================
def generate_sql(question, schema):

    invoke_config = {}
    if langfuse_handler:
        invoke_config["callbacks"] = [langfuse_handler]

    response = chain.invoke(
        {
            "input": question,
            "schema": schema,
        },
        config=invoke_config,
    )

    memory.add_messages([
        HumanMessage(content=question),
        AIMessage(content=response)
    ])

    return response

# =========================
# USER INPUT
# =========================
user_query = st.text_area(
    "Enter your requirement",
    placeholder="Example: Show all employees whose salary is greater than 50000",
)

languse = "sql"

# =========================
# GENERATE BUTTON
# =========================
if st.button("Generate SQL"):

    if user_query:

        with st.spinner("Generating SQL Query..."):

            result = generate_sql(
                user_query,
                database_schema or ""
            )

        st.subheader("Generated SQL Query")

        st.code(result, language=languse)

        st.success("Trace sent to Langfuse successfully!")

    else:
        st.warning("Please enter a query.")

# =========================
# OBSERVABILITY
# =========================
if st.checkbox("Show observability details"):

    st.subheader("Observability")

    st.markdown(f"- Database schema provided: {'Yes' if database_schema else 'No'}")
    st.markdown(f"- Schema length: {len(database_schema)} characters")
    st.markdown(f"- User query: {user_query or 'No query entered yet.'}")
    st.markdown(f"- Chat history entries: {len(memory.messages)}")

    st.markdown("### Database Schema")

    st.code(
        database_schema or "No schema provided.",
        language="text"
    )

# =========================
# CHAT HISTORY
# =========================
if memory.messages:

    st.subheader("Conversation History")

    for msg in memory.messages:

        if isinstance(msg, HumanMessage):

            st.markdown(f"**User:** {msg.content}")

        else:

            st.markdown("**SQL:**")

            st.code(msg.content, language=languse)
