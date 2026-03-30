import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 🛠️ 1. الإعدادات والربط
st.set_page_config(page_title="MVAC Pro System", layout="wide", page_icon="❄️")

conn = st.connection("gsheets", type=GSheetsConnection)
# الرابط الصحيح (تأكد أن هاد الرابط هو اللي فيه ورقة Clients)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

# 🔄 دالة جلب البيانات (Affichage)
def load_data(sheet_name):
    try:
        # ttl=0 باش يجيب الجديد ديك الساعة
        df = conn.read(spreadsheet=SHEET_URL, worksheet=sheet_name, ttl=0)
        if df is not None:
            df.columns = df.columns.str.strip() # تنظيف العناوين
            return df
        return pd.DataFrame()
    except Exception as e:
        # هنا غادي يبان ليك المشكل إلا كانت السمية غلط
        st.sidebar.error(f"⚠️ ورقة '{sheet_name}' غير موجودة")
        return pd.DataFrame()

# 💾 دالة الحفظ (Enregistrement)
def save_data(sheet_name, df):
    try:
        # كنحاولو نحفظو فـ Worksheet محددة
        conn.update(spreadsheet=SHEET_URL, worksheet=sheet_name, data=df)
        return True
    except Exception as e:
        st.error(f"❌ خطأ في الحفظ: {e}")
        return False

# 🧭 2. القائمة الجانبية
with st.sidebar:
    st.title("❄️ MVAC SYSTEM")
    st.markdown("---")
    page = st.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 السلعة والمخزون"])
    st.markdown("---")
    # زر للتحديث اليدوي
    if st.button("🔄 تحديث البيانات"):
        st.rerun()

# =========================================================
# 👥 3. صفحة إدارة الزبناء
# =========================================================
if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    
    # الأعمدة بالترتيب اللي بغيتي
    COLS_C = ["ID", "الاسم/الشركة", "النوع", "ICE", "الهاتف", "العنوان", "RIB"]
    
    df_c = load_data("Clients")

    # --- خانة الإضافة (Ajouter) ---
    with st.expander("📝 إضافة زبون جديد", expanded=True):
        with st.form("form_add_client", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("الاسم أو الشركة *")
                type_c = st.selectbox("النوع", ["Particulier", "Société"])
                ice = st.text_input("ICE")
            with col2:
                tel = st.text_input("رقم الهاتف")
                rib = st.text_input("RIB (البنك)")
                addr = st.text_area("العنوان الكامل")
            
            if st.form_submit_button("تسجيل والحفظ ✅"):
                if name:
                    # بناء السطر الجديد بالترتيب
                    new_id = int(df_c["ID"].max() + 1) if not df_c.empty and "ID" in df_c.columns else 1
                    new_row = pd.DataFrame([[new_id, name, type_c, ice, tel, addr, rib]], columns=COLS_C)
                    
                    # دمج
                    if df_c.empty:
                        df_updated = new_row
                    else:
                        df_updated = pd.concat([df_c, new_row], ignore_index=True)
                    
                    # الحفظ
                    if save_data("Clients", df_updated):
                        st.success(f"✅ تم حفظ {name}!")
                        st.rerun()
                else:
                    st.warning("السمية ضرورية!")

    # --- عرض البيانات (Affichage) ---
    st.markdown("---")
    st.subheader("📋 قائمة الزبناء المسجلين")
    if not df_c.empty:
        st.dataframe(df_c, use_container_width=True, hide_index=True)
    else:
        st.info("الجدول خاوي، زيد أول كليان!")

# =========================================================
# 📦 4. صفحة السلعة
# =========================================================
elif page == "📦 السلعة والمخزون":
    st.title("📦 إدارة السلعة")
    df_m = load_data("Materiels")
    st.dataframe(df_m, use_container_width=True)
