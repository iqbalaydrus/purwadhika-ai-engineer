import json
import os

import pandas as pd

from dotenv import load_dotenv
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models as qm


load_dotenv()
QDRANT_COLLECTION_NAME = "cv_resume"

data = pd.read_csv("data/Resume.csv").drop("Resume_html", axis=1)
docs: list[Document] = []
for _, row in data.iterrows():
    metadata = {
        "id": int(row["ID"]),
        "category": str(row["Category"]),
    }
    docs.append(
        Document(
            page_content=str(row["Resume_str"]),
            metadata=metadata,
        )
    )
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""],
)
docs = splitter.split_documents(docs)

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=os.getenv("OPENAI_API_KEY"),
)
vector_client = QdrantClient(
    api_key=os.getenv("QDRANT_API_KEY"),
    url=os.getenv("QDRANT_URL"),
)
vector_client.create_collection(
    collection_name=QDRANT_COLLECTION_NAME,
    vectors_config=qm.VectorParams(size=1536, distance=qm.Distance.COSINE),
)
vector_client.create_payload_index(
    collection_name=QDRANT_COLLECTION_NAME,
    field_name="metadata.id",
    field_schema="integer",
)
vector_client.create_payload_index(
    collection_name=QDRANT_COLLECTION_NAME,
    field_name="metadata.category",
    field_schema="keyword",
)
vector_db = QdrantVectorStore(
    client=vector_client,
    embedding=embeddings,
    collection_name=QDRANT_COLLECTION_NAME,
)
vector_db.add_documents(docs)
