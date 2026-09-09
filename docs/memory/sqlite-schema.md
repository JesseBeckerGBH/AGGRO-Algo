# SQLite Schema

## Objective

Persistent memory is required so the system can distinguish novelty from repetition and build cumulative research intelligence over time. The recovered workflow explicitly included persistent SQLite research memory as a core layer of the architecture.[cite:10]

## Why SQLite

SQLite is sufficient for early and mid-stage development because it is portable, transparent, cheap, auditable, and easy to version around. For this product stage, clarity and reliability matter more than premature distribution complexity.

## Core tables

### missions

Stores mission metadata.

Suggested fields:
- mission_id
- created_at
- updated_at
- mission_name
- objective
- priority_level
- source_class_preferences
- novelty_mode
- recency_mode
- status

### queries

Stores generated query families and execution history.

Suggested fields:
- query_id
- mission_id
- query_text
- query_type
- created_at
- executed_at
- connector_used
- result_count
- quality_flag

### results

Stores normalized search results before full curation.

Suggested fields:
- result_id
- mission_id
- query_id
- connector
- title
- url
- canonical_url
- domain
- snippet
- retrieved_at
- raw_rank
- normalized_rank
- source_class
- authority_score
- novelty_score
- redundancy_score
- final_score

### documents

Stores fetched and processed content metadata.

Suggested fields:
- document_id
- result_id
- extracted_text_hash
- summary
- content_type
- word_count
- processed_at

### briefings

Stores delivered outputs.

Suggested fields:
- briefing_id
- mission_id
- generated_at
- briefing_type
- usefulness_rating
- operator_notes

### failure_events

Stores self-annealing signals.

Suggested fields:
- failure_id
- mission_id
- query_id
- result_id
- connector
- failure_type
- severity
- detected_at
- remediation_status
- remediation_action
- outcome_reviewed_at

### adaptation_events

Stores learned changes.

Suggested fields:
- adaptation_id
- related_failure_id
- change_type
- old_value
- new_value
- rationale
- applied_at
- review_status

## Design principles

- Memory should store enough to compare, not everything forever.
- Structured fields matter more than raw dumps.
- Briefings and failures should be first-class records, not side effects.
- Self-annealing requires explicit memory of both failure and correction.

## Self-annealing layer

This database should support closed-loop learning:
- Failure is logged.
- Remediation is proposed.
- Adjustment is applied.
- Later outcomes are reviewed.
- Successful adjustments are retained.
- Failed adjustments are reversed or revised.

That cycle is what turns the product from a static search tool into a learning research system.
