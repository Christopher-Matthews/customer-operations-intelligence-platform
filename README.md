# Customer Operations Intelligence Platform

## North Star

> I understand how businesses model people, work, relationships, processes, outcomes, and analytics across domains.

The purpose of this project is to learn and demonstrate modern analytics engineering, semantic modeling, ontology design, graph-based business modeling, and AI-assisted analytics through a single business domain that is highly transferable across industries.

The platform is intentionally designed around universal business concepts rather than industry-specific terminology.

The goal is not to model databases.

The goal is to model business reality.

---

# Interview Story

This project demonstrates how to build a modern analytics platform that evolves from raw operational data into a semantic business layer that can be understood by humans, analytics tools, and AI agents.

The project begins with synthetic operational data stored in BigQuery.

The data is transformed using dbt into a dimensional analytics model.

A semantic layer is then added to define business entities, measures, dimensions, and metrics.

An ontology layer is introduced to model how business entities relate to each other through meaningful relationships and actions.

Finally, an AI layer uses ontology and semantic metadata to translate natural language questions into business-aware analytics queries and visualizations.

The project demonstrates understanding of:

* Analytics engineering
* Dimensional modeling
* Data warehousing
* dbt
* Semantic layers
* Knowledge graphs
* Ontology design
* GraphRAG
* AI-assisted analytics
* Business intelligence architecture

---

# Core Philosophy

Traditional analytics answers:

"What happened?"

Ontology-enhanced analytics answers:

"What happened, why did it happen, who was involved, what relationships mattered, and what should happen next?"

---

# Industry Mapping

The same ontology pattern can be applied across many industries.

The nouns change.

The relationships remain remarkably similar.

---

## SaaS / Technology

Customer → Account

Contact → User

Case → Support Ticket

Contract → Subscription

Service Event → Product Usage Event

Outcome → Renewal / Expansion / Churn

Example Question:

"Which accounts show signs of churn despite high product usage?"

---

## Healthcare

Customer → Patient

Employee → Provider

Case → Care Plan

Service Event → Encounter

Contract → Insurance Coverage

Outcome → Health Outcome

Example Question:

"Which patient behaviors correlate with successful outcomes?"

---

## Social Services

Customer → Client

Employee → Case Worker

Case → Service Case

Service Event → Visit

Contract → Program Enrollment

Outcome → Case Resolution

Example Question:

"Which interventions lead to the highest case success rates?"

---

## Financial Services

Customer → Client

Employee → Advisor

Case → Financial Review

Service Event → Consultation

Contract → Account / Policy

Outcome → Retention / Growth

Example Question:

"Which client interactions most strongly predict account growth?"

---

## Insurance

Customer → Policyholder

Case → Claim

Service Event → Claim Activity

Contract → Policy

Outcome → Claim Resolution

Example Question:

"What factors contribute to claim escalation?"

---

## Retail / E-Commerce

Customer → Shopper

Service Event → Order

Case → Return / Support Request

Contract → Loyalty Program

Outcome → Repeat Purchase

Example Question:

"What customer journeys lead to long-term loyalty?"

---

## Professional Services

Customer → Client

Employee → Consultant

Case → Engagement

Service Event → Project Activity

Contract → Service Agreement

Outcome → Client Retention

Example Question:

"What project behaviors correlate with long-term client retention?"

---

## Education

Customer → Student

Employee → Teacher

Case → Academic Plan

Service Event → Enrollment Activity

Contract → Enrollment

Outcome → Graduation / Completion

Example Question:

"What interventions improve student completion rates?"

---

## Property Management

Customer → Tenant

Employee → Property Manager

Case → Maintenance Request

Service Event → Repair Event

Contract → Lease

Outcome → Lease Renewal

Example Question:

"What tenant experiences drive renewals?"

---

# Customer Flow Analytics Domain

This project uses a fictional customer operations company.

The company sells services, supports customers, manages contracts, and measures outcomes.

---

# Core Objects

## Customer

Represents an individual or organization receiving products or services.

Examples:

* Customer
* Client
* Patient
* Student
* Tenant

---

## Contact

Represents a person associated with a customer account.

Examples:

* Decision Maker
* Primary Contact
* Family Member
* Authorized Representative

