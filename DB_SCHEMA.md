# CampusGPT — Database Schema

Database: **PostgreSQL 15/16** with the **`pgvector`** extension enabled.

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

This document defines the tables, key columns, types, and relationships. Treat it as the reference when writing SQLAlchemy models and Alembic migrations — keep column names consistent with what's listed here so generated code across modules doesn't drift.

> For where each table fits in the overall system, see [`ARCHITECTURE.md`](./ARCHITECTURE.md).

---

## Table of Contents

1. [Identity & Access](#1-identity--access)
2. [Academic Structure](#2-academic-structure)
3. [Timetable](#3-timetable)
4. [Attendance](#4-attendance)
5. [Assignments](#5-assignments)
6. [Notices](#6-notices)
7. [Documents & RAG](#7-documents--rag)
8. [AI Chat](#8-ai-chat)
9. [Notifications](#9-notifications)
10. [Misc](#10-misc)
11. [Entity Relationship Summary](#11-entity-relationship-summary)
12. [Indexing Notes](#12-indexing-notes)

---

## 1. Identity & Access

### `users`
| Column | Type | Notes |
|---|---|---|
| id | UUID / SERIAL PK | |
| email | VARCHAR, UNIQUE, NOT NULL | login identifier |
| hashed_password | VARCHAR, NOT NULL | bcrypt hash |
| full_name | VARCHAR, NOT NULL | |
| role | ENUM('ADMIN','FACULTY','STUDENT'), NOT NULL | |
| is_active | BOOLEAN, DEFAULT true | |
| created_at | TIMESTAMPTZ, DEFAULT now() | |
| updated_at | TIMESTAMPTZ | |

### `departments`
| Column | Type | Notes |
|---|---|---|
| id | UUID / SERIAL PK | |
| name | VARCHAR, UNIQUE, NOT NULL | |
| code | VARCHAR, UNIQUE | e.g. `CSE`, `ECE` |
| created_at | TIMESTAMPTZ | |

### `students`
| Column | Type | Notes |
|---|---|---|
| id | UUID / SERIAL PK | |
| user_id | FK → `users.id`, UNIQUE, NOT NULL | one-to-one with users |
| department_id | FK → `departments.id` | |
| roll_number | VARCHAR, UNIQUE, NOT NULL | |
| enrollment_year | INT | |
| semester | INT | |
| created_at | TIMESTAMPTZ | |

### `faculty`
| Column | Type | Notes |
|---|---|---|
| id | UUID / SERIAL PK | |
| user_id | FK → `users.id`, UNIQUE, NOT NULL | one-to-one with users |
| department_id | FK → `departments.id` | |
| designation | VARCHAR | e.g. Professor, Assistant Professor |
| employee_code | VARCHAR, UNIQUE | |
| created_at | TIMESTAMPTZ | |

---

## 2. Academic Structure

### `courses`
| Column | Type | Notes |
|---|---|---|
| id | UUID / SERIAL PK | |
| name | VARCHAR, NOT NULL | e.g. "B.Tech CSE" |
| department_id | FK → `departments.id` | |
| duration_years | INT | |

### `subjects`
| Column | Type | Notes |
|---|---|---|
| id | UUID / SERIAL PK | |
| name | VARCHAR, NOT NULL | |
| code | VARCHAR, UNIQUE, NOT NULL | |
| course_id | FK → `courses.id` | |
| semester | INT | |
| faculty_id | FK → `faculty.id` | primary instructor |
| credits | INT | |

### `classrooms`
| Column | Type | Notes |
|---|---|---|
| id | UUID / SERIAL PK | |
| room_number | VARCHAR, NOT NULL | |
| building | VARCHAR | |
| capacity | INT | |

---

## 3. Timetable

### `timetables`
| Column | Type | Notes |
|---|---|---|
| id | UUID / SERIAL PK | |
| subject_id | FK → `subjects.id`, NOT NULL | |
| faculty_id | FK → `faculty.id`, NOT NULL | |
| classroom_id | FK → `classrooms.id` | |
| day_of_week | ENUM('MON'..'SUN'), NOT NULL | |
| start_time | TIME, NOT NULL | |
| end_time | TIME, NOT NULL | |
| department_id | FK → `departments.id` | for filtering by cohort |
| semester | INT | |

---

## 4. Attendance

### `attendance_sessions`
| Column | Type | Notes |
|---|---|---|
| id | UUID / SERIAL PK | |
| subject_id | FK → `subjects.id`, NOT NULL | |
| faculty_id | FK → `faculty.id`, NOT NULL | who took the session |
| session_date | DATE, NOT NULL | |
| start_time | TIME | |
| end_time | TIME | |
| created_at | TIMESTAMPTZ | |

### `attendance_records`
| Column | Type | Notes |
|---|---|---|
| id | UUID / SERIAL PK | |
| session_id | FK → `attendance_sessions.id`, NOT NULL | |
| student_id | FK → `students.id`, NOT NULL | |
| status | ENUM('PRESENT','ABSENT','LATE','EXCUSED'), NOT NULL | |
| marked_by | FK → `faculty.id` | audit trail |
| marked_at | TIMESTAMPTZ, DEFAULT now() | |

> Unique constraint on `(session_id, student_id)` — one record per student per session.

---

## 5. Assignments

### `assignments`
| Column | Type | Notes |
|---|---|---|
| id | UUID / SERIAL PK | |
| subject_id | FK → `subjects.id`, NOT NULL | |
| faculty_id | FK → `faculty.id`, NOT NULL | |
| title | VARCHAR, NOT NULL | |
| description | TEXT | |
| due_date | TIMESTAMPTZ, NOT NULL | |
| max_marks | INT | |
| attachment_url | VARCHAR | optional file |
| created_at | TIMESTAMPTZ | |

### `assignment_submissions`
| Column | Type | Notes |
|---|---|---|
| id | UUID / SERIAL PK | |
| assignment_id | FK → `assignments.id`, NOT NULL | |
| student_id | FK → `students.id`, NOT NULL | |
| file_url | VARCHAR, NOT NULL | |
| submitted_at | TIMESTAMPTZ, DEFAULT now() | |
| marks_obtained | INT | nullable until graded |
| feedback | TEXT | |
| graded_by | FK → `faculty.id` | |
| graded_at | TIMESTAMPTZ | |

> Unique constraint on `(assignment_id, student_id)`.

---

## 6. Notices

### `notices`
| Column | Type | Notes |
|---|---|---|
| id | UUID / SERIAL PK | |
| title | VARCHAR, NOT NULL | |
| content | TEXT, NOT NULL | |
| posted_by | FK → `users.id`, NOT NULL | |
| target_role | ENUM('ALL','STUDENT','FACULTY'), DEFAULT 'ALL' | |
| department_id | FK → `departments.id` | nullable = all departments |
| is_pinned | BOOLEAN, DEFAULT false | |
| created_at | TIMESTAMPTZ | |
| expires_at | TIMESTAMPTZ | nullable |

---

## 7. Documents & RAG

### `documents`
| Column | Type | Notes |
|---|---|---|
| id | UUID / SERIAL PK | |
| title | VARCHAR, NOT NULL | |
| file_url | VARCHAR, NOT NULL | storage path/URL |
| uploaded_by | FK → `users.id`, NOT NULL | |
| document_type | VARCHAR | e.g. `syllabus`, `notes`, `notice` |
| subject_id | FK → `subjects.id` | nullable, for course material |
| department_id | FK → `departments.id` | nullable |
| file_size_bytes | INT | |
| mime_type | VARCHAR | validated server-side |
| created_at | TIMESTAMPTZ | |

### `document_chunks`
| Column | Type | Notes |
|---|---|---|
| id | UUID / SERIAL PK | |
| document_id | FK → `documents.id`, NOT NULL, ON DELETE CASCADE | |
| content | TEXT, NOT NULL | the chunk's raw text |
| chunk_index | INT, NOT NULL | order within the document |
| embedding | `VECTOR(384)` | dimension matches your embedding model (384 for `all-MiniLM-L6-v2`) |
| metadata | JSONB | page number, section heading, etc. |
| created_at | TIMESTAMPTZ | |

> The `embedding` column requires `pgvector`. Adjust the dimension to match whichever embedding model you standardize on — it must be identical for every row and for query-time embeddings.

---

## 8. AI Chat

### `chat_sessions`
| Column | Type | Notes |
|---|---|---|
| id | UUID / SERIAL PK | |
| user_id | FK → `users.id`, NOT NULL | |
| title | VARCHAR | auto-generated from first message, editable |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

### `chat_messages`
| Column | Type | Notes |
|---|---|---|
| id | UUID / SERIAL PK | |
| session_id | FK → `chat_sessions.id`, NOT NULL, ON DELETE CASCADE | |
| role | ENUM('user','assistant','system'), NOT NULL | |
| content | TEXT, NOT NULL | |
| source_type | ENUM('DB_TOOL','RAG','GENERAL_LLM') | nullable, set for assistant messages |
| source_refs | JSONB | e.g. list of `document_chunks.id` used as citations |
| created_at | TIMESTAMPTZ, DEFAULT now() | |

---

## 9. Notifications

### `notifications`
| Column | Type | Notes |
|---|---|---|
| id | UUID / SERIAL PK | |
| user_id | FK → `users.id`, NOT NULL | recipient |
| title | VARCHAR, NOT NULL | |
| body | TEXT | |
| type | VARCHAR | e.g. `assignment`, `notice`, `attendance` |
| is_read | BOOLEAN, DEFAULT false | |
| created_at | TIMESTAMPTZ | |

---

## 10. Misc

### `events`
| Column | Type | Notes |
|---|---|---|
| id | UUID / SERIAL PK | |
| title | VARCHAR, NOT NULL | |
| description | TEXT | |
| event_date | TIMESTAMPTZ, NOT NULL | |
| department_id | FK → `departments.id` | nullable = campus-wide |
| created_by | FK → `users.id` | |

### `recommendations`
| Column | Type | Notes |
|---|---|---|
| id | UUID / SERIAL PK | |
| student_id | FK → `students.id`, NOT NULL | |
| type | VARCHAR | e.g. `course`, `resource`, `career` |
| content | TEXT | |
| created_at | TIMESTAMPTZ | |

### `audit_logs`
| Column | Type | Notes |
|---|---|---|
| id | UUID / SERIAL PK | |
| user_id | FK → `users.id` | actor, nullable for system actions |
| action | VARCHAR, NOT NULL | e.g. `attendance.marked`, `user.deleted` |
| entity_type | VARCHAR | table/entity affected |
| entity_id | VARCHAR | |
| metadata | JSONB | before/after values, request context |
| created_at | TIMESTAMPTZ, DEFAULT now() | |

---

## 11. Entity Relationship Summary

```
users (1) ─── (1) students
users (1) ─── (1) faculty

departments (1) ─── (*) students
departments (1) ─── (*) faculty
departments (1) ─── (*) subjects

courses (1) ─── (*) subjects
subjects (1) ─── (*) timetables
subjects (1) ─── (*) attendance_sessions
subjects (1) ─── (*) assignments
subjects (1) ─── (*) documents

attendance_sessions (1) ─── (*) attendance_records
students (1) ─── (*) attendance_records

assignments (1) ─── (*) assignment_submissions
students (1) ─── (*) assignment_submissions

documents (1) ─── (*) document_chunks

users (1) ─── (*) chat_sessions
chat_sessions (1) ─── (*) chat_messages

users (1) ─── (*) notifications
users (1) ─── (*) notices (as poster)
```

---

## 12. Indexing Notes

- **Foreign keys**: index every FK column used in frequent lookups (`student_id`, `subject_id`, `session_id`, `document_id`, etc.) — SQLAlchemy/Alembic won't add these automatically unless declared.
- **`users.email`**: unique index (login lookups).
- **`students.roll_number`**, **`faculty.employee_code`**: unique indexes.
- **`attendance_records(session_id, student_id)`**: unique composite index — prevents duplicate marks and speeds up per-student lookups.
- **`assignment_submissions(assignment_id, student_id)`**: unique composite index.
- **`document_chunks.embedding`**: add an IVFFlat or HNSW index once the table has enough rows to benefit (pgvector supports both):
  ```sql
  CREATE INDEX ON document_chunks
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);
  ```
  Skip this on a small/dev dataset — brute-force scan is fine until you have thousands of chunks.
- **`notifications(user_id, is_read)`**: composite index for the common "unread notifications" query.
- **`chat_messages.session_id`**: index for fetching a session's message history in order (`session_id, created_at`).

---

## Migration Workflow (Alembic)

```bash
# After editing SQLAlchemy models:
alembic revision --autogenerate -m "add attendance tables"
alembic upgrade head
```

Always review autogenerated migrations before applying — Alembic doesn't always detect `pgvector` column types or index changes correctly; add those manually if missing.
