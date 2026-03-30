import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from fpdf import FPDF
import base64

# ==========================================
# ⚙️ 1. الإعدادات والربط (مرة واحدة فقط)
# ==========================================
st.set_page_config(page_title="MVAC Pro System", layout="wide", page_icon="❄️")

conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMl791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

# أسماء الأعمدة الموحدة
COLS_C = ["ID", "النوع", "الاسم/الشركة", "ICE", "RIB", "العنوان", "الهاتف"]
COLS_M = ["ID", "المرجع", "السلعة", "الوحدة", "الكمية", "ثمن الوحدة"]

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
    df_c = load_data("Customers")

    with st.expander("➕ إضافة زبون جديد"):
        with st.form("form_add_client", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                t_c = st.selectbox("النوع", ["Particulier", "Société"])
                n_c = st.text_input("الاسم أو الشركة *")
                i_c = st.text_input("🆔 ICE")
            with c2:
                r_c = st.text_input("💳 RIB")
                a_c = st.text_input("📍 العنوان")
                te_c = st.text_input("📞 الهاتف")
            
            if st.form_submit_button("حفظ ✅"):
                if n_c:
                    new_id = str(int(pd.to_numeric(df_c["ID"], errors='coerce').max() + 1)) if not df_c.empty else "1"
                    new_row = pd.DataFrame([[new_id, t_c, n_c, i_c, r_c, a_c, te_c]], columns=COLS_C)
                    if save_data("Customers", pd.concat([df_c, new_row], ignore_index=True)):
                        st.success("✅ تم الحفظ!"); st.rerun()

    search = st.text_input("🔍 قلب على كليان...", placeholder="مثال: anva")
    df_filtered = df_c[df_c['الاسم/الشركة'].str.contains(search, case=False, na=False)] if not df_c.empty else df_c

    if not df_filtered.empty:
        for index, row in df_filtered.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### 👤 {row['الاسم/الشركة']}")
                    st.write(f"🆔 ICE: `{row['ICE']}` | 📞 Tel: `{row['الهاتف']}`")
                with col2:
                    if st.button(f"🗑️ حذف", key=f"del_c_{row['ID']}"):
                        df_c = df_c.drop(index)
                        if save_data("Customers", df_c): st.rerun()

# ==========================================
# 📦 4. صفحة إدارة السلعة
# ==========================================
elif page == "📦 إدارة السلعة":
    st.title("📦 إدارة السلعة (Materiels)")
    df_m = load_data("Materiels")

    with st.expander("➕ إضافة سلعة جديدة"):
        with st.form("form_add_mat", clear_on_submit=True):
            m1, m2, m3 = st.columns(3)
            with m1:
                ref = st.text_input("🔢 المرجع (Ref)")
                des = st.text_input("📝 السلعة *")
            with m2:
                uni = st.selectbox("📏 الوحدة", ["U", "M", "M2", "ML", "Kg", "Ens"])
                qte = st.text_input("🔢 الكمية", value="0")
            with m3:
                pri = st.text_input("💰 ثمن الوحدة")
            
            if st.form_submit_button("حفظ السلعة ✅"):
                if des:
                    new_id = str(int(pd.to_numeric(df_m["ID"], errors='coerce').max() + 1)) if not df_m.empty else "1"
                    new_row = pd.DataFrame([[new_id, ref, des, uni, qte, pri]], columns=COLS_M)
                    if save_data("Materiels", pd.concat([df_m, new_row], ignore_index=True)):
                        st.success("✅ تم الحفظ!"); st.rerun()

    search_m = st.text_input("🔍 قلب على سلعة...")
    df_filtered_m = df_m[df_m['السلعة'].str.contains(search_m, case=False, na=False)] if not df_m.empty else df_m
    st.dataframe(df_filtered_m, use_container_width=True)

# ==========================================
# 📄 5. إنشاء Devis / Facture
# ==========================================
else:
    st.title("📄 إنشاء وثيقة تجارية")
    df_c = load_data("Customers")
    df_m = load_data("Materiels")

    if not df_c.empty and not df_m.empty:
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 2, 1])
            d_type = col1.selectbox("النوع:", ["DEVIS", "FACTURE"])
            client_name = col2.selectbox("اختار الزبون:", df_c["الاسم/الشركة"].unique())
            d_num = col3.text_input("N° الوثيقة:", value="A0045")

        if 'invoice_items' not in st.session_state: st.session_state.invoice_items = []

        with st.container(border=True):
            st.subheader("🛒 إضافة سلعة")
            i1, i2, i3 = st.columns([3, 1, 1])
            sel_mat = i1.selectbox("اختار السلعة:", df_m["السلعة"].unique())
            qte_in = i2.number_input("الكمية:", min_value=1, value=1)
            
            if i3.button("➕ إضافة"):
                m_info = df_m[df_m["السلعة"] == sel_mat].iloc[0]
                p_u = float(str(m_info["ثمن الوحدة"]).replace(',', '.').strip() or 0)
                st.session_state.invoice_items.append({
                    "Désignation": sel_mat, "Unité": m_info["الوحدة"],
                    "Qte": qte_in, "P.U HT": p_u, "Total HT": qte_in * p_u
                })
                st.rerun()

        if st.session_state.invoice_items:
            df_inv = pd.DataFrame(st.session_state.invoice_items)
            for idx, row in df_inv.iterrows():
                c_i, c_d = st.columns([6, 1])
                c_i.info(f"✅ {row['Désignation']} | {row['Qte']} {row['Unité']} x {row['P.U HT']} DH")
                if c_d.button("🗑️", key=f"del_item_{idx}"):
                    st.session_state.invoice_items.pop(idx); st.rerun()

            st.markdown("---")
            remise_pc = st.number_input("Remise / Commission (%)", min_value=0, max_value=100, value=0)
            brut_ht = df_inv["Total HT"].sum()
            net_ht = brut_ht * (1 - remise_pc/100)
            tva = net_ht * 0.20
            total_ttc = net_ht + tva

            st.write(f"Total HT: **{net_ht:,.2f} DH** | TVA (20%): **{tva:,.2f} DH**")
            st.error(f"### TOTAL TTC: {total_ttc:,.2f} DH")

            if st.button("📥 تحميل PDF"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Helvetica", 'B', 16)
                pdf.cell(0, 10, f"M-VAC - {d_type}", ln=True, align='C')
                # (باقي كود الـ PDF هنا...)
                st.success("تم تجهيز الملف!")
    else:
        st.warning("⚠️ دخل السلعة والكليان هو الأول.")
