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
# =========================================================================================================================================================================
    # =========================================================
    # 📄 صفحة الفاتورة المتكاملة (النسخة الاحترافية لشركة M-VAC)
    # =========================================================
    st.header("📄 Gestion des Factures & Devis PRO")
    
    # 1. جلب البيانات من السبريدشيت
    df_c = load_data("Customers")
    df_m = load_data("Materiels")
    df_f = load_data("Facturations")

    # تنظيف العناوين
    for df_tmp in [df_c, df_m, df_f]:
        if df_tmp is not None and not df_tmp.empty:
            df_tmp.columns = df_tmp.columns.str.strip()

    if 'cart' not in st.session_state:
        st.session_state.cart = []

    # 2. إعدادات الوثيقة
    with st.container(border=True):
        c1, c2, c3 = st.columns([1, 2, 1])
        d_type = c1.selectbox("Type", ["DEVIS", "FACTURE"], key="mvac_type")
        c_list = df_c['الاسم/الشركة'].tolist() if (df_c is not None and not df_c.empty) else ["Client Standard"]
        s_client = c2.selectbox("Client", c_list, key="mvac_client")
        d_num = c3.text_input("N° Doc", value=f"{d_type[:1]}{datetime.now().strftime('%y%m%d%H%M')}")

    # 3. إضافة السلع (Auto-fill)
    with st.container(border=True):
        i1, i2, i3, i4 = st.columns([3, 1, 1, 1])
        m_list = df_m['السلعة'].tolist() if (df_m is not None and not df_m.empty) else []
        s_name = i1.selectbox("Article", m_list, key="mvac_art")
        
        if (df_m is not None and not df_m.empty) and s_name:
            m_info = df_m[df_m['السلعة'] == s_name].iloc[0]
            unit_val = str(m_info.get('الوحدة', ''))
            price_val = float(m_info.get('ثمن الوحدة', 0))
        else:
            unit_val, price_val = "", 0.0

        s_unit = i2.text_input("Unité", value=unit_val, key="mvac_unit")
        s_qte = i3.number_input("Qté", min_value=0.1, value=1.0, key="mvac_qte")
        s_price = i4.number_input("Prix HT", value=price_val, key="mvac_price")

        if st.button("➕ Ajouter l'article", use_container_width=True):
            st.session_state.cart.append({
                "Désignation": s_name, "Unité": s_unit,
                "Qte": s_qte, "PU_HT": s_price, "Total_HT": s_qte * s_price
            })
            st.rerun()

    # 4. العرض والحسابات (التحويل للحروف)
    if st.session_state.cart:
        st.table(pd.DataFrame(st.session_state.cart))
        
        ht_brut = sum(item['Total_HT'] for item in st.session_state.cart)
        tva = ht_brut * 0.20
        ttc = ht_brut + tva
        
        # تحويل المبلغ لحروف
        try:
            ttc_letters = num2words(ttc, lang='fr').upper() + " DIRHAMS"
        except:
            ttc_letters = "---"

        st.info(f"**Arrêter le présent document à la somme de :** {ttc_letters}")

        # 5. أزرار الحفظ والـ PDF
        b1, b2, b3 = st.columns(3)

        if b1.button("💾 Enregistrer", type="primary", use_container_width=True):
            new_row = pd.DataFrame([[str(len(df_f)+1), datetime.now().strftime("%d/%m/%Y"), d_num, s_client, f"{ht_brut:.2f}", f"{tva:.2f}", f"{ttc:.2f}"]], 
                                   columns=["ID", "Date", "Num_Facture", "Client", "HT", "TVA", "TTC"])
            save_data("Facturations", pd.concat([df_f, new_row]))
            st.success("✅ Données sauvegardées !")

        if b2.button("📥 Télécharger PDF M-VAC", use_container_width=True):
            pdf = FPDF()
            pdf.add_page()
            
            # --- Header (Logo M-VAC) ---
            try: pdf.image("logo.png", 10, 8, 45)
            except: pdf.set_font("Arial", 'B', 16); pdf.cell(0, 10, "M-VAC SYSTEM", ln=1)
            
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, d_type, ln=1, align='R')
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 5, f"N°: {d_num}", ln=1, align='R')
            pdf.cell(0, 5, f"Date: {datetime.now().strftime('%d/%m/%Y')}", ln=1, align='R')
            
            pdf.ln(20)
            pdf.set_fill_color(240, 240, 240)
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 10, f" CLIENT: {s_client}", 1, 1, 'L', True)
            pdf.ln(5)

            # --- Table Design ---
            pdf.set_fill_color(0, 70, 70)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(85, 10, " DESIGNATION", 1, 0, 'L', True)
            pdf.cell(20, 10, "UNITE", 1, 0, 'C', True)
            pdf.cell(15, 10, "QTE", 1, 0, 'C', True)
            pdf.cell(30, 10, "P.U HT", 1, 0, 'C', True)
            pdf.cell(40, 10, "TOTAL HT", 1, 1, 'C', True)

            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", '', 9)
            for item in st.session_state.cart:
                pdf.cell(85, 8, f" {item['Désignation']}", 1)
                pdf.cell(20, 8, item['Unité'], 1, 0, 'C')
                pdf.cell(15, 8, str(item['Qte']), 1, 0, 'C')
                pdf.cell(30, 8, f"{item['PU_HT']:.2f}", 1, 0, 'R')
                pdf.cell(45, 8, f"{item['Total_HT']:.2f}", 1, 1, 'R')

            # --- Totals ---
            pdf.ln(5)
            pdf.cell(150, 8, "TOTAL HT :", 0, 0, 'R')
            pdf.cell(40, 8, f"{ht_brut:.2f} DH", 1, 1, 'C')
            pdf.cell(150, 8, "TOTAL TAXE (20%) :", 0, 0, 'R')
            pdf.cell(40, 8, f"{tva:.2f} DH", 1, 1, 'C')
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(150, 10, "TOTAL TTC :", 0, 0, 'R')
            pdf.cell(40, 10, f"{ttc:.2f} DH", 1, 1, 'C', True)

            # المبلغ بالحروف
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 9)
            pdf.multi_cell(0, 8, f"ARRETER LE PRESENT {d_type} A LA SOMME DE : {ttc_letters}")

            # --- Footer (معلومات الشركة من الصورة) ---
            pdf.set_y(-35)
            pdf.set_font("Arial", 'I', 7)
            footer_txt = "MARNYSY VENTILATION ET AIR CONDITIONNELL SARL AU\nSiage: N 196 LOTISSEMENT LAYMOUNE BEN SOUDA FES\nTEL: 06 63 45 18 55 - 06 61 57 43 81 | Email: mvac.sarl@gmail.com\nRC: 77421 - PT: 13441130 - IF: 53885224 - CNSS: 4987116 - ICE: 003337844000039"
            pdf.multi_cell(0, 4, footer_txt, 0, 'C')

            pdf_out = pdf.output(dest='S').encode('latin-1', errors='replace')
            b64 = base64.b64encode(pdf_out).decode()
            st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="{d_num}.pdf" style="text-decoration:none;"><button style="width:100%; background-color:#004646; color:white; padding:12px; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">📥 Télécharger le PDF Officiel</button></a>', unsafe_allow_html=True)

        if b3.button("🔄 Nouveau"):
            st.session_state.cart = []
            st.rerun()
