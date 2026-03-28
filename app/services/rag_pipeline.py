from app.services.retriever import get_retriever
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.services.schemas import LLMResponse

model = ChatOpenAI(
    base_url="https://api.euron.one/api/v1/euri",
    model="openai/gpt-oss-120b"
)


def format_context(docs):
    context = ""
    for i, doc in enumerate(docs):
        page = doc.metadata.get("page_number")
        page_display = page + 1 if isinstance(page, int) else "unknown"
                    
        context += f"""
        [Chunk {i+1}]
        Page_number: {page_display}
        Content: {doc.page_content}
        """
    
    return context

async def run_rag(query: str, doc_id: int):
    retriever = get_retriever(doc_id)
    docs = await retriever.ainvoke(query)

    if not docs:
        return {
            "answer": "No relevant information found",
            "sources": []
        }
    context = format_context(docs)

    template = PromptTemplate(
        template = """You are an AI assistant.
        Answer the question ONLY using the provide context.
        If the answer is not in the context, say "I don't know.".
        Context:
        {context}
        
        Question:
        {query}""", 
        input_variables=["context","query"]
    )

    parser = StrOutputParser()
    structur_model = model.with_structured_output(LLMResponse)

    chain = template | structur_model
    result = await chain.ainvoke({"context": context, "query": query})
    return result