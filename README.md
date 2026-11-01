<div align="center">

# 🎓 CampusGPT

### Your Campus. One Intelligent Platform.

**An AI-powered Campus ERP with a grounded AI assistant — connecting academic management, campus information, and student support in one unified experience.**

<p>
  <img src="https://img.shields.io/badge/Campus%20ERP-Intelligent%20Campus-7657E8?style=for-the-badge" alt="Campus ERP"/>
  <img src="https://img.shields.io/badge/Frontend-React%20%2B%20JavaScript-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React"/>
  <img src="https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Database-PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
</p>

<p>
  <a href="#-about-campusgpt">About</a> •
  <a href="#-the-campus-experience">Campus Experience</a> •
  <a href="#-features">Features</a> •
  <a href="#-ai-powered-campus-assistant">AI Assistant</a> •
  <a href="#-technology">Technology</a>
</p>

</div>

---

## 🌌 About CampusGPT

CampusGPT is an intelligent, unified campus management platform designed to simplify the academic experience for students, faculty, and administrators.

It brings essential campus activities — including attendance, timetables, assignments, notices, academic documents, and student information — together in one connected environment.

At its core, CampusGPT combines the capabilities of a traditional **Campus ERP** with an **AI-powered assistant**. Instead of navigating multiple sections or searching through scattered documents, users can access relevant campus information and interact with it through a conversational interface.

The platform is designed around three ideas:

- **Connect** — bring academic and administrative activities into one platform.
- **Simplify** — make campus information and everyday tasks easier to access.
- **Assist intelligently** — use AI to help users find relevant, institution-specific information.

## 🎯 The Campus Experience

CampusGPT provides a role-oriented experience for the different people who make up an academic institution.

<table>
<tr>
<td width="33%" align="center">

### 🎓 Students

A personal academic space to follow schedules, attendance, assignments, notices, documents, and opportunities.

</td>
<td width="33%" align="center">

### 👩‍🏫 Faculty

A workspace for academic activities, classroom information, attendance, assignments, and communication with students.

</td>
<td width="33%" align="center">

### 🛡️ Administrators

A centralised view of campus operations, users, academic information, and institutional activities.

</td>
</tr>
</table>

## ✨ Features

### 🔐 1. Secure Authentication & Role-Based Access

- User registration and sign-in.
- Email OTP verification.
- Google OAuth authentication.
- JWT-based authentication.
- Role-aware access for students, faculty, and administrators.
- Protected access to personal and institutional information.

### 🎓 2. Student Dashboard

A central academic dashboard that brings a student's important information together.

- Personal academic overview.
- Attendance summaries.
- Today's and upcoming timetable.
- Assignment deadlines and submission status.
- Latest campus notices.
- Academic documents and learning resources.
- Relevant academic updates and opportunities.

### 👩‍🏫 3. Faculty Dashboard

A dedicated workspace to support teaching and academic responsibilities.

- Class and timetable overview.
- Attendance management.
- Assignment creation and submission tracking.
- Student-related academic information.
- Notices and classroom communication.
- Access to relevant academic documents.

### 🛡️ 4. Admin Dashboard

A unified administrative workspace for managing campus information and activities.

- Student and faculty information management.
- Academic and course information.
- Timetable and attendance oversight.
- Notices and announcements.
- Document and institutional information management.
- Overview of important campus activities.

### 📅 5. Timetable Management

- View daily and weekly class schedules.
- Organise timetable information by class, subject, and faculty.
- Access upcoming academic sessions.
- Keep timetable information available from the relevant dashboards.

### 📊 6. Attendance Management

- Record and manage attendance.
- View attendance by subject and academic period.
- Track attendance summaries and percentages.
- Help students understand their attendance status.
- Support faculty and administrative attendance workflows.

### 📝 7. Assignment Management

- Publish assignments with descriptions and deadlines.
- Share assignment-related resources.
- Submit and manage student submissions.
- Track submission status and deadlines.
- Keep assignment information organised by course or subject.

### 📢 8. Notices & Notifications

- Publish campus-wide and targeted notices.
- Share academic announcements and important updates.
- Keep students and faculty informed.
- Organise notices by category and relevance.

### 📁 9. Document Management

- Upload and organise academic documents.
- Support common document formats such as PDF and DOCX.
- Access course materials, notes, notices, and institutional documents.
- Make relevant documents available to authorised users.
- Provide document content as a knowledge source for the AI assistant.

### 🤖 10. CampusGPT AI Assistant

A conversational assistant designed around campus-specific questions and tasks.

- Ask questions in natural language.
- Find relevant academic and institutional information.
- Get assistance with timetables, attendance, assignments, notices, and documents.
- Route questions to the appropriate information source.
- Provide responses grounded in authorised campus information.
- Support context-aware assistance for different user roles.

