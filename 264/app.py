import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# Page Config
# =========================
st.set_page_config(page_title="Housing Price Dashboard", layout="wide")

# =========================
# Load & Clean Data
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("final_dataset.csv")

    # 去除欄位空白
    df.columns = df.columns.str.strip()

    # 🔥 正確對應（你的檔案）
    df = df.rename(columns={
        "State_Name": "state",
        "median_home_value": "price",
        "median_income": "income",
        "pm25_state_mean": "pm25",
        "climate_event_count_5yr": "risk",
        "Crime_Rate": "crime",
        "Avg_Home_Insurance_2022": "insurance"
    })

    # 轉數字（避免錯誤）
    numeric_cols = ["price", "income", "pm25", "risk", "crime", "insurance"]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 清資料
    df = df.dropna()

    return df

df = load_data()

# =========================
# Sidebar
# =========================
st.sidebar.header("Filters")

selected_states = st.sidebar.multiselect(
    "Select up to 5 states",
    options=sorted(df["state"].unique()),
    max_selections=5
)

# =========================
# Title
# =========================
st.title("🏠 Housing Price Dashboard")

st.markdown("""
Analyze housing prices with income, air quality, climate risk, crime rate, and insurance cost.
""")

# =========================
# Mode Switch
# =========================
if len(selected_states) == 0:
    st.subheader("🌎 Overview (All States)")
    plot_df = df
else:
    st.subheader("📊 Selected State Comparison")
    plot_df = df[df["state"].isin(selected_states)]

# =========================
# KPI（重點：選州 → 每州顯示）
# =========================
st.subheader("📊 Key Metrics")

if len(selected_states) == 0:
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Avg Price", f"${plot_df['price'].mean():,.0f}")
    col2.metric("Avg Income", f"${plot_df['income'].mean():,.0f}")
    col3.metric("Avg PM2.5", f"{plot_df['pm25'].mean():.2f}")
    col4.metric("Avg Crime", f"{plot_df['crime'].mean():.2f}")
    col5.metric("Avg Insurance", f"${plot_df['insurance'].mean():,.0f}")

else:
    for _, row in plot_df.iterrows():
        st.markdown(f"### 🏙 {row['state']}")

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric("Price", f"${row['price']:,.0f}")
        c2.metric("Income", f"${row['income']:,.0f}")
        c3.metric("PM2.5", f"{row['pm25']:.2f}")
        c4.metric("Crime", f"{row['crime']:.2f}")
        c5.metric("Insurance", f"${row['insurance']:,.0f}")

# =========================
# Bar Charts（全部都有數字）
# =========================

# 🗺️ 替換原本的 Housing Price by State
st.subheader("🗺️ Housing Price Distribution")
fig_map = px.choropleth(
    plot_df,
    locations="state", 
    locationmode="USA-states", # 注意：這裡通常需要州名縮寫 (如 CA, TX)，若你的資料是全名可能需要轉換
    color="price",
    scope="usa",
    color_continuous_scale="Blues"
)
st.plotly_chart(fig_map, use_container_width=True)

# 收入
st.subheader("💰 Income by State")
fig_income = px.bar(
    plot_df.sort_values("income", ascending=False),
    x="state",
    y="income",
    text="income"
)
fig_income.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
st.plotly_chart(fig_income, use_container_width=True)

# PM2.5
st.subheader("🌫 PM2.5 by State")
fig_pm25 = px.bar(
    plot_df.sort_values("pm25", ascending=False),
    x="state",
    y="pm25",
    text="pm25"
)
fig_pm25.update_traces(texttemplate='%{text:.2f}', textposition='outside')
st.plotly_chart(fig_pm25, use_container_width=True)

# Climate Risk
st.subheader("🌪 Climate Risk by State")
fig_risk = px.bar(
    plot_df.sort_values("risk", ascending=False),
    x="state",
    y="risk",
    text="risk"
)
fig_risk.update_traces(texttemplate='%{text:.0f}', textposition='outside')
st.plotly_chart(fig_risk, use_container_width=True)

# 犯罪率
st.subheader("🚨 Crime Rate by State")
fig_crime = px.bar(
    plot_df.sort_values("crime", ascending=False),
    x="state",
    y="crime",
    text="crime"
)
fig_crime.update_traces(texttemplate='%{text:.2f}', textposition='outside')
st.plotly_chart(fig_crime, use_container_width=True)

