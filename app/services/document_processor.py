from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pdf2image import convert_from_path
from langchain_core.documents import Document
from uuid import uuid4
import tempfile
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
import requests
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
    temp_file = None
    try:
        temp_file = download_pdf(file_path)
        docs = []
        try:
            loader = PyPDFLoader(temp_file)
            docs = loader.load()

            if not docs or not any(d.page_content.strip() for d in docs):
                docs = []
        except Exception:
            docs = []
        
        if not docs:
            print("🧠 Using OCR...")

            images = convert_from_path(temp_file, dpi=200, fmt="jpeg")

            for i, img in enumerate(images):
                text = pytesseract.image_to_string(
                    img, config="--oem 3 --psm 6"
                )
                docs.append(
                    Document(
                        page_content= text,
                        metadata= {"page_number": i}
                    )
                )
        else:
            print("✅ Text PDF detected")

            # Normalize metadata format
            for d in docs:
                d.metadata = {
                    "page_number": d.metadata.get("page", 0)
                }
        # add pagelevel metadata
        for doc in docs:
            doc.metadata["document_id"] = str(doc_id)

        # Splitt Chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size = 900,
            chunk_overlap=180
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

    finally:
        # This ensures the file is deleted even if the loader crashes
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)