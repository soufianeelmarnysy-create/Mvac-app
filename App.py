import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="MVAC System", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)
# الرابط المباشر
URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

def save_data(sheet_name, df):
    try:
        # هاد السطر كيحدّث البيانات فالبلاصة بلا ما يقلب فـ Cache
        conn.update(spreadsheet=URL, worksheet=sheet_name, data=df)
        return True
    except Exception as e:
        st.error(f"❌ خطأ 404: البرنامج ملقاش '{sheet_name}'")
        # --- هاد الجزء غايفضح لينا المشكل ---
        try:
            # كنحاولو نقراو غير باش نشوفو الأسماء اللي كاينين فـ Sheets
            test_df = conn.read(spreadsheet=URL, ttl=0)
            st.info(f"البرنامج كيشوف هاد الأوراق فقط: {list(test_df.keys()) if isinstance(test_df, dict) else 'ورقة واحدة'}")
        except:
            pass
        return False

# --- كمل الكود ديالك عادي ---
st.title("👥 إدارة الزبناء")
COLS = ["ID", "الاسم/الشركة", "النوع", "ICE", "RIB", "العنوان", "الهاتف"]

# جلب البيانات
try:
    df_c = conn.read(spreadsheet=URL, worksheet="Clients", ttl=0)
except:
    df_c = pd.DataFrame(columns=COLS)

with st.form("my_form"):
    name = st.text_input("الاسم")
    if st.form_submit_button("حفظ ✅"):
        if name:
            new_id = int(df_c["ID"].max() + 1) if not df_c.empty else 1
            new_row = pd.DataFrame([[new_id, name, "", "", "", "", ""]], columns=COLS)
            df_updated = pd.concat([df_c, new_row], ignore_index=True)
            
            # هنا كيعيط للدالة
            if save_data("Clients", df_updated):
                st.success("تم الحفظ!")
                st.rerun()
