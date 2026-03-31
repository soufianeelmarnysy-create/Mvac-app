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
    
    # 1. جلب البيانات
    df_c = load_data("Customers")
    df_m = load_data("Materiels")
    df_f = load_data("Facturations")

    if 'cart' not in st.session_state:
        st.session_state.cart = []

    # 2. إعدادات الوثيقة
    with st.container(border=True):
        c1, c2, c3 = st.columns([1, 2, 1])
        d_type = c1.selectbox("Type", ["DEVIS", "FACTURE"], key="type_final_fixed")
        
        # تنظيف قائمة الكليان
        c_list = df_c['الاسم/الشركة'].tolist() if not df_c.empty else ["Client Standard"]
        s_client = c2.selectbox("Client", c_list, key="client_final_fixed")
        d_num = c3.text_input("N° Doc", value=f"{d_type[0]}{datetime.now().strftime('%y%m%d%H%M')}")

    # 3. إضافة السلع (البحث بالسمية مع تنظيف المسافات)
    with st.container(border=True):
        st.subheader("📦 Ajouter des articles")
        i1, i2, i3, i4 = st.columns([3, 1, 1, 1])
        
        # قائمة السلع
        m_list = df_m['السلعة'].tolist() if not df_m.empty else []
        s_name = i1.selectbox("Article", [""] + m_list, key="art_final_fixed")
        
        u_v, p_v = "", 0.0
        if s_name != "" and not df_m.empty:
            # كنقلبو على السلعة وكنأكدو أننا كنمسحو أي فراغ
            m_info = df_m[df_m['السلعة'].str.strip() == s_name.strip()].iloc[0]
            u_v = str(m_info.get('الوحدة', ''))
            
            try:
                # تحويل الثمن لرقم (مع تبديل الفاصلة بالنقطة)
                val_price = str(m_info.get('ثمن الوحدة', 0)).replace(',', '.').strip()
                p_v = float(val_price)
            except:
                p_v = 0.0

        s_unit = i2.text_input("Unité", value=u_v, key="u_fixed")
        s_qte = i3.number_input("Qté", min_value=0.1, value=1.0, key="q_fixed")
        s_price = i4.number_input("Prix HT", value=p_v, key="p_fixed")

        if st.button("➕ Ajouter à la liste", use_container_width=True):
            if s_name != "":
                st.session_state.cart.append({
                    "Désignation": s_name, "Unité": s_unit,
                    "Qte": s_qte, "PU_HT": s_price, "Total_HT": s_qte * s_price
                })
                st.rerun()

    # 4. عرض الجدول والمسح
    if st.session_state.cart:
        st.markdown("### 🛒 Articles sélectionnés")
        for idx, item in enumerate(st.session_state.cart):
            col_l1, col_l2 = st.columns([6, 1])
            col_l1.success(f"**{item['Désignation']}** ({item['Qte']} {item['Unité']}) = {item['Total_HT']:.2f} DH")
            if col_l2.button("🗑️", key=f"del_{idx}"):
                st.session_state.cart.pop(idx)
                st.rerun()

        # 5. الحسابات والرميز
        st.markdown("---")
        ht_brut = sum(i['Total_HT'] for i in st.session_state.cart)
        remise_pct = st.number_input("Remise (%)", min_value=0, max_value=100, value=0)
        remise_val = ht_brut * (remise_pct / 100)
        ht_net = ht_brut - remise_val
        tva_val = ht_net * 0.20
        ttc_total = ht_net + tva_val

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total HT", f"{ht_brut:,.2f}")
        m2.metric(f"Remise", f"-{remise_val:,.2f}")
        m3.metric("TVA (20%)", f"{tva_val:,.2f}")
        m4.metric("TOTAL TTC", f"{ttc_total:,.2f}")

        try:
            from num2words import num2words
            ttc_letters = num2words(ttc_total, lang='fr').upper() + " DIRHAMS"
        except:
            ttc_letters = "---"
        st.info(f"**Somme en lettres :** {ttc_letters}")

        # 6. الأزرار (حل مشكلة PDF النهائي)
        b1, b2 = st.columns(2)
        
        if b1.button("💾 Enregistrer dans Sheets", type="primary", use_container_width=True):
            summary = ", ".join([i['Désignation'] for i in st.session_state.cart])
            new_row = pd.DataFrame([[
                str(len(df_f)+1), datetime.now().strftime("%d/%m/%Y"), d_type, d_num, 
                s_client, summary, f"{ht_net:.2f}", f"{tva_val:.2f}", f"{ttc_total:.2f}"
            ]], columns=["ID", "Date", "Type", "Num_Facture", "Client", "Articles", "HT", "TVA", "TTC"])
            if save_data("Facturations", pd.concat([df_f, new_row])):
                st.success("✅ Enregistré !")

        if b2.button("📥 Télécharger PDF Officiel", use_container_width=True):
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, f"M-VAC SYSTEM - {d_type}", ln=1, align='C')
                pdf.ln(10)
                
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(100, 10, "Designation", 1); pdf.cell(30, 10, "Qte", 1); pdf.cell(60, 10, "Total HT", 1, ln=1)
                
                pdf.set_font("Arial", '', 9)
                for item in st.session_state.cart:
                    pdf.cell(100, 8, str(item['Désignation']), 1)
                    pdf.cell(30, 8, f"{item['Qte']} {item['Unité']}", 1)
                    pdf.cell(60, 8, f"{item['Total_HT']:.2f}", 1, ln=1)
                
                pdf.ln(5)
                pdf.set_font("Arial", 'B', 11)
                pdf.cell(130, 10, "TOTAL TTC :", 0, 0, 'R'); pdf.cell(60, 10, f"{ttc_total:.2f} DH", 1, ln=1, align='R')

                # الحل اللي غادي يحيد AttributeError: encode
                pdf_output = pdf.output(dest='S')
                if isinstance(pdf_output, str): # إلا كان رجع نص
                    pdf_bytes = pdf_output.encode('latin-1')
                else: # إلا كان ديجا bytes (bytearray)
                    pdf_bytes = bytes(pdf_output)

                b64 = base64.b64encode(pdf_bytes).decode()
                href = f'<a href="data:application/pdf;base64,{b64}" download="{d_num}.pdf" style="text-decoration:none;"><button style="width:100%; background-color:#005050; color:white; padding:10px; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">📥 Télécharger le PDF</button></a>'
                st.markdown(href, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Erreur PDF: {e}")

        if st.button("🔄 Nouveau Document"):
            st.session_state.cart = []; st.rerun()
