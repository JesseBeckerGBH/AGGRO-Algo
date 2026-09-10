# telemetry/

Stage 6 keeps the failure log and drift-check history **in the SQLite memory
store** (`failure_events`, `drift_checks` tables), queryable via:

    research-os failures --mission M.yaml
    research-os drift    --mission M.yaml

`adaptation-log.jsonl` — the versioned record of *applied* policy changes that
`adaptation-rules.yaml` `governance.change_log` calls for — lands here in
Stage 7. Per `ethics.telemetry_is_local`, any `*.jsonl` written here is
gitignored; it is the operator's own store.
