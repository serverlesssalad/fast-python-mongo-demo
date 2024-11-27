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

print(f"mongodb_url : {mongodb_url}")
print(f"mongodb_user : {mongodb_user}")
print(f"mongodb_password : {mongodb_password}")

# SSL certificate path (adjust this path based on where you place the certificate in your Docker container)
ssl_cert_path = "/app/certs/global-bundle.pem"

# MongoDB client initialization with conditional SSL configuration
if os.path.exists(ssl_cert_path):
    client = motor.motor_asyncio.AsyncIOMotorClient(
        mongodb_url, 
        username=mongodb_user, 
        password=mongodb_password,
        ssl=True,  # Enable SSL
        tlsCAFile=ssl_cert_path  # Provide the path to the certificate
    )
else:
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
