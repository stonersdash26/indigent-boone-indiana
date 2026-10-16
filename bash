python audit_logger_email.py
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="your-email@gmail.com"
export SMTP_PASSWORD="your-app-or-smtp-password"
export EMAIL_RECIPIENT="compliance-team@example.com"
python audit_logger_email.py

export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="your-email@gmail.com"
export SMTP_PASSWORD="your-app-or-smtp-password"
export EMAIL_RECIPIENT="compliance-team@example.com"

export AUDIT_SECRET="federal-oversight-secure-key-2026"
python oversight_crawler_ledger.py crawl \
    --seed https://example.gov/oversight-home \
    --db federal_oversight.db \
    --ledger ledger.jsonl \
    --actor "citizen-auditor-alpha" \
    --max-pages 10
