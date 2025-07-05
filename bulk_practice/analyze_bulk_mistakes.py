import streamlit as st
import json
import os
import plotly.express as px
import pandas as pd
from utils.utils import load_questions  # Import from utils.py

BULK_MISTAKES_FILE = "bulk_practice/data/bulk_mistakes.json"

def analyze_bulk_mistakes():
    st.header("📊 Bulk Mistake Analysis")
    if not os.path.exists(BULK_MISTAKES_FILE):
        st.info("No bulk mistakes found.")
        return

    with open(BULK_MISTAKES_FILE, "r", encoding="utf-8") as f:
        mistakes = json.load(f)
    if not mistakes:
        st.info("No bulk mistakes found.")
        return

    questions = load_questions()  # Should return a list

    # Prepare DataFrame for analysis
    data = []
    for key, count in mistakes.items():
        try:
            day, qidx = key.replace("day", "").split("_q")
            day = int(day)
            qidx = int(qidx)
            question_idx = (day - 1) * 40 + qidx
            q = questions[question_idx]
            question_text = q.get("question", "Question not found")
            data.append({
                "day": day,
                "qidx": qidx,
                "count": count,
                "key": key,
                "question": question_text
            })
        except Exception as e:
            data.append({
                "day": None,
                "qidx": None,
                "count": count,
                "key": key,
                "question": f"Error: {e}"
            })
    df = pd.DataFrame(data)

    # Mistake count per day
    st.subheader("Mistake Trend by Day")
    day_counts = df.groupby("day")["count"].sum().reset_index()
    fig = px.bar(day_counts, x="day", y="count", title="Mistakes per Day")
    st.plotly_chart(fig, use_container_width=True)

    # Top mistaken questions
    st.subheader("Top Mistaken Questions")
    top_qs = df.sort_values("count", ascending=False).head(10)
    st.dataframe(top_qs[["day", "qidx", "question", "count"]], use_container_width=True)

    # Creative analysis: mistake distribution
    st.subheader("Mistake Distribution Insights")
    st.write(f"Total unique questions with mistakes: {df['key'].nunique()}")
    if not day_counts.empty:
        st.write(f"Day with most mistakes: {day_counts.loc[day_counts['count'].idxmax(), 'day']}")

    # --- Mistaken Questions Review Section ---
    st.subheader("📝 Mistaken Questions Review")
    for key, count in mistakes.items():
        try:
            day, qidx = key.replace("day", "").split("_q")
            day = int(day)
            qidx = int(qidx)
            question_idx = (day - 1) * 40 + qidx
            q = questions[question_idx]

            st.markdown(f"**Day {day} Q{qidx+1}.** {q['question']}")
            st.info(q.get("instruction", ""))
            for k, v in q.get("options", {}).items():
                st.markdown(f"- {k}: {v}")
            correct_answers = q.get("answers", [])
            sorted_answers = sorted(correct_answers)
            st.success("✅ Correct Answer(s): " + ", ".join(sorted_answers))
            st.warning(f"❌ You answered this wrong {count} time(s).")
            st.markdown("---")
        except Exception as e:
            st.error(f"Error processing question {key}: {e}")
            continue