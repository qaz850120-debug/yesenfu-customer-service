import streamlit as st
import pandas as pd
import gspread
from google.colab import auth
from datetime import datetime

# Authenticate
auth.authenticate_user()
gc = gspread.oauth()

SHEET_ID = "17U1SHsoAW-Y3oA8pkFCOv1982L3v7Pal_FLLx3OTbFu0"
sh = gc.open_by_key(SHEET_ID)
ws = sh.worksheet("工作台1")

# Page Configuration
st.set_page_config(page_title="野森客服追蹤系統", layout="wide")
st.title("🐯 野森客服追蹤系統")

# Get all data from the sheet
data = ws.get_all_records()
df = pd.DataFrame(data)

if len(df) == 0:
    st.error("🚫 目前無客戶資料")
else:
    # Create tabs for different views
    tab1, tab2 = st.tabs(["📊 查看資料", "➕ 新增記錄"])
    
    with tab1:
        st.subheader("📋 客戶服務記錄")
        
        # Status filter
        col1, col2 = st.columns([1, 1])
        with col1:
            filter_status = st.multiselect(
                "狀態篩選",
                options=df["狀態"].unique().tolist() if "狀態" in df.columns else []
            )
        with col2:
            filter_staff = st.multiselect(
                "員工篩選",
                options=df["員工"].unique().tolist() if "員工" in df.columns else []
            )
        
        # Filter data
        if filter_status:
            df = df[df["狀態"].isin(filter_status)]
        if filter_staff:
            df = df[df["員工"].isin(filter_staff)]
        
        # Display data
        st.dataframe(df, use_container_width=True)
    
    with tab2:
        st.subheader("➕ 新增記錄")
        with st.form("新增記錄表單"):
            ticket_id = st.text_input("票號ID")
            customer_name = st.text_input("客戶名稱")
            contact_phone = st.text_input("聯絡電話")
            status = st.selectbox("狀態", ["全部", "未讀", "處理中", "已完成"])
            staff = st.selectbox("分配員工", ["全部"] + (df["員工"].unique().tolist() if "員工" in df.columns else []))
            notes = st.text_area("備註", height=80)
            
            if st.form_submit_button("🟢 保存"):
                # Add new row
                new_row = {
                    "票號ID": ticket_id,
                    "客戶名稱": customer_name,
                    "聯絡電話": contact_phone,
                    "狀態": status,
                    "員工": staff,
                    "備註": notes,
                    "建檔時間": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                # Append to worksheet
                ws.append_row([new_row.get(col, "") for col in ws.row_values(1)])
                st.success("✅ 記錄已保存！")
                st.rerun()