### 🔎 11. Intelligent Document Search (RAG)

Retrieval-Augmented Generation (RAG) helps the assistant answer questions using relevant institutional documents.

- Document ingestion and processing.
- Text extraction and chunking.
- Embedding generation.
- Semantic similarity search.
- Context retrieval from relevant documents.
- Source-grounded answer generation.

### 🧭 12. Intent Detection & Intelligent Routing

CampusGPT is designed to understand the purpose behind a user's question and select an appropriate response path.

- Identify the intent of a user query.
- Distinguish campus-data questions from document questions and general queries.
- Route requests to relevant backend tools or retrieval systems.
- Apply user permissions before accessing protected information.
- Return responses based on the selected source.

### 📈 13. Academic Analytics

- Attendance and academic summaries.
- Visual insights into academic activity.
- Progress trends and useful indicators.
- Data-driven views for students, faculty, and administrators.

### 🎯 14. Placement & Career Opportunities

- Placement-related information.
- Company and opportunity details.
- Internship discovery.
- Hackathon and competition updates.
- Centralised access to career-related opportunities.

### 🧠 15. Course Recommendation System

- Explore relevant courses and learning resources.
- Discover learning paths based on academic interests.
- Support informed learning and skill-development choices.

### 🖼️ 16. Visual Learning Workspace

An interactive learning environment designed to make complex academic topics easier to explore.

- Visual explanations of concepts.
- Structured learning content.
- Interactive learning experiences.
- A richer companion to traditional study materials.

### 🎙️ 17. Voice Interaction

- Voice-based interaction with the CampusGPT assistant.
- Natural conversational access to campus information.
- An additional interaction mode for hands-free assistance.

## 🧠 AI-Powered Campus Assistant

CampusGPT is designed to go beyond a conventional chatbot.

A campus question may require live academic data, information from an uploaded document, or a general explanation. The assistant uses intent detection and routing to select the appropriate path.

```mermaid
flowchart TD
    A["User asks a question"] --> B["CampusGPT AI Assistant"]
    B --> C["Intent Detection"]
    C --> D["Campus ERP Data"]
    C --> E["Document Retrieval (RAG)"]
    C --> F["General AI Assistance"]
    D --> G["Authorised Campus Context"]
    E --> G
    F --> H["General Explanation"]
    G --> I["Context-Grounded Response"]
    H --> J["Response to User"]
    I --> J
```

### Grounded, role-aware responses

- Campus-specific answers are based on available institutional data and documents.
- Access permissions are enforced before protected information is retrieved.
- The assistant is designed not to invent campus facts when the required information is unavailable.
- General AI explanations are distinct from answers sourced from institutional records.

## 🏗️ High-Level Architecture

CampusGPT uses a modular application architecture with a React frontend, FastAPI backend, and PostgreSQL database.

```mermaid
flowchart TB
    U["Students · Faculty · Administrators"]
    FE["React.js Frontend"]
    API["FastAPI Backend"]
    AUTH["Authentication & Role Access"]
    ERP["Campus ERP Modules"]
    AI["AI Assistant & Intent Router"]
    RAG["Document Retrieval Pipeline"]
    DB[("PostgreSQL")]
    VEC[("pgvector")]
    MODEL["AI / LLM Provider"]

    U --> FE
    FE --> API
    API --> AUTH
    API --> ERP
    API --> AI
    AUTH --> DB
    ERP --> DB
    AI --> RAG
    RAG --> DB
    RAG --> VEC
    AI --> MODEL
```

## 🛠️ Technology

| Layer | Technologies |
|---|---|
| Frontend | React.js, JavaScript (JSX), Vite |
| UI & Styling | Tailwind CSS v4 |
| Icons | Lucide React |
| Backend | Python, FastAPI |
| Data validation | Pydantic |
| ORM | SQLAlchemy 2.x |
| Database migrations | Alembic |
| Primary database | PostgreSQL |
| Vector search | pgvector |
| Authentication | JWT, Google OAuth, Email OTP |
| Realtime communication | WebSocket |
| Reverse proxy | Nginx |
| Containerisation | Docker, Docker Compose |

## 🧱 Design Principles

- **Unified experience:** keep essential campus workflows connected.
- **Role-aware by design:** provide relevant functionality according to user permissions.
- **Security first:** protect student, faculty, and institutional information.
- **Grounded AI:** base campus-specific responses on authorised information sources.
- **Modular architecture:** keep features organised and maintainable.
- **Accessible information:** make academic resources easier to discover and use.

---

<div align="center">

### 🌱 One campus. Connected knowledge. Smarter experiences.

**CampusGPT**  
*Learn · Connect · Thrive*

<sub>An intelligent campus experience for the academic community.</sub>

</div>
