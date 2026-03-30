import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 🛠️ 1. الإعدادات
st.set_page_config(page_title="MVAC System", layout="wide", page_icon="❄️")

conn = st.connection("gsheets", type=GSheetsConnection)
URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

# 🔄 2. دالة جلب البيانات (مع قتل الكاش)
def load_data(sheet):
    try:
        # ttl=0 هي السر! كتقول للبرنامج: "ما تحفظ والو، ديما جيب الجديد من Sheets"
        df = conn.read(spreadsheet=URL, worksheet=sheet, ttl=0)
        if df is not None:
            df.columns = df.columns.str.strip()
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ مشكل في القراءة: {e}")
        return pd.DataFrame()

# 💾 3. دالة الحفظ
def save_data(sheet, df):
    try:
        conn.update(spreadsheet=URL, worksheet=sheet, data=df)
        return True
    except Exception as e:
        st.error(f"❌ مشكل في الحفظ: {e}")
        return False

# 🧭 4. الواجهة
st.sidebar.title("❄️ MVAC SYSTEM")
page = st.sidebar.radio("القائمة:", ["👥 إدارة الزبناء", "📦 السلعة"])

if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    
    # جلب البيانات "دابا نيت"
    df_c = load_data("Clients")

    # --- عرض الجدول (Affichage) ---
    st.write("### قائمة الزبناء")
    if not df_c.empty:
        st.dataframe(df_c, use_container_width=True, hide_index=True)
    else:
        st.info("الجدول خاوي، زيد أول كليان!")

    # --- إضافة زبون (Enregistrement) ---
    with st.expander("➕ إضافة زبون جديد", expanded=True):
        with st.form("add_client", clear_on_submit=True):
            name = st.text_input("اسم الزبون / الشركة *")
            tel = st.text_input("الهاتف")
            submit = st.form_submit_button("تسجيل وحفظ ✅")
            
            if submit and name:
                # حساب ID جديد أوتوماتيكيا
                new_id = int(df_c["ID"].max() + 1) if not df_c.empty and "ID" in df_c.columns else 1
                new_row = pd.DataFrame([{"ID": new_id, "الاسم/الشركة": name, "الهاتف": tel}])
                
                # لصق الجديد مع القديم
                df_updated = pd.concat([df_c, new_row], ignore_index=True)
                
                # الحفظ
                if save_data("Clients", df_updated):
                    st.success(f"✅ تم حفظ {name}!")
                    # هاد السطر كيخليه يعاود يقرا الجدول ويبين الكليان الجديد ديك الساعة
                    st.rerun()

elif page == "📦 السلعة":
    st.title("📦 إدارة السلعة")
    df_m = load_data("Materiels")
    st.dataframe(df_m, use_container_width=True)
