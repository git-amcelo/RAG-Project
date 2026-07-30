# 📋 GitHub Upload Assignment — Anurag Sharma (AS)

> **Role:** Team Member — Environment Setup, Data Pipeline, API Backend & UI Integration
> **GitHub Repo:** `RAG-Project` (Group 10)

---

## 🗂️ Jira Tickets Assigned to You

| Ticket | Title |
|--------|-------|
| SCRUM-6 | Understand RAG Systems |
| SCRUM-7 | Learning About Jira |
| SCRUM-11 | Project Proposal Draft Creation |
| SCRUM-14 | Install and Configure Python Environment: PyTorch, Transformers, FAISS, LangChain |
| SCRUM-18 | Evaluation Metrics — Retrieval Quality Assessment |
| SCRUM-25 | FastAPI Backend & Frontend API Integration |
| SCRUM-30 | UI Enhancement & End-to-End Integration |
| SCRUM-33 | Failure Categorization & Root Cause Triage |
| SCRUM-37 | Working on the Edge Cases or Bugs |

---

## 📁 Files You Need to Upload to GitHub

### ── 1. Root Level Files

| File | Upload Location in Repo | Jira Ticket | Notes |
|------|--------------------------|-------------|-------|
| `requirements.txt` | `RAG-Project/requirements.txt` | SCRUM-14 | You verified/updated this during environment setup. Coordinate with PS before pushing. |
| `extract_data.py` | `RAG-Project/extract_data.py` | SCRUM-18 | Data extraction script — already exists at root level. |

---

### ── 2. Source Code — `src/` folder

| File | Upload Location in Repo | Jira Ticket | Notes |
|------|--------------------------|-------------|-------|
| `data_loader.py` | `RAG-Project/src/data_loader.py` | SCRUM-14, SCRUM-18 | MS MARCO data loading and preprocessing logic. Your core data pipeline file. |
| `gemini_client.py` | `RAG-Project/src/gemini_client.py` | SCRUM-25 | Gemini LLM API client integration for the backend. |
| `model_config.py` | `RAG-Project/src/model_config.py` | SCRUM-25 | Model configuration and selection logic for the API backend. |

---

### ── 3. API — `src/api/` folder

| File | Upload Location in Repo | Jira Ticket | Notes |
|------|--------------------------|-------------|-------|
| `main.py` | `RAG-Project/src/api/main.py` | SCRUM-25, SCRUM-30 | FastAPI application — all REST endpoints, request/response models, CORS config, and frontend API integration. This is your most important code file. |

---

### ── 4. Frontend — `frontend/` folder

| File | Upload Location in Repo | Jira Ticket | Notes |
|------|--------------------------|-------------|-------|
| `index.html` | `RAG-Project/frontend/index.html` | SCRUM-30 | The full frontend UI — Chat interface, API calls to FastAPI backend, and end-to-end integration. Already exists — ensure UI enhancements are committed. |

---

### ── 5. Evaluation — `src/evaluation/` folder

| File | Upload Location in Repo | Jira Ticket | Notes |
|------|--------------------------|-------------|-------|
| `comparison.py` | `RAG-Project/src/evaluation/comparison.py` | SCRUM-18, SCRUM-33 | Model comparison, retrieval quality assessment, and failure categorization logic. |

---

### ── 6. Progress / Weekly Notes — `progress/` folder

| File | Upload Location in Repo | Jira Ticket | Notes |
|------|--------------------------|-------------|-------|
| `WEEK_3_TASKS.md` | `RAG-Project/progress/week 3/WEEK_3_TASKS.md` | SCRUM-14, SCRUM-18 | Week 3 task breakdown. Already exists. |

---

### ── 7. Documentation — `knowledge/` folder

| File | Upload Location in Repo | Jira Ticket | Notes |
|------|--------------------------|-------------|-------|
| `Team10_COMP8967_Proposal_Final.pdf` | `RAG-Project/knowledge/Team10_COMP8967_Proposal_Final.pdf` | SCRUM-11 | Project proposal PDF. Already exists — upload final version if needed. |

---

## 📂 Complete Repo Folder Structure Reference

```
RAG-Project/                                    ← ROOT
│
├── requirements.txt                            ← YOU co-own (SCRUM-14) ✅
├── extract_data.py                             ← YOU ✅
│
├── src/
│   ├── data_loader.py                          ← YOU ✅ (SCRUM-14, SCRUM-18)
│   ├── gemini_client.py                        ← YOU ✅ (SCRUM-25)
│   ├── model_config.py                         ← YOU ✅ (SCRUM-25)
│   │
│   ├── api/
│   │   └── main.py                             ← YOU ✅ (SCRUM-25, SCRUM-30)
│   │
│   └── evaluation/
│       └── comparison.py                       ← YOU ✅ (SCRUM-18, SCRUM-33)
│
├── frontend/
│   └── index.html                              ← YOU ✅ (SCRUM-30)
│
├── progress/
│   └── week 3/
│       └── WEEK_3_TASKS.md                     ← YOU ✅
│
└── knowledge/
    └── Team10_COMP8967_Proposal_Final.pdf      ← YOU ✅ (SCRUM-11)
```

---

## ✅ Upload Checklist

- [ ] `extract_data.py` — data extraction script present
- [ ] `src/data_loader.py` — MS MARCO data pipeline implemented
- [ ] `src/gemini_client.py` — Gemini LLM client working
- [ ] `src/model_config.py` — model configuration finalized
- [ ] `src/api/main.py` — FastAPI backend with all endpoints
- [ ] `src/evaluation/comparison.py` — retrieval comparison & failure categorization
- [ ] `frontend/index.html` — UI enhancements and full end-to-end integration
- [ ] `progress/week 3/WEEK_3_TASKS.md` — week 3 notes uploaded
- [ ] `knowledge/Team10_COMP8967_Proposal_Final.pdf` — proposal uploaded
- [ ] Any bug-fix commits for edge cases (SCRUM-37) are pushed with clear commit messages

---

> **Note:** You do NOT need to edit or touch files assigned to other team members. Focus only on the files listed above.
