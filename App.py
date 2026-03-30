import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 🛠️ 1. إعدادات الصفحة (حيدنا الأيقونات البرانية)
st.set_page_config(page_title="MVAC System", layout="wide", page_icon="❄️")

conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

# 🔄 2. دالة جلب البيانات مع تنظيفها
def load_data(sheet_name):
    try:
        # ttl=0 باش يجيب البيانات دابا نيت بلا تعطل
        df = conn.read(spreadsheet=SHEET_URL, worksheet=sheet_name, ttl=0)
        # تنظيف العناوين من الفراغات
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        return pd.DataFrame()

# 🧭 3. القائمة الجانبية (Sidebar) نقيّة
with st.sidebar:
    st.title("❄️ MVAC SYSTEM")
    st.markdown("---")
    page = st.radio("اختار الصفحة:", ["👤 إدارة الزبناء", "📦 السلعة والمخزون", "📄 إنشاء Devis/Facture"])
    st.markdown("---")
    st.caption("سفيان - نظام تسيير MVAC")

# =========================================================
# 👤 صفحة الزبناء (الخدمة هنا)
# =========================================================
if page == "👤 إدارة الزبناء":
    st.title("👤 إدارة الزبناء")
    
    df_c = load_data("Clients")

    # --- 4. الجزء ديال إضافة زبون جديد (ديما باين باش تخدم) ---
    with st.expander("➕ إضافة زبون جديد", expanded=True):
        with st.form("add_new_client"):
            c1, c2 = st.columns(2)
            name = c1.text_input("الاسم أو الشركة *")
            tel = c2.text_input("رقم الهاتف")
            ice = c1.text_input("ICE")
            type_c = c2.selectbox("نوع الزبون", ["Particulier", "Société"])
            addr = st.text_area("العنوان الكامل")
            
            submit = st.form_submit_button("تسجيل الزبون في القاعدة ✅")
            
            if submit and name:
                # حساب الـ ID الجديد
                new_id = int(df_c["ID"].max() + 1) if not df_c.empty and "ID" in df_c.columns else 1
                new_row = pd.DataFrame([{"ID": new_id, "الاسم/الشركة": name, "النوع": type_c, "ICE": ice, "الهاتف": tel, "العنوان": addr}])
                
                # دمج وحفظ
                df_updated = pd.concat([df_c, new_row], ignore_index=True)
                conn.update(spreadsheet=SHEET_URL, worksheet="Clients", data=df_updated)
                st.success(f"تمت إضافة {name} بنجاح!")
                st.rerun()

    # --- 5. عرض الجدول (فين غاتبان anva) ---
    st.markdown("### قائمة الزبناء المسجلين")
    if not df_c.empty:
        st.dataframe(df_c, use_container_width=True, hide_index=True)
        
        # زر المسح (إلى بغيتي تمسح شي حد)
        st.markdown("---")
        del_name = st.selectbox("اختار زبون للمسح:", [""] + df_c["الاسم/الشركة"].tolist())
        if st.button("🗑️ مسح الزبون المختار"):
            if del_name:
                df_c = df_c[df_c["الاسم/الشركة"] != del_name]
                conn.update(spreadsheet=SHEET_URL, worksheet="Clients", data=df_c)
                st.warning(f"تم مسح {del_name}")
                st.rerun()
    else:
        st.info("الجدول خاوي حالياً. استعمل الفورم اللي فوق باش تزيد أول كليان!")

# الصفحات الأخرى خاوية دابا حتى نساليو مع الكليان
else:
    st.title(page)
    st.info("هاد الصفحة غانكملوها غير نتأكدوا باللي الكليان خدامين ناضي.")
