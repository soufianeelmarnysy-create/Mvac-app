import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from fpdf import FPDF
import base64

# 🛠️ 1. الإعدادات الأساسية
st.set_page_config(page_title="MVAC Pro System", layout="wide", page_icon="❄️")

# الربط مع Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMl791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

# 🔄 دالة جلب البيانات وتنظيفها
def load_data(sheet_name):
    try:
        st.cache_data.clear()
        df = conn.read(spreadsheet=SHEET_URL, worksheet=sheet_name, ttl=0)
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip()
            df = df.fillna("").astype(str).replace(r'\.0$', '', regex=True)
            return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# 💾 دالة الحفظ
def save_data(sheet_name, df):
    try:
        conn.update(spreadsheet=SHEET_URL, worksheet=sheet_name, data=df)
        return True
    except Exception as e:
        st.error(f"❌ عطب في الحفظ: {e}")
        return False

# 🧭 2. القائمة الجانبية (Navigation)
with st.sidebar:
    st.title("❄️ MVAC SYSTEM")
    st.markdown("---")
    page = st.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 إدارة السلعة", "📄 Devis / Facture"])
    st.markdown("---")
    st.info("SOUFIANE - Pro Edition v1.2")

# =========================================================
# 👥 3. صفحة إدارة الزبناء (كود ديالك كيفما هو)
# =========================================================
if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء (Customers)")
    COLS_C = ["ID", "النوع", "الاسم/الشركة", "ICE", "RIB", "العنوان", "الهاتف"]
    df_c = load_data("Customers")

    # --- إضافة زبون جديد ---
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
                    df_updated = pd.concat([df_c, new_row], ignore_index=True)
                    if save_data("Customers", df_updated):
                        st.success("✅ تم الحفظ!")
                        st.rerun()

    st.markdown("---")
    search = st.text_input("🔍 قلب على كليان بالسمية...", placeholder="مثال: anva")
    df_filtered = df_c[df_c['الاسم/الشركة'].str.contains(search, case=False, na=False)] if not df_c.empty else df_c

    if not df_filtered.empty:
        for index, row in df_filtered.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### 👤 {row['الاسم/الشركة']} ({row['النوع']})")
                    st.write(f"🆔 ICE: `{row['ICE']}` | 📞 Tel: `{row['الهاتف']}`")
                    st.write(f"💳 RIB: `{row['RIB']}` | 📍 {row['العنوان']}")
                with col2:
                    st.write(" ")
                    if st.button(f"📝 تعديل", key=f"edit_c_{row['ID']}"): st.session_state[f"ec_{row['ID']}"] = True
                    if st.button(f"🗑️ حذف", key=f"del_c_{row['ID']}"): st.session_state[f"dc_{row['ID']}"] = True

                # نافذة التعديل
                if st.session_state.get(f"ec_{row['ID']}", False):
                    with st.container(border=True):
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            en = st.text_input("الاسم", value=row['الاسم/الشركة'], key=f"n_{row['ID']}")
                            ei = st.text_input("ICE", value=row['ICE'], key=f"i_{row['ID']}")
                        with ec2:
                            er = st.text_input("RIB", value=row['RIB'], key=f"r_{row['ID']}")
                            et = st.text_input("الهاتف", value=row['الهاتف'], key=f"t_{row['ID']}")
                        if st.button("تحديث 💾", key=f"up_c_{row['ID']}", type="primary"):
                            df_c.loc[index, ['الاسم/الشركة', 'ICE', 'RIB', 'الهاتف']] = [en, ei, er, et]
                            if save_data("Customers", df_c): st.rerun()
                        if st.button("إلغاء ❌", key=f"can_c_{row['ID']}"):
                            st.session_state[f"ec_{row['ID']}"] = False
                            st.rerun()

                # نافذة الحذف
                if st.session_state.get(f"dc_{row['ID']}", False):
                    st.error("⚠️ مسح؟")
                    if st.button("نعم ✅", key=f"y_c_{row['ID']}"):
                        df_c = df_c.drop(index)
                        if save_data("Customers", df_c): st.rerun()
                    if st.button("لا ❌", key=f"n_c_{row['ID']}"):
                        st.session_state[f"dc_{row['ID']}"] = False
                        st.rerun()
    else: st.info("خاوي.")

