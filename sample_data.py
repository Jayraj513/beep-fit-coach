"""
Beep Fit Coach - Sample Data for Demonstration and Testing
Realistic, fictional profiles representing Indian college students/graduates
and typical entry-level job descriptions.
"""

SAMPLE_RESUME_DATA_ANALYST = """ROHIT SHARMA
Bengaluru, Karnataka | rohit.sharma.sample@email.com | github.com/rohit-sample-ds

EDUCATION
B.Tech in Information Technology
Visvesvaraya Technological University (VTU), 2021 – 2025 (Final Year)
CGPA: 8.2 / 10.0

TECHNICAL SKILLS
- Programming & Query Languages: Python, SQL (MySQL)
- Libraries & Tools: Pandas, NumPy, Matplotlib, Seaborn, Scikit-Learn (Basics)
- Data Tools: Microsoft Excel (VLOOKUP, Pivot Tables, Conditional Formatting), Jupyter Notebook
- Coursework: Database Management Systems, Object Oriented Programming, Statistics & Probability

PROJECTS
1. E-Commerce Customer Churn Analysis | Python, Pandas, Matplotlib, Seaborn
- Analyzed a dataset of 10,000+ customer records from Kaggle to understand churn patterns.
- Cleaned missing values and engineered features including customer tenure and purchase frequency.
- Built exploratory visualizations identifying high-risk customer segments with >40% churn.
- Trained a baseline Logistic Regression model achieving 76% accuracy on test data.

2. College Library Management System | Python, MySQL, Tkinter
- Developed a desktop application to record book issues, returns, and overdue fines for 1,200+ students.
- Designed relational database schema with 5 normalized tables and wrote SQL queries for inventory tracking.

EXTRACURRICULAR & LEADERSHIP
- Student Coordinator, College Data Science Club (organized 2 beginner Python workshops).
- Active participant in intra-college hackathons.
"""

SAMPLE_JD_DATA_ANALYST = """Job Title: Data Analyst Intern
Company: FinPulse Analytics (FinTech Startup)
Location: Bengaluru (Hybrid)
Duration: 6 Months (with PPO opportunity)

About the Role:
We are looking for an analytical, curious Data Analyst Intern to join our Product & Growth analytics team. You will work alongside senior analysts and product managers to extract insights from transaction and user engagement data.

Key Responsibilities:
- Write and optimize SQL queries across large-scale relational databases to answer daily business questions.
- Clean, aggregate, and perform exploratory data analysis on user behavior and cohort retention using Python (Pandas/NumPy).
- Build and maintain interactive dashboards in Tableau or PowerBI for weekly business review meetings.
- Assist product teams in designing and analyzing A/B tests for checkout conversion funnels.
- Document metrics, data dictionaries, and report findings to non-technical stakeholders.

Requirements & Qualifications:
1. Strong proficiency in SQL (multi-table JOINs, GROUP BY, aggregations, and window functions).
2. Hands-on experience with Python or R for data wrangling and statistical analysis.
3. Demonstrated ability to create clear dashboards using BI tools (Tableau, PowerBI, or Metabase).
4. Familiarity with fundamental statistics, hypothesis testing, and A/B test analysis.
5. Familiarity with Git for version-controlled collaborative analysis.
6. Strong verbal and written communication skills with the ability to summarize numbers into business insights.
"""

SAMPLE_RESUME_AI_INTERN = """PRIYA VENKATESH
Chennai, Tamil Nadu | priya.v.sample@email.com | github.com/priyav-sample-ai

EDUCATION
B.E. in Computer Science and Engineering
Anna University, 2021 – 2025
CGPA: 8.7 / 10.0

TECHNICAL SKILLS
- Languages: Python, C++
- ML & Deep Learning: PyTorch, NumPy, Scikit-learn, OpenCV
- Tools & Platforms: Git, Google Colab, Linux, Jupyter
- Core Concepts: Convolutional Neural Networks (CNNs), Model Evaluation, Linear Algebra, Optimization

PROJECTS
1. Medical Chest X-Ray Pathology Classifier | PyTorch, torchvision, OpenCV
- Fine-tuned a ResNet-18 model on a public chest X-ray dataset containing 5,000 images across 3 classes.
- Implemented data augmentation (rotations, color jitter) to mitigate overfitting on imbalanced classes.
- Achieved 88.5% validation accuracy and visualized model attention using Grad-CAM heatmaps.

2. Campus Event Chatbot | Python, Regex, SQLite
- Built a rule-based query bot answering questions on college symposium schedules and registration links.
- Handled 15+ intent patterns and stored query logs in SQLite.

CERTIFICATIONS & WORKSHOPS
- Deep Learning Specialization (Coursera - deeplearning.ai)
- PyTorch for Deep Learning Bootcamp (Udemy)
"""

