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
    page = st.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 إدارة السلعة", "📄 إنشاء Devis/Facture"])
    st.markdown("---")
    st.info("SOUFIANE - Pro Edition v2.5")

# ==========================================
# 👥 3. صفحة إدارة الزبناء
# ==========================================
if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء (Customers)")
    COLS_C = ["ID", "النوع", "الاسم/الشركة", "ICE", "RIB", "العنوان", "الهاتف"]
    df_c = load_data("Customers")

    with st.expander("➕ إضافة زبون جديد"):
        with st.form("add_client"):
            c1, c2 = st.columns(2)
            with c1:
                t_c = st.selectbox("النوع", ["Société", "Particulier"])
                n_c = st.text_input("الاسم أو الشركة *")
                i_c = st.text_input("🆔 ICE")
            with c2:
                a_c = st.text_input("📍 العنوان")
                te_c = st.text_input("📞 الهاتف")
            if st.form_submit_button("حفظ ✅"):
                if n_c:
                    new_id = str(int(pd.to_numeric(df_c["ID"], errors='coerce').max() + 1)) if not df_c.empty else "1"
                    new_row = pd.DataFrame([[new_id, t_c, n_c, i_c, "", a_c, te_c]], columns=COLS_C)
                    if save_data("Customers", pd.concat([df_c, new_row], ignore_index=True)):
                        st.success("تم الحفظ بنجاح!"); st.rerun()

    st.dataframe(df_c, use_container_width=True)

# ==========================================
# 📦 4. صفحة إدارة السلعة
# ==========================================
elif page == "📦 إدارة السلعة":
    st.title("📦 إدارة السلعة (Materiels)")
    COLS_M = ["ID", "المرجع", "السلعة", "الوحدة", "الكمية", "ثمن الوحدة"]
    df_m = load_data("Materiels")

    with st.expander("➕ إضافة سلعة جديدة"):
        with st.form("add_mat"):
            m1, m2 = st.columns(2)
            with m1:
                des = st.text_input("السلعة (Désignation) *")
                ref = st.text_input("المرجع (Ref)")
            with m2:
                uni = st.selectbox("الوحدة", ["U", "M", "M2", "ML", "Ens"])
                pri = st.text_input("ثمن الوحدة (P.U)")
            if st.form_submit_button("حفظ السلعة ✅"):
                if des:
                    new_id = str(int(pd.to_numeric(df_m["ID"], errors='coerce').max() + 1)) if not df_m.empty else "1"
                    new_row = pd.DataFrame([[new_id, ref, des, uni, "0", pri]], columns=COLS_M)
                    if save_data("Materiels", pd.concat([df_m, new_row], ignore_index=True)):
                        st.success("تم حفظ السلعة!"); st.rerun()

    st.dataframe(df_m, use_container_width=True)

# ==========================================
# 📄 5. إنشاء Devis / Facture (النسخة الاحترافية)
# ==========================================
else:
    st.title("📄 إنشاء وثيقة تجارية")
    df_c = load_data("Customers")
    df_m = load_data("Materiels")

    if not df_c.empty and not df_m.empty:
        # 1. إعدادات الوثيقة
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 2, 1])
            d_type = col1.selectbox("النوع:", ["DEVIS", "FACTURE"])
            client_name = col2.selectbox("اختار الزبون:", df_c["الاسم/الشركة"].unique())
            d_num = col3.text_input("N° الوثيقة:", value="A0045")
            
            client_data = df_c[df_c["الاسم/الشركة"] == client_name].iloc[0]

        # 2. إضافة الأسطر (Session State)
        if 'invoice_items' not in st.session_state: st.session_state.invoice_items = []

        with st.container(border=True):
            st.subheader("🛒 إضافة سلعة للجدول")
            i1, i2, i3 = st.columns([3, 1, 1])
            sel_mat = i1.selectbox("اختار السلعة:", df_m["السلعة"].unique())
            qte_in = i2.number_input("الكمية:", min_value=1, value=1)
            
            if i3.button("➕ إضافة"):
                m_info = df_m[df_m["السلعة"] == sel_mat].iloc[0]
                p_u = float(str(m_info["ثمن الوحدة"]).replace(',', '.').strip())
                st.session_state.invoice_items.append({
                    "Désignation": sel_mat, "Unité": m_info["الوحدة"],
                    "Qte": qte_in, "P.U HT": p_u, "Total HT": qte_in * p_u
                })
                st.rerun()

        # 3. عرض الجدول والتحكم في الحذف
        if st.session_state.invoice_items:
            df_inv = pd.DataFrame(st.session_state.invoice_items)
            st.markdown("### الأسطر الحالية:")
            for idx, row in df_inv.iterrows():
                col_info, col_del = st.columns([6, 1])
                col_info.info(f"✅ {row['Désignation']} | {row['Qte']} {row['Unité']} x {row['P.U HT']} DH")
                if col_del.button("🗑️", key=f"del_{idx}"):
                    st.session_state.invoice_items.pop(idx)
                    st.rerun()

            # 4. الحسابات مع الـ Commission (Remise)
            st.markdown("---")
            calc1, calc2 = st.columns([2, 1])
            with calc2:
                remise_pc = st.number_input("Remise / Commission (%)", min_value=0, max_value=100, value=0)
                brut_ht = df_inv["Total HT"].sum()
                val_remise = brut_ht * (remise_pc / 100)
                net_ht = brut_ht - val_remise
                tva = net_ht * 0.20
                total_ttc = net_ht + tva

                st.write(f"Total HT Brut: **{brut_ht:,.2f} DH**")
                if remise_pc > 0:
                    st.write(f"Remise ({remise_pc}%): **-{val_remise:,.2f} DH**")
                st.write(f"Total Taxe (20%): **{tva:,.2f} DH**")
                st.error(f"## TOTAL TTC: {total_ttc:,.2f} DH")

            # 5. توليد PDF (كود مبسط واحترافي)
            if st.button("📥 تحميل PDF"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Helvetica", 'B', 16)
                pdf.cell(0, 10, f"M-VAC - {d_type}", ln=True, align='C')
                pdf.set_font("Helvetica", '', 10)
                pdf.cell(0, 10, f"Numéro: {d_num} | Date: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
                pdf.cell(0, 10, f"Client: {client_name}", ln=True)
                pdf.ln(10)
                
                # إخراج ملف PDF
                pdf_output = pdf.output()
                b64 = base64.b64encode(pdf_output).decode()
                href = f'<a href="data:application/pdf;base64,{b64}" download="{d_type}_{d_num}.pdf">إضغط هنا لتحميل الملف 📄</a>'
                st.markdown(href, unsafe_allow_html=True)
    else:
        st.warning("⚠️ المرجو ملء بيانات الزبناء والسلعة أولاً.")
