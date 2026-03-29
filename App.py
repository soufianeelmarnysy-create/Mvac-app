import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# إعداد الصفحة
st.set_page_config(page_title="نظام MVAC", layout="wide")

# الربط مع Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📊 إدارة بيانات الزبناء - MVAC")

# قراءة البيانات من ورقة "Clients"
try:
    df = conn.read(worksheet="Clients")
    st.success("تم الاتصال بنجاح!")
except Exception as e:
    st.error(f"خطأ في الاتصال: {e}")
    df = pd.DataFrame(columns=["الاسم/الشركة", "ICE", "الهاتف"])

# عرض الجدول
st.subheader("📋 قائمة الزبناء")
st.dataframe(df, use_container_width=True)

# إضافة زبون جديد
with st.expander("➕ إضافة زبون جديد"):
    with st.form("add_client"):
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("الاسم/الشركة")
        with col2:
            ice = st.text_input("ICE")
        with col3:
            phone = st.text_input("الهاتف")
        
        submit = st.form_submit_button("حفظ المعلومات")
        
        if submit:
            if name and ice:
                # إضافة السطر الجديد
                new_row = pd.DataFrame([{"الاسم/الشركة": name, "ICE": ice, "الهاتف": phone}])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                # تحديث Google Sheets
                conn.update(worksheet="Clients", data=updated_df)
                st.success(f"تم حفظ {name} بنجاح!")
                st.rerun()
            else:
                st.warning("المرجو إدخال الاسم والـ ICE على الأقل.")
