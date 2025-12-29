import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json
import os

# Page Configuration
st.set_page_config(page_title="野森客服追蹤系統", layout="wide")
st.title("🐯 野森客服追蹤系統")

# Google Sheets Configuration
SHEET_ID = "1IPgOL5Z4M1w45CaHwi6BW4UF8HFP8LJd2c_GMJgwFF8"
WORKSHEET_NAME = "工作台1"

@st.cache_resource
def get_sheets_client():
    """取得 Google Sheets 客戶端"""
    try:
        # 從 Streamlit Secrets 中獲取認証資訊
        if "GOOGLE_APPLICATION_CREDENTIALS" in st.secrets:
            credentials_dict = st.secrets["GOOGLE_APPLICATION_CREDENTIALS"]
            credentials = Credentials.from_service_account_info(
                credentials_dict,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            return gspread.authorize(credentials)
        else:
            # 從環境變量中獲取
            creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
            if creds_json:
                credentials_dict = json.loads(creds_json)
                credentials = Credentials.from_service_account_info(
                    credentials_dict,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
                return gspread.authorize(credentials)
            else:
                return None
    except Exception as e:
        st.error(f"認証失敗: {str(e)}")
        return None

@st.cache_data(ttl=60)
def load_data():
    """從 Google Sheets 載入數據"""
    try:
        gc = get_sheets_client()
        if gc is None:
            st.error("🚫 無法連接 Google Sheets！請設置認証資料。")
            return pd.DataFrame()
        
        sh = gc.open_by_key(SHEET_ID)
        ws = sh.worksheet(WORKSHEET_NAME)
        data = ws.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.warning(f"載入數據失敗：{str(e)}")
        return pd.DataFrame()

def append_record(ticket_id, customer_name, contact_phone, status, staff, notes):
    """新增記錄到 Google Sheets"""
    try:
        gc = get_sheets_client()
        if gc is None:
            st.error("無法連接 Google Sheets！")
            return False
        
        sh = gc.open_by_key(SHEET_ID)
        ws = sh.worksheet(WORKSHEET_NAME)
        
        # 新增一行數據
        new_row = [
            ticket_id,
            customer_name,
            contact_phone,
            status,
            staff,
            notes,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
        ws.append_row(new_row)
        return True
    except Exception as e:
        st.error(f"新增記錄失敗：{str(e)}")
        return False

# 載入數據
df = load_data()

if len(df) == 0:
    st.warning("🚫 目前無數據！請稄保認証設置！")
else:
    # 建立標籤頁
    tab1, tab2 = st.tabs(["📊 查看資料", "➕ 新增記録"])
    
    with tab1:
        st.subheader("📋 客戶服務記錄")
        
        # 篩選
        col1, col2 = st.columns([1, 1])
        with col1:
            filter_status = st.multiselect(
                "按狀態篩選",
                options=df["狀態"].unique().tolist() if "狀態" in df.columns else [],
                default=df["狀態"].unique().tolist() if "狀態" in df.columns else []
            )
        with col2:
            filter_staff = st.multiselect(
                "按員工篩選",
                options=df["員工"].unique().tolist() if "員工" in df.columns else [],
                default=df["員工"].unique().tolist() if "員工" in df.columns else []
            )
        
        # 篩選數據
        filtered_df = df.copy()
        if "狀態" in df.columns and filter_status:
            filtered_df = filtered_df[filtered_df["狀態"].isin(filter_status)]
        if "員工" in df.columns and filter_staff:
            filtered_df = filtered_df[filtered_df["員工"].isin(filter_staff)]
        
        # 顯示指標
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 總記錄數", len(filtered_df))
        with col2:
            pending = len(filtered_df[filtered_df["狀態"] == "未讀"]) if "狀態" in filtered_df.columns else 0
            st.metric("💸 待處理", pending)
        with col3:
            completed = len(filtered_df[filtered_df["狀態"] == "已完成"]) if "狀態" in filtered_df.columns else 0
            st.metric("✅ 已完成", completed)
        
        # 顯示數據表
        st.dataframe(filtered_df, use_container_width=True)
    
    with tab2:
        st.subheader("➕ 新增客戶記錄")
        st.info("✨ 您的記錄將被保存到 Google Sheets 中！")
        
        with st.form("新增記錄表單"):
            ticket_id = st.text_input("票號ID", placeholder="輸入票號ID")
            customer_name = st.text_input("客戶名稱", placeholder="輸入客戶名稱")
            contact_phone = st.text_input("聯絡電話", placeholder="輸入電話號碼")
            status = st.selectbox(
                "狀態",
                ["未讀", "處理中", "已完成"],
                index=0
            )
            
            # 取得員工清單
            staff_options = df["員工"].unique().tolist() if "員工" in df.columns else []
            staff = st.selectbox(
                "分配員工",
                staff_options if staff_options else ["未指派"]
            )
            notes = st.text_area("備註", placeholder="輸入備註", height=100)
            
            if st.form_submit_button("🟢 保存", use_container_width=True):
                if ticket_id and customer_name:
                    if append_record(ticket_id, customer_name, contact_phone, status, staff, notes):
                        st.success(f"✅ 記錄 {ticket_id} 已保存！")
                        st.rerun()
                    else:
                        st.error("保存失敗！")
                else:
                    st.error("💶 請填寫必填欄位！")

# 頁腧
 st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🐯 野森動物學校")
with col2:
    st.caption(f"🕒 最残更新：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
with col3:
    st.caption("🚀 介接 Google Sheets")
