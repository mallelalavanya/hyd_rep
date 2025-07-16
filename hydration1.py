import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Function to predict water intake
def predict_water_intake(weight, steps):
    return 0.03 * weight + 0.001 * steps

# Set page configuration
st.set_page_config(page_title="Hydration Monitor", layout="centered")
st.title("💧 Hydration Monitor")

# Create or read hydration log CSV
log_file = "hydration_log.csv"
if os.path.exists(log_file):
    hydration_log = pd.read_csv(log_file)
else:
    hydration_log = pd.DataFrame(columns=["Date", "Weight (kg)", "Steps Taken", "Predicted Intake", "Actual Intake", "Hydration Status"])

# User inputs
weight = st.number_input("Enter your weight (kg)", min_value=25, max_value=120, value=43)
steps = st.number_input("Enter your steps taken", min_value=10, value=3000)
actual_intake = st.number_input("Enter your actual water intake (Liters)", min_value=0.0, value=1.5)

# On button click
if st.button("💡 Check Hydration"):
    predicted_intake = predict_water_intake(weight, steps)
    hydration_status = "Hydrated" if actual_intake >= predicted_intake else "Underhydrated"
    hydration_score = min(actual_intake / predicted_intake, 1.0) * 100
    progress = min(actual_intake / predicted_intake, 1.0)
    percentage = int(progress * 100)
    color = "#00cc66" if hydration_status == "Hydrated" else "#ff6666"

    # Time-based hydration expectation
    current_hour = datetime.now().hour
    if current_hour < 12:
        period = "morning"
        time_target = 0.5
    elif current_hour < 17:
        period = "afternoon"
        time_target = 0.75
    else:
        period = "evening"
        time_target = 1.0

    expected_intake_by_now = predicted_intake * time_target
    if actual_intake < expected_intake_by_now:
        st.warning(f"⏰ It's {period} — by now, you should have consumed around {expected_intake_by_now:.2f}L of water.")

    # Display hydration metrics
    st.metric("Predicted Water Intake (Liters)", round(predicted_intake, 2))
    st.metric("Hydration Score", f"{hydration_score:.0f}%")
    st.metric("Hydration Status", hydration_status)

    # Toasts and sound
    if hydration_status == "Underhydrated":
        remaining = round(predicted_intake - actual_intake, 2)
        st.error(f"⚠️ You are underhydrated. Drink at least **{remaining} more liters** to meet your goal.")
        st.toast("🚰 Time to hydrate! Drink some water 💦", icon="⚠️")
        st.markdown("""
        <audio autoplay>
          <source src="https://www.soundjay.com/button/beep-07.wav" type="audio/wav">
        </audio>
        """, unsafe_allow_html=True)
    else:
        st.success("✅ You're well hydrated! Keep it up! 💪")
        st.toast("🎉 Great job staying hydrated!", icon="✅")

    # Ring-style progress indicator
    st.markdown(f"""
    <div style="display: flex; justify-content: center; align-items: center; margin: 20px 0;">
        <svg width="150" height="150" viewBox="0 0 36 36">
          <circle cx="18" cy="18" r="16" fill="none" stroke="#eeeeee" stroke-width="2"/>
          <path
            stroke="{color}"
            stroke-dasharray="{percentage}, 100"
            stroke-linecap="round"
            d="M18 2.0845
               a 15.9155 15.9155 0 0 1 0 31.831
               a 15.9155 15.9155 0 0 1 0 -31.831"
            fill="none"
            stroke-width="2.5"
          />
          <text x="18" y="21" font-size="7" text-anchor="middle" fill="white" font-weight="bold">{percentage}%</text>
        </svg>
    </div>
    """, unsafe_allow_html=True)

    # Update hydration log
    today = datetime.today().strftime('%Y-%m-%d')
    new_entry = pd.DataFrame({
        "Date": [today],
        "Weight (kg)": [weight],
        "Steps Taken": [steps],
        "Predicted Intake": [round(predicted_intake, 2)],
        "Actual Intake": [actual_intake],
        "Hydration Status": [hydration_status]
    })
    hydration_log = pd.concat([hydration_log, new_entry], ignore_index=True)
    hydration_log.to_csv(log_file, index=False)

    st.write("### Intake Log")
    st.dataframe(new_entry)

    # ------------------- TREND GRAPH -------------------
    st.write("### 📈 Hydration Trend Over Time")

    if len(hydration_log) > 1:
        trend_df = hydration_log.copy()
        trend_df["Date"] = pd.to_datetime(trend_df["Date"])
        trend_df = trend_df.sort_values("Date")

        fig, ax = plt.subplots()
        ax.plot(trend_df["Date"], trend_df["Actual Intake"], marker='o', label="Actual Intake")
        ax.plot(trend_df["Date"], trend_df["Predicted Intake"], linestyle='--', marker='x', label="Predicted Intake", color='orange')
        ax.set_title("Water Intake Over Time")
        ax.set_xlabel("Date")
        ax.set_ylabel("Liters")
        ax.legend()
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.info("Enter at least 2 days of data to view trend graph.")

    # ------------------- PIE CHART -------------------
    st.write("### 🥧 Hydration Status Distribution")

    status_counts = hydration_log["Hydration Status"].value_counts()

    if not status_counts.empty:
        fig2, ax2 = plt.subplots()
        ax2.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90, colors=['#00cc66', '#ff6666'])
        ax2.axis('equal')
        st.pyplot(fig2)
    else:
        st.info("Not enough data to generate pie chart.")

# Bonus: Motivation tips button
if st.button("💬 Hydration Tip"):
    tips = [
        "💧 A healthy outside starts from the inside!",
        "🚰 Sip water regularly — not just when you're thirsty!",
        "🧠 Your brain is 75% water — keep it hydrated!",
        "🌊 Water is life. Stay fresh. Stay focused!"
    ]
    st.info(random.choice(tips))
