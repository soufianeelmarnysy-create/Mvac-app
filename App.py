import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from fpdf import FPDF
import base64

# ==========================================
# ⚙️ 1. الإعدادات والربط الأساسي
# ==========================================
st.set_page_config(page_title="MVAC Pro System", layout="wide", page_icon="❄️")

conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMl791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

# أسماء الأعمدة الموحدة لتجنب الأخطاء
COLS_C = ["ID", "النوع", "الاسم/الشركة", "ICE", "RIB", "العنوان", "الهاتف"]
COLS_M = ["ID", "المرجع", "السلعة", "الوحدة", "الكمية", "ثمن الوحدة"]

def load_data(sheet_name, columns):
    try:
        st.cache_data.clear()
        df = conn.read(spreadsheet=SHEET_URL, worksheet=sheet_name, ttl=0)
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip()
            df = df.fillna("").astype(str).replace(r'\.0$', '', regex=True)
            return df[columns]
        return pd.DataFrame(columns=columns)
    except:
        return pd.DataFrame(columns=columns)

def save_data(sheet_name, df):
    try:
        conn.update(spreadsheet=SHEET_URL, worksheet=sheet_name, data=df)
        return True
    except Exception as e:
        st.error(f"❌ عطب في الحفظ: {e}")
        return False

# ==========================================
# 🧭 2. المنيو الجانبي
# ==========================================
with st.sidebar:
    st.title("❄️ MVAC SYSTEM")
    st.markdown("---")
    page = st.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 إدارة السلعة", "📄 Devis / Facture"])
    st.markdown("---")
    st.info("SOUFIANE - Full Pro v3.0")

