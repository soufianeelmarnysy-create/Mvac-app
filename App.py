import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 🛠️ الإعدادات الأساسية
st.set_page_config(page_title="MVAC Pro System", layout="wide", page_icon="❄️")

conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

# 🔄 دالة جلب البيانات
def load_data(sheet_name):
    try:
        df = conn.read(spreadsheet=SHEET_URL, worksheet=sheet_name, ttl=0)
        return df
    except:
        return pd.DataFrame()

# 💾 دالة حفظ البيانات
def save_data(sheet_name, df):
    try:
        conn.update(spreadsheet=SHEET_URL, worksheet=sheet_name, data=df)
        return True
    except Exception as e:
        st.error(f"خطأ في الحفظ: {e}")
        return False

# 🧭 القائمة الجانبية
with st.sidebar:
    st.title("❄️ MVAC SYSTEM")
    st.image("https://cdn-icons-png.flaticon.com/512/3209/3209943.png", width=100) # لوغو تقريبي
    page = st.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 السلعة والمخزون", "📄 إنشاء Devis/Facture"])
    st.markdown("---")
    st.caption("MVAC سفيان - نظام تسيير v1.0")

# =========================================================
# 👥 صفحة الزبناء
# =========================================================
if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    df_c = load_data("Clients")

    if not df_c.empty:
        # فورم الإضافة
        with st.expander("📝 إضافة زبون جديد"):
            with st.form("add_client"):
                c1, c2 = st.columns(2)
                name = c1.text_input("الاسم / الشركة *")
                tel = c2.text_input("الهاتف")
                ice = c1.text_input("ICE")
                type_c = c2.selectbox("النوع", ["Particulier", "Société"])
                addr = st.text_area("العنوان")
                submit = st.form_submit_button("حفظ ✅")
                
                if submit and name:
                    new_id = int(df_c["ID"].max() + 1) if not df_c.empty else 1
                    new_row = pd.DataFrame([{"ID": new_id, "الاسم/الشركة": name, "النوع": type_c, "ICE": ice, "الهاتف": tel, "العنوان": addr}])
                    df_c = pd.concat([df_c, new_row], ignore_index=True)
                    if save_data("Clients", df_c):
                        st.success("تم تسجيل الزبون!")
                        st.rerun()

        # عرض البيانات مع إمكانية المسح
        st.markdown("### لـيـسـتـة الـزبـنـاء")
        for i, row in df_c.iterrows():
            col1, col2 = st.columns([6, 1])
            col1.info(f"👤 **{row['الاسم/الشركة']}** | 📞 {row['الهاتف']} | 📍 {row['العنوان']}")
            if col2.button("🗑️", key=f"del_{i}"):
                df_c = df_c.drop(i)
                save_data("Clients", df_c)
                st.rerun()
    else:
        st.warning("الجدول خاوي أو ورقة Clients ما كايناش.")

# =========================================================
# 📦 صفحة السلعة
# =========================================================
elif page == "📦 السلعة والمخزون":
    st.title("📦 إدارة السلعة والمخزون")
    df_m = load_data("Materiels")

    with st.expander("➕ إضافة سلعة جديدة"):
        with st.form("add_mat"):
            c1, c2, c3 = st.columns([3, 1, 1])
            item = c1.text_input("اسم المادة (Désignation)")
            unit = c2.text_input("الوحدة (Unit)")
            price = c3.number_input("الثمن (DH)", min_value=0.0)
            if st.form_submit_button("إضافة ✅"):
                new_id = int(df_m["ID"].max() + 1) if not df_m.empty else 1
                new_row = pd.DataFrame([{"ID": new_id, "التعيين": item, "الوحدة": unit, "الثمن": price}])
                df_m = pd.concat([df_m, new_row], ignore_index=True)
                save_data("Materiels", df_m)
                st.rerun()
    
    st.dataframe(df_m, use_container_width=True, hide_index=True)

# =========================================================
# 📄 صفحة الفواتير
# =========================================================
else:
    st.title("📄 إنشاء Devis / Facture")
    df_c = load_data("Clients")
    df_m = load_data("Materiels")

    col1, col2 = st.columns(2)
    client_choice = col1.selectbox("اختار الزبون:", df_c["الاسم/الشركة"].tolist() if not df_c.empty else [])
    doc_type = col2.selectbox("نوع الوثيقة:", ["Devis", "Facture"])

    st.markdown("---")
    st.subheader("🛒 السلعة المختارة")
    
    # هنا كنزيدو السيستيم ديال اختيار السلعة والحساب
    if not df_m.empty:
        selected_item = st.selectbox("اختار السلعة:", df_m["التعيين"].tolist())
        qte = st.number_input("الكمية:", min_value=1)
        if st.button("إضافة للفاتورة ➕"):
            st.success(f"تمت إضافة {qte} من {selected_item}")
            # هادي غانكملو فيها الحساب والـ PDF فالمرحلة الجاية

    st.button("📥 تحميل الوثيقة (PDF)")
