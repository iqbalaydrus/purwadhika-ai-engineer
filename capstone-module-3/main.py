import os
import sys

import streamlit as st

from dotenv import load_dotenv

load_dotenv()

# QDRANT_URL = st.secrets["QDRANT_URL"]
# QDRANT_API_KEY = st.secrets["QDRANT_API_KEY"]
# OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
# DISCORD_CHANNEL_NAME = st.secrets["DISCORD_CHANNEL_NAME"]
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_CHANNEL_NAME = os.getenv("DISCORD_CHANNEL_NAME")

_ = """
TODO: Create a skill summary for each category/industry:
  "profile_summary": string,            // 120-180 words, concise and factual
  "top_skills": string[],               // <= 12
  "tools": string[],                    // <= 12
  "roles": string[],                    // <= 8
  "education": string[],                // concise items
  "years_experience_estimate": number | null,
  "highlights": string[]                // <= 8 bullet outcomes

Modes:
1. Recruiter - Put job description, output best matching CV. With the actual CV shown as html.
2. Applicant - Put their CV and Industry, output which skills he has to have. And estimate
the likelihood of the applicant to be hired.
"""


def main_program():
    option = st.selectbox(
        "Who are you?",
        ("", "Recruiter", "Applicant"),
        key="option",
    )
    if option in ["Recruiter", "Applicant"]:
        # imports are in a function to speedup first load
        from langchain_openai import ChatOpenAI
        from langchain_openai import OpenAIEmbeddings
        from langchain_qdrant import QdrantVectorStore
        from langchain.tools import tool
        from langchain.schema import Document
        from langgraph.prebuilt import create_react_agent
        from langchain_core.messages import ToolMessage
        from langchain_community.document_loaders import PyPDFLoader
        from qdrant_client import models

        llm = ChatOpenAI(model="gpt-5-nano", api_key=OPENAI_API_KEY)
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small", api_key=OPENAI_API_KEY
        )
        collection_name = "cv_resume"
        cv_categories = [
            "HR",
            "DESIGNER",
            "INFORMATION-TECHNOLOGY",
            "TEACHER",
            "ADVOCATE",
            "BUSINESS-DEVELOPMENT",
            "HEALTHCARE",
            "FITNESS",
            "AGRICULTURE",
            "BPO",
            "SALES",
            "CONSULTANT",
            "DIGITAL-MEDIA",
            "AUTOMOBILE",
            "CHEF",
            "FINANCE",
            "APPAREL",
            "ENGINEERING",
            "ACCOUNTANT",
            "CONSTRUCTION",
            "PUBLIC-RELATIONS",
            "BANKING",
            "ARTS",
            "AVIATION",
        ]
        qdrant = QdrantVectorStore.from_existing_collection(
            embedding=embeddings,
            collection_name=collection_name,
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
        )

        @tool
        def search_cv(question: str):
            """Search for relevant resume or CV"""
            results = qdrant.similarity_search(question, k=5)
            return results

        @tool
        def search_cv_with_category(question: str, category: str):
            """Search for relevant resume or CV with category defined in category_list tool/function"""
            results = qdrant.similarity_search(
                question,
                k=5,
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="metadata.category",
                            match=models.MatchValue(value=category),
                        ),
                    ]
                ),
            )
            return results

        @tool
        def category_list() -> list[str]:
            """Get possible CV categories"""
            return cv_categories

        @tool
        def cv_html(doc: Document) -> str:
            """Extract HTML from returned CV/Document"""
            return doc.metadata.get("cv_html")

        if "messages" not in st.session_state:
            st.session_state.messages = []
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["role"] == "ai":
                    st.html(message["content"])
                else:
                    st.markdown(message["content"])

        tools = [search_cv, search_cv_with_category, category_list, cv_html]
        if option == "Recruiter":
            if prompt := st.chat_input("Put the job descriptions"):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                agent = create_react_agent(
                    model=llm,
                    tools=tools,
                    prompt="You will help a recruiter to find the best matching CV based on the job description provided. You can use the tools provided to search the CV. You have to STRICTLY answer in HTML format. In the document returned from the tools, there's cv_html field in the metadata for you to include in your HTML response if you want to display the matching CV.",
                )
                result = agent.invoke(
                    {"messages": st.session_state.messages[-20:]}  # noqa
                )
                answer = result["messages"][-1].content
                st.session_state.messages.append({"role": "ai", "content": answer})
                with st.chat_message("ai"):
                    st.html(answer)
                with st.expander("**Tool Calls:**"):
                    tool_messages = []
                    for message in result["messages"]:
                        if isinstance(message, ToolMessage):
                            tool_messages.append(message.content)
                    st.code(tool_messages)
        elif option == "Applicant":
            prompt = st.chat_input("Ask me recipes question")


st.title("Smart CV Reviewer")
st.write(
    """Modes:
1. Recruiter - Put job description, output best matching CV. With the actual CV shown as html.
2. Applicant - Upload CV. Output which industry is best suited."""
)

# If the widget disappears, so is the state. This is a hack mentioned in:
# https://discuss.streamlit.io/t/session-state-resets-when-i-press-a-button/50516/2
for k, v in st.session_state.items():
    st.session_state[k] = v

if not st.session_state.get("token") or st.session_state.token != DISCORD_CHANNEL_NAME:
    st.text_input("Enter our discord channel name - needed for auth:", key="token")
    st.write(":red[Incorrect channel name]")
else:
    main_program()
