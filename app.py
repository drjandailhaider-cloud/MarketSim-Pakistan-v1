import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# ------------------------
# CONFIG
# ------------------------
st.set_page_config(page_title="MarketSim Pakistan", layout="wide")

HUGGINGFACE_API_KEY = "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"
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

# ------------------------
# AI FUNCTION
# ------------------------
def generate_ai_strategy(prompt):
    payload = {"inputs": prompt}
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()[0]["generated_text"]
    else:
        return "AI service busy. Try again."

# ------------------------
# UI DESIGN
# ------------------------
st.markdown("""
<style>
body {
    background-color: #0E1117;
}
.big-title {
    font-size:48px;
    font-weight:800;
    background: linear-gradient(90deg,#00C9FF,#92FE9D);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.card {
    background-color: #161B22;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">MarketSim Pakistan</p>', unsafe_allow_html=True)
st.caption("AI-Powered Marketing Intelligence Engine")

# ------------------------
# LOAD DATA
# ------------------------
areas_df = pd.read_excel("data/areas.xlsx")
benchmarks_df = pd.read_excel("data/industry_benchmarks.xlsx")
influencers_df = pd.read_excel("data/influencers.xlsx")
vendors_df = pd.read_excel("data/vendors.xlsx")

# ------------------------
# INPUT SECTION
# ------------------------
st.header("Business Input")

col1, col2 = st.columns(2)

with col1:
    industry = st.selectbox("Select Industry", benchmarks_df["Industry"].unique())
    budget = st.number_input("Total Budget (PKR)", min_value=50000)

with col2:
    city = st.selectbox("Select City", areas_df["City"].unique())
    goal = st.selectbox("Campaign Goal", ["Sales", "Brand Awareness", "Lead Generation"])
col1, col2, col3 = st.columns(3)

col1.metric("Expected Revenue", f"PKR {int(expected_revenue):,}")
col2.metric("Conservative", f"PKR {int(conservative):,}")
col3.metric("Aggressive", f"PKR {int(aggressive):,}")
# ------------------------
# GENERATE STRATEGY
# ------------------------
if st.button("Generate Market Strategy"):

    # AREA SCORING
    city_areas = areas_df[areas_df["City"] == city].copy()
    city_areas["Score"] = (
        city_areas["Income_Score"] * 0.30 +
        city_areas["Footfall_Score"] * 0.25 +
        city_areas["Commercial_Score"] * 0.25 +
        city_areas["Population_Density"] * 0.10 -
        city_areas["Competition_Score"] * 0.10
    )

    top_areas = city_areas.sort_values("Score", ascending=False).head(3)

    st.subheader("Top Recommended Areas")
    st.dataframe(top_areas[["Area", "Score"]])

    # ROI SIMULATION
    benchmark = benchmarks_df[benchmarks_df["Industry"] == industry].iloc[0]

    conversion = benchmark["Conversion_Rate"]
    avg_value = benchmark["Avg_Customer_Value"]

    expected_revenue = (budget * conversion) * avg_value / 1000
    conservative = expected_revenue * 0.7
    aggressive = expected_revenue * 1.3

    roi_data = pd.DataFrame({
        "Scenario": ["Conservative", "Expected", "Aggressive"],
        "Revenue": [conservative, expected_revenue, aggressive]
    })

    st.subheader("ROI Simulation")
    fig = px.bar(roi_data, x="Scenario", y="Revenue", color="Scenario")
    st.plotly_chart(fig)

    # INFLUENCERS
    st.subheader("Influencer Suggestions")
    st.dataframe(influencers_df[influencers_df["City"] == city])

    # VENDORS
    st.subheader("Vendor Suggestions")
    st.dataframe(vendors_df[vendors_df["City"] == city])

    # AI STRATEGY
    st.subheader("AI Marketing Plan")

    prompt = f"""
    Create a marketing strategy for a {industry} in {city}
    with a budget of {budget} PKR.
    Focus on {goal}.
    Suggest campaign ideas, hooks, and promotional tactics.
    """

    ai_output = generate_ai_strategy(prompt)
    st.success(ai_output)
