import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="MVAC Pro System", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)
URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

# الترتيب اللي فالتصويرة ديالك بالظبط: ID, النوع, الاسم/الشركة, ICE, RIB, العنوان, الهاتف
COLS_C = ["ID", "النوع", "الاسم/الشركة", "ICE", "RIB", "العنوان", "الهاتف"]

def load_data(sheet_name):
    try:
        df = conn.read(spreadsheet=URL, worksheet=sheet_name, ttl=0)
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip()
            return df[COLS_C]
        return pd.DataFrame(columns=COLS_C)
    except:
        return pd.DataFrame(columns=COLS_C)

def save_data(sheet_name, df):
    try:
        conn.update(spreadsheet=URL, worksheet=sheet_name, data=df)
        return True
    except Exception as e:
        st.error(f"❌ مشكل فالحفظ: {e}")
        st.info("تأكد أنك رديتي 'Lecteur' لـ 'Éditeur' فـ Google Sheets")
        return False

# --- الواجهة ---
st.sidebar.title("❄️ MVAC SYSTEM")
page = st.sidebar.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 السلعة"])

if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    df_c = load_data("Customers")

    with st.expander("📝 إضافة زبون جديد", expanded=True):
        with st.form("add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                type_c = st.selectbox("النوع", ["Particulier", "Société"])
                name = st.text_input("الاسم أو الشركة *")
                ice = st.text_input("ICE")
            with c2:
                rib = st.text_input("RIB")
                addr = st.text_input("العنوان")
                tel = st.text_input("الهاتف")
            
            if st.form_submit_button("حفظ فـ Google Sheets ✅"):
                if name:
                    new_id = int(df_c["ID"].max() + 1) if not df_c.empty else 1
                    # الترتيب حسب التصويرة: ID, النوع, الاسم, ICE, RIB, العنوان, الهاتف
                    new_row = pd.DataFrame([[new_id, type_c, name, ice, rib, addr, tel]], columns=COLS_C)
                    df_updated = pd.concat([df_c, new_row], ignore_index=True)
                    if save_data("Customers", df_updated):
                        st.success("✅ تم الحفظ بنجاح!")
                        st.rerun()

    st.markdown("---")
    st.dataframe(df_c, use_container_width=True, hide_index=True)

elif page == "📦 السلعة":
    st.title("📦 السلعة")
    st.dataframe(load_data("Materiels"), use_container_width=True)
