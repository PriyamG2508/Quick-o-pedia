"""
RAG model for chat functionality with Wikipedia scraped content.
"""
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq  
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from scraper import scrape_wikipedia
from langchain.schema import Document
from dotenv import load_dotenv
import os
import streamlit as st

@st.cache_resource
def get_cached_embeddings():
    """Load embeddings model once and reuse it"""
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Converting the scraped text to document object
def convert_text_to_documents(text, topic_name):
    chunks = split_text(text)
    documents = []
    for i, chunk in enumerate(chunks):
        doc = Document(
            page_content=chunk,
            metadata={
                "source": f"Wikipedia: {topic_name}",
                "chunk_id": i,
                "topic": topic_name
            }
        )
        documents.append(doc)
    return documents

# Function to split text into manageable chunks
def split_text(text, chunk_size=1000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    return text_splitter.split_text(text)

def setup_vector_store(topic_name):
    embeddings = get_cached_embeddings()  
    topic_key = topic_name.lower().replace(' ', '_')
    persist_dir = f"chroma_db/{topic_key}"  
    vector_store = Chroma(
        embedding_function=embeddings, 
        persist_directory=persist_dir
    )
    return vector_store

def populate_vector_store(text, topic_name):
    vector_store = setup_vector_store(topic_name)
    
    # Check if data already exists
    try:
        existing = vector_store.get()
        if existing['ids']:  # Data exists, reuse it
            return vector_store
    except:
        pass  # No existing data, create new
    
    # Create new data
    documents = convert_text_to_documents(text, topic_name)
    vector_store.add_documents(documents)
    return vector_store

def setup_rag_chain(vector_store):
    # Load environment variables again to be sure
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", None)
    
    try:
        # Initialize the Groq client with explicit API key
        client = ChatGroq(
            api_key=api_key,  
            model_name="llama-3.3-70b-versatile",  
            temperature=0.7,
        )
    except Exception as e:
        raise

    # Define the prompt template
    prompt_template = PromptTemplate(
        template= """You are a helpful assistant answering question based on the wikipedia content.

        Content: {context}
        Question: {question}
        
        Instructions:
        - Answer based ONLY on the provided context
        - If information isn't in the context, say so clearly
        - Be conversational and comprehensive
        - Include relevant details from the context
        Answer: """,
        input_variables=["context", "question"]
    )

    # RetrievalQA chain setup
    qa_chain = RetrievalQA.from_chain_type(
        llm=client,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": prompt_template},
        return_source_documents=True
    )

    return qa_chain

def ask_question_langchain(topic, question):
    # Scrape Wikipedia content
    content = scrape_wikipedia(topic)
    if not content:
        return "Sorry, couldn't find information about that topic."
    
    # Setup RAG system
    vector_store = populate_vector_store(content, topic)
    qa_chain = setup_rag_chain(vector_store)
    
    # Get answer
    try:
        result = qa_chain({"query": question})
        return result["result"]
    except Exception as e:
        return f"Error getting response: {str(e)}"
    
