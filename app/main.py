import os
from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
import motor.motor_asyncio
from urllib.parse import quote_plus

app = FastAPI(
    title="Fastapi and mongodb demo API",
    summary="A sample application showing how to use FastAPI to add a ResT API to a MongoDB collection.",
)

# MongoDB setup
# Access MongoDB credentials from environment variables
raw_mongodb_url = os.getenv("DB_URL", "mongodb://localhost:27017")
mongodb_user = os.getenv("DB_USERNAME", "root")
mongodb_password = os.getenv("DB_PASSWORD", "pw")

print(f"mongodb_url : {raw_mongodb_url}")
print(f"mongodb_user : {mongodb_user}")
print(f"mongodb_password : {mongodb_password}")

# Encode username & password
encoded_user = quote_plus(mongodb_user)
encoded_password = quote_plus(mongodb_password)

# Construct the MongoDB URI
if "@" in raw_mongodb_url:
    # If DB_URL already contains credentials, use it as is
    mongodb_url = raw_mongodb_url
else:
    mongodb_url = f"mongodb://{encoded_user}:{encoded_password}@{raw_mongodb_url.split('mongodb://')[1]}"

print(f"Using MongoDB URL: {mongodb_url}")


# SSL certificate path (adjust this path based on where you place the certificate in your Docker container)
ssl_cert_path = "/app/certs/global-bundle.pem"

# Initialize MongoDB client with conditional SSL
client_options = {
    "tlsCAFile": ssl_cert_path,
    "tls": True
} if os.path.exists(ssl_cert_path) else {}

client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_url, **client_options)

db = client.college
word_collection = db.get_collection("word")


class WordModel(BaseModel):
    """Model for word data."""
    word: str

class WordUpdateModel(BaseModel):
    word: str = None


@app.get("/api/words", response_model=List[WordModel], summary="Get all words")
async def get_all_words():
    words = await word_collection.find().to_list(100)
    return [WordModel(**word) for word in words]


@app.get("/api/words/{word_id}", response_model=WordModel, summary="Get a word by ID")
async def get_word(word_id: str):
    word = await word_collection.find_one({"_id": word_id})
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    return WordModel(**word)


@app.post("/api/words", response_model=WordModel, summary="Create a new word")
async def create_word(word: WordModel):
    result = await word_collection.insert_one(word.dict())
    new_word = await word_collection.find_one({"_id": result.inserted_id})
    return WordModel(**new_word)


@app.put("/api/words/{word_id}", response_model=WordModel, summary="Update an existing word")
async def update_word(word_id: str, word: WordUpdateModel):
    update_data = {k: v for k, v in word.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await word_collection.update_one({"_id": word_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Word not found")

    updated_word = await word_collection.find_one({"_id": word_id})
    return WordModel(**updated_word)


@app.delete("/api/words/{word_id}", summary="Delete a word")
async def delete_word(word_id: str):
    result = await word_collection.delete_one({"_id": word_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Word not found")
    return {"message": "Word deleted successfully"}

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
    Ensure the database connection is established before performing operations.
    """
    try:
        # Test the database connection
        await client.server_info()  # This will raise an exception if the connection fails
        print("MongoDB connection established successfully.")

        # Check if the collection is empty
        existing_word = await word_collection.find_one({"word": {"$exists": True}})
        if not existing_word:
            # Seed the database with an initial value
            await word_collection.insert_one({"word": "Serverless Salad Infrapal World"})
            print("Initialized word collection with default word value.")
        else:
            print("Word collection already initialized.")

    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        # Optionally, terminate the application if the database connection is critical
        raise RuntimeError("Application startup failed due to database connection issues.") from e
