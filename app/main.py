import os
from fastapi import FastAPI
from pydantic import BaseModel
import motor.motor_asyncio

app = FastAPI(
    title="Fastapi and mongodb demo API",
    summary="A sample application showing how to use FastAPI to add a ResT API to a MongoDB collection.",
)

# MongoDB setup
# Access MongoDB credentials from environment variables
mongodb_url = os.getenv("DB_URL", "mongodb://localhost:27017")
mongodb_user = os.getenv("DB_USER", "root")
mongodb_password = os.getenv("DB_PASSWORD", "pw")

client = motor.motor_asyncio.AsyncIOMotorClient(
    mongodb_url, 
    username=mongodb_user, 
    password=mongodb_password
)
db = client.college
word_collection = db.get_collection("word")


class WordModel(BaseModel):
    """Model for word data."""
    word: str


@app.get(
    "/hello",
    response_description="Get hello world",
    response_model=WordModel,
)
async def get_helloworld():
    """
    Returns a hello world message. If word exists in the collection, return 'Hello {word}', 
    otherwise return 'Hello None'.
    """
    word_document = await word_collection.find_one({})  # Find the first document in the collection
    
    if word_document and "word" in word_document:
        word = word_document["word"]
    else:
        word = "None"
    
    return WordModel(word=f"Hello {word}")

@app.get("/health", response_description="Health check")
async def health_check():
    """
    Returns the health status of the application.
    """
    try:
        # Check MongoDB connection
        await client.server_info()  # Raises an exception if the MongoDB connection is down
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "details": str(e)}


@app.on_event("startup")
async def startup_db():
    """
    Initialize the word collection at application startup if it is empty.
    """
    # Check if the collection is empty
    existing_word = await word_collection.find_one({"word": {"$exists": True}})
    if not existing_word:
        # Initialize the word field if no document exists
        await word_collection.insert_one({"word": "Serverless Salad Infrapal World"})
        print("Initialized word collection with default word value.")