# =========================================================
# 📦 4. صفحة إدارة السلعة (بنفس نظام الزبناء)
# =========================================================
elif page == "📦 إدارة السلعة":
    st.title("📦 إدارة السلعة (Inventory)")
    COLS_M = ["ID", "المرجع", "السلعة", "الوحدة", "الكمية", "ثمن الوحدة"]
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
                pri = st.text_input("💰 ثمن الوحدة HT")
            if st.form_submit_button("حفظ السلعة ✅"):
                if des:
                    new_id = str(int(pd.to_numeric(df_m["ID"], errors='coerce').max() + 1)) if not df_m.empty else "1"
                    new_row = pd.DataFrame([[new_id, ref, des, uni, qte, pri]], columns=COLS_M)
                    if save_data("Materiels", pd.concat([df_m, new_row], ignore_index=True)):
                        st.success("✅ تم الحفظ!"); st.rerun()

    search_m = st.text_input("🔍 قلب بسمية السلعة...")
    df_fm = df_m[df_m['السلعة'].str.contains(search_m, case=False, na=False)] if not df_m.empty else df_m

    for idx, row in df_fm.iterrows():
        with st.container(border=True):
            c_info, c_btns = st.columns([3, 1])
            c_info.write(f"### 📦 {row['السلعة']} (Ref: {row['المرجع']})")
            c_info.write(f"🔢 Qte: `{row['الكمية']}` | 💰 Price: `{row['ثمن الوحدة']} DH`")
            
            if c_btns.button("📝 تعديل", key=f"em_{row['ID']}"): st.session_state[f"edit_m_{row['ID']}"] = True
            if c_btns.button("🗑️ حذف", key=f"dm_{row['ID']}"): st.session_state[f"del_m_{row['ID']}"] = True

            if st.session_state.get(f"edit_m_{row['ID']}", False):
                with st.container(border=True):
                    m_en_des = st.text_input("السلعة", value=row['السلعة'], key=f"md_{row['ID']}")
                    m_en_qte = st.text_input("الكمية", value=row['الكمية'], key=f"mq_{row['ID']}")
                    m_en_pri = st.text_input("الثمن", value=row['ثمن الوحدة'], key=f"mp_{row['ID']}")
                    if st.button("تحديث 💾", key=f"up_m_{row['ID']}"):
                        df_m.loc[idx, ["السلعة", "الكمية", "ثمن الوحدة"]] = [m_en_des, m_en_qte, m_en_pri]
                        if save_data("Materiels", df_m): st.rerun()
# =========================================================
# 📄 5. صفحة الفاتورة (Facturation)
# ========================================================================================================================================================================
import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import base64

# =========================================================
# 🛠️ 1. الدوال الأساسية (تحميل، حفظ، PDF)
# =========================================================

# دالة التحميل السريع لتجنب Quota Exceeded و البطء
@st.cache_data(ttl=60)
def load_data_fast(sheet_name):
    # هادي كتعيط للدالة الأصلية load_data اللي عندك فالتطبيق
    return load_data(sheet_name)

def generate_pdf(doc_type, ref, client, items, total_ht, tva, ttc):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"M-VAC SYSTEM - {doc_type}", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Ref: {ref} | Client: {client} | Date: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(10)
    
    # الجدول
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(80, 10, "Article", 1, 0, 'C', True)
    pdf.cell(20, 10, "Qty", 1, 0, 'C', True)
    pdf.cell(45, 10, "P.U HT", 1, 0, 'C', True)
    pdf.cell(45, 10, "Total HT", 1, 1, 'C', True)
    
    for item in items:
        pdf.cell(80, 10, str(item['Désignation'])[:30], 1)
        pdf.cell(20, 10, str(item['Qte']), 1, 0, 'C')
        pdf.cell(45, 10, f"{item['PU_HT']:.2f}", 1, 0, 'C')
        pdf.cell(45, 10, f"{item['Total']:.2f}", 1, 1, 'C')
    
    pdf.ln(10)
    pdf.cell(145, 10, "TOTAL TTC", 0, 0, 'R')
    pdf.cell(45, 10, f"{ttc:,.2f} DH", 1, 1, 'C')
    
    # تصحيح خطأ bytearray
    pdf_output = pdf.output(dest='S')
    return bytes(pdf_output) if isinstance(pdf_output, (bytearray, bytes)) else pdf_output.encode('latin-1')

# =========================================================
# 📄 2. الدالة الرئيسية لصفحة الفاتورة
# =========================================================

