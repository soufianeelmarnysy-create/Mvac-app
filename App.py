import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 🛠️ 1. الإعدادات والربط
st.set_page_config(page_title="MVAC Pro System", layout="wide", page_icon="❄️")

conn = st.connection("gsheets", type=GSheetsConnection)

# الرابط الصحيح (تأكد أن هاد الرابط هو اللي فيه ورقة Customers)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMl791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

# الترتيب اللي عندك فـ Sheets بالظبط: ID, النوع, الاسم/الشركة, ICE, RIB, العنوان, الهاتف
COLS_C = ["ID", "النوع", "الاسم/الشركة", "ICE", "RIB", "العنوان", "الهاتف"]

# 🔄 دالة جلب البيانات (Affichage)
def load_data(sheet_name):
    try:
        # ttl=0 باش يجيب anva وأي حاجة جديدة فالبلاصة
        df = conn.read(spreadsheet=SHEET_URL, worksheet=sheet_name, ttl=0)
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip()
            # كيجبر الكود يحترم الترتيب ديالك
            return df[COLS_C]
        return pd.DataFrame(columns=COLS_C)
    except:
        return pd.DataFrame(columns=COLS_C)

# 💾 دالة الحفظ (Enregistrement)
def save_data(sheet_name, df):
    try:
        conn.update(spreadsheet=SHEET_URL, worksheet=sheet_name, data=df)
        return True
    except Exception as e:
        st.error(f"❌ خطأ فالحفظ: {e}")
        return False

# 🧭 2. القائمة الجانبية
with st.sidebar:
    st.title("❄️ MVAC SYSTEM")
    st.markdown("---")
    page = st.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 السلعة"])
    st.markdown("---")
    st.write("سفيان - MVAC v1.0")

# =========================================================
# 👥 3. صفحة إدارة الزبناء
# =========================================================
if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    
    # تحميل البيانات (هنا غاتبان ليك anva)
    df_c = load_data("Customers")

    # --- خانة الإضافة (Ajouter) مرتبة كيف Sheets ---
    with st.expander("📝 إضافة زبون جديد", expanded=True):
        with st.form("form_add_client", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                type_c = st.selectbox("النوع", ["Particulier", "Société"])
                name = st.text_input("الاسم أو الشركة *")
                ice = st.text_input("ICE")
            with col2:
                rib = st.text_input("RIB")
                addr = st.text_input("العنوان")
                tel = st.text_input("الهاتف")
            
            if st.form_submit_button("حفظ فـ Google Sheets ✅"):
                if name:
                    # حساب ID جديد أوتوماتيكياً
                    new_id = int(df_c["ID"].max() + 1) if not df_c.empty else 1
                    
                    # تجميع السطر بالترتيب ديال Sheets
                    new_row = pd.DataFrame([[new_id, type_c, name, ice, rib, addr, tel]], columns=COLS_C)
                    
                    # دمج وحفظ
                    df_updated = pd.concat([df_c, new_row], ignore_index=True)
                    if save_data("Customers", df_updated):
                        st.success(f"✅ تم تسجيل {name} بنجاح!")
                        st.rerun()
                else:
                    st.warning("السمية ضرورية!")

    # --- عرض الجدول (Affichage) ---
    st.markdown("---")
    st.subheader("📋 قائمة الزبناء المسجلين")
    if not df_c.empty:
        st.dataframe(df_c, use_container_width=True, hide_index=True)
    else:
        st.info("الجدول خاوي. جرب تزيد أول كليان!")

# =========================================================
# 📦 4. صفحة السلعة
# =========================================================
elif page == "📦 السلعة":
    st.title("📦 إدارة السلعة")
    df_m = load_data("Materiels")
    st.dataframe(df_m, use_container_width=True, hide_index=True)
