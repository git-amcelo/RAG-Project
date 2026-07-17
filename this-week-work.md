# Week 10 Work - Final Submission

## Current Status

Based on the progress folder, the project has completed:
- ✅ Week 1-2: Requirements Analysis & Planning
- ✅ Week 3: Embedding Model Selection
- ✅ Week 4-5: Core RAG Application (FastAPI backend, HTML frontend)
- ✅ Week 6: Hybrid Retrieval & Advanced Features
- ✅ Week 7: Optimization & Evaluation - Part 1 (Profiling)
- ✅ Week 8: Evaluation & Performance Optimization - Part 2 (Integrated prompt optimizer, faithfulness evaluation, and active model re-parsing/re-vectorization)
- ✅ Week 9: Analysis & Documentation - Part 1 (Failure analysis, categorized failure modes, analysis figures, and pipeline/API documentation)

**Current Week: Week 10**

---

## Week 10: Final Submission (July 30 - August 5, 2026)

According to the RAG Project Guideline, Week 10 focuses on **Phase 9: Final Submission**. The main objective is to consolidate all work from Weeks 1-9 into the final deliverables: the IEEE-style report and the presentation slides.

**Also, the professor sent an additional Project Report Template email for Group 10 with extra submission requirements (deadline, filename, extra front/back matter sections, and formatting rules) — these are layered onto the guideline's IEEE report below and must all be satisfied.** See [Additional Professor Requirements](#-additional-professor-requirements-group-10-project-report-email) for the full list.

### Week 10 Scope & Objectives

#### 1. IEEE-Style Final Report (Priority: High)
- **Draft the full report** in IEEE two-column format, targeting 6-8 pages, with the required sections: Abstract, Introduction, Related Work, Methodology, Experimental Setup, Results and Discussion, Conclusion, References.
- **Methodology section**: Describe the hybrid retrieval architecture (dense + BM25), embedding model comparison (BGE/E5/SentenceTransformers), reranking/query expansion, chunk optimization, and context compression as the core contributions.
- **Results and Discussion section**: Incorporate the Week 9 failure analysis, evaluation tables (Recall@K, Precision@K, MRR, Faithfulness) from Week 8, and the analysis figures/visualizations.
- **References**: Compile citations from the Week 1-2 literature summary.
- **Plus (from professor's email)**: wrap the IEEE body with the additional front/back matter and formatting rules required for Group 10 — see the section below.

#### 2. Final Presentation Slides (Priority: High)
- **Build the slide deck** summarizing motivation, system architecture, methodology, experiments, results, and conclusions.
- **Include key visuals**: embedding comparison charts, retrieval metric tables, and failure-mode figures from Week 9.
- **Prepare a live/recorded walkthrough** of the working RAG system for the demo.

#### 3. Final Deliverables Package Assembly (Priority: Medium)
- **Consolidate experimental results** into final performance tables and comparison graphs.
- **Package visualization assets** (retrieval and embedding analysis).
- **Verify against the guideline's Expected Final Deliverables checklist**: Source Code, Working RAG System, Experimental Results, Visualization, Final Presentation, IEEE-Style Final Report.

---

## 📋 Additional Professor Requirements (Group 10 Project Report email)

These are extra points sent directly by the professor for Group 10, on top of the guideline's IEEE report content. Add these as additional sections/rules around the IEEE body (Abstract → References) described above.

### Deadline
**July 29, 2026** (earlier than the guideline's Week 10 end date of Aug 5 — treat this as the hard deadline).

### Submission
- File name: **`Group10_Project_Report_S26.pdf`**
- Only **one** team member (one of those who submitted the interim report) needs to submit it.

### Extra Front/Back Matter to Add Around the IEEE Body
1. **Title Page** — must strictly follow the template already shared for other reports: `knowledge/Interim Report-S26-Template-COMP 8967.docx`. Reuse its title page layout/fields for the final report.
2. **Acknowledgments**
3. **Table of Contents** (with page numbers)
4. **List of Figures/Tables** (every figure/table in the report must be numbered per APA guidelines, e.g., "Figure 1", "Table 1")
5. Within the main body, also cover (in addition to the IEEE sections above):
   - Motivation (alongside Introduction)
   - Background Study (alongside/feeding Related Work)
   - Flow chart(s) (if any)
   - Implementation Details
   - Challenges Faced
   - Help File and Important Information for the Next Team *(assume the project is ongoing — write this as a handoff/continuation guide)*
   - Recommendations for Future Work (alongside Conclusion)
6. **Appendix**, including:
   - Repository links (if applicable)
   - Source code — **must include comments** if the team wrote it
   - Datasets used
   - Any other relevant supporting information
7. Include any additional sections your supervisor has suggested, if applicable.

**No page limit** — include as much content as is relevant and reasonable given the project's scope.

### Formatting Instructions (Mandatory, per professor's email)
- Font: **Times New Roman**
- Size: **12 pt**
- Spacing: **Single-spaced**
- Paragraph alignment: **Justified (Ctrl+J)** — mandatory
- Figures/Tables: numbered per APA guidelines, with entries in the List of Figures/Tables

> Note: This APA-style formatting (12pt Times New Roman, single-spaced, justified) conflicts with the guideline's IEEE two-column template conventions. Since the professor's email is the more specific/recent instruction for Group 10, follow the professor's formatting rules for the final document layout while keeping the IEEE section content/structure as the backbone of the main body.

---

## Week 10 Deliverables

### Technical Deliverables
- **IEEE-Style Final Report**: Draft covering all required IEEE sections, plus the professor's additional front/back matter (Title Page, Acknowledgments, TOC, List of Figures/Tables, Appendix) — formatted per the professor's rules (Times New Roman 12pt, single-spaced, justified) and submitted as `Group10_Project_Report_S26.pdf`.
- **Final Presentation Slides**: Deck summarizing the project for the final demo.
- **Consolidated Experimental Results**: Final performance tables and comparison graphs.

---

## Success Criteria for Week 10

- [ ] Final report drafted covering all required IEEE sections (Abstract through References).
- [ ] Title page created strictly from `knowledge/Interim Report-S26-Template-COMP 8967.docx`.
- [ ] Report includes Acknowledgments, Table of Contents (with page numbers), and List of Figures/Tables.
- [ ] Main body also covers Motivation, Background Study, Flow chart(s), Implementation Details, Challenges Faced, Help File for Next Team, and Recommendations for Future Work.
- [ ] All figures/tables numbered per APA and listed in the List of Figures/Tables.
- [ ] Appendix includes repository link, commented source code, and datasets used.
- [ ] Formatting verified: Times New Roman, 12pt, single-spaced, Ctrl+J justified throughout.
- [ ] Final file named exactly `Group10_Project_Report_S26.pdf`.
- [ ] Presentation slides created with key results and visualizations included.
- [ ] Source code cleaned, organized, and documentation verified as complete.
- [ ] All expected final deliverables assembled and checked against the guideline's checklist.

---

## Week 9 Archive (Completed)

### Completed Work:
- ✅ **Failure Analysis**: Extracted and categorized retrieval failures from SQuAD v2 and MS MARCO benchmarks (semantic drift, complex query structures, out-of-vocabulary terms, poor chunk boundaries).
- ✅ **Analysis Figures**: Generated visualizations (charts, confusion matrices, histograms) of failure categories and quality distributions.
- ✅ **Documentation**: Documented the RAG core pipeline, model switching API logic, prompt optimizer, and faithfulness evaluator.

---

## Next Steps (Following Weeks per RAG Project Guideline)
- **Week 11 (August 6-12)**: Final Demo Preparation & Presentation.

---

*Last Updated: July 16, 2026*
