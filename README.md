# ShopBot

A customer support chatbot API for e-commerce stores, built with FastAPI and the OpenAI Assistants API. Handles product queries, shipping information, and return requests with persistent multi-turn conversation support.

## 🤖 Bot Capabilities

#### **Customer Support Topics**
- **Returns**: Unopened items returnable within 30 days via account dashboard, prepaid labels provided, refunds processed in 5–7 business days
- **Shipping**: Free on orders over $50, 2–5 business days domestically
- **Product Queries**: General product and store support

#### **Conversation Management**
- **Persistent Threads**: Multi-turn conversations maintained via OpenAI thread IDs
- **Stateless API**: Pass `thread_id` across requests to preserve context without server-side session storage
- **Auto Thread Creation**: Omit `thread_id` to automatically start a new conversation

#### **Reliability**
- **Exponential Backoff Polling**: Starts at 0.5s, caps at 2s per poll cycle
- **60s Safety Timeout**: Prevents hung requests from blocking indefinitely
- **Run Status Validation**: Explicit error if assistant run ends in a non-completed state

## ⚡ Technical Details

#### **Architecture**
- **Single-file API**: Minimal footprint with all logic in `main.py`
- **Async Throughout**: Built entirely on `asyncio` and FastAPI's async support
- **Assistant Caching**: OpenAI Assistant created once and reused across all requests

#### **API Design**
- **RESTful Endpoints**: Clean separation between thread creation and chat
- **Pydantic Validation**: Request and response models with full type safety
- **Configurable Model**: Switch OpenAI model via environment variable without code changes

## 🛠️ Tech Stack

- FastAPI 0.115.0
- Uvicorn 0.30.6
- OpenAI Python SDK 2.5.0
- Pydantic 2.9.2
- Python 3.10+

## 🎯 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check — returns status and active model |
| POST | `/threads` | Create a new conversation thread |
| POST | `/chat` | Send a message and receive a response |

### POST `/chat`

**Request:**
```json
{
  "message": "What is your return policy?",
  "thread_id": "thread_abc123"
}
```
> Omit `thread_id` to start a new conversation thread.

**Response:**
```json
{
  "response": "You can return unopened items within 30 days...",
  "thread_id": "thread_abc123"
}
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys)

### Installation
```bash
# Clone the repository
git clone https://github.com/<your-username>/shopbot.git
cd shopbot

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=<your-openai-api-key>
export ASSISTANT_MODEL=gpt-4o-mini  # optional, this is the default

# Start development server
uvicorn main:app --reload
```

**Application will be available at `http://localhost:8000`**

## 📁 Project Structure

```
ShopBot/
├── main.py              # FastAPI app — endpoints, assistant logic, polling
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container build config
└── .dockerignore        # Files excluded from Docker build
```

## 🏗️ Build & Deployment

```bash
# Build Docker image
docker build -t shopbot .

# Run container
docker run -p 8080:8080 -e OPENAI_API_KEY=<your-openai-api-key> shopbot
```

**Application will be available at `http://localhost:8080`**