# 保險費
st.subheader("🛡 Insurance Cost by State")
fig_ins = px.bar(
    plot_df.sort_values("insurance", ascending=False),
    x="state",
    y="insurance",
    text="insurance"
)
fig_ins.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
st.plotly_chart(fig_ins, use_container_width=True)

# =========================
# Scatter（分析）
# =========================
# 🫧 替換原本的 Price vs Income
st.subheader("🫧 Affordability vs Risk Analysis")
fig_bubble = px.scatter(
    plot_df, 
    x="income", 
    y="price", 
    size="insurance",  # 氣泡大小代表保險費
    color="risk",      # 顏色代表氣候風險
    hover_name="state",
    size_max=40
)
st.plotly_chart(fig_bubble, use_container_width=True)

st.subheader("🚨 Price vs Crime")
st.plotly_chart(px.scatter(plot_df, x="crime", y="price", color="state"), use_container_width=True)

st.subheader("🛡 Price vs Insurance")
st.plotly_chart(px.scatter(plot_df, x="insurance", y="price", color="state"), use_container_width=True)

# 🌡️ 新增相關性分析
st.subheader("🌡️ Variable Correlation Heatmap")
# 只取數值欄位算相關性
corr_matrix = plot_df[["price", "income", "pm25", "risk", "crime", "insurance"]].corr()
fig_corr = px.imshow(
    corr_matrix, 
    text_auto=".2f", 
    aspect="auto",
    color_continuous_scale="RdBu_r"
)
st.plotly_chart(fig_corr, use_container_width=True)

# 🌳 替換原本的 Insurance Cost
st.subheader("🌳 Insurance Cost & Climate Risk")
fig_tree = px.treemap(
    plot_df, 
    path=[px.Constant("US"), "state"], 
    values="insurance", 
    color="risk",
    color_continuous_scale="Reds"
)
fig_tree.update_traces(root_color="lightgrey")
st.plotly_chart(fig_tree, use_container_width=True)


# 📊 替換原本的 PM2.5 或 Crime Rate
st.subheader("📊 Crime Rate Distribution Across States")
fig_hist = px.histogram(
    plot_df, 
    x="crime", 
    nbins=15, 
    marginal="box", # 上方額外加上箱型圖顯示中位數與離群值
    color_discrete_sequence=["indianred"]
)
st.plotly_chart(fig_hist, use_container_width=True)


# =========================
# Insights（選州時）
# =========================
if len(selected_states) > 0:

    st.subheader("🧠 Insights")

    df_selected = plot_df.copy()

    highest_price = df_selected.loc[df_selected["price"].idxmax()]
    lowest_price = df_selected.loc[df_selected["price"].idxmin()]

    highest_crime = df_selected.loc[df_selected["crime"].idxmax()]
    lowest_crime = df_selected.loc[df_selected["crime"].idxmin()]

    highest_ins = df_selected.loc[df_selected["insurance"].idxmax()]
    lowest_ins = df_selected.loc[df_selected["insurance"].idxmin()]

    df_selected["affordability"] = df_selected["price"] / df_selected["income"]

    best_affordable = df_selected.loc[df_selected["affordability"].idxmin()]
    worst_affordable = df_selected.loc[df_selected["affordability"].idxmax()]

    st.markdown(f"""
### Key Findings:

- **Highest Price:** {highest_price['state']} (${highest_price['price']:,.0f})
- **Lowest Price:** {lowest_price['state']} (${lowest_price['price']:,.0f})

- **Highest Crime:** {highest_crime['state']} ({highest_crime['crime']:.2f})
- **Lowest Crime:** {lowest_crime['state']} ({lowest_crime['crime']:.2f})

- **Highest Insurance:** {highest_ins['state']} (${highest_ins['insurance']:,.0f})
- **Lowest Insurance:** {lowest_ins['state']} (${lowest_ins['insurance']:,.0f})

### Affordability:

- **Best:** {best_affordable['state']}
- **Worst:** {worst_affordable['state']}
""")

# =========================
# Footer
# =========================
st.markdown("---")
st.markdown("Data Sources: Census, EPA, FEMA, Crime Data, Insurance Data")