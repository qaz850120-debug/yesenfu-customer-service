import streamlit as st
import pandas as pd
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="野森客服追蹤系統", layout="wide")
st.title("🐯 野森客服追蹤系統")

# Sample data for demo
sample_data = {
    "票號ID": ["TK001", "TK002", "TK003"],
    "客戶名稱": ["王後涅", "漢处光", "李良"],
    "聯絡電話": ["0912-345-678", "0923-456-789", "0934-567-890"],
    "狀態": ["處理中", "已完成", "未讀"],
    "員工": ["師傄斯", "太郎", "久美"],
}

df = pd.DataFrame(sample_data)

# Create tabs
tab1, tab2 = st.tabs(["📊 查看資料", "➕ 新增記錄"])

with tab1:
    st.subheader("📋 客戶服務記錄")
    
    # Filters
    col1, col2 = st.columns([1, 1])
    with col1:
        status_filter = st.multiselect(
            "按狀態篩選",
            options=df["狀態"].unique().tolist(),
            default=df["狀態"].unique().tolist()
        )
    with col2:
        staff_filter = st.multiselect(
            "按員工篩選",
            options=df["員工"].unique().tolist(),
            default=df["員工"].unique().tolist()
        )
    
    # Filter data
    filtered_df = df[df["狀態"].isin(status_filter) & df["員工"].isin(staff_filter)]
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 總記錄數", len(filtered_df))
    with col2:
        st.metric("💸 待處理", len(filtered_df[filtered_df["狀態"] == "未讀"]))
    with col3:
        st.metric("✅ 已完成", len(filtered_df[filtered_df["狀態"] == "已完成"]))
    
    # Display table
    st.dataframe(filtered_df, use_container_width=True)

with tab2:
    st.subheader("➕ 新增客戶記錄")
    st.info("🔁 此爲本是示範案例。正式新增功能需要連接 Google Sheets API")
    
    with st.form("新增記錄表單"):
        ticket_id = st.text_input("票號ID", placeholder="輸入票號ID")
        customer_name = st.text_input("客戶名稱", placeholder="輸入客戶名稱")
        contact_phone = st.text_input("聯絡電話", placeholder="輸入電話號碼")
        status = st.selectbox(
            "狀態",
            ["未讀", "處理中", "已完成"],
            index=0
        )
        staff = st.selectbox(
            "分配員工",
            df["員工"].unique().tolist()
        )
        notes = st.text_area("備註", placeholder="輸入備註", height=100)
        
        if st.form_submit_button("🟢 保存", use_container_width=True):
            if ticket_id and customer_name:
                st.success(f"✅ 已決定保存 {ticket_id}!")
            else:
                st.error("💶 請填寫必填欄位")

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🐯 野森動物學校")
with col2:
    st.caption(f"🕒 最残更新：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
with col3:
    st.caption("🚀 由 Streamlit Cloud 開失")
