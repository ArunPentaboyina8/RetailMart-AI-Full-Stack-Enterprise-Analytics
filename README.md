# RetailMart Enterprise Analytics Platform

> A comprehensive, **AI-powered** analytics platform built with PostgreSQL, FastAPI, React (Vite), LangChain/LangGraph, and ChromaDB — featuring 25+ views, an AI chat agent with RAG, and a modern, dynamic interactive dashboard.

<img width="1900" height="915" alt="image" src="https://github.com/user-attachments/assets/0cee42ef-7594-41b7-9eae-26ab950baa6f" />


## 🎯 Project Overview

This project demonstrates enterprise-grade SQL analytics capabilities with an **AI-powered natural language interface**, transforming raw retail data into actionable business insights. Built as the capstone project for AccioJob SQL Bootcamp, it showcases real-world data engineering, AI/ML integration, and analytics patterns used at companies like Flipkart, Amazon, and Swiggy.

### Key Features

- **📊 25+ Regular Views** - Real-time analytics across 6 business domains
- **⚡ 10 Materialized Views** - Pre-computed KPIs for instant dashboard loading
- **🔄 32 JSON Export Functions** - API-ready data for frontend consumption
- **📱 7-Tab Dashboard** - Professional, responsive visualization
- **🚨 6 Alert Types** - Proactive business monitoring
- **📈 Complete ETL Pipeline** - Automated refresh and export scripts
- **🤖 AI Chat Agent** - Ask questions in natural language (LangGraph + RAG)
- **🔒 SQL Guardrails** - Injection prevention, query validation, read-only enforcement
- **🧠 RAG Pipeline** - ChromaDB vector store with 22 embedded KPI documents
- **📉 AI Evaluation** - RAGAS-style evaluation with 20 test queries (97% recall, 100% view accuracy)
- **🐳 Docker Compose** - Full-stack containerization (PostgreSQL + FastAPI + Dashboard)
- **⚙️ CI/CD Pipeline** - GitHub Actions for linting, testing, and Docker builds

## 🛠️ Tech Stack

| Category | Technologies |
|----------|-------------|
| **Languages** | Python, JavaScript (React), SQL |
| **Database** | PostgreSQL 16+ (multi-schema, 53 indexes) |
| **Backend** | FastAPI, Pydantic, psycopg2, REST APIs |
| **AI & LLM** | Google Gemini 2.5 Flash, LangChain, LangGraph |
| **RAG** | ChromaDB (vector DB), Embeddings, Retrieval-Augmented Generation |
| **AI Ops** | Guardrails, Fallback chains, Token/cost monitoring, Budget enforcement |
| **Evaluation** | RAGAS-style metrics (Precision, Recall, F1, View Accuracy) |
| **DevOps** | Docker, Docker Compose, GitHub Actions CI/CD, Git |
| **Frontend** | React, Vite, TailwindCSS, Chart.js, Framer Motion |

## 🏗️ Architecture

```
retailmart_analytics/
│
├── 01_setup/                          # Foundation scripts
│   ├── 01_create_analytics_schema.sql
│   ├── 02_create_metadata_tables.sql
│   └── 03_create_indexes.sql
│
├── 02_data_quality/                   # Data validation (27 checks)
│   └── data_quality_checks.sql
│
├── 03_kpi_queries/                    # Analytics modules
│   ├── 01_sales_analytics.sql         # 8 views, 2 MVs
│   ├── 02_customer_analytics.sql      # 4 views, 3 MVs
│   ├── 03_product_analytics.sql       # 3 views, 2 MVs
│   ├── 04_store_analytics.sql         # 3 views, 1 MV
│   ├── 05_operations_analytics.sql    # 5 views, 1 MV
│   └── 06_marketing_analytics.sql     # 4 views, 1 MV
│
├── 04_alerts/                         # Business alerts
│   └── business_alerts.sql
│
├── 05_refresh/                        # Automation
│   ├── refresh_all_analytics.sql
│   └── export_all_json.sh
│
├── frontend/                          # Modern React Application (NEW)
│   ├── src/
│   │   ├── components/                # Reusable React components (Charts, KPI Cards)
│   │   ├── pages/                     # Dashboard pages (Sales, Customers, etc.)
│   │   └── App.jsx                    # Main application router
│   ├── package.json                   # Node dependencies
│   └── vite.config.js                 # Vite build configuration
│
└── 07_documentation/
│
backend/                               # AI-Powered API (NEW)
├── main.py                            # FastAPI app (25+ REST endpoints)
├── config.py                          # Pydantic Settings
├── database.py                        # PostgreSQL connection pool
├── models.py                          # Request/Response models
├── ai/
│   ├── agent.py                       # LangGraph 6-node agent pipeline
│   ├── prompts.py                     # Structured prompts + few-shot examples
│   ├── rag.py                         # ChromaDB RAG pipeline (22 KPI docs)
│   ├── guardrails.py                  # SQL injection prevention & validation
│   └── fallback.py                    # 3-tier degradation strategy
├── monitoring/
│   └── tracker.py                     # Token/cost/latency tracking
│
evaluation/                            # AI Quality Testing (NEW)
├── eval_rag.py                        # RAGAS-style evaluation (20 queries)
└── eval_results.json                  # Latest evaluation results
│
streamlit_app/                         # Streamlit Demo (NEW)
└── app.py                             # Interactive AI chat interface
│
Dockerfile.backend                     # Backend container
docker-compose.yml                     # Full-stack orchestration
.github/workflows/ci.yml              # CI/CD pipeline
```

