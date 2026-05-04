from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from uuid import uuid4
import tempfile

import requests
import os

def download_file(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        raise

    content_type = response.headers.get("content-type", "")
    if "pdf" in content_type:
        ext = ".pdf"
    elif "text" in content_type:
        ext = ".txt"
    else:
        raise ValueError("Unsupported file type")

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    temp.write(response.content)
    temp.close()
    return temp.name

async def pdf_to_chunk(file_path: str,doc_id: int):
    # load document
    temp_file = None
    try:
        temp_file = download_file(file_path)
    except Exception as e:
        raise
    ext = temp_file.split(".")[-1].lower()
    docs = []
    try:
        if ext == "pdf":
            loader = PyPDFLoader(temp_file)
            docs = loader.load()
            if not docs or not any(d.page_content.strip() for d in docs):
                raise ValueError("This PDF appears to be scanned")

            for d in docs:
                d.metadata = {
                    "page_number": d.metadata.get("page", 0)
                }

        elif ext == "txt":

            with open(temp_file, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

            docs.append(
                Document(
                    page_content=text,
                    metadata={"page_number": 0}
                )
            )
        # add pagelevel metadata
        for doc in docs:
            doc.metadata["document_id"] = str(doc_id)

        # Splitt Chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size = 700,
            chunk_overlap=100
        )

        chunks = splitter.create_documents(
            [doc.page_content for doc in docs],
            metadatas=[doc.metadata for doc in docs]
        )
        # Add chunk level metadata
        for idx, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"]= str(uuid4())
            chunk.metadata["chunk_index"]= idx

        return chunks
    except Exception as e:
        raise
    finally:
        # This ensures the file is deleted even if the loader crashes
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)