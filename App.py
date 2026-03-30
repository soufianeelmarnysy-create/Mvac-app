import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. إعداد الصفحة والربط
st.set_page_config(page_title="MVAC Pro System", layout="wide", page_icon="❄️")

conn = st.connection("gsheets", type=GSheetsConnection)
# الرابط الكامل للملف (تأكد أنه هو هذا اللي عندك)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

# 🔄 2. دالة جلب البيانات (Affichage)
def load_data(sheet_name):
    try:
        # ttl=0 كتحيد الكاش باش يبان التغيير ديك الساعة
        df = conn.read(spreadsheet=SHEET_URL, worksheet=sheet_name, ttl=0)
        if df.empty:
            return pd.DataFrame(columns=["ID", "الاسم/الشركة", "النوع", "ICE", "الهاتف", "العنوان", "RIB"])
        # تنظيف بسيط للبيانات
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"خطأ في قراءة ورقة {sheet_name}: {e}")
        return pd.DataFrame()

# 💾 3. دالة تسجيل البيانات (Enregistrement)
def save_data(sheet_name, df):
    try:
        conn.update(spreadsheet=SHEET_URL, worksheet=sheet_name, data=df)
        return True
    except Exception as e:
        st.error(f"خطأ في الحفظ: {e}")
        return False

# 🧭 4. القائمة الجانبية
with st.sidebar:
    st.title("❄️ MVAC SYSTEM")
    page = st.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 السلعة والمخزون"])

# =========================================================
# 👤 صفحة الزبناء
# =========================================================
if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    
    # جلب البيانات (هنا غاتطلع anva)
    df_c = load_data("Clients")

    # --- خانة الإضافة (Enregistrer) ---
    with st.expander("➕ إضافة زبون جديد", expanded=True):
        with st.form("add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("الاسم أو الشركة *")
            tel = c2.text_input("رقم الهاتف")
            ice = c1.text_input("ICE")
            type_c = c2.selectbox("النوع", ["Particulier", "Société"])
            addr = st.text_area("العنوان")
            
            if st.form_submit_button("تسجيل والحفظ ✅"):
                if name:
                    # حساب ID جديد
                    new_id = int(df_c["ID"].max() + 1) if not df_c.empty and "ID" in df_c.columns else 1
                    new_row = pd.DataFrame([{"ID": new_id, "الاسم/الشركة": name, "النوع": type_c, "ICE": ice, "الهاتف": tel, "العنوان": addr}])
                    
                    # دمج وحفظ
                    df_updated = pd.concat([df_c, new_row], ignore_index=True)
                    if save_data("Clients", df_updated):
                        st.success(f"تم تسجيل {name} بنجاح!")
                        st.rerun()
                else:
                    st.warning("دخل السمية هي الأولى!")

    # --- عرض البيانات (Afficher) ---
    st.markdown("### قائمة الزبناء")
    if not df_c.empty:
        # هاد السطر هو اللي كيعرض ليك الجدول كيفما في Google Sheets
        st.dataframe(df_c, use_container_width=True, hide_index=True)
    else:
        st.info("الجدول خاوي، تأكد من اسم الورقة في Google Sheets.")

# =========================================================
# 📦 صفحة السلعة
# =========================================================
else:
    st.title("📦 إدارة السلعة")
    df_m = load_data("Materiels")
    st.dataframe(df_m, use_container_width=True)
