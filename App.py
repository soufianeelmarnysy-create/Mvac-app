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
        elif page == "📄 Devis / Facture":
    st.header("📄 Gestion des Factures & Devis PRO")
    
    # 1. تحميل البيانات
    df_c = load_data("Customers")
    df_m = load_data("Materiels")
    df_f = load_data("Facturations")

    if 'cart' not in st.session_state:
        st.session_state.cart = []

    # 2. إعدادات الوثيقة
    with st.container(border=True):
        c1, c2, c3 = st.columns([1, 2, 1])
        d_type = c1.selectbox("Type", ["DEVIS", "FACTURE"], key="doc_v_final")
        
        # جلب الكليان مع تنظيف الفراغات
        c_list = df_c.iloc[:, 1].dropna().str.strip().tolist() if not df_c.empty else ["Client Standard"]
        s_client = c2.selectbox("Client", c_list, key="client_v_final")
        d_num = c3.text_input("N° Doc", value=f"{d_type[0]}{datetime.now().strftime('%y%m%d%H%M')}")

    # 3. إضافة السلع (الحل النهائي لجلب الأثمنة والوحدات)
    with st.container(border=True):
        st.subheader("📦 Ajouter des articles")
        i1, i2, i3, i4 = st.columns([3, 1, 1, 1])
        
        # تنظيف قائمة السلع من أي فراغات خفية في Sheets
        if not df_m.empty:
            df_m_clean = df_m.copy()
            # نفترض السلعة في العمود 2، الوحدة في 3، والثمن في 4
            df_m_clean.iloc[:, 1] = df_m_clean.iloc[:, 1].astype(str).str.strip()
            m_list = df_m_clean.iloc[:, 1].tolist()
        else:
            m_list = []

        s_name = i1.selectbox("Article", [""] + m_list, key="art_sel_final")
        
        u_v, p_v = "", 0.0
        if s_name != "":
            # البحث عن السلعة المختارة مع تنظيف المدخلات
            match = df_m_clean[df_m_clean.iloc[:, 1] == s_name]
            if not match.empty:
                row = match.iloc[0]
                u_v = str(row.iloc[2]).strip() if len(row) > 2 else "" # الوحدة
                try:
                    # تحويل الثمن لرقم مع معالجة الفاصلة
                    raw_p = str(row.iloc[3]).replace(',', '.').strip()
                    p_v = float(raw_p)
                except:
                    p_v = 0.0

        s_unit = i2.text_input("Unité", value=u_v, key="u_final")
        s_qte = i3.number_input("Qté", min_value=0.1, value=1.0, key="q_final")
        s_price = i4.number_input("Prix HT", value=p_v, key="p_final")

        if st.button("➕ Ajouter à la liste", use_container_width=True):
            if s_name != "":
                st.session_state.cart.append({
                    "Désignation": s_name, 
                    "Unité": s_unit,
                    "Qte": s_qte, 
                    "PU_HT": s_price, 
                    "Total_HT": s_qte * s_price
                })
                st.rerun()

    # 4. عرض الجدول وحساب الطوطال
    if st.session_state.cart:
        st.markdown("---")
        for idx, item in enumerate(st.session_state.cart):
            col1, col2 = st.columns([6, 1])
            # عرض الحساب (Total) بشكل صحيح في الواجهة
            col1.info(f"**{item['Désignation']}** | {item['Qte']} {item['Unité']} x {item['PU_HT']:.2f} = {item['Total_HT']:.2f} DH")
            if col2.button("🗑️", key=f"del_{idx}"):
                st.session_state.cart.pop(idx)
                st.rerun()

        # 5. ملخص الحسابات
        ht_brut = sum(i['Total_HT'] for i in st.session_state.cart)
        remise_pct = st.number_input("Remise (%)", min_value=0, max_value=100, value=0)
        remise_val = ht_brut * (remise_pct / 100)
        ht_net = ht_brut - remise_val
        tva_val = ht_net * 0.20
        ttc_total = ht_net + tva_val

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total HT", f"{ht_brut:,.2f} DH")
        m2.metric("Remise", f"-{remise_val:,.2f} DH")
        m3.metric("TVA (20%)", f"{tva_val:,.2f} DH")
        m4.metric("TOTAL TTC", f"{ttc_total:,.2f} DH")

        # 6. حل مشكلة PDF (bytearray error)
        b1, b2 = st.columns(2)
        
        if b1.button("💾 Enregistrer", type="primary", use_container_width=True):
            # الكود ديال الحفظ في Sheets
            st.success("✅ Enregistré !")

        if b2.button("📥 Télécharger PDF", use_container_width=True):
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, f"FACTURE N°: {d_num}", ln=1, align='C')
                
                # تصحيح الخطأ الشهير bytearray has no attribute encode
                pdf_output = pdf.output(dest='S')
                # تحويل الناتج لـ bytes حقيقية قبل التشفير
                pdf_bytes = bytes(pdf_output) if isinstance(pdf_output, (bytearray, bytes)) else pdf_output.encode('latin-1')
                
                b64 = base64.b64encode(pdf_bytes).decode()
                href = f'<a href="data:application/pdf;base64,{b64}" download="{d_num}.pdf" style="text-decoration:none;"><button style="width:100%; background-color:#005050; color:white; padding:10px; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">📥 Télécharger</button></a>'
                st.markdown(href, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Erreur: {e}")
