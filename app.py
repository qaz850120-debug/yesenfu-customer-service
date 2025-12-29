import streamlit as st
import pandas as pd
import gspread
from google.colab import auth
from datetime import datetime

auth.authenticate_user()
gc = gspread.oauth()

SHEET_ID = "17UlSW1xMrY3oABpkfCOvi982Ljv7Pml_ELLx3OTbFu0"
sh = gc.open_by_key(SHEET_ID)
ws = sh.worksheet("工作表1")

st.set_page_config(page_title="野森客服追蹤系統", layout="wide")
st.title("📋 野森客服即時追蹤系統")

data = ws.get_all_records()
df = pd.DataFrame(data)

if len(df) == 0:
    st.error("📭 暫無案件資料")
else:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 總案件", len(df))
    col2.metric("📨 未讀", len(df[df["狀態"] == "未讀"]))
    col3.metric("⏳ 待處理", len(df[df["狀態"] == "待處理"]))
    col4.metric("✅ 已完成", len(df[df["狀態"] == "已完成"]))
    
    st.markdown("---")
    
    with st.sidebar:
        st.subheader("📋 案件列表")
        filter_status = st.selectbox("篩選狀態", ["全部", "未讀", "待處理", "進行中", "已完成"])
        
        if filter_status != "全部":
            filtered = df[df["狀態"] == filter_status]
        else:
            filtered = df
        
        if len(filtered) > 0:
            selected_idx = st.selectbox(
                "選擇案件",
                range(len(filtered)),
                format_func=lambda i: f"{filtered.iloc[i]['票務ID']} | {filtered.iloc[i]['訪客姓名']}"
            )
            actual_idx = filtered.index[selected_idx]
    
    if len(filtered) > 0:
        ticket = df.loc[actual_idx]
        row_num = actual_idx + 2
        
        st.subheader(f"🔍 案件詳情：{ticket['票務ID']}")
        
        col1, col2, col3 = st.columns(3)
        col1.write(f"**票務ID**\n{ticket['票務ID']}")
        col1.write(f"**訪客**\n{ticket['訪客姓名']}")
        col2.write(f"**問題**\n{ticket['問題描述']}")
        col2.write(f"**建立時間**\n{ticket['建立時間']}")
        col3.write(f"**狀態**\n{ticket['狀態']}")
        col3.write(f"**指派**\n{ticket['指派團隊']}")
        
        st.markdown("---")
        
        st.subheader("⚡ 更新狀態")
        col1, col2 = st.columns([2, 1])
        new_status = col1.selectbox("新狀態", ["未讀", "待處理", "進行中", "已完成"], index=["未讀", "待處理", "進行中", "已完成"].index(ticket["狀態"]))
        
        if col2.button("💾 保存"):
            ws.update_cell(row_num, 4, new_status)
            ws.update_cell(row_num, 8, datetime.now().strftime("%Y-%m-%d %H:%M"))
            st.success("✅ 已更新！")
            st.rerun()
        
        st.markdown("---")
        
        st.subheader("📝 新增追蹤")
        note = st.text_area("輸入內容", height=80)
        if st.button("➡ 添加"):
            if note:
                current = ticket.get("內部備註", "")
                ts = datetime.now().strftime("%Y-%m-%d %H:%M")
                new_note = f"{current}\n[{ts}] {note}" if current else f"[{ts}] {note}"
                ws.update_cell(row_num, 7, new_note)
                st.success("✅ 已添加！")
                st.rerun()
        
        st.markdown("---")
        st.subheader("📊 所有案件")
        st.dataframe(df[["票務ID", "訪客姓名", "問題描述", "狀態", "指派團隊", "建立時間"]], use_container_width=True, hide_index=True)
