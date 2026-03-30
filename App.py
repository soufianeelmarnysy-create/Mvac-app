import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# =========================================================
# 🛠️ 1. الإعدادات والربط (الأساس)
# =========================================================
st.set_page_config(page_title="MVAC Pro System", layout="wide", page_icon="❄️")

# الربط مع Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# الرابط المباشر للملف (تأكد أن هاد الرابط هو اللي فيه ورقة Clients)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

# الترتيب اللي عندك فـ Sheets بالظبط (مراية ديال الملف)
COLS_C = ["ID", "الاسم/الشركة", "النوع", "ICE", "RIB", "العنوان", "الهاتف"]

# 🔄 دالة جلب البيانات (Affichage)
def load_data(sheet_name):
    try:
        # ttl=0 باش يجيب anva وأي جديد فالبلاصة
        df = conn.read(spreadsheet=SHEET_URL, worksheet=sheet_name, ttl=0)
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip() # تنظيف العناوين
            return df[COLS_C] # كيجبر الكود يحترم الترتيب ديالك
        return pd.DataFrame(columns=COLS_C)
    except:
        return pd.DataFrame(columns=COLS_C)

# 💾 دالة الحفظ المضمونة (Enregistrement) - ضد الـ 404
def save_data(sheet_name, df):
    try:
        # هنا كنستعملو الرابط المباشر باش نتفاداو أي غلط فالربط
        conn.update(spreadsheet=SHEET_URL, worksheet=sheet_name, data=df)
        return True
    except Exception as e:
        st.error(f"❌ خطأ 404: البرنامج ملقاش ورقة سميتها '{sheet_name}'")
        st.info("نصيحة: سير لـ Google Sheets وتأكد أن الورقة سميتها Clients (بـ C كبيرة وبلا فراغ موراها)")
        return False

# =========================================================
# 🧭 2. القائمة الجانبية (Sidebar)
# =========================================================
with st.sidebar:
    st.title("❄️ MVAC SYSTEM")
    st.markdown("---")
    page = st.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 السلعة والمخزون"])
    st.markdown("---")
    st.write("سفيان - MVAC v1.0")

# =========================================================
# 👥 3. صـفـحـة إدارة الـزبـنـاء
# =========================================================
if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    
    # جلب البيانات الحالية (هنا غاتبان ليك anva)
    df_c = load_data("Clients")

    # --- خانة الإضافة (Ajouter) مرتبة كيف Sheets ---
    with st.expander("📝 إضافة زبون جديد", expanded=True):
        with st.form("form_add_client", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("الاسم أو الشركة *")
                type_c = st.selectbox("النوع", ["Particulier", "Société"])
                ice = st.text_input("ICE")
            with col2:
                rib = st.text_input("RIB")
                tel = st.text_input("الهاتف")
                addr = st.text_area("العنوان")
            
            if st.form_submit_button("حفظ فـ Google Sheets ✅"):
                if name:
                    # حساب ID جديد أوتوماتيكياً
                    new_id = int(df_c["ID"].max() + 1) if not df_c.empty else 1
                    
                    # تجميع السطر بالترتيب ديال Sheets (ID, الاسم, النوع, ICE, RIB, العنوان, الهاتف)
                    new_row = pd.DataFrame([[new_id, name, type_c, ice, rib, addr, tel]], columns=COLS_C)
                    
                    # دمج الجديد مع القديم
                    df_updated = pd.concat([df_c, new_row], ignore_index=True)
                    
                    # محاولة الحفظ باستعمال الدالة الجديدة
                    if save_data("Clients", df_updated):
                        st.success(f"✅ تم تسجيل {name} بنجاح!")
                        st.rerun()
                else:
                    st.warning("دخل السمية هي الأولى!")

    # --- عرض الجدول (Affichage) ---
    st.markdown("---")
    st.subheader("📋 قائمة الزبناء (Affichage)")
    if not df_c.empty:
        st.dataframe(df_c, use_container_width=True, hide_index=True)
    else:
        st.info("الجدول خاوي أو الورقة غير موجودة. جرب تزيد أول كليان.")

# =========================================================
# 📦 4. صـفـحـة الـسـلـعـة والـمـخـزون
# =========================================================
elif page == "📦 السلعة والمخزون":
    st.title("📦 إدارة السلعة")
    df_m = load_data("Materiels")
    if not df_m.empty:
        st.dataframe(df_m, use_container_width=True, hide_index=True)
    else:
        st.warning("تأكد من وجود ورقة 'Materiels' في الملف بنفس العناوين.")
