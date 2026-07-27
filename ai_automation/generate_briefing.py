import os
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# --- Stage 1: pull the data ---
PG_PASSWORD = os.environ["PG_PASSWORD"]
engine = create_engine(f"postgresql://postgres:{PG_PASSWORD}@localhost:5432/trinity_metro")

df = pd.read_sql("""
    SELECT route_long_name, total_stop_events, total_trips,
           unique_stops_served, pct_after_midnight
    FROM staging.route_service_summary
    ORDER BY total_stop_events DESC
""", engine)

# --- Stage 2: pre-compute facts in Python (deterministic, never wrong) ---
df["stops_per_trip"] = (df["total_stop_events"] / df["total_trips"]).round(1)

top_5 = df.head(5)
bottom_5 = df.tail(5).iloc[::-1]
late_night = df[df["pct_after_midnight"] > 0].sort_values("pct_after_midnight", ascending=False)
shortest_loops = df.sort_values("stops_per_trip").head(3)

facts_text = f"""VERIFIED FACTS (use only these for any ranking or comparison):

Total routes: {len(df)}

Highest volume routes (by total_stop_events):
{top_5[['route_long_name','total_stop_events','total_trips','unique_stops_served']].to_string(index=False)}

Lowest volume routes:
{bottom_5[['route_long_name','total_stop_events','total_trips','unique_stops_served']].to_string(index=False)}

Late-night service (only {len(late_night)} routes have any):
{late_night[['route_long_name','pct_after_midnight']].to_string(index=False)}

Shortest loops (fewest stops per trip):
{shortest_loops[['route_long_name','stops_per_trip','unique_stops_served']].to_string(index=False)}
"""

# --- Stage 3: LLM writes commentary only ---
client = Groq(api_key=os.environ["GROQ_API_KEY"])

system_msg = """You are a transit data analyst commenting on GTFS scheduled service data.
- This is scheduled data, not actual arrival data. Never claim a route is late, on time, delayed, reliable, or unreliable.
- Never invent numbers, route IDs, time windows, or units. Use only figures given to you.
- The data measures scheduled stop events, not passengers or ridership.
- Never speculate about neighborhoods, land use, trip purpose, or agency intent.
- Refer to routes only by their exact name. Write plain prose, no markdown."""

user_msg = f"""{facts_text}

Write a 200-word weekly briefing for a transit operations manager. Use ONLY the verified facts above for any ranking or superlative. Cover: highest and lowest volume routes, how concentrated late-night service is, and 2-3 routes worth monitoring with structural reasoning. Be specific with the numbers given."""

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg},
    ],
    temperature=0.3,
)

briefing = response.choices[0].message.content

# --- Stage 4: save to a dated file ---
os.makedirs("ai_automation/briefings", exist_ok=True)
filename = f"ai_automation/briefings/briefing_{datetime.now():%Y-%m-%d}.md"
with open(filename, "w", encoding="utf-8") as f:
    f.write(f"# Trinity Metro Weekly Service Briefing\n")
    f.write(f"*Generated {datetime.now():%Y-%m-%d %H:%M}*\n\n")
    f.write(briefing)
    f.write("\n\n---\n*Generated from GTFS scheduled service data. "
            "Reflects structural service patterns, not actual vehicle performance.*\n")

print(f"Saved briefing to {filename}\n")
print(briefing)