## 🚀 Quick Start

### Prerequisites

- PostgreSQL 16+
- pgAdmin 4 or any PostgreSQL client
- Web browser (for dashboard)
- Bash shell (for export script)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/retailmart-analytics.git
   cd retailmart-analytics
   ```

2. **Create the RetailMart database** (if not exists)
   ```sql
   CREATE DATABASE retailmart;
   ```

3. **Run setup scripts in order**
   ```bash
   psql -d retailmart -f 01_setup/01_create_analytics_schema.sql
   psql -d retailmart -f 01_setup/02_create_metadata_tables.sql
   psql -d retailmart -f 01_setup/03_create_indexes.sql
   ```

4. **Run data quality checks**
   ```bash
   psql -d retailmart -f 02_data_quality/data_quality_checks.sql
   ```

5. **Create analytics views**
   ```bash
   psql -d retailmart -f 03_kpi_queries/01_sales_analytics.sql
   psql -d retailmart -f 03_kpi_queries/02_customer_analytics.sql
   psql -d retailmart -f 03_kpi_queries/03_product_analytics.sql
   psql -d retailmart -f 03_kpi_queries/04_store_analytics.sql
   psql -d retailmart -f 03_kpi_queries/05_operations_analytics.sql
   psql -d retailmart -f 03_kpi_queries/06_marketing_analytics.sql
   ```

6. **Create alerts**
   ```bash
   psql -d retailmart -f 04_alerts/business_alerts.sql
   ```

7. **Set up refresh functions**
   ```bash
   psql -d retailmart -f 05_refresh/refresh_all_analytics.sql
   ```

8. **Start the Frontend Dashboard**
   ```bash
   cd frontend
   npm install
   npm run dev
   # Open http://localhost:5173 in browser
   ```

### AI Backend Setup (NEW)

1. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Gemini API key and PostgreSQL credentials
   ```

3. **Start the AI-powered API**
   ```bash
   uvicorn main:app --reload --port 8000
   # API docs at http://localhost:8000/docs
   # AI Chat at POST http://localhost:8000/api/chat
   ```

5. **Run evaluation**
   ```bash
   python evaluation/eval_rag.py
   ```

### Docker (Full Stack)

```bash
# Start everything: PostgreSQL + FastAPI + Dashboard
docker-compose up -d

# API at http://localhost:8000, Dashboard at http://localhost:3000
```

## 📊 Analytics Modules

### 1. Sales Analytics
| KPI | Type | Description |
|-----|------|-------------|
| Monthly Sales Dashboard | MV | MoM, YoY growth, moving averages |
| Executive Summary | MV | Top-level KPIs for C-suite |
| Daily Sales Summary | View | Day-level metrics with DoD growth |
| Payment Mode Analysis | View | Revenue by payment method |

<img width="1901" height="912" alt="image" src="https://github.com/user-attachments/assets/3846b855-2c01-432b-bce0-6b923a4ccd5f" />

### 2. Customer Analytics
| KPI | Type | Description |
|-----|------|-------------|
| Customer Lifetime Value | MV | CLV with Platinum/Gold/Silver/Bronze tiers |
| RFM Analysis | MV | Recency-Frequency-Monetary segmentation |
| Cohort Retention | MV | Monthly cohort retention rates |
| Churn Risk | View | High-value customers at risk |

<img width="1902" height="909" alt="image" src="https://github.com/user-attachments/assets/3ef3fe15-1bfa-4928-a830-a6abb13a2a0d" />


### 3. Product Analytics
| KPI | Type | Description |
|-----|------|-------------|
| Top Products | MV | Products ranked by revenue and units |
| ABC Analysis | MV | Pareto classification (80/20 rule) |
| Category Performance | View | Category-level metrics |
| Inventory Turnover | View | Stock velocity and health |

<img width="1903" height="911" alt="image" src="https://github.com/user-attachments/assets/030fda48-99ba-4e4d-ab80-d8e3366af24b" />

