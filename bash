export AUDIT_SECRET="federal-oversight-secure-key-2026"
python oversight_crawler_ledger.py crawl \
    --seed https://example.gov/oversight-home \
    --db federal_oversight.db \
    --ledger ledger.jsonl \
    --actor "citizen-auditor-alpha" \
    --max-pages 10
