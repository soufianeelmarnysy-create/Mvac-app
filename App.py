import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="نظام MVAC", layout="wide")

# الرابط المباشر للملف
URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📊 إدارة بيانات الزبناء - MVAC")

try:
    # القراءة باستعمال الرابط المباشر
    df = conn.read(spreadsheet=URL, worksheet="Clients")
    st.success("تم الاتصال بنجاح!")
except Exception as e:
    st.error(f"خطأ في الاتصال: {e}")
    df = pd.DataFrame(columns=["الاسم/الشركة", "ICE", "الهاتف"])

st.subheader("📋 قائمة الزبناء")
st.dataframe(df, use_container_width=True)
