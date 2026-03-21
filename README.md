# production-efficiency-powerbi-dashboard
Industrial production efficiency dashboard built with Python, Power BI and AI-assisted data preparation.

## Project Overview

This project demonstrates how data analytics can support industrial production monitoring and operational decision-making.

The dashboard was built to analyze production output, machine downtime, production efficiency and shift performance in a realistic factory environment.

The dataset was synthetically generated to simulate a credible industrial production scenario, then enriched and validated using Python before being modeled and visualized in Power BI.

---

## Business Questions Addressed

This dashboard helps answer key operational questions such as:

- Which plants contribute the most to production output?
- Which machines generate the most downtime?
- How does machine age relate to production risk?
- Which shift performs best in terms of production, efficiency and quality?
- How does production evolve over time?

---

## Data Workflow

This project follows a modern analytics workflow:

1. Synthetic dataset generation using AI
2. Data enrichment and validation using Python
3. Star schema data modeling in Power BI
4. Dashboard design and KPI development in Power BI

---

## Dashboard Structure

### 1. Production Efficiency Overview

![Production Overview](images/page1_overview.png)

This page provides a high-level view of production output, downtime, efficiency and plant comparison.

Main elements:
- Total production
- Total downtime
- Average production efficiency
- Total lost production
- Production trend over time
- Plant performance comparison

---

### 2. Machine Performance Analysis

![Machine Performance](images/page2_machine_performance.png)

This page focuses on machine reliability and production impact.

Main elements:
- Top downtime contributors
- Key production contributors
- Machine risk segmentation
- Machine age vs downtime analysis

---

### 3. Operational Efficiency by Shift

![Shift Efficiency](images/page3_shift_efficiency.png)

This page compares operational performance across shifts.

Main elements:
- Shift performance KPIs
- Production output by shift
- Efficiency comparison by shift
- Quality performance by shift
- Operational load over time

---

## Tools Used

- Power BI
- DAX
- Python
- pandas
- GitHub
- AI-assisted dataset design and preparation

---

## Repository Structure

- `dashboard/` → Power BI dashboard file
- `data/` → raw and enriched datasets
- `analysis/` → Python scripts for data validation and preparation
- `images/` → dashboard screenshots

---

## Skills Demonstrated

This project highlights the following skills:

- data modeling with a star schema
- DAX KPI creation
- dashboard storytelling
- Python-based data preparation
- sanity checks and data validation
- industrial analytics
- AI-assisted analytics workflow
