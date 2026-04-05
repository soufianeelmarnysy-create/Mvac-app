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

# --- وظيفة عرض الـ PDF في الصفحة ---
def display_pdf(pdf_bytes):
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)

if page == "📄 Devis / Facture":
    st.header("📄 Création de Document PRO")

    # 1. Load Initial (البيانات من الصور لي صفتي)
    df_c = load_data("Customers")
    df_m = load_data("Materiels")
    df_f = load_data("Facturations")
    df_d = load_data("Devis")

    if 'cart' not in st.session_state: st.session_state.cart = []
    if 'pdf_ready' not in st.session_state: st.session_state.pdf_ready = None

    # 2. إعدادات الوثيقة
    with st.container(border=True):
        col1, col2, col3 = st.columns([1, 2, 1])
        doc_type = col1.selectbox("Document", ["DEVIS", "FACTURE"])
        
        # ComboBox Clients (العمود 2: الاسم/الشركة)
        clients = df_c.iloc[:, 2].tolist() if not df_c.empty else ["Passager"]
        selected_client = col2.selectbox("Sélectionner Client", clients)
        
        doc_ref = col3.text_input("Référence", value=f"{doc_type[0]}-{datetime.now().strftime('%y%m%d%H%M')}")

    # 3. ComboBox Articles & Infos
    with st.container(border=True):
        st.subheader("📦 Sélection des Articles")
        a1, a2, a3, a4 = st.columns([3, 1, 1, 1])
        
        # ComboBox Articles (العمود 2: السلعة)
        articles = df_m.iloc[:, 2].tolist() if not df_m.empty else []
        selected_art = a1.selectbox("Article", [""] + articles)
        
        u_val, p_ht = "", 0.0
        if selected_art:
            row = df_m[df_m.iloc[:, 2] == selected_art].iloc[0]
            u_val = row.iloc[3] # الوحدة
            p_ht = float(str(row.iloc[5]).replace(',', '.')) # ثمن الوحدة HT
        
        a2.text_input("Unité", value=u_val, disabled=True)
        qte = a3.number_input("Quantité", min_value=0.1, value=1.0)
        price_ht = a4.number_input("Prix HT (DH)", value=float(p_ht))
        
        if st.button("➕ Ajouter au Tableau", use_container_width=True):
            if selected_art:
                st.session_state.cart.append({
                    "Désignation": selected_art, "Unité": u_val,
                    "Qte": qte, "P.U HT": price_ht, "Total HT": qte * price_ht
                })
                st.rerun()

    # 4. Tableau interactif (عرض ومسح)
    if st.session_state.cart:
        st.divider()
        df_cart = pd.DataFrame(st.session_state.cart)
        st.subheader("📑 Détails de la commande")
        
        for i, item in enumerate(st.session_state.cart):
            c_art, c_del = st.columns([10, 1])
            c_art.info(f"{item['Désignation']} | {item['Qte']} {item['Unité']} x {item['P.U HT']} = {item['Total HT']:.2f} DH")
            if c_del.button("❌", key=f"del_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()

        # الحسابات
        total_ht = sum(i['Total HT'] for i in st.session_state.cart)
        tva = total_ht * 0.20
        total_ttc = total_ht + tva
        
        st.write(f"**Total HT:** {total_ht:.2f} DH | **TVA (20%):** {tva:.2f} DH")
        st.success(f"### TOTAL TTC: {total_ttc:.2f} DH")

        # 5. Enregistrer & Preview PDF
        if st.button("💾 Enregistrer le document", type="primary", use_container_width=True):
            # تحديد الصفحة المستهدفة في Sheets
            target_sheet = "Facturations" if doc_type == "FACTURE" else "Devis"
            target_df = df_f if doc_type == "FACTURE" else df_d
            
            # تسجيل البيانات
            new_data = [len(target_df)+1, datetime.now().strftime("%d/%m/%Y"), doc_ref, selected_client, total_ht, tva, total_ttc]
            save_data(target_sheet, pd.concat([target_df, pd.DataFrame([new_data], columns=target_df.columns[:7])]))
            
            # توليد PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, f"M-VAC PRO - {doc_type}", ln=True, align='C')
            pdf.ln(10)
            pdf.set_font("Arial", '', 12)
            pdf.cell(0, 10, f"Client: {selected_client} | Ref: {doc_ref}", ln=True)
            
            # الجدول في PDF
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(100, 10, "Article", 1, 0, 'C', 1)
            pdf.cell(40, 10, "Qte", 1, 0, 'C', 1)
            pdf.cell(50, 10, "Total HT", 1, 1, 'C', 1)
            for item in st.session_state.cart:
                pdf.cell(100, 10, str(item['Désignation']), 1)
                pdf.cell(40, 10, str(item['Qte']), 1)
                pdf.cell(50, 10, f"{item['Total HT']:.2f}", 1, 1)

            st.session_state.pdf_ready = pdf.output(dest='S').encode('latin-1')
            st.success(f"✅ {doc_type} enregistré avec succès !")

        # عرض وتحميل PDF
        if st.session_state.pdf_ready:
            st.divider()
            st.subheader("👁️ Aperçu du document")
            display_pdf(st.session_state.pdf_ready)
            
            st.download_button(
                label="📥 Télécharger le PDF",
                data=st.session_state.pdf_ready,
                file_name=f"{doc_ref}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
