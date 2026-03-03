import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os

# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------
st.set_page_config(page_title="MarketSim Pakistan", layout="wide")

# ------------------------------------------------
# DIGITAL UI STYLE
# ------------------------------------------------
st.markdown("""
<style>
body {
    background-color: #0E1117;
}
.block-container {
    padding-top: 2rem;
}
.title-gradient {
    font-size:48px;
    font-weight:900;
    background: linear-gradient(90deg,#00F5A0,#00D9F5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.section-title {
    font-size:22px;
    font-weight:700;
    color:#00F5A0;
    margin-top:20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="title-gradient">MarketSim Pakistan</p>', unsafe_allow_html=True)
st.caption("AI-Powered Marketing Intelligence & ROI Simulation Engine")

# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------
areas_df = pd.read_excel("data/areas.xlsx")
benchmarks_df = pd.read_excel("data/industry_benchmarks.xlsx")
influencers_df = pd.read_excel("data/influencers.xlsx")
vendors_df = pd.read_excel("data/vendors.xlsx")

# ------------------------------------------------
# INPUT SECTION
# ------------------------------------------------
st.markdown('<p class="section-title">Business Input</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    industry = st.selectbox("Industry", benchmarks_df["Industry"].unique())

with col2:
    city = st.selectbox("City", areas_df["City"].unique())

with col3:
    budget = st.number_input("Marketing Budget (PKR)", min_value=50000)

goal = st.selectbox("Campaign Goal", ["Sales", "Brand Awareness", "Lead Generation"])

# ------------------------------------------------
# AI FUNCTION
# ------------------------------------------------
def generate_ai_strategy(prompt):
    try:
        api_key = os.environ.get("HUGGINGFACE_API_KEY")
        if not api_key:
            return None

        API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {"inputs": prompt}

        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            return response.json()[0]["generated_text"]
        else:
            return None
    except:
        return None

# ------------------------------------------------
# MAIN BUTTON
# ------------------------------------------------
if st.button("Generate Market Intelligence Report"):

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

    st.markdown('<p class="section-title">Top Recommended Areas</p>', unsafe_allow_html=True)

    fig_area = px.bar(top_areas, x="Area", y="Score", color="Score")
    st.plotly_chart(fig_area, use_container_width=True)

    # ROI CALCULATION
    benchmark = benchmarks_df[benchmarks_df["Industry"] == industry].iloc[0]

    conversion = float(benchmark["Conversion_Rate"])
    avg_value = float(benchmark["Avg_Customer_Value"])

    expected_revenue = (budget * conversion) * avg_value / 1000
    conservative = expected_revenue * 0.7
    aggressive = expected_revenue * 1.3

    st.markdown('<p class="section-title">Revenue Simulation</p>', unsafe_allow_html=True)

    colA, colB, colC = st.columns(3)
    colA.metric("Conservative", f"PKR {int(conservative):,}")
    colB.metric("Expected", f"PKR {int(expected_revenue):,}")
    colC.metric("Aggressive", f"PKR {int(aggressive):,}")

    # BUDGET ALLOCATION
    st.markdown('<p class="section-title">Budget Allocation</p>', unsafe_allow_html=True)

    allocation = {
        "Digital Ads": budget * 0.35,
        "Influencers": budget * 0.25,
        "Outdoor Media": budget * 0.25,
        "Podcast & Activation": budget * 0.15
    }

    alloc_df = pd.DataFrame(list(allocation.items()), columns=["Channel", "Budget"])

    fig_alloc = px.pie(alloc_df, names="Channel", values="Budget", hole=0.5)
    st.plotly_chart(fig_alloc, use_container_width=True)

    # INFLUENCERS
    st.markdown('<p class="section-title">Influencer Matches</p>', unsafe_allow_html=True)
    st.dataframe(influencers_df[influencers_df["City"] == city])

    # VENDORS
    st.markdown('<p class="section-title">Vendor Options</p>', unsafe_allow_html=True)
    st.dataframe(vendors_df[vendors_df["City"] == city])

    # ACTION PLAN
    st.markdown('<p class="section-title">Strategic Action Plan</p>', unsafe_allow_html=True)

    prompt = f"""
    Create a structured marketing action plan for a {industry} in {city}.
    Budget: {budget} PKR.
    Goal: {goal}.
    Include area focus, channel mix, influencer strategy,
    promotional hooks, SEO keywords, and risk level.
    """

    ai_output = generate_ai_strategy(prompt)

    if ai_output:
        st.markdown(ai_output)
    else:
        st.markdown(f"""
        ### Recommended Execution Plan
        
        **1. Focus Areas:** {", ".join(top_areas["Area"].tolist())}
        
        **2. Channel Allocation:**
        - 35% Digital Ads
        - 25% Influencers
        - 25% Outdoor Media
        - 15% Podcast
        
        **3. SEO Focus:**
        - Best {industry} in {city}
        - Affordable {industry}
        - Top rated {industry}
        
        **Risk Level:** Moderate
        """)
