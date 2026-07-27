import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres:Xangelina.19@localhost:5432/trinity_metro")

query = """
    SELECT route_long_name, total_stop_events, total_trips,
           unique_stops_served, pct_after_midnight
    FROM staging.route_service_summary
    ORDER BY total_stop_events DESC
"""
df = pd.read_sql(query, engine)

output_path = "ai_automation/route_service_summary.csv"
df.to_csv(output_path, index=False)
print(f"Exported {len(df)} rows to {output_path}")