### 4. Store Analytics
| KPI | Type | Description |
|-----|------|-------------|
| Store Performance | MV | Revenue, profit, efficiency by store |
| Regional Performance | View | Regional aggregation |
| Store Inventory Status | View | Inventory health by location |

<img width="1902" height="911" alt="image" src="https://github.com/user-attachments/assets/ac9b2d74-e9ba-4281-8d36-69ddedcc7a48" />

### 5. Operations Analytics
| KPI | Type | Description |
|-----|------|-------------|
| Delivery Performance | View | SLA tracking, on-time % |
| Courier Comparison | View | Courier partner benchmarking |
| Return Analysis | View | Return rates by category |
| Payment Success Rate | View | Payment gateway metrics |

<img width="1902" height="911" alt="image" src="https://github.com/user-attachments/assets/66a07140-d86f-4616-a742-fda9eed2b433" />

### 6. Marketing Analytics
| KPI | Type | Description |
|-----|------|-------------|
| Campaign Performance | View | ROI, CPA, conversion rates |
| Channel Performance | View | Ad spend efficiency by channel |
| Promotion Effectiveness | View | Promotion impact analysis |

<img width="1904" height="915" alt="image" src="https://github.com/user-attachments/assets/2f0a5f08-1201-4735-b0c2-fe57ce846ce4" />

## 🚨 Business Alerts

The platform includes 6 proactive alert types:

1. **Critical Stock** - Top products with stock < 10 units
2. **High-Value Churn** - Platinum/Gold customers inactive 60+ days
3. **Revenue Anomaly** - Daily revenue < 75% of 7-day average
4. **Delayed Shipments** - Orders not shipped within 3 days
5. **High Return Rate** - Categories with return rate > 15%
6. **Payment Concentration** - Single payment mode > 70%

## 🔄 Refresh & Automation

### Manual Refresh
```sql
-- Refresh all materialized views
SELECT * FROM analytics.fn_refresh_all_analytics();

-- Refresh specific module
SELECT * FROM analytics.fn_refresh_module('sales');

-- Check refresh status
SELECT * FROM analytics.fn_get_refresh_status();
```

### Scheduled Refresh (cron)
```bash
# Add to crontab for hourly refresh
5 * * * * /path/to/export_all_json.sh --refresh >> /var/log/analytics.log 2>&1
```

## 🖥️ Dashboard Features

- **Modern React Architecture**: Fast, component-based rendering powered by Vite.
- **7 Dynamic Tabs**: Executive, Sales, Customers, Products, Stores, Operations, Marketing
- **AI Chat Widget**: Embedded directly into the interface for instant natural-language querying.
- **Responsive Design**: Fluid layout that works seamlessly across desktop and mobile devices.
- **Interactive Visualizations**: Real-time rendering using Chart.js.

## 📈 Performance Optimizations

- **53 Indexes** on frequently queried columns
- **Materialized Views** for expensive aggregations
- **Composite Indexes** for common query patterns
- **ANALYZE** statistics for query planner optimization

## 🤖 AI Agent Architecture

```
User Question → Intent Classification → RAG Retrieval (ChromaDB)
       → SQL Generation (Gemini 2.5 Flash) → Guardrails Validation
       → PostgreSQL Execution (read-only) → Answer Synthesis
```

**Key AI Features:**
- **6-node LangGraph pipeline** with typed state management
- **22-document knowledge base** embedded in ChromaDB
- **SQL Guardrails** blocking injection, DML, system access, and complexity
- **3-tier fallback** chain: primary model → smaller model → pre-computed answers
- **Token/cost monitoring** with daily budget enforcement
- **Semantic caching** for repeated questions

### AI Evaluation Results

| Metric | Score |
|--------|-------|
| Context Recall | 97.1% |
| View Accuracy | 100.0% |
| Context Precision | 39.0% |
| F1 Score | 55.6% |

## 🎓 Learning Outcomes

This project demonstrates mastery of:

### SQL & Data Engineering
- ✅ Complex SQL queries with CTEs, window functions, and subqueries
- ✅ Materialized views for performance optimization
- ✅ Database schema design and normalization
- ✅ Data quality validation patterns
- ✅ ETL pipeline development
- ✅ JSON data export for API consumption
- ✅ Frontend integration with Chart.js

### AI & LLM
- ✅ LLM integration with structured outputs (Google Gemini 2.5 Flash)
- ✅ RAG pipeline with vector database (ChromaDB)
- ✅ Prompt engineering with few-shot examples and schema context
- ✅ LLM orchestration with LangChain and LangGraph
- ✅ AI quality evaluation (RAGAS-style metrics)
- ✅ Guardrails, monitoring, and fallback strategies

### DevOps & Cloud
- ✅ REST API development with FastAPI and Pydantic
- ✅ Docker containerization with Docker Compose
- ✅ CI/CD with GitHub Actions
- ✅ Production deployment practices

