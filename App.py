import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from fpdf import FPDF
import base64

# 🛠️ 1. الإعدادات الأساسية والربط
st.set_page_config(page_title="MVAC Pro System", layout="wide", page_icon="❄️")

conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMl791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

# تعريف الأعمدة
COLS_C = ["ID", "النوع", "الاسم/الشركة", "ICE", "RIB", "العنوان", "الهاتف"]
COLS_M = ["ID", "المرجع", "السلعة", "الوحدة", "الكمية", "ثمن الوحدة"]

# 🔄 دالة جلب البيانات
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

# 💾 دالة الحفظ
def save_data(sheet_name, df):
    try:
        conn.update(spreadsheet=SHEET_URL, worksheet=sheet_name, data=df)
        return True
    except Exception as e:
        st.error(f"❌ خطأ في الحفظ: {e}")
        return False

# 🧭 2. القائمة الجانبية
with st.sidebar:
    st.title("❄️ MVAC SYSTEM")
    page = st.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 إدارة السلعة", "📄 Devis / Facture"])
    st.markdown("---")
    st.info("SOUFIANE - Pro Edition v3.8")

# ==========================================
# 👥 3. صفحة الزبناء (إضافة، بحث، تعديل، حذف)
# ==========================================
if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء (Customers)")
    df_c = load_data("Customers", COLS_C)

    with st.expander("➕ إضافة زبون جديد"):
        with st.form("add_client_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                t_c = st.selectbox("النوع", ["Société", "Particulier"])
                n_c = st.text_input("الاسم أو الشركة *")
                i_c = st.text_input("🆔 ICE")
            with c2:
                te_c = st.text_input("📞 الهاتف")
                a_c = st.text_input("📍 العنوان")
            if st.form_submit_button("حفظ ✅"):
                if n_c:
                    new_id = str(int(pd.to_numeric(df_c["ID"], errors='coerce').max() + 1)) if not df_c.empty else "1"
                    new_row = pd.DataFrame([[new_id, t_c, n_c, i_c, "", a_c, te_c]], columns=COLS_C)
                    if save_data("Customers", pd.concat([df_c, new_row], ignore_index=True)):
                        st.success("✅ تم الحفظ!"); st.rerun()

    st.markdown("---")
    search_c = st.text_input("🔍 قلب على كليان بالسمية أو ICE...")
    df_f = df_c[df_c['الاسم/الشركة'].str.contains(search_c, case=False, na=False) | 
                df_c['ICE'].str.contains(search_c, case=False, na=False)] if search_c else df_c

    if not df_f.empty:
        for idx, row in df_f.iterrows():
            with st.container(border=True):
                col_info, col_btns = st.columns([3, 1])
                with col_info:
                    st.markdown(f"### 👤 {row['الاسم/الشركة']} ({row['النوع']})")
                    st.write(f"🆔 ICE: `{row['ICE']}` | 📞 Tel: `{row['الهاتف']}` | 📍 {row['العنوان']}")
                
                with col_btns:
                    st.write("")
                    if st.button("📝 تعديل", key=f"edit_c_{row['ID']}"): st.session_state[f"mode_c_{row['ID']}"] = True
                    if st.button("🗑️ حذف", key=f"del_c_{row['ID']}"):
                        if save_data("Customers", df_c.drop(idx)): st.rerun()

                # نافذة التعديل (Edit Mode)
                if st.session_state.get(f"mode_c_{row['ID']}", False):
                    with st.form(f"edit_form_c_{row['ID']}"):
                        st.info(f"تعديل بيانات: {row['الاسم/الشركة']}")
                        new_n = st.text_input("الاسم", value=row['الاسم/الشركة'])
                        new_i = st.text_input("ICE", value=row['ICE'])
                        new_t = st.text_input("الهاتف", value=row['الهاتف'])
                        new_a = st.text_input("العنوان", value=row['العنوان'])
                        
                        b_up, b_can = st.columns(2)
                        if b_up.form_submit_button("تحديث 💾"):
                            df_c.loc[idx, ["الاسم/الشركة", "ICE", "الهاتف", "العنوان"]] = [new_n, new_i, new_t, new_a]
                            if save_data("Customers", df_c):
                                st.session_state[f"mode_c_{row['ID']}"] = False
                                st.rerun()
                        if b_can.form_submit_button("إلغاء ❌"):
                            st.session_state[f"mode_c_{row['ID']}"] = False
                            st.rerun()

# ==========================================
# 📦 4. صفحة السلعة (إضافة، بحث، تعديل، حذف)
# ==========================================
elif page == "📦 إدارة السلعة":
    st.title("📦 إدارة السلعة (Inventory)")
    df_m = load_data("Materiels", COLS_M)

    with st.expander("➕ إضافة سلعة جديدة"):
        with st.form("add_mat_form", clear_on_submit=True):
            m1, m2 = st.columns(2)
            with m1:
                ref = st.text_input("🔢 المرجع (Ref)")
                des = st.text_input("📝 السلعة *")
            with m2:
                qte = st.text_input("🔢 الكمية", value="0")
                pri = st.text_input("💰 ثمن الوحدة HT")
            if st.form_submit_button("حفظ السلعة ✅"):
                if des:
                    new_id = str(int(pd.to_numeric(df_m["ID"], errors='coerce').max() + 1)) if not df_m.empty else "1"
                    new_row = pd.DataFrame([[new_id, ref, des, "U", qte, pri]], columns=COLS_M)
                    if save_data("Materiels", pd.concat([df_m, new_row], ignore_index=True)):
                        st.success("✅ تم الحفظ!"); st.rerun()

    st.markdown("---")
    search_m = st.text_input("🔍 قلب بسمية السلعة...")
    df_fm = df_m[df_m['السلعة'].str.contains(search_m, case=False, na=False)] if search_m else df_m

    for idx, row in df_fm.iterrows():
        with st.container(border=True):
            ci, ca = st.columns([3, 1])
            with ci:
                st.markdown(f"### 📦 {row['السلعة']}")
                st.write(f"🔢 Ref: `{row['المرجع']}` | 🔢 Qte: `{row['الكمية']}` | 💰 Price: `{row['ثمن الوحدة']} DH`")
            with ca:
                st.write("")
                if st.button("📝 تعديل", key=f"edit_m_{row['ID']}"): st.session_state[f"mode_m_{row['ID']}"] = True
                if st.button("🗑️ حذف", key=f"del_m_{row['ID']}"):
                    if save_data("Materiels", df_m.drop(idx)): st.rerun()

            if st.session_state.get(f"mode_m_{row['ID']}", False):
                with st.form(f"edit_form_m_{row['ID']}"):
                    n_des = st.text_input("السلعة", value=row['السلعة'])
                    n_ref = st.text_input("المرجع", value=row['المرجع'])
                    n_qte = st.text_input("الكمية", value=row['الكمية'])
                    n_pri = st.text_input("ثمن الوحدة", value=row['ثمن الوحدة'])
                    if st.form_submit_button("تحديث 💾"):
                        df_m.loc[idx, ["السلعة", "المرجع", "الكمية", "ثمن الوحدة"]] = [n_des, n_ref, n_qte, n_pri]
                        if save_data("Materiels", df_m):
                            st.session_state[f"mode_m_{row['ID']}"] = False
                            st.rerun()

# ==========================================
# 📄 5. صفحة الفاتورة (Facturation)
# ==========================================
else:
    st.title("📄 Devis / Facture Pro")
    df_c = load_data("Customers", COLS_C)
    df_m = load_data("Materiels", COLS_M)

    if not df_c.empty and not df_m.empty:
        c1, c2, c3 = st.columns([2, 1, 1])
        selected_client = c1.selectbox("اختار الزبون", df_c["الاسم/الشركة"].tolist())
        doc_type = c2.selectbox("النوع", ["DEVIS", "FACTURE"])
        doc_num = c3.text_input("رقم الوثيقة", value="A2024-001")

        if 'cart' not in st.session_state: st.session_state.cart = []

        with st.container(border=True):
            st.subheader("🛒 إضافة السلع")
            i1, i2, i3 = st.columns([3, 1, 1])
            s_item = i1.selectbox("السلعة", df_m["السلعة"].tolist())
            s_qte = i2.number_input("الكمية", min_value=1, value=1)
            if i3.button("➕ إضافة"):
                m_data = df_m[df_m["السلعة"] == s_item].iloc[0]
                p_u = float(str(m_data["ثمن الوحدة"]).replace(',', '.') or 0)
                st.session_state.cart.append({"Désignation": s_item, "Qte": s_qte, "P.U": p_u, "Total": s_qte * p_u})
                st.rerun()

        if st.session_state.cart:
            df_cart = pd.DataFrame(st.session_state.cart)
            st.table(df_cart)
            ht = df_cart["Total"].sum()
            tva = ht * 0.20
            ttc = ht + tva
            
            st.write(f"**Total HT:** {ht:,.2f} DH | **TVA 20%:** {tva:,.2f} DH")
            st.error(f"### TOTAL TTC: {ttc:,.2f} DH")

            if st.button("📥 تحميل PDF"):
                pdf = FPDF()
                pdf.add_page(); pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, f"MVAC - {doc_type} N: {doc_num}", ln=1, align='C')
                pdf.set_font("Arial", '', 12)
                pdf.cell(0, 10, f"Client: {selected_client} | Date: {datetime.now().strftime('%d/%m/%Y')}", ln=1)
                pdf.ln(5)
                for item in st.session_state.cart:
                    pdf.cell(0, 10, f"- {item['Désignation']} | {item['Qte']} x {item['P.U']} = {item['Total']} DH", ln=1)
                pdf_output = pdf.output(dest='S').encode('latin-1')
                b64 = base64.b64encode(pdf_output).decode()
                st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="Facture_{doc_num}.pdf">📥 اضغط هنا للتحميل</a>', unsafe_allow_html=True)

            if st.button("🗑️ إفراغ الجدول"):
                st.session_state.cart = []; st.rerun()
    else:
        st.warning("⚠️ دخل السلعة والكليان هما الأولين!")
