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

# --- 1. دالة عرض الـ PDF المباشر ---
def display_pdf(pdf_bytes):
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- 2. بداية الصفحة ---
if page == "📄 Devis / Facture":
    st.header("📄 Gestion Commerciale : M-VAC PRO")
    
    # تحميل البيانات الحية من Sheets
    df_c = load_data("Customers")
    df_m = load_data("Materiels")
    df_f = load_data("Facturations")
    df_d = load_data("Devis")

    # تهيئة السلة في الذاكرة
    if 'cart' not in st.session_state:
        st.session_state.cart = []
    if 'preview_pdf' not in st.session_state:
        st.session_state.preview_pdf = None

    # --- الجزء 1: معلومات الوثيقة ---
    with st.container(border=True):
        c1, c2, c3 = st.columns([1, 2, 1])
        doc_type = c1.selectbox("Type de Document", ["DEVIS", "FACTURE"], key="main_type")
        
        # اختيار الكليان من جدول Customers (العمود 2)
        clients = df_c.iloc[:, 2].dropna().tolist() if not df_c.empty else ["Passager"]
        s_client = c2.selectbox("Sélectionner le Client", clients)
        
        # مرجع الوثيقة تلقائي
        d_ref = c3.text_input("Référence", value=f"{doc_type[0]}-{datetime.now().strftime('%y%m%d%H%M')}")

    # --- الجزء 2: إضافة السلع مع تحديث الستوك الفوري ---
    with st.container(border=True):
        st.subheader("📦 Sélection des Articles")
        i1, i2, i3, i4, i5, i6 = st.columns([3, 1, 1, 1, 1, 1])
        
        # لستة السلع من جدول Materiels (العمود 2)
        articles = df_m.iloc[:, 2].dropna().tolist() if not df_m.empty else []
        s_art = i1.selectbox("Choisir Article", [""] + articles, key="art_selector")
        
        u_v, p_v, s_v = "", 0.0, 0.0
        if s_art:
            # جلب معلومات السلعة من السطر المناسب
            row = df_m[df_m.iloc[:, 2] == s_art].iloc[0]
            u_v = str(row.iloc[3])  # الوحدة (العمود 3)
            s_v = float(row.iloc[4]) # الستوك (العمود 4)
            p_v = float(str(row.iloc[5]).replace(',', '.')) # الثمن HT (العمود 5)
        
        # عرض الوحدة والستوك فمربعات "Design"
        i2.markdown(f"<div style='border:2px solid #2980b9; border-radius:10px; text-align:center; padding:5px;'>Unité<br><b>{u_v}</b></div>", unsafe_allow_html=True)
        color = "green" if s_v > 0 else "red"
        i3.markdown(f"<div style='border:2px solid {color}; border-radius:10px; text-align:center; padding:5px;'>Stock<br><b style='color:{color};'>{s_v}</b></div>", unsafe_allow_html=True)
        
        q_in = i4.number_input("Qté", min_value=0.1, value=1.0, key="qte_input")
        p_in = i5.number_input("Prix HT", value=p_v, key="price_input")

        # زر الإضافة مع منطق الستوك
        if i6.button("➕ Ajouter", use_container_width=True):
            if s_art:
                if doc_type == "FACTURE" and q_in > s_v:
                    st.error("Stock insuffisant!")
                else:
                    # إضافة للسلة
                    st.session_state.cart.append({
                        "Désignation": s_art, "Unité": u_v, 
                        "Qte": q_in, "PU_HT": p_in, "Total": q_in * p_in
                    })
                    
                    # تنقيص الستوك فـ Google Sheets فالحين إذا كانت Facture
                    if doc_type == "FACTURE":
                        idx = df_m[df_m.iloc[:, 2] == s_art].index[0]
                        df_m.iloc[idx, 4] = float(df_m.iloc[idx, 4]) - q_in
                        save_data("Materiels", df_m)
                    
                    st.rerun()

    # --- الجزء 3: جدول الملخص (Tableau) ---
    if st.session_state.cart:
        st.subheader("📑 Articles Sélectionnés")
        for i, item in enumerate(st.session_state.cart):
            col_a, col_b, col_c = st.columns([8, 2, 1])
            col_a.info(f"**{item['Désignation']}** ({item['Unité']})")
            col_b.write(f"{item['Qte']} x {item['PU_HT']:.2f} = **{item['Total']:.2f}**")
            
            # زر الحذف مع إرجاع الستوك
            if col_c.button("🗑️", key=f"del_{i}"):
                if doc_type == "FACTURE":
                    idx = df_m[df_m.iloc[:, 2] == item['Désignation']].index[0]
                    df_m.iloc[idx, 4] = float(df_m.iloc[idx, 4]) + item['Qte']
                    save_data("Materiels", df_m)
                st.session_state.cart.pop(i)
                st.rerun()

        # الحسابات الإجمالية
        total_ht = sum(i['Total'] for i in st.session_state.cart)
        tva = total_ht * 0.20
        total_ttc = total_ht + tva
        st.success(f"### TOTAL TTC: {total_ttc:,.2f} DH")

        # --- الجزء 4: الحفظ والمعاينة ---
        st.divider()
        if st.button("💾 Enregistrer & Générer PDF", type="primary", use_container_width=True):
            # حفظ في جدول Facturations أو Devis
            sheet_name = "Facturations" if doc_type == "FACTURE" else "Devis"
            df_target = df_f if doc_type == "FACTURE" else df_d
            new_row = [len(df_target)+1, datetime.now().strftime("%d/%m/%Y"), d_ref, s_client, total_ht, tva, total_ttc]
            save_data(sheet_name, pd.concat([df_target, pd.DataFrame([new_row], columns=df_target.columns[:7])]))
            
            # صنع الـ PDF للمعاينة
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, f"M-VAC PRO - {doc_type}", ln=True, align='C')
            pdf.set_font("Arial", '', 12)
            pdf.cell(0, 10, f"Ref: {d_ref} | Client: {s_client}", ln=True)
            pdf.ln(5)
            
            # رسم الجدول فـ PDF
            pdf.cell(100, 10, "Article", 1); pdf.cell(20, 10, "Qte", 1); pdf.cell(30, 10, "P.U", 1); pdf.cell(40, 10, "Total", 1, 1)
            for item in st.session_state.cart:
                pdf.cell(100, 10, item['Désignation'], 1)
                pdf.cell(20, 10, str(item['Qte']), 1)
                pdf.cell(30, 10, str(item['PU_HT']), 1)
                pdf.cell(40, 10, f"{item['Total']:.2f}", 1, 1)
            
            st.session_state.preview_pdf = pdf.output(dest='S').encode('latin-1')
            st.success("✅ Document Enregistré !")

        # عرض الـ PDF المباشر
        if st.session_state.preview_pdf:
            st.subheader("👁️ Aperçu du Document")
            display_pdf(st.session_state.preview_pdf)
            st.download_button("📥 Télécharger PDF", data=st.session_state.preview_pdf, file_name=f"{d_ref}.pdf", mime="application/pdf")

    # زر إفراغ السلة
    if st.button("🗑️ Vider le panier"):
        st.session_state.cart = []
        st.session_state.preview_pdf = None
        st.rerun()