SAMPLE_JD_AI_INTERN = """Job Title: AI / Machine Learning Engineer Intern
Company: NeuralBridge Technologies
Location: Bengaluru / Remote
Duration: 6 Months

About the Role:
NeuralBridge is seeking an ambitious AI/ML Intern to contribute to our next-generation customer support intelligence platform. You will work on fine-tuning models, evaluating generative AI pipelines, and deploying inference microservices.

Responsibilities:
- Build and evaluate Retrieval-Augmented Generation (RAG) pipelines using LLM frameworks (LangChain or LlamaIndex).
- Implement vector search and embeddings indexing using vector databases (FAISS, Chroma, or Pinecone).
- Package and deploy ML/LLM inference endpoints using FastAPI or Flask in containerized environments (Docker).
- Conduct quantitative benchmark evaluations (latency, retrieval accuracy, hallucination rates).
- Collaborate with software engineers via Git, code reviews, and automated CI/CD pipelines.

Requirements:
1. Solid Python programming skills with clean, modular coding practices and Git version control.
2. Conceptual and practical knowledge of Deep Learning and Transformer architectures.
3. Experience with PyTorch or TensorFlow for training/fine-tuning.
4. Familiarity with Large Language Models (LLMs), prompt engineering, or RAG concepts.
5. Experience building or consuming REST APIs using FastAPI or Flask.
6. Exposure to vector search concepts (embeddings, cosine similarity).
"""

