# AI Placement Coach — REST API Reference

All requests and responses use JSON format. Protected endpoints require the `Authorization: Bearer <JWT_TOKEN>` header.

---

## 1. Authentication (`/api/auth`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/auth/register` | Register student account with academic info | No |
| `POST` | `/api/auth/login` | Authenticate student, return JWT | No |
| `GET` | `/api/auth/me` | Fetch active user profile | Yes |
| `PUT` | `/api/auth/profile` | Update profile information & target role | Yes |
| `POST` | `/api/auth/logout` | Revoke session | Yes |

---

## 2. Dashboard (`/api/dashboard`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/dashboard` | Placement readiness %, category scores, activities, recs | Yes |
| `GET` | `/api/dashboard/ai-status` | Report live AI vs offline practice mode state | No |

---

## 3. Aptitude (`/api/aptitude`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/aptitude/categories` | List available aptitude categories | No |
| `POST` | `/api/aptitude/start` | Generate test question set | Yes |
| `POST` | `/api/aptitude/submit` | Evaluate answers, compute objective score | Yes |
| `GET` | `/api/aptitude/results/{id}` | Detailed score breakdown & explanation review | Yes |
| `GET` | `/api/aptitude/history` | Historical test attempts | Yes |

---

## 4. Group Discussion (`/api/gd`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/gd/topics` | List curated GD topics (search/filter support) | No |
| `GET` | `/api/gd/topics/{id}` | Detailed prep material for single topic | No |
| `POST` | `/api/gd/generate` | Generate complete prep guide for custom topic | Yes |
| `POST` | `/api/gd/start` | Start live simulated GD session | Yes |
| `POST` | `/api/gd/respond` | Submit user response, receive AI peer reactions | Yes |
| `POST` | `/api/gd/evaluate` | Evaluate GD session on 5 communicative dimensions | Yes |

---

## 5. Mock Interview (`/api/interview`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/interview/start` | Initialize interview session & retrieve Question 1 | Yes |
| `POST` | `/api/interview/answer` | Evaluate candidate answer & generate adaptive Q | Yes |
| `POST` | `/api/interview/end` | Conclude session & compile comprehensive report | Yes |
| `GET` | `/api/interview/{id}` | Fetch full session transcript and scores | Yes |
| `GET` | `/api/interview/history`| List completed interview attempts | Yes |

---

## 6. Resume AI (`/api/resume`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/resume/upload` | Upload PDF/DOCX, parse skills & projects | Yes |
| `GET` | `/api/resume/latest` | Fetch user's latest parsed resume | Yes |
| `GET` | `/api/resume/{id}` | Fetch specific parsed resume | Yes |
| `POST` | `/api/resume/questions` | Generate interview questions matching resume | Yes |

---

## 7. Companies (`/api/companies`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/companies` | List all 10 company profiles | No |
| `GET` | `/api/companies/{id}` | Hiring pattern, technical syllabus, sample Qs | No |

---

## 8. Progress Analytics (`/api/progress`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/progress` | Aggregate analytics, timeline, radar, practice activity | Yes |
| `GET` | `/api/progress/aptitude` | Historical aptitude performance trend | Yes |
| `GET` | `/api/progress/gd` | Historical GD performance trend | Yes |
| `GET` | `/api/progress/interview` | Historical interview performance trend | Yes |

---

## 9. Full Placement Simulation (`/api/simulation`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/simulation/start` | Initiate 4-round recruitment drive | Yes |
| `POST` | `/api/simulation/complete-round` | Record score & advance to next round | Yes |
| `GET` | `/api/simulation/{id}` | Final comprehensive placement report | Yes |
