# 09 — Database Data Dictionary

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

Column names for the existing tables below come from the audit and the migration files read in the snapshot; exact types, lengths and defaults are **REQUIRES VERIFICATION** against the live schema in WP0. All other tables are **PROPOSED**.

## Existing tables

### `users` — IMPLEMENTED
| Column (audit-reported) | Meaning | Notes |
|---|---|---|
| id | Primary key | UUID in migrations 0002+ (verify) |
| email | Unique login identifier | Domain checked against college |
| hashed_password | bcrypt hash | **Nullable** since migration 0004 (Google-created users) — source of defect C1 |
| full_name | Display name | verify exact column name |
| role | ADMIN / FACULTY / STUDENT enum | Source of defect C3 |
| college | COEP / PICT / VIT enum | Added in 0004 |
| auth_provider | LOCAL / GOOGLE enum | |
| google_id | Google subject | nullable, unique |
| is_active | Account enabled | |
| is_email_verified | Email verified | |
| profile_picture | URL/text | widened in 0005 |
| created_at, updated_at | Timestamps | |

### `otp_verifications` — IMPLEMENTED (Hardened in WP2)
| Column | Meaning | Notes |
|---|---|---|
| id | PK | UUID |
| user_id | FK users, nullable (added in 0003) | nullable so sign-up OTPs can exist before a user |
| email | Target email | |
| otp_hash | Hashed code | |
| purpose | EMAIL_VERIFY / PASSWORD_RESET enum | |
| expires_at | 10-minute expiry | |
| attempts | Wrong guesses (max 5) | |
| is_used | Consumed or locked | Set to true on 5 failed attempts or successful verification |
| verified_at | Proof of verification | Nullable timestamptz (added in 0007); set ONLY on successful OTP verification |
| created_at | | index on (email, purpose, is_used) |

### `role_requests` — IMPLEMENTED (WP2: Revision 0008)
| Column | Meaning | Notes |
|---|---|---|
| id | PK | UUID |
| user_id | FK users (ON DELETE SET NULL) | Nullable to preserve audit history |
| applicant_email | Immutable email | Guaranteed retention even if user is deleted |
| requested_role | UserRole enum | FACULTY (ADMIN rejected publicly) |
| status | RoleRequestStatus enum | PENDING / APPROVED / REJECTED |
| reviewed_by | FK users (ON DELETE SET NULL) | Admin who reviewed the request |
| reviewed_at | Review timestamp | Timestamptz |
| note | Administrative note | Nullable text |
| created_at | Creation timestamp | Timestamptz |

## Proposed foundation tables
- **`login_codes`** (WP4): id, code_hash UNIQUE, user_id FK users, expires_at, used_at, created_at
- **`refresh_tokens`** (WP6): id, jti UNIQUE, family_id, user_id FK users, issued_at, expires_at, revoked_at, replaced_by, user_agent, ip_hash
- **`auth_attempts`** (WP5): id, action, identifier_hash, ip_hash, success, created_at; index (action, identifier_hash, created_at)
- **`audit_logs`** (WP11): id, actor_id, action, target_type, target_id, outcome, ip_hash, request_id, metadata JSON, created_at (append-only)

## Proposed academic structure
- **`institutions`** (PD-07): id, name, college_code — only if multi-tenant is chosen
- **`departments / branches / programs`** (P05): id, name, (institution_id per PD-07), parent keys
- **`academic_years / semesters / terms`** (P05): id, label, starts_on, ends_on
- **`subjects`** (P05): id, code, name, credits, branch_id, semester_id
- **`classes`** (P05): id, name, branch_id, academic_year_id, semester_id
- **`enrolments`** (P05): id, student_id, class_id, term_id; UNIQUE(student_id, class_id, term_id)
- **`designations / user_designations`** (PD-14): configurable HOD/Dean/Coordinator scopes

## Proposed module tables
- _Student Dashboard and Profile_ — student_profiles(id, user_id FK users, roll_no, prn, department_id, branch_id, program_id, academic_year_id, semester_id, contact JSON, verified_at, created_at)  
  (P05–P06)
- _Student Dashboard and Profile_ — student_extras(id, student_id, kind[skill|certification|project|achievement|internship|interest], title, detail, created_at)  
  (P05–P06)
- _Student Dashboard and Profile_ — marks(id, student_id, subject_id, kind[internal|exam], marks, max_marks, term, entered_by, created_at)  
  (P05–P06)
- _Student Dashboard and Profile_ — sgpa_records(id, student_id, semester_id, sgpa, cgpa, computed_at)  
  (P05–P06)
- _Attendance Management_ — attendance_policies(id, scope, threshold_pct, late_weight, geofence_id, verification_required, fallback_allowed)  
  (P07)
- _Attendance Management_ — attendance_sessions(id, class_id, subject_id, faculty_id, timetable_entry_id, started_at, ended_at, status, verification_mode)  
  (P07)
- _Attendance Management_ — attendance_records(id, session_id, student_id, status, source[face|manual|override], marked_at, verification_event_id, UNIQUE(session_id, student_id))  
  (P07)
- _Attendance Management_ — attendance_overrides(id, record_id, old_status, new_status, reason, actor_id, created_at)  
  (P07)
- _Attendance Management_ — verification_events(id, session_id, student_id, provider, match_score, liveness_result, geofence_result, outcome, created_at)  
  (P07)
- _Attendance Management_ — geofences(id, name, polygon JSON, active)  
  (P07)
- _Attendance Management_ — (biometric tables: face_consents, face_templates, liveness_challenges — see doc 14)  
  (P07)
- _Face Recognition and Liveness_ — face_consents(id, student_id, policy_version, granted_at, withdrawn_at)  
  (P07 (slice B))
- _Face Recognition and Liveness_ — face_templates(id, student_id, template_encrypted, key_id, created_at, deleted_at)  
  (P07 (slice B))
- _Face Recognition and Liveness_ — liveness_challenges(id, session_id, student_id, challenge, issued_at, expires_at, consumed_at)  
  (P07 (slice B))
- _Face Recognition and Liveness_ — verification_events (see doc 13)  
  (P07 (slice B))
- _Face Recognition and Liveness_ — biometric_policies(id, retention_days, raw_image_retention, geofence_required, threshold_config)  
  (P07 (slice B))
- _Timetable Management_ — classrooms(id, name, capacity)  
  (P08)
- _Timetable Management_ — timetable_entries(id, class_id, subject_id, faculty_id, classroom_id, weekday, start_time, end_time, valid_from, valid_to)  
  (P08)
- _Timetable Management_ — timetable_changes(id, entry_id, date, kind[cancel|reschedule|room], detail, created_by)  
  (P08)
- _Timetable Management_ — academic_calendar_events(id, title, date_from, date_to, kind)  
  (P08)
- _Timetable Management_ — lecture_notes(id, entry_id, date, note, homework, created_by)  
  (P08)
- _Assignment Management_ — assignments(id, class_id, subject_id, faculty_id, title, instructions, due_at, max_marks, allow_late, published_at)  
  (P09)
- _Assignment Management_ — assignment_files(id, assignment_id, file_id)  
  (P09)
- _Assignment Management_ — rubric_criteria(id, assignment_id, label, max_marks)  
  (P09)
- _Assignment Management_ — submissions(id, assignment_id, student_id, submitted_at, is_late, status, version)  
  (P09)
- _Assignment Management_ — submission_files(id, submission_id, file_id)  
  (P09)
- _Assignment Management_ — evaluations(id, submission_id, evaluator_id, total, feedback, published_at)  
  (P09)
- _Assignment Management_ — evaluation_scores(id, evaluation_id, criterion_id, marks)  
  (P09)
- _Assignment Management_ — stored_files(id, owner_id, path, sha256, size, mime, created_at)  
  (P09)
- _Notices and Notifications_ — notices(id, author_id, title, body_html, category, priority, publish_at, expires_at, requires_ack)  
  (P10)
- _Notices and Notifications_ — notice_targets(id, notice_id, scope_type, scope_id)  
  (P10)
- _Notices and Notifications_ — notice_reads(notice_id, user_id, read_at, acknowledged_at)  
  (P10)
- _Notices and Notifications_ — notifications(id, user_id, kind, title, body, link, created_at, read_at)  
  (P10)
- _Document Management_ — documents(id, owner_id, title, kind, department_id, branch_id, year_id, semester_id, subject_id, unit, topic, visibility, current_version_id)  
  (P11)