def show_facturation_page():
    # عنوان مزوق
    st.markdown("<h1 style='text-align: center; color: #008080;'>📄 MVAC SYSTEM - GESTION PRO</h1>", unsafe_allow_html=True)
    st.divider()

    # تحميل الداتا (سريع)
    df_c = load_data_fast("Customers")
    df_m = load_data_fast("Materiels")
    df_f = load_data_fast("Facturations")
    df_d = load_data_fast("Devis")

    # تهيئة السلة
    if 'cart' not in st.session_state:
        st.session_state.cart = []

    # --- القسم 1: معلومات المستند ---
    with st.container(border=True):
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            doc_type = st.selectbox("Type", ["DEVIS", "FACTURE"], key="doc_type_v5")
        with c2:
            clients = df_c.iloc[:, 2].dropna().unique().tolist() if not df_c.empty else ["Passager"]
            s_client = st.selectbox("Client", clients, key="client_v5")
        with c3:
            d_ref = st.text_input("Référence", value=f"{doc_type[0]}-{datetime.now().strftime('%d%H%M')}")

    # --- القسم 2: إضافة السلع (الحل لمشكل المسح والأثمنة) ---
    st.subheader("🛒 Articles")
    with st.container(border=True):
        articles = df_m.iloc[:, 2].dropna().unique().tolist() if not df_m.empty else []
        sel_art = st.selectbox("🔍 Choisir un article", [""] + articles, key="art_sel_v5")
        
        u_v, s_v, p_v = "", 0.0, 0.0
        if sel_art:
            row = df_m[df_m.iloc[:, 2] == sel_art].iloc[0]
            u_v = str(row.iloc[3])
            try:
                s_v = float(str(row.iloc[4]).replace(',', '.').strip())
                p_v = float(str(row.iloc[5]).replace(',', '.').strip())
            except: pass

        i1, i2, i3, i4, i5 = st.columns([1, 1, 1, 1, 1.2])
        i1.metric("Unité", u_v)
        # تلوين الستوك
        st_color = "inverse" if s_v < 5 else "normal"
        i2.metric("Stock", s_v, delta_color=st_color)
        
        q_in = i3.number_input("Qté", min_value=0.1, value=1.0, key="qty_v5")
        p_in = i4.number_input("Prix HT", value=p_v, key="price_v5")

        if i5.button("➕ Ajouter", use_container_width=True, type="primary"):
            if sel_art != "":
                st.session_state.cart.append({
                    "Désignation": sel_art, "Unité": u_v, 
                    "Qte": q_in, "PU_HT": p_in, "Total": q_in * p_in
                })
                st.toast(f"✅ Ajouté: {sel_art}")
                st.rerun()

    # --- القسم 3: الجدول والحسابات ---
    if st.session_state.cart:
        st.markdown("### 📋 Liste des Articles")
        for idx, item in enumerate(st.session_state.cart):
            col_a, col_b = st.columns([8, 1])
            col_a.info(f"**{item['Désignation']}** | {item['Qte']} {item['Unité']} x {item['PU_HT']:.2f} = {item['Total']:.2f} DH")
            if col_b.button("🗑️", key=f"del_{idx}"):
                st.session_state.cart.pop(idx)
                st.rerun()

        t_ht = sum(i['Total'] for i in st.session_state.cart)
        t_tva = t_ht * 0.2
        t_ttc = t_ht + t_tva

        # عرض المجموع بشكل احترافي
        st.markdown(f"""
        <div style="background-color:#e0f2f1; padding:20px; border-radius:10px; text-align:right;">
            <p style="margin:0; font-size:14px;">Total HT: {t_ht:,.2f} DH</p>
            <p style="margin:0; font-size:14px;">TVA (20%): {t_tva:,.2f} DH</p>
            <h2 style="margin:0; color:#00695c;">TOTAL TTC: {t_ttc:,.2f} DH</h2>
        </div>
        """, unsafe_allow_html=True)

        # --- القسم 4: الحفظ و PDF ---
        st.divider()
        b1, b2, b3 = st.columns(3)
        
        with b1:
            if st.button("💾 Enregistrer dans Sheets", use_container_width=True, type="primary"):
                target = "Facturations" if doc_type == "FACTURE" else "Devis"
                # تحميل بدون كاش للحفظ
                current_df = load_data(target)
                new_row = [len(current_df)+1, datetime.now().strftime("%d/%m/%Y"), d_ref, s_client, t_ht, t_tva, t_ttc]
                
                # ميزان الأعمدة
                if len(new_row) < len(current_df.columns):
                    new_row += [""] * (len(current_df.columns) - len(new_row))
                
                new_df = pd.DataFrame([new_row], columns=current_df.columns)
                if save_data(target, pd.concat([current_df, new_df], ignore_index=True)):
                    # تنقيص الستوك
                    if doc_type == "FACTURE":
                        for item in st.session_state.cart:
                            idx = df_m[df_m.iloc[:, 2] == item['Désignation']].index[0]
                            df_m.iloc[idx, 4] -= item['Qte']
                        save_data("Materiels", df_m)
                    
                    st.cache_data.clear()
                    st.success("✅ Enregistré !")
                    st.balloons()

        with b2:
            pdf_bytes = generate_pdf(doc_type, d_ref, s_client, st.session_state.cart, t_ht, t_tva, t_ttc)
            st.download_button("📥 Télécharger PDF", data=pdf_bytes, file_name=f"{d_ref}.pdf", mime="application/pdf", use_container_width=True)

        with b3:
            if st.button("🔄 Nouveau Document", use_container_width=True):
                st.session_state.cart = []
                st.rerun()

# --- تفعيل الصفحة ---
if page == "📄 Devis / Facture":
    show_facturation_page()
