from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def create_gst_chain(llm, retriever=None):
    """
    Creates a LangChain sequence for GST policy Q&A.
    If a retriever is provided, it can be integrated here.
    """
    prompt = PromptTemplate.from_template(
        """You are a GST expert for the Government of Kerala Finance Department.
Answer the following GST policy question based on the provided context.
Always mention the applicable GST rate, HSN code, and relevant notification number when available.

QUESTION: {query}

CONTEXT:
{context}

ANSWER (with specific circular/notification references):"""
    )
    
    # Example of a simple chain, can be expanded to RAG
    chain = (
        {"context": lambda x: x.get("context", ""), "query": lambda x: x.get("query", "")}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain
