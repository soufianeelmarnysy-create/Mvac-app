import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# =========================================================
# 🛠️ 1. الإعدادات والربط (الأساس)
# =========================================================
st.set_page_config(page_title="MVAC Pro System", layout="wide", page_icon="❄️")

conn = st.connection("gsheets", type=GSheetsConnection)
URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

# الترتيب الصحيح للأعمدة (مراية ديال Google Sheets)
COLS_C = ["ID", "الاسم/الشركة", "النوع", "ICE", "الهاتف", "العنوان", "RIB"]

# 🔄 دالة جلب البيانات (Affichage)
def load_data(sheet_name, columns):
    try:
        df = conn.read(spreadsheet=URL, worksheet=sheet_name, ttl=0)
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip()
            # تأكد بلي الأعمدة كاملة كاينا بالترتيب
            for col in columns:
                if col not in df.columns: df[col] = ""
            return df[columns]
        return pd.DataFrame(columns=columns)
    except:
        return pd.DataFrame(columns=columns)

# 💾 دالة الحفظ (Enregistrement)
def save_data(sheet_name, df):
    try:
        conn.update(spreadsheet=URL, worksheet=sheet_name, data=df)
        return True
    except Exception as e:
        st.error(f"❌ خطأ في الحفظ: {e}")
        return False

# =========================================================
# 🧭 2. القائمة الجانبية (عزل الصفحات)
# =========================================================
with st.sidebar:
    st.title("❄️ MVAC SYSTEM")
    st.markdown("---")
    page = st.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 السلعة والمخزون", "📄 إنشاء Devis/Facture"])
    st.markdown("---")
    st.write("سفيان - MVAC v1.0")

# =========================================================
# 👥 3. صـفـحـة إدارة الـزبـنـاء (Ajouter / Afficher)
# =========================================================
if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    
    # جلب البيانات
    df_c = load_data("Clients", COLS_C)

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
                addr = st.text_area("العنوان الكامل", height=100)
            
            if st.form_submit_button("تسجيل الزبون ✅"):
                if name:
                    # حساب ID جديد
                    new_id = int(df_c["ID"].max() + 1) if not df_c.empty else 1
                    
                    # تجميع البيانات بنفس الترتيب ديال الأعمدة
                    new_row = pd.DataFrame([[new_id, name, type_c, ice, tel, addr, rib]], columns=COLS_C)
                    
                    # دمج وحفظ
                    df_updated = pd.concat([df_c, new_row], ignore_index=True)
                    if save_data("Clients", df_updated):
                        st.success(f"✅ تم تسجيل {name} بنجاح!")
                        st.rerun()
                else:
                    st.warning("السمية ضرورية!")

    # --- عرض البيانات (Affichage) ---
    st.markdown("---")
    st.subheader("📋 قائمة الزبناء المسجلين")
    if not df_c.empty:
        # البحث
        search = st.text_input("🔍 بحث عن زبون...")
        df_display = df_c[df_c["الاسم/الشركة"].astype(str).str.contains(search, case=False)] if search else df_c
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # زر المسح (Supprimer)
        with st.expander("🗑️ مسح زبون من القائمة"):
            to_del = st.selectbox("اختار الاسم للمسح", [""] + df_c["الاسم/الشركة"].tolist())
            if st.button("تأكيد المسح 🗑️"):
                if to_del:
                    df_c = df_c[df_c["الاسم/الشركة"] != to_del]
                    if save_data("Clients", df_c):
                        st.rerun()
    else:
        st.info("الجدول خاوي، زيد أول كليان!")

# =========================================================
# 📦 4. صـفـحـة الـسـلـعـة والـمـخـزون
# =========================================================
elif page == "📦 السلعة والمخزون":
    st.title("📦 إدارة السلعة")
    COLS_M = ["ID", "التعيين", "الوحدة", "الثمن", "الكمية"]
    df_m = load_data("Materiels", COLS_M)

    with st.expander("➕ إضافة سلعة جديدة"):
        with st.form("form_mat"):
            c1, c2, c3 = st.columns([3, 1, 1])
            nom = c1.text_input("Désignation")
            unite = c2.selectbox("Unité", ["U", "M", "M2", "ML", "Kg"])
            price = c3.number_input("Prix (DH)", min_value=0.0)
            
            if st.form_submit_button("إضافة ✅"):
                new_id = int(df_m["ID"].max() + 1) if not df_m.empty else 1
                new_m = pd.DataFrame([[new_id, nom, unite, price, 0]], columns=COLS_M)
                df_updated_m = pd.concat([df_m, new_m], ignore_index=True)
                save_data("Materiels", df_updated_m)
                st.rerun()

    st.dataframe(df_m, use_container_width=True, hide_index=True)

# =========================================================
# 📄 5. صـفـحـة Devis/Facture (واجدة للربط)
# =========================================================
else:
    st.title("📄 إنشاء وثيقة Devis / Facture")
    st.info("هنا غادي نخدمو على الـ PDF فالمرحلة الجاية.")