# ==========================================
# 👥 3. صفحة إدارة الزبناء (CRUD)
# ==========================================
if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء (Customers)")
    df_c = load_data("Customers", COLS_C)

    with st.expander("➕ إضافة زبون جديد"):
        with st.form("add_c", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                t_c = st.selectbox("النوع", ["Société", "Particulier"])
                n_c = st.text_input("الاسم أو الشركة *")
                i_c = st.text_input("ICE")
            with c2:
                r_c = st.text_input("RIB")
                te_c = st.text_input("الهاتف")
                a_c = st.text_input("العنوان")
            if st.form_submit_button("حفظ ✅"):
                if n_c:
                    new_id = str(int(pd.to_numeric(df_c["ID"], errors='coerce').max() + 1)) if not df_c.empty else "1"
                    new_row = pd.DataFrame([[new_id, t_c, n_c, i_c, r_c, a_c, te_c]], columns=COLS_C)
                    if save_data("Customers", pd.concat([df_c, new_row], ignore_index=True)):
                        st.success("تم الحفظ!"); st.rerun()

    search = st.text_input("🔍 بحث عن زبون (الاسم، ICE...):")
    df_f = df_c[df_c.stack().str.contains(search, case=False).groupby(level=0).any()] if search else df_c

    for idx, row in df_f.iterrows():
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            col1.write(f"**{row['الاسم/الشركة']}** | {row['النوع']} | ICE: {row['ICE']} | 📞 {row['الهاتف']}")
            if col2.button("🗑️ حذف", key=f"del_c_{row['ID']}"):
                if save_data("Customers", df_c.drop(idx)): st.rerun()

# ==========================================
# 📦 4. صفحة إدارة السلعة (CRUD)
# ==========================================
elif page == "📦 إدارة السلعة":
    st.title("📦 إدارة السلعة (Inventory)")
    df_m = load_data("Materiels", COLS_M)

    with st.expander("➕ إضافة سلعة جديدة"):
        with st.form("add_m", clear_on_submit=True):
            m1, m2 = st.columns(2)
            with m1:
                ref = st.text_input("المرجع (Ref)")
                des = st.text_input("السلعة (Désignation) *")
                uni = st.selectbox("الوحدة", ["U", "M", "ML", "Kg", "Ens"])
            with m2:
                qte = st.text_input("الكمية", value="0")
                pri = st.text_input("ثمن الوحدة (HT)")
            if st.form_submit_button("حفظ السلعة ✅"):
                if des:
                    new_id = str(int(pd.to_numeric(df_m["ID"], errors='coerce').max() + 1)) if not df_m.empty else "1"
                    new_row = pd.DataFrame([[new_id, ref, des, uni, qte, pri]], columns=COLS_M)
                    if save_data("Materiels", pd.concat([df_m, new_row], ignore_index=True)):
                        st.success("تم الحفظ!"); st.rerun()

    search_m = st.text_input("🔍 بحث عن سلعة:")
    df_fm = df_m[df_m['السلعة'].str.contains(search_m, case=False, na=False)] if search_m else df_m
    st.dataframe(df_fm, use_container_width=True, hide_index=True)

# ==========================================
# 📄 5. صفحة الفاتورة (Facturation)
# ==========================================
else:
    st.title("📄 إنشاء Devis / Facture")
    df_c = load_data("Customers", COLS_C)
    df_m = load_data("Materiels", COLS_M)

    if not df_c.empty and not df_m.empty:
        col_doc1, col_doc2, col_doc3 = st.columns([1, 2, 1])
        doc_type = col_doc1.selectbox("نوع الوثيقة", ["DEVIS", "FACTURE"])
        client_sel = col_doc2.selectbox("اختار الزبون", df_c["الاسم/الشركة"].tolist())
        doc_num = col_doc3.text_input("رقم الوثيقة", value="2024/001")

        if 'cart' not in st.session_state: st.session_state.cart = []

        with st.container(border=True):
            st.subheader("🛒 إضافة السلع للوثيقة")
            i1, i2, i3 = st.columns([3, 1, 1])
            sel_item = i1.selectbox("اختار السلعة من المخزن", df_m["السلعة"].tolist())
            qte_sel = i2.number_input("الكمية", min_value=1, value=1)
            if i3.button("➕ إضافة للجدول"):
                item_data = df_m[df_m["السلعة"] == sel_item].iloc[0]
                p_u = float(str(item_data["ثمن الوحدة"]).replace(',', '.') or 0)
                st.session_state.cart.append({
                    "Désignation": sel_item, "Unité": item_data["الوحدة"],
                    "Qte": qte_sel, "P.U HT": p_u, "Total HT": qte_sel * p_u
                })
                st.rerun()

        if st.session_state.cart:
            df_inv = pd.DataFrame(st.session_state.cart)
            st.table(df_inv)
            
            # الحسابات
            total_ht = df_inv["Total HT"].sum()
            tva = total_ht * 0.20
            total_ttc = total_ht + tva

            c1, c2 = st.columns([2, 1])
            with c2:
                st.write(f"Total HT: **{total_ht:,.2f} DH**")
                st.write(f"TVA (20%): **{tva:,.2f} DH**")
                st.error(f"### TOTAL TTC: {total_ttc:,.2f} DH")

            if st.button("📥 إنشاء PDF"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, f"MVAC - {doc_type}", ln=True, align='C')
                pdf.set_font("Arial", '', 12)
                pdf.cell(0, 10, f"Client: {client_sel} | Date: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
                pdf.cell(0, 10, f"Document N: {doc_num}", ln=True)
                pdf.ln(10)
                # جدول بسيط في PDF
                pdf.set_fill_color(200, 220, 255)
                pdf.cell(100, 10, "Designation", 1, 0, 'C', 1)
                pdf.cell(30, 10, "Qte", 1, 0, 'C', 1)
                pdf.cell(30, 10, "P.U", 1, 0, 'C', 1)
                pdf.cell(30, 10, "Total", 1, 1, 'C', 1)
                for item in st.session_state.cart:
                    pdf.cell(100, 10, str(item['Désignation']), 1)
                    pdf.cell(30, 10, str(item['Qte']), 1)
                    pdf.cell(30, 10, f"{item['P.U HT']:.2f}", 1)
                    pdf.cell(30, 10, f"{item['Total HT']:.2f}", 1, 1)
                
                pdf.ln(5)
                pdf.cell(0, 10, f"TOTAL TTC: {total_ttc:,.2f} DH", ln=True, align='R')
                
                pdf_data = pdf.output(dest='S').encode('latin-1')
                b64 = base64.b64encode(pdf_data).decode()
                href = f'<a href="data:application/pdf;base64,{b64}" download="{doc_type}_{doc_num}.pdf">إضغط هنا لتحميل الفاتورة 📄</a>'
                st.markdown(href, unsafe_allow_html=True)
            
            if st.button("🗑️ إفراغ الجدول"):
                st.session_state.cart = []; st.rerun()
    else:
        st.warning("⚠️ المرجو ملء بيانات الزبناء والسلعة أولاً لتتمكن من إنشاء فاتورة.")
