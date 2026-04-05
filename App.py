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
import io

# --- 1. دالة توليد الـ PDF (نسخة محسنة) ---
def generate_pdf(doc_type, ref, client, items, total_ht, tva, ttc):
    pdf = FPDF()
    pdf.add_page()
    
    # العنوان
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"M-VAC PRO - {doc_type}", ln=True, align='C')
    
    # المعلومات العامة
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    pdf.cell(0, 8, f"Reference: {ref}", ln=True)
    pdf.cell(0, 8, f"Client: {client}", ln=True)
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(5)
    
    # رأس الجدول
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(80, 10, "Article", 1, 0, 'C', True)
    pdf.cell(25, 10, "Qte", 1, 0, 'C', True)
    pdf.cell(40, 10, "P.U HT (DH)", 1, 0, 'C', True)
    pdf.cell(45, 10, "Total HT (DH)", 1, 1, 'C', True)
    
    # محتوى الجدول
    pdf.set_font("Arial", '', 10)
    for item in items:
        pdf.cell(80, 10, str(item['Désignation'])[:40], 1)
        pdf.cell(25, 10, str(item['Qte']), 1, 0, 'C')
        pdf.cell(40, 10, f"{item['PU_HT']:,.2f}", 1, 0, 'C')
        pdf.cell(45, 10, f"{item['Total']:,.2f}", 1, 1, 'C')
    
    # الخلاصة
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(145, 10, "Total HT", 0, 0, 'R')
    pdf.cell(45, 10, f"{total_ht:,.2f} DH", 1, 1, 'C')
    
    pdf.cell(145, 10, "TVA (20%)", 0, 0, 'R')
    pdf.cell(45, 10, f"{tva:,.2f} DH", 1, 1, 'C')
    
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(145, 10, "TOTAL TTC", 0, 0, 'R')
    pdf.cell(45, 10, f"{ttc:,.2f} DH", 1, 1, 'C', True)
    
    # تصدير كـ bytes
    return pdf.output()

# --- 2. منطق الصفحة الرئيسية ---
def show_facturation_page():
    st.header("📄 Création Devis & Facture")

    # تحميل البيانات (بافتراض وجود دوال load_data و save_data عندك)
    df_c = load_data("Customers").dropna(how='all')
    df_m = load_data("Materiels").dropna(how='all')
    df_f = load_data("Facturations").dropna(how='all')
    df_d = load_data("Devis").dropna(how='all')

    if 'cart' not in st.session_state:
        st.session_state.cart = []

    # --- القسم 1: معلومات المستند ---
    with st.container(border=True):
        c1, c2, c3 = st.columns([1, 2, 1])
        doc_type = c1.selectbox("Type de Document", ["DEVIS", "FACTURE"])
        
        # جلب الكليان (العمود 2 غالباً هو الاسم)
        clients_list = df_c.iloc[:, 2].dropna().unique().tolist() if not df_c.empty else ["Passager"]
        s_client = c2.selectbox("Sélectionner le Client", clients_list)
        
        d_ref = c3.text_input("Référence", value=f"{doc_type[0]}-{datetime.now().strftime('%d%H%M')}")

    # --- القسم 2: اختيار السلعة ---
    with st.expander("➕ Ajouter des articles", expanded=True):
        # العمود 2 هو اسم السلعة
        articles_list = df_m.iloc[:, 2].dropna().tolist() if not df_m.empty else []
        sel_art = st.selectbox("Choisir l'article", [""] + articles_list)
        
        u_v, s_v, p_v = "", 0.0, 0.0
        
        if sel_art:
            row = df_m[df_m.iloc[:, 2] == sel_art].iloc[0]
            u_v = str(row.iloc[3]) # Unité
            s_v = float(row.iloc[4]) # Stock
            # تحويل الثمن مع معالجة الفاصلة
            p_val = str(row.iloc[5]).replace(',', '.')
            p_v = float(p_val) if p_val != "nan" else 0.0

            i1, i2, i3, i4, i5 = st.columns([1, 1, 1, 1, 1])
            i1.metric("Unité", u_v)
            i2.metric("Stock Actuel", s_v)
            q_in = i3.number_input("Quantité", min_value=0.1, value=1.0, step=1.0)
            p_in = i4.number_input("Prix HT (DH)", value=p_v)
            
            if i5.button("➕ Ajouter", use_container_width=True):
                if q_in > s_v and doc_type == "FACTURE":
                    st.warning(f"Stock insuffisant ! (Disponible: {s_v})")
                else:
                    st.session_state.cart.append({
                        "Désignation": sel_art, 
                        "Unité": u_v, 
                        "Qte": q_in, 
                        "PU_HT": p_in, 
                        "Total": q_in * p_in
                    })
                    st.toast(f"Ajouté: {sel_art}")
                    st.rerun()

    # --- القسم 3: عرض الجدول والعمليات النهائية ---
    if st.session_state.cart:
        st.subheader("📋 Liste des Articles Sélectionnés")
        df_cart = pd.DataFrame(st.session_state.cart)
        
        # عرض الجدول مع إمكانية حذف سطر (اختياري)
        st.dataframe(df_cart, use_container_width=True)

        t_ht = df_cart['Total'].sum()
        t_tva = t_ht * 0.20
        t_ttc = t_ht + t_tva

        col_tot1, col_tot2 = st.columns([2, 1])
        with col_tot2
            
            st.success("✅ Document enregistré avec succès !")
            st.download_button("📥 Télécharger le PDF", data=pdf_data, file_name=f"{d_ref}.pdf", mime="application/pdf")
            
            # مسح السلة بعد الحفظ
            # st.session_state.cart = []
