# Civie Chatbot

A comprehensive chatbot API with RAG (Retrieval-Augmented Generation) capabilities, document ingestion, and customer support features built with FastAPI.

## Features

- 🤖 **Intelligent Chatbot**: Advanced conversational AI with context awareness
- 📚 **Document Ingestion**: Support for PDF, DOCX, and various document formats
- 🔍 **RAG System**: Retrieval-Augmented Generation for accurate responses
- 💾 **Vector Database**: Efficient document storage and retrieval using Qdrant
- 📊 **MongoDB Logging**: Comprehensive logging and monitoring
- 🔒 **Security Middleware**: Built-in security and performance monitoring
- 🌐 **RESTful API**: Full-featured REST API with FastAPI
- 📝 **Patient Management**: Healthcare-focused patient information management

## Installation

### From PyPI

```bash
pip install civie-chatbot
```

### From Source

```bash
git clone https://github.com/civie/civie-chatbot.git
cd civie-chatbot
pip install -e .
```

## Quick Start

### Using as a Library

```python
from civie_chatbot import create_app, initialize_chatbot, process_chat_message

# Initialize the chatbot
chatbot = initialize_chatbot({"debug": True})
print(chatbot['status'])

# Process a chat message
response = await process_chat_message(
    message="Hello, I need help with my account",
    session_id="user-123"
)
print(response['answer'])
```

### Using as a FastAPI Application

```python
from civie_chatbot import create_app
import uvicorn

# Create the app
app = create_app(
    title="My Chatbot API",
    version="1.0.0"
)

# Run the server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Document Ingestion

```python
from civie_chatbot import ingest_documents

# Ingest documents
result = await ingest_documents(
    file_paths=["document1.pdf", "document2.pdf"],
    collection_name="knowledge_base",
    chunk_size=1000,
    chunk_overlap=200
)
print(result['status'])
```

### Query Documents

```python
from civie_chatbot import query_documents

# Query the knowledge base
results = await query_documents(
    query="What is the refund policy?",
    collection_name="knowledge_base",
    top_k=5
)

for doc in results['documents']:
    print(doc['text'])
```

## Available Services

The package exports the following services that you can use directly:

- `ChatService` - Handle chat interactions
- `CollectionService` - Manage document collections
- `DatabaseService` - Database operations
- `MongoService` - MongoDB-specific operations
- `S3Service` - AWS S3 file operations
- `AsyncIngestionService` - Asynchronous document ingestion
- `LLMService` - Language model interactions
- `RAGService` - Retrieval-Augmented Generation
- `EmbeddingService` - Generate embeddings
- `ChunkingService` - Text chunking utilities
- `PatientService` - Patient management

## API Endpoints

When running as a FastAPI application, the following endpoints are available:

- `GET /health` - Health check endpoint
- `POST /api/chat` - Chat with the bot
- `POST /api/ingest` - Ingest documents
- `GET /api/collections` - List collections
- `POST /api/collections` - Create a collection
- `DELETE /api/collections/{name}` - Delete a collection
- `GET /api/patients` - List patients
- `POST /api/patients` - Create patient record

For complete API documentation, visit `/docs` (Swagger UI) or `/redoc` (ReDoc) when running the server.

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=civie_chatbot

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# AWS Configuration (if using S3)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key
```

## Development

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
flake8 .
```

## Docker Support

### Build Docker Image

```bash
docker build -t civie-chatbot .
```

### Run with Docker Compose

```bash
docker-compose up
```

## Requirements

- Python >= 3.8
- FastAPI
- MongoDB
- Qdrant (Vector Database)
- OpenAI API Key (or compatible LLM service)

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## Support

For issues, questions, or support:
- 📧 Email: support@civie.com
- 🐛 Issues: https://github.com/civie/civie-chatbot/issues
- 📖 Documentation: https://docs.civie.com

## Changelog

### Version 2.0.0
- Initial PyPI release
- Complete RAG system implementation
- MongoDB logging integration
- Enhanced security middleware
- Patient management features

## Authors

**Civie Team**

---

Made with ❤️ by the Civie Team
