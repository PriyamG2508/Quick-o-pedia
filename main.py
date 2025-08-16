"""fast api for this app"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from scraper import scrape_wikipedia
from pydantic import BaseModel, Field

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Request model for scraping
class ScrapeRequest(BaseModel):
    topic: str = Field(..., title= "Wikipedia Topic", description="The topic to scrape from Wikipedia", example="Python (programming language)")
    
class ChatRequest(BaseModel):
    topic: str = Field(...,title="Wikipedia Topic",description="The topic of the Wikipedia page to chat about.", min_length=1)
    question: str = Field(...,title="Question",description="The question to ask the AI about the topic.",min_length=1)

# Response model for scraping
class ScrapeResponse(BaseModel):
    topic: str = Field(..., description="The topic that was scraped.", example="Artificial intelligence")
    content_length: int = Field(..., description="The total number of characters in the scraped content.", example=75321)
    content: str = Field(..., description="The cleaned text content from the Wikipedia page.")

class ChatResponse(BaseModel):
    topic: str = Field(..., description="The topic that was discussed.", example="History of Python (programming language)")
    question: str = Field(..., description="The question that was asked.", example="Who is the creator of Python?")
    answer: str = Field(..., description="The AI-generated answer.")
    
@app.get("/")
def read_root():
    return {"message": "Welcome to the Quick o Pedia API!"}

@app.post("/scrape", response_model=ScrapeResponse, tags=["Wikipedia"])
async def scrape(topic: ScrapeRequest):
    """
    Scrape a Wikipedia page for the given topic.
    """
    try:
        content = scrape_wikipedia(topic.topic)
        if not content:
            raise HTTPException(status_code=404, detail="Topic not found or no content available.")
        
        return ScrapeResponse(
            topic=topic.topic,
            content_length=len(content),
            content=content
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/chat", response_model=ChatResponse, tags=["Wikipedia"])
async def chat_with_wikipedia(request: ChatRequest):
    """
    Ask a question about a Wikipedia topic and get an AI-generated answer.
    """
    try:
        from langchain_rag import ask_question_langchain  
        answer = ask_question_langchain(request.topic, request.question)
        
        return ChatResponse(
            topic=request.topic,
            question=request.question,
            answer=answer
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))