SAMPLE_DEMO_ANALYSIS_MARKDOWN = """# Beep Fit Coach: Job-Fit Analysis & Action Plan

**Role:** Data Analyst Intern at FinPulse Analytics  
**Candidate Profile:** Final-Year IT Undergraduate (Python, Basic SQL, Excel, EDA Project)  
**Analysis Date:** Prototype Demo Mode  
**Notice:** *This assessment is based strictly on the provided resume and job description. Missing skills are noted as "Not evidenced in the provided resume" and do not imply a lack of capability.*

---

## 1. Role Summary & Fit Snapshot

### A. Role Summary
- **Target Role & Core Purpose:** Data Analyst Intern at FinPulse Analytics, focused on product and growth analytics to extract insights from transaction and user engagement metrics.
- **Explicit Job Requirements:** Proficiency in SQL (joins, window functions), Python/R data wrangling (Pandas/NumPy), BI dashboarding (Tableau/PowerBI), basic A/B testing and statistics, and Git version control.
- **Inferred Priorities & Nuances:** Fast-paced FinTech startup culture prioritizing actionable metric storytelling for non-technical product managers, data hygiene, and proactive metric exploration rather than purely passive reporting.

### B. Qualitative Fit Snapshot
- **Qualitative Assessment:** **Partial Evidence**
- **Evidence-Grounded Summary:** The candidate demonstrates strong foundational strengths in Python data wrangling (Pandas, NumPy, Matplotlib) and basic relational database concepts (MySQL, normalized schemas). However, key industry requirements such as BI dashboarding (Tableau/PowerBI), advanced SQL (window functions), and A/B testing frameworks are not evidenced in the resume.
- **Rubric Scope & Limitations:** This snapshot reflects only what is documented in the submitted text. It is not an algorithmic score, does not guarantee or deny interview selection, and should be used solely as a diagnostic roadmap for focused preparation.

---

## 2. Requirement-by-Requirement Comparison Table

| Requirement | JD Importance | Resume Evidence | Status | Practical Next Action |
| :--- | :--- | :--- | :--- | :--- |
| **Advanced SQL** (Multi-table joins, aggregations, window functions) | **High (Core responsibility)** | Mentions MySQL coursework & project with 5 normalized tables and basic inventory queries. No window functions mentioned. | [Partial Evidence] | Complete 15 targeted LeetCode / StrataScratch SQL challenges focusing on `ROW_NUMBER()`, `RANK()`, and `LAG()/LEAD()`. |
| **Python Data Wrangling** (Pandas, NumPy, EDA) | **High (Core responsibility)** | Cleaned missing values, engineered features, and analyzed 10k+ records in Kaggle Churn Project. | [Evidence Found] | Organize code into a clean, well-commented GitHub repository with a clear README summarizing findings. |
| **BI Dashboarding** (Tableau, PowerBI, or Metabase) | **High (Weekly business reviews)** | Excel Pivot Tables & charts mentioned. No BI dashboard tool mentioned. | [Not Evidenced] | Build a public 1-page interactive dashboard on Tableau Public or PowerBI using your churn project dataset. |
| **A/B Testing & Statistics** (Hypothesis testing, conversion funnels) | **Medium (Product collaboration)** | Mentions college coursework in Statistics & Probability. No A/B testing experience noted. | [Partial Evidence] | Review two-sample t-tests and write a short case study outlining an A/B test for a checkout flow. |
| **Git Version Control** | **Medium (Team collaboration)** | Mentions GitHub profile link in header; no specific Git workflows detailed. | [Partial Evidence] | Commit daily practice code with structured commit messages and link repositories in resume. |
| **Communication & Stakeholder Reporting** | **High (Cross-functional reporting)** | Led 2 beginner Python workshops as Data Science Club Coordinator. | [Evidence Found] | Highlight ability to translate technical analysis into actionable recommendations during interviews. |

---

## 3. Top 3 Priority Gaps

### Priority 1: Interactive BI Dashboarding (Tableau / PowerBI)
- **Why it matters:** The job description specifically emphasizes presenting weekly dashboards to non-technical product managers and leadership. Excel alone is rarely sufficient for modern product analytics roles.
- **What you can do:** Take your existing E-commerce Churn dataset and recreate the key charts as an interactive Tableau Public or PowerBI report with interactive slicers, KPI summary cards, and cohort filters.
- **Tangible output:** A live Tableau Public URL embedded directly into your resume and portfolio.

### Priority 2: Advanced SQL Querying (Window Functions & Aggregations)
- **Why it matters:** Entry-level technical screenings for Data Analyst roles almost universally include live SQL coding sessions testing window functions and multi-table aggregations.
- **What you can do:** Practice 20 medium SQL problems on HackerRank or LeetCode covering `OVER (PARTITION BY ... ORDER BY ...)`, `SUM() OVER`, and CTEs (Common Table Expressions).
- **Tangible output:** A GitHub repository titled `sql-interview-prep` containing documented solutions and explanations for top analytical query patterns.

### Priority 3: A/B Testing & Funnel Analysis Fundamentals
- **Why it matters:** FinTech and e-commerce companies run continuous experimentation. Understanding sample size, p-values, conversion rates, and split-testing is a key differentiator for junior candidates.
- **What you can do:** Study basic A/B test mechanics (null hypothesis, statistical power, type I/II errors) and write a 1-page experiment proposal for checkout drop-off.
- **Tangible output:** A 1-page PDF memo proposing an A/B test for a FinTech checkout flow.

---

## 4. Truthful Resume Improvements

> **Guideline:** These suggestions refine bullet phrasing without exaggerating your actual background. Use bracketed placeholders to confirm exact numbers before updating your resume.

### Project 1: E-Commerce Customer Churn Analysis
- **Current Phrasing:** *"Analyzed a dataset of 10,000+ customer records from Kaggle to understand churn patterns. Built exploratory visualizations identifying high-risk customer segments with >40% churn."*
- **Suggested Truthful Revision:** *"Conducted exploratory data analysis on 10,000+ e-commerce transaction records using Python (Pandas, Seaborn); identified 3 key churn risk factors and quantified high-risk segments with [confirm metric, e.g., 42%] churn rate."*
- **Why this is better:** Directly names the tools and frames the insight in business terminology while retaining strict factual truth.

### Project 2: College Library Management System
- **Current Phrasing:** *"Designed relational database schema with 5 normalized tables and wrote SQL queries for inventory tracking."*
- **Suggested Truthful Revision:** *"Architected a 3NF normalized MySQL database schema with 5 relational tables for 1,200+ users; authored complex SQL queries (multi-table JOINs, GROUP BY) to track book circulation and overdue fines."*
- **Why this is better:** Specifies database normalization standard and query complexity without making up fake enterprise scale.

---

## 5. Portfolio / Mini-Project Blueprint

**Project Title:** FinTech Transaction & Cohort Retention Dashboard  
*Note: This is a suggested future project to build evidence for this specific JD. It is not currently on your resume.*

- **Objective:** Analyze synthetic credit/debit card transaction cohorts to measure monthly user retention and visualize spend patterns for product stakeholders.
- **Recommended Tools:** Python (Pandas for data transformation), PostgreSQL or SQLite, Tableau Public or Streamlit / PowerBI.
- **Dataset / Materials:** Kaggle "Credit Card Customer Churn" dataset or synthetic transaction logs generated via Faker.
- **Implementation Steps:**
  1. *Data Cleaning & Schema:* Ingest CSV data into relational tables; clean null transactions and cast timestamp columns.
  2. *SQL Cohort Analysis:* Write queries calculating user retention rates indexed by signup month (`Cohort Index`).
  3. *Metric Computation:* Calculate monthly active users (MAU), average revenue per user (ARPU), and churn rate.
  4. *Dashboard Creation:* Build a 1-page dashboard showing a retention heatmap and 4 KPI summary cards.
- **Expected Deliverable:** A hosted dashboard link (Tableau Public or Streamlit Community Cloud) + GitHub repository with SQL scripts.
- **How to Showcase in an Interview:** Walk the interviewer through how you structured the retention query, what business decision the retention heatmap informs, and how you validated edge cases.

---

## 6. Realistic Seven-Day Action Plan

| Day | Focus Area | Daily Task | Estimated Time | Specific Deliverable & Completion Check |
| :---: | :--- | :--- | :---: | :--- |
| **Day 1** | **Advanced SQL** | Practice window functions (`ROW_NUMBER`, `DENSE_RANK`, `LEAD/LAG`) on LeetCode/HackerRank. | 90 mins | **Deliverable:** 5 solved problems. *Check:* All 5 pass test cases without syntax errors. |
| **Day 2** | **SQL Aggregations** | Solve 5 multi-table JOIN and `HAVING` aggregation queries. | 75 mins | **Deliverable:** Markdown notes on common join pitfalls and filtering aggregations. |
| **Day 3** | **BI Tool Setup** | Download Tableau Public or PowerBI Desktop; connect to your churn project dataset. | 90 mins | **Deliverable:** Working data connection with verified column types and clean measures. |
| **Day 4** | **Dashboard Build** | Build an interactive churn dashboard (KPI scorecards, bar charts with filters, cohort breakdown). | 120 mins | **Deliverable:** Published Tableau Public or PowerBI report URL. |
| **Day 5** | **Experimentation** | Read primer on A/B testing (sample size, p-value, hypothesis definition). | 60 mins | **Deliverable:** 1-page draft outline of an A/B test for an e-commerce checkout page. |
| **Day 6** | **Resume Polish** | Update resume bullet points with truthful metrics and insert the Tableau Public URL. | 60 mins | **Deliverable:** Updated 1-page PDF resume ready for review. |
| **Day 7** | **Mock Interview** | Practice answering the 5 technical & behavioral questions out loud or with a peer. | 75 mins | **Deliverable:** Recorded 2-minute audio self-evaluation answering "Walk me through your churn project". |

---

## 7. Role-Specific Interview Preparation

### Question 1: *"Can you explain the difference between `WHERE` and `HAVING` clauses in SQL, and when you would use each?"*
- **What the interviewer is assessing:** Basic relational understanding of query execution order and data aggregation mechanics.
- **What a strong answer should cover:** `WHERE` filters rows *before* aggregation occurs, while `HAVING` filters group-level metrics *after* the `GROUP BY` operation. Give a concrete business example (e.g., filtering transactions in 2024 with `WHERE`, then finding users with total spend > ₹50,000 using `HAVING SUM(amount) > 50000`).

### Question 2: *"In your churn analysis project, how did you handle missing or outlier values, and why?"*
- **What the interviewer is assessing:** Practical data hygiene awareness and defensible decision-making during exploratory data analysis.
- **What a strong answer should cover:** Distinguish between categorical missing values (imputation vs. unknown flag) and numerical outliers. Explain whether you clipped outliers or used median imputation and why that choice prevented distorted model baselines.

### Question 3: *"How would you explain a 10% drop in user checkout conversion to a non-technical Product Manager?"*
- **What the interviewer is assessing:** Cross-functional communication and structured root-cause decomposition.
- **What a strong answer should cover:** Avoid jumping to conclusions. Break the problem into dimensions: time (sudden drop vs. gradual decline), platform (iOS vs. Android vs. Web), cohort (new vs. returning users), and technical errors (payment gateway timeout). Summarize findings in simple business terms.

### Question 4: *"What is a window function in SQL, and can you give an example of how you would find each user's latest transaction?"*
- **What the interviewer is assessing:** Fluency with SQL analytics patterns common in product analytics roles.
- **What a strong answer should cover:** Explain that window functions calculate values across a set of rows without collapsing rows into a single output row. Mention `ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY transaction_date DESC)` and filtering where `row_num = 1`.

### Question 5: *"Suppose we want to test a new one-click payment button. How would you design an A/B test to measure its impact?"*
- **What the interviewer is assessing:** Conceptual understanding of experimentation and metric selection.
- **What a strong answer should cover:** Define the primary metric (Checkout Conversion Rate), a guardrail metric (Payment Error Rate / Refund Rate), hypothesis statement, 50/50 randomized split, and minimum sample size needed before declaring statistical significance.

---

## 8. Limitations & Constructive Reflection
- **Information Boundary:** This analysis is based exclusively on the provided text. If you possess unlisted experience (e.g., college coursework in PowerBI or internship experience not mentioned), those skills could not be assessed.
- **No Guarantee of Hiring:** Job descriptions frequently list aspirational wishlists. A "Partial Evidence" assessment does not mean you will not be considered; it highlights strategic leverage points to emphasize in your cover letter and interview.
- **Next Step:** Update your resume with evidenced projects and test your skills using the 7-day action plan above.
"""
