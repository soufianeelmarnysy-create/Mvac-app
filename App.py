import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from fpdf import FPDF
import base64

# ==========================================
# 🛠️ 1. الإعدادات والربط
# ==========================================
st.set_page_config(page_title="MVAC Pro System", layout="wide", page_icon="❄️")

conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMl791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

def load_data(sheet_name):
    try:
        st.cache_data.clear()
        df = conn.read(spreadsheet=SHEET_URL, worksheet=sheet_name, ttl=0)
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip()
            df = df.fillna("").astype(str).replace(r'\.0$', '', regex=True)
            return df
        return pd.DataFrame()
    except: return pd.DataFrame()

# ==========================================
# 🧭 2. المنيو الجانبي
# ==========================================
with st.sidebar:
    st.title("❄️ MVAC SYSTEM")
    page = st.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 إدارة السلعة", "📄 إنشاء Devis/Facture"])
    st.markdown("---")
    st.info("SOUFIANE - Pro Edition v2.0")

# --- (صفحات الزبناء والسلعة كتبقى كوداتها سابقة وخدامة) ---
if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    # ... (كود الزبناء)
elif page == "📦 إدارة السلعة":
    st.title("📦 إدارة السلعة")
    # ... (كود السلعة)

# ==========================================
# 📄 3. إنشاء Devis / Facture (مع التخفيض والـ PDF)
# ==========================================
else:
    st.title("📄 إنشاء وثيقة تجارية")
    df_clients = load_data("Customers")
    df_mats = load_data("Materiels")

    if not df_clients.empty and not df_mats.empty:
        # 1. إعدادات الوثيقة
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 2, 1])
            doc_type = c1.selectbox("نوع الوثيقة:", ["DEVIS", "FACTURE"])
            selected_client = c2.selectbox("اختار الزبون:", df_clients["الاسم/الشركة"].unique())
            doc_date = c3.date_input("التاريخ", datetime.now())
            
            # جلب معلومات الزبون المختار
            client_info = df_clients[df_clients["الاسم/الشركة"] == selected_client].iloc[0]

        # 2. إدارة الأسطر
        if 'invoice_items' not in st.session_state: st.session_state.invoice_items = []

        with st.container(border=True):
            st.subheader("🛒 إضافة السلعة")
            i1, i2, i3 = st.columns([3, 1, 1])
            sel_mat = i1.selectbox("السلعة:", df_mats["السلعة"].unique())
            qte = i2.number_input("الكمية:", min_value=1, value=1)
            if i3.button("➕ إضافة"):
                m_info = df_mats[df_mats["السلعة"] == sel_mat].iloc[0]
                price = float(m_info["ثمن الوحدة"])
                st.session_state.invoice_items.append({
                    "Désignation": sel_mat, "U": m_info["الوحدة"],
                    "Qte": qte, "P.U HT": price, "Total HT": price * qte
                })
                st.rerun()

        # 3. عرض الجدول والتحكم في الأسطر
        if st.session_state.invoice_items:
            df_inv = pd.DataFrame(st.session_state.invoice_items)
            st.table(df_inv)
            
            # زر مسح آخر سطر
            if st.button("⬅️ مسح آخر سطر"):
                st.session_state.invoice_items.pop()
                st.rerun()

            st.markdown("---")
            
            # --- 💰 خاصية التخفيض (Commission/Remise) ---
            col_calc1, col_calc2 = st.columns([2, 1])
            with col_calc2:
                discount_pc = st.number_input("تخفيض / Remise (%)", min_value=0, max_value=100, value=0)
                
                total_ht_raw = df_inv["Total HT"].sum()
                discount_val = total_ht_raw * (discount_pc / 100)
                total_ht_final = total_ht_raw - discount_val
                tva = total_ht_final * 0.20
                total_ttc = total_ht_final + tva

                st.write(f"**Total HT Brut:** {total_ht_raw:,.2f} DH")
                if discount_pc > 0:
                    st.write(f"**Remise ({discount_pc}%):** -{discount_val:,.2f} DH")
                st.write(f"**Total HT Net:** {total_ht_final:,.2f} DH")
                st.write(f"**TVA (20%):** {tva:,.2f} DH")
                st.error(f"### TOTAL TTC: {total_ttc:,.2f} DH")

            # 4. زر تحميل الـ PDF (تحضير الملف)
            if st.button("📥 Télécharger PDF"):
                # كود بسيط لتوليد PDF (مثال توضيحي)
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, txt=f"MVAC - {doc_type}", ln=True, align='C')
                pdf.set_font("Arial", '', 12)
                pdf.cell(200, 10, txt=f"Client: {selected_client}", ln=True)
                pdf.cell(200, 10, txt=f"Date: {doc_date}", ln=True)
                pdf.cell(200, 10, txt=f"Total TTC: {total_ttc:,.2f} DH", ln=True)
                
                # تحميل الملف
                pdf_output = pdf.output(dest='S').encode('latin-1')
                b64 = base64.b64encode(pdf_output).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="{doc_type}_{selected_client}.pdf">اضغط هنا لتحميل الملف PDF 📄</a>'
                st.markdown(href, unsafe_allow_html=True)

    else:
        st.warning("⚠️ عمر البيانات في 'الزبناء' و 'السلعة' أولاً.")
