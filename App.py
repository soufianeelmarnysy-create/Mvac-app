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

# --- دالة عرض الـ PDF المباشر ---
def display_pdf(pdf_bytes):
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- واجهة الصفحة ---
st.set_page_config(layout="wide") # باش يجي العرض كبير بحال التصويرة

if page == "📄 Devis / Facture":
    # 1. تحميل البيانات (Load Data)
    df_c = load_data("Customers")
    df_m = load_data("Materiels")
    df_f = load_data("Facturations")
    df_d = load_data("Devis")

    # تهيئة السلة والـ PDF
    if 'cart' not in st.session_state: st.session_state.cart = []
    if 'pdf_preview' not in st.session_state: st.session_state.pdf_preview = None

    st.title("📄 Système de Facturation Intelligent")
    st.divider()

    # --- الجزء 1: اختيار النوع والزبون ---
    with st.container(border=True):
        col_t1, col_t2, col_t3 = st.columns([1, 2, 1])
        with col_t1:
            doc_type = st.radio("📑 Type de Document", ["DEVIS", "FACTURE"], horizontal=True)
        with col_t2:
            clients_list = df_c.iloc[:, 2].dropna().tolist() if not df_c.empty else ["Client Standard"]
            sel_client = st.selectbox("👤 Sélectionner le Client", clients_list)
        with col_t3:
            doc_ref = st.text_input("N° Document", value=f"{doc_type[0]}-{datetime.now().strftime('%y%m%d%H%M')}")

    # --- الجزء 2: اختيار السلعة مع عرض الستوك (Stock Check) ---
    with st.container(border=True):
        st.subheader("📦 Sélection des Articles")
        a1, a2, a3, a4, a5 = st.columns([3, 1, 1, 1, 1])
        
        # لستة السلع من العمود 2
        m_list = df_m.iloc[:, 2].dropna().tolist() if not df_m.empty else []
        sel_art = a1.selectbox("🔍 Choisir un article", [""] + m_list)
        
        u_v, p_v, s_v = "", 0.0, 0.0
        if sel_art:
            row = df_m[df_m.iloc[:, 2] == sel_art].iloc[0]
            u_v = str(row.iloc[3]) # الوحدة (العمود 3)
            s_v = float(row.iloc[4]) # الستوك الحالي (العمود 4)
            p_v = float(str(row.iloc[5]).replace(',', '.')) # الثمن HT (العمود 5)
        
        # عرض الستوك بلون تنبيهي
        color = "green" if s_v > 0 else "red"
        a2.markdown(f"<p style='text-align:center;'>Stock<br><b style='color:{color}; font-size:20px;'>{s_v}</b></p>", unsafe_allow_html=True)
        
        a3.text_input("Unité", value=u_v, disabled=True)
        q_in = a4.number_input("Qté", min_value=0.1, value=1.0, step=1.0)
        p_in = a5.number_input("Prix HT", value=p_v)

        if st.button("➕ Ajouter à la liste", use_container_width=True, type="secondary"):
            if sel_art:
                if doc_type == "FACTURE" and q_in > s_v:
                    st.error(f"❌ Stock insuffisant ! (Max: {s_v})")
                else:
                    st.session_state.cart.append({
                        "Désignation": sel_art, "Unité": u_v,
                        "Qte": q_in, "PU_HT": p_in, "Total_HT": q_in * p_in
                    })
                    st.rerun()

    # --- الجزء 3: الجدول التفاعلي (Tableau interactif) ---
    if st.session_state.cart:
        st.subheader("📋 Liste des Articles Sélectionnés")
        # تحويل السلة لـ DataFrame باش يبان جدول ناضي
        df_display = pd.DataFrame(st.session_state.cart)
        
        # عرض الجدول مع إمكانية المسح (IconButton)
        for i, item in enumerate(st.session_state.cart):
            row_col = st.columns([5, 1, 1, 1, 1, 0.5])
            row_col[0].write(f"**{item['Désignation']}**")
            row_col[1].write(f"{item['Unité']}")
            row_col[2].write(f"{item['Qte']}")
            row_col[3].write(f"{item['PU_HT']:.2f}")
            row_col[4].write(f"**{item['Total_HT']:.2f}**")
            if row_col[5].button("🗑️", key=f"del_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()

        # الحسابات الإجمالية
        ht = sum(i['Total_HT'] for i in st.session_state.cart)
        tva = ht * 0.20
        ttc = ht + tva

        st.divider()
        res_c1, res_c2 = st.columns([2, 1])
        with res_c2:
            st.markdown(f"""
            | DÉTAILS | MONTANT (DH) |
            | :--- | :--- |
            | **Total HT** | {ht:,.2f} |
            | **TVA (20%)** | {tva:,.2f} |
            | **TOTAL TTC** | <b style='font-size:22px; color:#2980b9;'>{ttc:,.2f}</b> |
            """, unsafe_allow_html=True)

        # --- الجزء 4: الحفظ والمعاينة (Enregistrer & Preview) ---
        st.divider()
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            if st.button("💾 Valider & Enregistrer dans Sheets", type="primary", use_container_width=True):
                # 1. تحديث الستوك (فقط فالفاتورة)
                if doc_type == "FACTURE":
                    df_m_new = load_data("Materiels")
                    for item in st.session_state.cart:
                        idx = df_m_new[df_m_new.iloc[:, 2] == item['Désignation']].index[0]
                        df_m_new.iloc[idx, 4] = float(df_m_new.iloc[idx, 4]) - item['Qte']
                    save_data("Materiels", df_m_new)
                
                # 2. حفظ الفاتورة/الدوڤي
                sheet_target = "Facturations" if doc_type == "FACTURE" else "Devis"
                df_target = df_f if doc_type == "FACTURE" else df_d
                new_row = [len(df_target)+1, datetime.now().strftime("%d/%m/%Y"), doc_ref, sel_client, ht, tva, ttc]
                save_data(sheet_target, pd.concat([df_target, pd.DataFrame([new_row], columns=df_target.columns[:7])]))
                
                # 3. توليد الـ PDF للمعاينة
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, f"M-VAC PRO - {doc_type}", 0, 1, 'C')
                pdf.set_font("Arial", '', 12)
                pdf.cell(0, 10, f"Client: {sel_client} | Ref: {doc_ref} | Date: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
                pdf.ln(10)
                pdf.cell(100, 10, "Article", 1); pdf.cell(20, 10, "Qte", 1); pdf.cell(30, 10, "P.U", 1); pdf.cell(40, 10, "Total", 1, 1)
                for item in st.session_state.cart:
                    pdf.cell(100, 10, str(item['Désignation']), 1)
                    pdf.cell(20, 10, str(item['Qte']), 1)
                    pdf.cell(30, 10, str(item['PU_HT']), 1)
                    pdf.cell(40, 10, f"{item['Total_HT']:.2f}", 1, 1)
                
                st.session_state.pdf_preview = pdf.output(dest='S').encode('latin-1')
                st.success("✅ Enregistré avec succès ! Vous pouvez maintenant voir et télécharger le PDF.")

        # عرض الـ PDF والتحميل
        if st.session_state.pdf_preview:
            with st.expander("👁️ Cliquer هنا لمشاهدة الـ PDF قبل التحميل", expanded=True):
                display_pdf(st.session_state.pdf_preview)
                st.download_button("📥 Télécharger le PDF Officiel", 
                                 data=st.session_state.pdf_preview, 
                                 file_name=f"{doc_ref}.pdf", 
                                 mime="application/pdf", 
                                 use_container_width=True)

    if st.button("🗑️ Vider le panier"):
        st.session_state.cart = []
        st.session_state.pdf_preview = None
        st.rerun()