---

## Employee

Represents workers who interact with customers.

Examples:

* Sales Representative
* Case Worker
* Consultant
* Advisor
* Provider

---

## Product

Represents products, services, programs, or offerings.

Examples:

* Software Package
* Service Plan
* Insurance Policy
* Educational Program

---

## Opportunity

Represents a potential sale or engagement.

---

## Case

Represents an issue, request, workflow, or customer need.

Examples:

* Support Ticket
* Claim
* Service Request
* Care Plan

---

## Service Event

Represents an interaction that occurs between customers and employees.

Examples:

* Meeting
* Visit
* Phone Call
* Consultation
* Support Session

---

## Contract

Represents a formal agreement.

Examples:

* Subscription
* Lease
* Service Agreement
* Insurance Policy

---

## Outcome

Represents measurable business results.

Examples:

* Renewal
* Churn
* Resolution
* Completion
* Revenue Growth

---

# Starter Ontology

The ontology intentionally models business reality rather than database structure.

---

## Relationships

Customer HAS Contact

Customer OWNS Contract

Customer OPENS Case

Customer RECEIVES Service Event

Customer PURCHASES Product

Customer ACHIEVES Outcome

---

Contact BELONGS_TO Customer

Contact PARTICIPATES_IN Service Event

Contact INFLUENCES Opportunity

---

Employee OWNS Customer

Employee HANDLES Case

Employee PERFORMS Service Event

Employee MANAGES Employee

---

Opportunity CONVERTS_TO Contract

Opportunity CONTAINS Product

Opportunity INVOLVES Contact

---

Case RELATES_TO Customer

Case RELATES_TO Contract

Case RESULTS_IN Outcome

---

Contract COVERS Product

Contract GENERATES Revenue

---

Service Event SUPPORTS Case

Service Event PRODUCES Outcome

Service Event INVOLVES Employee

Service Event INVOLVES Customer

---

Outcome BELONGS_TO Customer

Outcome BELONGS_TO Contract

---

# Example Natural Language Questions

Which customers are most likely to churn?

Which employee activities correlate with renewals?

Which customer journeys produce the highest revenue?

Which products are associated with long-term retention?

Which customer segments require the most support?

What sequence of service events typically leads to successful outcomes?

Which accounts appear healthy but are showing early churn signals?

---

# Learning Roadmap

---

# Phase 0 — Data Generation

Goal:

Create realistic operational data.

Status:

Initial synthetic operational data has been generated as a canonical full-load batch. The retained full dataset contains approximately 10,000 customers and connected contacts, employees, products, opportunities, contracts, cases, service events, and outcomes spanning roughly seven years of company history.

The committed sample files under `data/samples/` mirror the retained full-load batch schemas and include the first rows from each generated object for inspection.

Modules:

* Synthetic customer generation
* Synthetic employee generation
* Account hierarchy generation
* Product catalog generation
* Contract generation
* Opportunity generation
* Case generation
* Service event generation
* Outcome generation
* Temporal event simulation
* Customer lifecycle simulation

Deliverable:

Synthetic operational CSV files ready for the data engineer workflow to load into BigQuery staging tables and merge into raw tables.

Repository data policy:

Full generated datasets are excluded from Git because they are local working artifacts for loading into BigQuery.

Small sample batches are committed under `data/samples/` so the schema, field values, and generated business patterns can be inspected without storing the full dataset in the repository.

Data engineer load workflow:

The data engineer workflow loads generated CSV files into BigQuery staging tables, validates the staging load, and appends new hash-versioned records into raw tables.

Expected local `.env` keys:

```bash
GOOGLE_APPLICATION_CREDENTIALS=.gcp-sa.json
GCP_PROJECT_ID=your-project-id

BQ_TEST_STAGING_DATASET=customer_ops_staging_test
BQ_TEST_RAW_DATASET=customer_ops_raw_test
BQ_PROD_STAGING_DATASET=customer_ops_staging_prod
BQ_PROD_RAW_DATASET=customer_ops_raw_prod
```

Initial full test load:

```bash
python scripts/load_bigquery_staging.py --env test --batch-id batch_2026_06_13_002
python scripts/validate_bigquery_load.py --env test --batch-id batch_2026_06_13_002
python scripts/merge_bigquery_raw.py --env test --batch-id batch_2026_06_13_002
```

