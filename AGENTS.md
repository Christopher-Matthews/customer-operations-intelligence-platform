# Starting Vision Architecture

This is the starting vision architecture for the Customer Operations Intelligence Platform. Use it as a reference while the project grows across data generation, warehousing, dbt, semantic modeling, ontology design, graph modeling, and AI-assisted analytics.

```text
customer_operations_intelligence_platform/
  README.md
  AGENTS.md
  .env
  .gitignore
  requirements.txt

  .agents/
    data-generation-agent.md
    data-engineer-agent.md
    dbt-agent.md
    semantic-layer-agent.md
    ontology-agent.md
    graph-agent.md
    ai-analytics-agent.md
    reviewer-agent.md

  docs/
    roadmap.md
    architecture.md
    decisions/
      0001-project-stack.md

  configs/
    synthetic_data.yml
    warehouse.yml
    ontology.yml

  src/
    customer_ops_intel/
      __init__.py
      data_generation/
      warehouse/
      ontology/
      graph/
      ai/
      common/

  scripts/
    generate_seed_data.py
    load_bigquery.py
    validate_data.py

  data/
    generated/
    samples/

  analytics/
    dbt/
      dbt_project.yml
      models/
        staging/
        intermediate/
        marts/
        semantic/
      macros/
      tests/
      seeds/
      snapshots/

  ontology/
    entities.yml
    relationships.yml
    actions.yml
    metrics.yml

  graph/
    node_specs.yml
    edge_specs.yml
    exports/

  prompts/
    system/
    sql_generation/
    ontology_mapping/
    evaluation/

  evals/
    questions.yml
    expected_behavior.yml

  tests/
    unit/
    integration/
```

## Agent Routing

Use the specialized agent files in `.agents/` for phase-specific work.

- For synthetic operational data generation, use `.agents/data-generation-agent.md`.
- For data loading and BigQuery handoff work, use `.agents/data-engineer-agent.md`.
- For dbt project setup, warehouse modeling, and model tests, use `.agents/dbt-agent.md`.
- For semantic models, metrics, and entity definitions, use `.agents/semantic-layer-agent.md`.
- For ontology entities, relationships, actions, and business meaning, use `.agents/ontology-agent.md`.
- For graph modeling, node/edge design, and traversal logic, use `.agents/graph-agent.md`.
- For AI analytics, prompts, SQL generation, retrieval, and evaluation, use `.agents/ai-analytics-agent.md`.
- For reviews, quality checks, and risk finding, use `.agents/reviewer-agent.md`.

Before working in a phase-specific area, read the matching `.agents/` file first and follow its local guidance.
