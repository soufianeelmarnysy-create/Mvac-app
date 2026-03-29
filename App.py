import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="نظام MVAC", layout="wide")

# الرابط المباشر للملف (تأكد من gists أو gid)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📊 إدارة بيانات الزبناء - MVAC")

try:
    # قراءة البيانات من ورقة "Clients"
    df = conn.read(spreadsheet=SHEET_URL, worksheet="Clients")
    st.success("✅ تم الاتصال بقاعدة البيانات بنجاح!")
except Exception as e:
    st.error(f"⚠️ تنبيه: {e}")
    # جدول احتياطي بنفس ترتيب أعمدة الصورة ديالك
    df = pd.DataFrame(columns=["الاسم/الشركة", "ICE", "الهاتف", "العنوان", "RIB"])

# عرض الجدول
st.subheader("📋 قائمة الزبناء الحاليين")
st.dataframe(df, use_container_width=True)

# إضافة زبون جديد بنفس ترتيب Google Sheet
with st.expander("➕ إضافة زبون جديد"):
    with st.form("new_client"):
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("الاسم/الشركة")
            tel = st.text_input("الهاتف")
            addr = st.text_input("العنوان")
        with c2:
            ice = st.text_input("ICE")
            rib = st.text_input("RIB")
        
        submit = st.form_submit_button("حفظ البيانات")
        
        if submit:
            if nom:
                # ترتيب البيانات مطابق للصورة
                new_row = pd.DataFrame([{"الاسم/الشركة": nom, "ICE": ice, "الهاتف": tel, "العنوان": addr, "RIB": rib}])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                
                # تحديث الملف
                conn.update(spreadsheet=SHEET_URL, worksheet="Clients", data=updated_df)
                st.success(f"تمت إضافة {nom} بنجاح!")
                st.rerun()
            else:
                st.warning("المرجو إدخال اسم الزبون على الأقل.")