- _Document Management_ — document_versions(id, document_id, file_id, version_no, sha256, size, mime, created_at)  
  (P11)
- _Document Management_ — document_acl(id, document_id, principal_type, principal_id, permission)  
  (P11)
- _Document Management_ — document_processing_jobs(id, version_id, status, attempts, error, started_at, finished_at)  
  (P11)
- _CampusGPT AI Assistant_ — conversations(id, user_id, title, created_at, updated_at, deleted_at)  
  (P12)
- _CampusGPT AI Assistant_ — messages(id, conversation_id, role, content, model, tokens, created_at)  
  (P12)
- _CampusGPT AI Assistant_ — message_sources(id, message_id, source_type, source_id, chunk_id, score)  
  (P12)
- _CampusGPT AI Assistant_ — message_feedback(id, message_id, rating, comment, created_at)  
  (P12)
- _Intent Detection and Routing_ — intent_evaluations(id, utterance_hash, expected_intent, predicted_intent, confidence, created_at) — development evaluation only  
  (P13)
- _RAG Architecture_ — document_chunks(id, document_id, version_id, ordinal, text, page, section, metadata JSON, embedding vector(N), tsv tsvector)  
  (P14)
- _RAG Architecture_ — embedding_models(id, name, dimension, active)  
  (P14)
- _RAG Architecture_ — retrieval_evaluations(id, query, expected_chunk_ids, result_ids, hit, created_at)  
  (P14)
- _Document Ingestion and Retrieval Pipeline_ — document_processing_jobs (see doc 18)  
  (P14)
- _Document Ingestion and Retrieval Pipeline_ — document_chunks (see doc 21)  
  (P14)
- _Academic Analytics_ — Uses marks, attendance and assignment tables; optional materialised views (PROPOSED)  
  (P15)
- _Placement Intelligence_ — companies(id, name, sector, website)  
  (P16)
- _Placement Intelligence_ — placement_opportunities(id, company_id, title, criteria JSON, deadline, created_by)  
  (P16)
- _Placement Intelligence_ — placement_applications(id, opportunity_id, student_id, status, updated_at)  
  (P16)
- _Placement Intelligence_ — interview_rounds(id, application_id, round_no, kind, scheduled_at, outcome)  
  (P16)
- _Placement Intelligence_ — offers(id, application_id, ctc, role, accepted_at)  
  (P16)
- _Internships and Hackathons_ — opportunities(id, type, title, org, criteria JSON, stipend, deadline, url, created_by)  
  (P17)
- _Internships and Hackathons_ — opportunity_bookmarks(student_id, opportunity_id)  
  (P17)
- _Internships and Hackathons_ — opportunity_participation(id, student_id, opportunity_id, status)  
  (P17)
- _Course Recommendation System_ — courses(id, title, category, difficulty, duration_hours, prerequisites JSON, resources JSON)  
  (P18)
- _Course Recommendation System_ — course_skills(course_id, skill)  
  (P18)
- _Course Recommendation System_ — course_progress(id, student_id, course_id, progress_pct, score, completed_at)  
  (P18)
- _Course Recommendation System_ — recommendation_feedback(id, student_id, course_id, signal, created_at)  
  (P18)
- _Visual Learning Workspace_ — visual_boards(id, owner_id, title, scene JSON, version, updated_at)  
  (P19)
- _Visual Learning Workspace_ — visual_board_shares(board_id, principal_type, principal_id, permission)  
  (P19)
- _Voice Interaction (Vapi)_ — voice_sessions(id, user_id, created_at, expires_at, ended_at, status, vapi_call_id, tool_scope)  
  (P22)
- _Voice Interaction (Vapi)_ — voice_tool_calls(id, voice_session_id, tool_name, outcome, latency_ms, created_at) — no arguments or results stored by default  
  (P22)
- _Faculty Dashboard_ — faculty_profiles(id, user_id, department_id, designation_id, employee_no)  
  (P20)
- _Faculty Dashboard_ — faculty_assignments(id, faculty_id, subject_id, class_id, term_id)  
  (P20)
- _Admin Dashboard_ — designations(id, name, scope_type)  
  (P21)
- _Admin Dashboard_ — user_designations(user_id, designation_id, scope_id)  
  (P21)
- _Admin Dashboard_ — institution_settings(key, value, updated_by, updated_at)  
  (P21)
