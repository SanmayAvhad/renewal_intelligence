# Renewal Intelligence Engine

## Overview

The Renewal Intelligence Engine is a data-driven system designed to identify customer accounts at risk of churn or renewal failure. It consolidates information from multiple business systems, generates account-level risk signals, computes a renewal risk score, and produces actionable insights for Customer Success, Sales, and Business Operations teams.

The project demonstrates how structured data, customer feedback, support activity, product usage, and customer success notes can be combined into a unified renewal intelligence workflow.

---

## Project Architecture

```text
Accounts
Usage Metrics
Support Tickets
NPS Data
CSM Notes
Change Logs
      │
      ▼
Data Loading & Cleaning
      │
      ▼
CSM Note Extraction (LLM)
      │
      ▼
Account Reconciliation
      │
      ▼
Master Dataset Creation
      │
      ▼
Feature Engineering
      │
      ▼
Risk Scoring
      │
      ▼
Renewal Insights & Recommendations
```

---

## Key Features

### Data Consolidation

Combines information from multiple datasets into a unified account-level view.

### LLM-Based CSM Note Extraction

Uses Google's Gemini models to extract:

* Account identifiers
* Company names
* Dates
* Customer signals

from unstructured Customer Success notes.

### Account Reconciliation

Handles:

* Missing account IDs
* Missing company names
* Fuzzy matching of customer names
* Entity normalization

using RapidFuzz.

### Feature Engineering

Generates risk indicators including:

* Product adoption decline
* Support escalation patterns
* Competitor mentions
* Budget pressure
* Executive involvement
* NPS deterioration
* Product dissatisfaction
* Security concerns
* Migration concerns

### Risk Scoring

Produces an account-level renewal risk score based on engineered signals.

### Business Insights

Generates high-level observations such as:

* Competitor evaluation trends
* Budget-related risk patterns
* Silent churn accounts
* Product adoption concerns

---

## Installation

### Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Pipeline

Execute:

```bash
python src/main.py
```

View the streamlit dashboard:
```bash
streamlit run app.py
```

## Author

Sanmay Avhad

Master's in Artificial Intelligence
Queen Mary University of London
