# VIPOE BACKEND

A **FastAPI** backend service for the **Vietnamese Poetry Web Platform with AI Assistance – VIPOE**, combining traditional Vietnamese poetry creation with modern **AI assistance** and **web search capabilities**.

---

## 🌸 Overview

**VIPOE** is a platform for poetry lovers to create, explore, and engage with traditional and modern Vietnamese poetry. The system leverages **Google Gemini AI** and **web RAG (Retrieval-Augmented Generation)** to guide users in poetic creation and literary exploration.

---

## ✨ Features

### 🔐 Core Functionality
- **User Management**: Register, login, JWT-based auth, email verification
- **Poetry CRUD**: Create, view, update, delete poems across multiple formats
- **Collections**: Organize and save favorite poems
- **Genres & Tags**: Support traditional genres and tagging system
- **Community**: Comment system and notifications

### 🤖 AI & Search
- **AI Assistant**: Smart chat powered by **Google Gemini**
- **Web RAG**: Real-time web search using **Google Custom Search**
- **Summarization**: Context summarization and enhancement
- **Poetic Guidance**: AI tuned for Vietnamese literary traditions

### 🛠️ Technical Features
- **FastAPI REST API**: Clean architecture with versioning
- **Database**: PostgreSQL with **SQLAlchemy** ORM and **Alembic** migrations
- **Auth**: JWT tokens & password hashing (passlib)
- **Email Service**: SMTP for verification and notifications
- **File Upload**: Cloudinary integration
- **Deployment**: Dockerized & deployed via **Fly.io** + **GitHub Actions**

---

## ⚙️ Tech Stack

| Component       | Technology            |
|----------------|------------------------|
| Backend         | FastAPI                |
| Database        | PostgreSQL + SQLAlchemy |
| AI Assistant    | Google Gemini AI       |
| Web RAG         | Trafilatura + Google Search |
| Auth            | JWT + passlib          |
| File Storage    | Cloudinary             |
| Email           | SMTP                   |
| Containerization| Docker + Docker Compose |
| Deployment      | Fly.io + GitHub Actions |

---

## 🧩 API Structure

```text
/api/v1/
├── auth/ # Auth routes
│ ├── register
│ ├── login
│ └── verify-email
├── user/ # User profile
│ └── profile
├── poem/ # Poem operations
│ ├── /
│ ├── /search
│ ├── /feed
│ └── /genres
├── collection/ # Saved poems
│ └── /
└── assistant/ # AI assistant
└── /chat
```

---

## 🚀 Getting Started

#### Local Setup (Linux)
1. ``python -m venv venv``
2. ``source venv/bin/activate``
3. ``pip install -r requirements.txt``
4. ``docker-compose up --build``
5. ``docker-compose exec backend alembic upgrade head``
5. ``docker-compose exec backend alembic revision --autogenerate -m "Init database"``
6. ``psql -U johnvo -d vipoedb -h localhost -p 5433 -f app/init_data.sql``