Incremental test load:

```bash
python scripts/load_bigquery_staging.py --env test --batch-id batch_2026_06_13_incremental1
python scripts/validate_bigquery_load.py --env test --batch-id batch_2026_06_13_incremental1
python scripts/merge_bigquery_raw.py --env test --batch-id batch_2026_06_13_incremental1
```

Production full load after human validation:

```bash
python scripts/load_bigquery_staging.py --env prod --batch-id batch_2026_06_13_002 --confirm-prod
python scripts/validate_bigquery_load.py --env prod --batch-id batch_2026_06_13_002 --confirm-prod
python scripts/merge_bigquery_raw.py --env prod --batch-id batch_2026_06_13_002 --confirm-prod
```

Production incremental load after human validation:

```bash
python scripts/load_bigquery_staging.py --env prod --batch-id batch_2026_06_13_incremental1 --confirm-prod
python scripts/validate_bigquery_load.py --env prod --batch-id batch_2026_06_13_incremental1 --confirm-prod
python scripts/merge_bigquery_raw.py --env prod --batch-id batch_2026_06_13_incremental1 --confirm-prod
```

---

# Phase 1 — Data Warehousing

Goal:

Build an analytics-ready warehouse.

Modules:

* Fact and dimension modeling
* Star schema design
* Surrogate keys
* Slowly changing dimensions
* Data quality validation
* Business grain definition
* Time dimensions

Deliverable:

Clean warehouse model.

---

# Phase 2 — dbt Fundamentals

Goal:

Learn analytics engineering.

Modules:

* Sources
* Models
* Materializations
* Tests
* Documentation
* Exposures
* Macros
* Snapshots
* Incremental models
* CI/CD

Deliverable:

Production-style dbt project.

---

# Phase 3 — Analytics Layer

Goal:

Create reusable business analytics.

Modules:

* KPI design
* Customer metrics
* Retention metrics
* Revenue metrics
* Operational metrics
* Funnel metrics
* Cohort analysis

Deliverable:

Gold-layer business models.

---

# Phase 4 — Semantic Layer

Goal:

Model business meaning.

Modules:

* Semantic models
* Entities
* Measures
* Dimensions
* Metrics
* Entity relationships
* Metric governance

Deliverable:

dbt Semantic Layer implementation.

---

# Phase 5 — Ontology Layer

Goal:

Model business reality.

Modules:

* Ontology concepts
* Nodes
* Edges
* Business entities
* Business verbs
* Relationship modeling
* Ontology metadata design
* YAML ontology definitions

Deliverable:

Business ontology repository.

---

# Phase 6 — Graph Modeling

Goal:

Convert ontology into a navigable graph.

Modules:

* Graph theory basics
* Property graphs
* Node properties
* Relationship properties
* Graph storage models
* Network analysis
* Path traversal

Deliverable:

Business graph representation.

---

# Phase 7 — AI Context Layer

Goal:

Enable AI understanding of business meaning.

Modules:

* Metadata retrieval
* Ontology retrieval
* Semantic context construction
* Prompt grounding
* Business-aware query generation
* SQL generation validation

Deliverable:

Ontology-aware analytics assistant.

---

# Phase 8 — GraphRAG

Goal:

Retrieve graph relationships for reasoning.

Modules:

* GraphRAG fundamentals
* Entity retrieval
* Relationship retrieval
* Neighborhood expansion
* Graph embeddings
* Hybrid retrieval
* Context assembly

Deliverable:

GraphRAG-powered business reasoning layer.

---

# Phase 9 — AI Analytics Platform

Goal:

Build a natural language analytics experience.

Modules:

* Question interpretation
* Ontology mapping
* Semantic retrieval
* SQL generation
* Visualization generation
* Explanation generation
* Recommendation generation

Deliverable:

Customer Operations Intelligence Platform v1.

Natural Language Example:

"Which customer behaviors most strongly predict contract renewal, and show the trend by customer segment?"

The platform should understand:

* customer
* behavior
* contract
* renewal
* customer segment

without requiring the user to know table names, joins, or SQL.
