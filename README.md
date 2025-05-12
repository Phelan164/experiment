# Experiment: Music Instrument Chatbot System

## Overview
This project consists of two main services:

- **Mock API Service**: Serves order and customer information for testing and development.
- **Chatbot Backend Service**: Provides a chatbot API to help users find music instrument products and track their orders.
- **Frontend Chat App**: A simple Next.js web app for chatting with the chatbot backend.

## Setup Instructions

### 1. Install Requirements
Before running any service, make sure to install the required Python packages:

```sh
pip install -r requirements.txt
```

### 2. Start the Mock API Service
This service provides endpoints for order and customer data.

```sh
python3 mock_api/mock_api.py
```

The mock API will start (by default) on port 8000.

### 3. Start the Chatbot API Service
This service provides the chatbot backend for product search and order tracking.

```sh
cd chatbot_backend
uvicorn app:app --reload --host 0.0.0.0 --port 8001
```

The chatbot API will be available at `http://localhost:8001`.

### 4. Run the Test Client App
You can test the chatbot service using the provided test client:

```sh
cd chatbot_backend
python test.py
```

### 5. Set Up and Run the Frontend Chat App
A simple Next.js frontend is provided for chatting with the backend.

```sh
cd chatbot_frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000` by default. It connects to the chatbot backend at `http://localhost:8001`.

## System Overview
- The **mock API service** serves as a backend to provide order and customer information for the chatbot to use.
- The **chatbot backend service** helps users find music instrument products and track their orders by interacting with the mock API.
- The **frontend chat app** provides a user-friendly web interface for chatting with the chatbot backend.

## Notes
- Ensure all services are running for full functionality.
- The chatbot service depends on the mock API for order-related queries.
- The frontend expects the chatbot backend to be running at `http://localhost:8001`.
- Make sure to configure any required environment variables (such as API keys) in a `.env` file (which should not be committed to git).

---

Feel free to contribute or open issues for improvements!
