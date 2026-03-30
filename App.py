import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# إعداد الصفحة
st.set_page_config(page_title="MVAC Control Panel", layout="wide")

# الربط باستخدام ID الملف مباشرة (أضمن طريقة)
conn = st.connection("gsheets", type=GSheetsConnection)
# هاد الـ ID جبناه من الرابط ديالك
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMl791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

# دالة جلب البيانات
def get_data():
    try:
        # استبدال SHEET_URL بـ SHEET_ID
        return conn.read(spreadsheet=SHEET_ID, worksheet="Clients")
    except:
        return pd.DataFrame(columns=["ID", "الاسم/الشركة", "النوع", "ICE", "الهاتف", "العنوان", "RIB"])

st.title("👥 إدارة زبناء MVAC")

db_clients = get_data()

# فورم الإضافة
with st.expander("➕ إضافة زبون جديد"):
    with st.form("add_form"):
        nom = st.text_input("الاسم/الشركة")
        tel = st.text_input("الهاتف")
        if st.form_submit_button("حفظ"):
            if nom:
                new_id = int(db_clients["ID"].max() + 1) if not db_clients.empty else 1
                new_row = pd.DataFrame([{"ID":new_id, "الاسم/الشركة":nom, "الهاتف":tel}])
                db_clients = pd.concat([db_clients, new_row], ignore_index=True)
                
                # التحديث باستخدام الـ ID
                conn.update(spreadsheet=SHEET_ID, worksheet="Clients", data=db_clients)
                st.success("تم الحفظ!")
                st.rerun()

st.dataframe(db_clients, use_container_width=True)
