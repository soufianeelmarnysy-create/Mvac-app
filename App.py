import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. إعدادات ناضية
st.set_page_config(page_title="MVAC Pro System", layout="wide", page_icon="❄️")

conn = st.connection("gsheets", type=GSheetsConnection)
# الرابط المباشر ديالك
URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

# الترتيب اللي اتفقنا عليه (مراية ديال Sheets)
COLS_C = ["ID", "الاسم/الشركة", "النوع", "ICE", "RIB", "العنوان", "الهاتف"]

# 🔄 دالة جلب البيانات (Affichage)
def load_data(sheet_name):
    try:
        df = conn.read(spreadsheet=URL, worksheet=sheet_name, ttl=0)
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip()
            return df[COLS_C]
        return pd.DataFrame(columns=COLS_C)
    except:
        return pd.DataFrame(columns=COLS_C)

# 💾 دالة الحفظ (Enregistrement) - بالسمية الجديدة Customers
def save_data(sheet_name, df):
    try:
        conn.update(spreadsheet=URL, worksheet=sheet_name, data=df)
        return True
    except Exception as e:
        st.error(f"❌ خطأ: ملقيتش ورقة سميتها '{sheet_name}'")
        st.info("تأكد أنك بدلتي السمية فـ Google Sheets لـ Customers")
        return False

# 🧭 2. Sidebar
with st.sidebar:
    st.title("❄️ MVAC SYSTEM")
    st.markdown("---")
    page = st.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 السلعة والمخزون", "📄 إنشاء Devis/Facture"])

# =========================================================
# 👥 3. صفحة الزبناء (Customers)
# =========================================================
if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    
    # كنعيطو لـ Customers
    df_c = load_data("Customers")

    # --- فورم الإضافة (جامع كلشي ومرتب) ---
    with st.expander("📝 إضافة زبون جديد (Enregistrer)", expanded=True):
        with st.form("form_add_customer", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("الاسم أو الشركة *")
                type_c = st.selectbox("النوع", ["Particulier", "Société"])
                ice = st.text_input("ICE")
            with c2:
                rib = st.text_input("RIB (Bank)")
                tel = st.text_input("الهاتف")
                addr = st.text_area("العنوان")
            
            if st.form_submit_button("حفظ فـ Google Sheets ✅"):
                if name:
                    new_id = int(df_c["ID"].max() + 1) if not df_c.empty else 1
                    # الترتيب العسكري اللي فـ Sheets
                    new_row = pd.DataFrame([[new_id, name, type_c, ice, rib, addr, tel]], columns=COLS_C)
                    df_updated = pd.concat([df_c, new_row], ignore_index=True)
                    
                    if save_data("Customers", df_updated):
                        st.success(f"✅ تم حفظ {name} بنجاح!")
                        st.rerun()
                else:
                    st.warning("السمية ضرورية!")

    # --- العرض (Affichage) ---
    st.markdown("---")
    st.subheader("📋 قائمة الزبناء (Affichage)")
    if not df_c.empty:
        st.dataframe(df_c, use_container_width=True, hide_index=True)
    else:
        st.info("الجدول خاوي. جرب تزيد أول زبون فـ 'Customers'.")

# =========================================================
# 📦 4. باقي الصفحات
# =========================================================
elif page == "📦 السلعة والمخزون":
    st.title("📦 إدارة السلعة")
    df_m = load_data("Materiels")
    st.dataframe(df_m, use_container_width=True)

else:
    st.title("📄 إنشاء Devis / Facture")
    st.info("هنا غادي نخدمو على الـ PDF فالمرحلة الجاية.")
