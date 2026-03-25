from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from uuid import uuid4
import tempfile
import requests
import tempfile
import os

def download_pdf(url):
    response = requests.get(url)
    response.raise_for_status()

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp.write(response.content)
    temp.close()
    return temp.name

async def pdf_to_chunk(file_path: str,doc_id: int):
    # load document
    try:
        temp_file = download_pdf(file_path)
        loader = PyPDFLoader(temp_file)
        docs = loader.load()

        # add pagelevel metadata
        for doc in docs:
            doc.metadata = {
                "document_id": str(doc_id),
                "page": doc.metadata.get("page")
            }

        # Splitt Chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size = 900,
            chunk_overlap=180
        )

        chunks = splitter.split_documents(docs)

        # Add chunk level metadata
        for idx, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"]= str(uuid4())
            chunk.metadata["chunk_index"]= idx

        return chunks

    finally:
        # This ensures the file is deleted even if the loader crashes
        if os.path.exists(temp_file):
            os.remove(temp_file)