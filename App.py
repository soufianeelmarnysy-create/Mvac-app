import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# ==========================================
# 🛠️ 1. الإعدادات والربط
# ==========================================
st.set_page_config(page_title="MVAC Pro System", layout="wide", page_icon="❄️")

conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMl791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

# دالة جلب البيانات مع تنظيف الأرقام
def load_data(sheet_name):
    try:
        st.cache_data.clear()
        df = conn.read(spreadsheet=SHEET_URL, worksheet=sheet_name, ttl=0)
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip()
            # تحويل الأرقام لنصوص وحذف .0 الزائدة
            df = df.fillna("").astype(str).replace(r'\.0$', '', regex=True)
            return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# دالة الحفظ
def save_data(sheet_name, df):
    try:
        conn.update(spreadsheet=SHEET_URL, worksheet=sheet_name, data=df)
        return True
    except Exception as e:
        st.error(f"❌ خطأ في الحفظ: {e}")
        return False

# ==========================================
# 🧭 2. المنيو الجانبي
# ==========================================
with st.sidebar:
    st.title("❄️ MVAC SYSTEM")
    st.markdown("---")
    page = st.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 إدارة السلعة", "📄 إنشاء Devis/Facture"])
    st.markdown("---")
    st.info("SOUFIANE - Pro Edition v1.5")

# ==========================================
# 👥 3. صفحة إدارة الزبناء
# ==========================================
if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    df_c = load_data("Customers")
    COLS_C = ["ID", "النوع", "الاسم/الشركة", "ICE", "RIB", "العنوان", "الهاتف"]

    with st.expander("➕ إضافة زبون جديد"):
        with st.form("add_client"):
            c1, c2 = st.columns(2)
            t_c = c1.selectbox("النوع", ["Société", "Particulier"])
            n_c = c1.text_input("الاسم أو الشركة *")
            i_c = c1.text_input("ICE")
            r_c = c2.text_input("RIB")
            a_c = c2.text_area("العنوان")
            te_c = c2.text_input("الهاتف")
            if st.form_submit_button("حفظ ✅"):
                if n_c:
                    new_id = str(int(pd.to_numeric(df_c["ID"], errors='coerce').max() + 1)) if not df_c.empty else "1"
                    new_row = pd.DataFrame([[new_id, t_c, n_c, i_c, r_c, a_c, te_c]], columns=COLS_C)
                    df_c = pd.concat([df_c, new_row], ignore_index=True)
                    if save_data("Customers", df_c): st.rerun()

    st.dataframe(df_c, use_container_width=True, hide_index=True)

# ==========================================
# 📦 4. صفحة إدارة السلعة
# ==========================================
elif page == "📦 إدارة السلعة":
    st.title("📦 إدارة السلعة (Materiels)")
    df_m = load_data("Materiels")
    COLS_M = ["ID", "المرجع", "السلعة", "الوحدة", "الكمية", "ثمن الوحدة"]

    with st.expander("➕ إضافة سلعة جديدة"):
        with st.form("add_mat"):
            m1, m2 = st.columns(2)
            ref = m1.text_input("المرجع (Ref)")
            des = m1.text_input("السلعة (Désignation) *")
            uni = m2.selectbox("الوحدة", ["U", "M", "M2", "ML", "Kg", "Ens"])
            pri = m2.number_input("ثمن الوحدة (HT)", min_value=0.0)
            if st.form_submit_button("حفظ السلعة ✅"):
                if des:
                    new_id = str(int(pd.to_numeric(df_m["ID"], errors='coerce').max() + 1)) if not df_m.empty else "1"
                    new_row = pd.DataFrame([[new_id, ref, des, uni, "0", str(pri)]], columns=COLS_M)
                    df_m = pd.concat([df_m, new_row], ignore_index=True)
                    if save_data("Materiels", df_m): st.rerun()

    st.dataframe(df_m, use_container_width=True, hide_index=True)

# ==========================================
# 📄 5. إنشاء Devis (المحرك الرئيسي)
# ==========================================
else:
    st.title("📄 إنشاء وثيقة جديدة (Devis/Facture)")
    
    df_clients = load_data("Customers")
    df_mats = load_data("Materiels")

    if not df_clients.empty and not df_mats.empty:
        # أ. معلومات الفاتورة
        with st.container(border=True):
            col1, col2 = st.columns(2)
            selected_client = col1.selectbox("اختار الزبون:", df_clients["الاسم/الشركة"].unique())
            doc_date = col2.date_input("التاريخ", datetime.now())
            
        # ب. إضافة الأسطر (Items)
        if 'invoice_items' not in st.session_state:
            st.session_state.invoice_items = []

        with st.container(border=True):
            st.subheader("🛒 إضافة السلعة")
            i1, i2, i3 = st.columns([3, 1, 1])
            selected_mat = i1.selectbox("السلعة:", df_mats["السلعة"].unique())
            qte = i2.number_input("الكمية:", min_value=1, value=1)
            
            if i3.button("➕ إضافة للجدول"):
                # جلب الثمن والوحدة أوتوماتيكياً
                mat_info = df_mats[df_mats["السلعة"] == selected_mat].iloc[0]
                price = float(mat_info["ثمن الوحدة"])
                unit = mat_info["الوحدة"]
                total_line = price * qte
                
                st.session_state.invoice_items.append({
                    "DESIGNATION": selected_mat,
                    "UNITE": unit,
                    "QTE": qte,
                    "P.UNIT HT": price,
                    "TOTAL HT": total_line
                })

        # ج. عرض الجدول والحسابات (النتيجة النهائية)
        if st.session_state.invoice_items:
            st.markdown("---")
            df_invoice = pd.DataFrame(st.session_state.invoice_items)
            st.table(df_invoice)
            
            # الحسابات (Calculs)
            sum_ht = df_invoice["TOTAL HT"].sum()
            tva = sum_ht * 0.20
            total_ttc = sum_ht + tva
            
            # عرض النتائج بحال النموذج اللي صيفطتي
            c_res1, c_res2 = st.columns([2, 1])
            with c_res2:
                st.write(f"**TOTAL HT:** {sum_ht:,.2f} DH")
                st.write(f"**TVA (20%):** {tva:,.2f} DH")
                st.markdown(f"### **TOTAL TTC: {total_ttc:,.2f} DH**")
            
            if st.button("🗑️ مسح الجدول"):
                st.session_state.invoice_items = []
                st.rerun()
    else:
        st.warning("⚠️ تأكد من إضافة الزبناء والسلعة أولاً!")
