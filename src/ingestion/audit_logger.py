import os
import pandas as pd
from datetime import datetime


AUDIT_LOG_FILE = "logs/audit_log.csv"


def log_ingestion(
    category,
    total_articles,
    new_articles,
    duplicate_articles,
    status
):
    """
    Write ingestion audit information to audit_log.csv
    """

    os.makedirs("logs", exist_ok=True)

    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "category": category,
        "total_articles": total_articles,
        "new_articles": new_articles,
        "duplicate_articles": duplicate_articles,
        "status": status
    }

    if os.path.exists(AUDIT_LOG_FILE):
        audit_df = pd.read_csv(AUDIT_LOG_FILE)
    else:
        audit_df = pd.DataFrame()

    audit_df = pd.concat(
        [audit_df, pd.DataFrame([log_entry])],
        ignore_index=True
    )

    audit_df.to_csv(AUDIT_LOG_FILE, index=False)

    print(
        f"Audit log updated for category: {category}"
    )