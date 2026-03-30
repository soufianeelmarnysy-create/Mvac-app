import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 🛠️ 1. الإعدادات والربط المباشر
st.set_page_config(page_title="MVAC Pro System", layout="wide", page_icon="❄️")

conn = st.connection("gsheets", type=GSheetsConnection)
# الرابط اللي عطيتيني (مفتوح للعديل)
URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit?usp=sharing"

# الترتيب اللي فـ Sheets ديالك بالظبط (مهم جداً)
COLS_C = ["ID", "الاسم/الشركة", "النوع", "ICE", "RIB", "العنوان", "الهاتف"]

# 🔄 جلب البيانات (Affichage)
def load_data(sheet_name):
    try:
        # ttl=0 باش يجيب anva وأي حاجة جديدة فالبلاصة
        df = conn.read(spreadsheet=URL, worksheet=sheet_name, ttl=0)
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip() # تنظيف العناوين
            return df[COLS_C] # كيجبر الكود يحترم ترتيبك
        return pd.DataFrame(columns=COLS_C)
    except:
        return pd.DataFrame(columns=COLS_C)

# 💾 حفظ البيانات (Enregistrement)
def save_data(sheet_name, df):
    try:
        conn.update(spreadsheet=URL, worksheet=sheet_name, data=df)
        return True
    except Exception as e:
        st.error(f"❌ خطأ فالحفظ: {e}")
        return False

# 🧭 2. القائمة الجانبية
with st.sidebar:
    st.title("❄️ MVAC SYSTEM")
    st.markdown("---")
    page = st.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 السلعة والمخزون"])

# =========================================================
# 👥 3. صفحة الزبناء (Ajouter & Afficher)
# =========================================================
if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    
    # جلب البيانات الحالية (غاتبان ليك anva هنا)
    df_c = load_data("Clients")

    # --- خانة الإضافة (مرتبة كيف Sheets) ---
    with st.expander("📝 إضافة زبون جديد", expanded=True):
        with st.form("form_add_client", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("الاسم أو الشركة *")
                type_c = st.selectbox("النوع", ["Particulier", "Société"])
                ice = st.text_input("ICE")
            with c2:
                rib = st.text_input("RIB")
                tel = st.text_input("الهاتف")
                addr = st.text_area("العنوان")
            
            if st.form_submit_button("تسجيل والحفظ ✅"):
                if name:
                    # حساب ID جديد أوتوماتيكياً
                    new_id = int(df_c["ID"].max() + 1) if not df_c.empty else 1
                    # تجميع السطر بالترتيب ديال Sheets
                    new_row = pd.DataFrame([[new_id, name, type_c, ice, rib, addr, tel]], columns=COLS_C)
                    df_updated = pd.concat([df_c, new_row], ignore_index=True)
                    
                    if save_data("Clients", df_updated):
                        st.success(f"✅ تم تسجيل {name} بنجاح!")
                        st.rerun()
                else:
                    st.warning("دخل السمية هي الأولى!")

    # --- عرض الجدول ---
    st.markdown("---")
    st.subheader("📋 قائمة الزبناء (Affichage)")
    if not df_c.empty:
        st.dataframe(df_c, use_container_width=True, hide_index=True)
    else:
        st.info("الجدول خاوي، زيد أول كليان.")

# =========================================================
# 📦 4. صفحة السلعة
# =========================================================
else:
    st.title("📦 إدارة السلعة")
    df_m = load_data("Materiels")
    if not df_m.empty:
        st.dataframe(df_m, use_container_width=True, hide_index=True)
    else:
        st.warning("تأكد من وجود ورقة 'Materiels' في الملف.")
