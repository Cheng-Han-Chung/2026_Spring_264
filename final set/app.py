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

# 房價
st.subheader("🏠 Housing Price by State")
fig_price = px.bar(
    plot_df.sort_values("price", ascending=False),
    x="state",
    y="price",
    text="price"
)
fig_price.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
st.plotly_chart(fig_price, use_container_width=True)

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
st.subheader("📈 Price vs Income")
st.plotly_chart(px.scatter(plot_df, x="income", y="price", color="state"), use_container_width=True)

st.subheader("🚨 Price vs Crime")
st.plotly_chart(px.scatter(plot_df, x="crime", y="price", color="state"), use_container_width=True)

st.subheader("🛡 Price vs Insurance")
st.plotly_chart(px.scatter(plot_df, x="insurance", y="price", color="state"), use_container_width=True)

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


import google.generativeai as genai

# =========================
# AI Agent 配置
# =========================
# 請填入你的 Gemini API Key
genai.configure(api_key="AIzaSyCSUJ1C_hjIrSKEWwKrMynQvyF7tOy_lNA")
model = genai.GenerativeModel('gemini-2.5-flash')

with st.sidebar:
    st.markdown("---")
    st.subheader(" AI Assistant")

    # 【關鍵修改 1】：建立一個專屬的「聊天室容器」，設定高度讓它可以獨立上下滑動
    chat_container = st.container(height=450)

    # 初始化對話紀錄
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 【關鍵修改 2】：把先前的歷史紀錄，畫在這個容器 (chat_container) 裡面
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # 聊天輸入框 (Streamlit 會自動把它釘在側邊欄最底端)
    if prompt := st.chat_input("Ask me about the data..."):
        
        # 【關鍵修改 3】：把「新的對話」，也畫在這個容器 (chat_container) 裡面！
        with chat_container:
            # 顯示並儲存使用者訊息
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # 準備數據摘要給 AI
            data_summary = plot_df.describe().to_string()
            
            # 建立 Prompt (確保繁體中文與修復 $ 符號亂碼)
            full_prompt = f"""
            You are a professional Data Science assistant. 
            Here is the summary of the housing data the user is currently looking at:
            {data_summary}
            
            User current filters: {selected_states if selected_states else "All States"}
            
            User Question: {prompt}
            
            Please provide a concise, data-driven answer based on the summary provided. 
            If the user asks for a recommendation, consider variables like Crime Rate, Insurance, and PM2.5.
            
            IMPORTANT RULES:
            1. DO NOT use the '$' symbol for currency, use 'USD' instead, as the '$' symbol breaks the markdown rendering.
            """

            # 取得並顯示 AI 回應
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = model.generate_content(full_prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})


# =========================
# Footer
# =========================
st.markdown("---")
st.markdown("Data Sources: Census, EPA, FEMA, Crime Data, Insurance Data")