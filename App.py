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
from fpdf import FPDF
from datetime import datetime
import base64

# --- 1. إعدادات الـ PDF الاحترافي ---
class MVAC_PDF(FPDF):
    def header(self):
        # اللوغو (تأكد أن الصورة موجودة ف نفس الملف)
        try: self.image('mvac_logo.png', 10, 8, 33)
        except: pass
        self.set_font('Arial', 'B', 15)
        self.cell(80)
        self.cell(30, 10, 'M-VAC SARL', 0, 0, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'M-VAC SARL - ICE: 00000000 - RC: 12345 - Adresse: Votre Adresse Ici', 0, 0, 'C')

# --- 2. دالة البحث والمخزون (المرحلة 2) ---
def sync_with_stock():
    if 'p_item_select' in st.session_state:
        sel = st.session_state.p_item_select
        df = st.session_state.df_m
        try:
            # كنقلبو ف العمود 3 (Index 2)
            item_row = df[df.iloc[:, 2] == sel].iloc[0]
            st.session_state.p_unit = str(item_row.iloc[3])
            st.session_state.p_price = float(item_row.iloc[5])
            # نفترض أن الـ Stock موجود ف العمود رقم 7 (Index 6)
            st.session_state.p_stock = float(item_row.iloc[6]) if len(item_row) > 6 else 0
        except: pass

# --- 3. واجهة البرنامج ---
if page == "📄 Devis / Facture":
    st.title("📄 Système de Facturation M-VAC")
    
    df_c = load_data("Customers")
    df_m = load_data("Materiels")
    df_f = load_data("Facturations")
    st.session_state.df_m = df_m

    # --- المرحلة 2: اختيار السلعة ومعرفة الـ Stock ---
    with st.container():
        st.subheader("📦 Recherche & Stock")
        items = df_m.iloc[:, 2].dropna().tolist() if df_m is not None else []
        col_s1, col_s2 = st.columns([3, 1])
        s_name = col_s1.selectbox("Article", items, key="p_item_select", on_change=sync_with_stock)
        
        # عرض حالة المخزون
        stock_val = st.session_state.get('p_stock', 0)
        col_s2.metric("Stock Actuel", f"{stock_val}")

        with st.form("add_form"):
            c1, c2, c3 = st.columns(3)
            u = c1.text_input("Unité", key="p_unit")
            p = c2.number_input("Prix HT", key="p_price")
            q = c3.number_input("Quantité à utiliser", min_value=0.1, value=1.0)
            
            if st.form_submit_button("➕ Ajouter au document"):
                if q > stock_val:
                    st.error(f"Attention! الكمية المطلوبة ({q}) كثر من اللي كاين ف Stock ({stock_val})")
                else:
                    st.session_state.cart.append({"Désignation": s_name, "Unité": u, "Qte": q, "P.U": p, "Total": q*p})
                    st.rerun()

    # --- المرحلة 3: الحفظ المختصر ---
    st.divider()
    c_info, c_calc = st.columns(2)
    with c_info:
        client = st.selectbox("Client", df_c.iloc[:, 2].tolist())
        doc_type = st.radio("Type", ["DEVIS", "FACTURE"], horizontal=True)
        doc_ref = st.text_input("Numéro", value=f"MVAC-{datetime.now().strftime('%y%m%d%H%M')}")

    with c_calc:
        total_ht = sum(item['Total'] for item in st.session_state.cart)
        ttc = total_ht * 1.20
        st.metric("Total TTC", f"{ttc:,.2f} DH")
        
        if st.button("💾 Valider & Générer PDF", type="primary"):
            # 1. الحفظ ف Sheets (المرحلة 3: معلومات مختصرة فقط)
            new_row = [len(df_f)+1, datetime.now().strftime("%d/%m/%Y"), doc_ref, client, total_ht, total_ht*0.2, ttc, doc_type]
            save_data("Facturations", pd.concat([df_f, pd.DataFrame([new_row], columns=df_f.columns[:8])], ignore_index=True))
            
            # 2. إنشاء PDF (المرحلة 4)
            pdf = MVAC_PDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, f"{doc_type} N: {doc_ref}", ln=True)
            pdf.cell(0, 10, f"Client: {client}", ln=True)
            
            # الجدول
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(90, 10, "Designation", 1, 0, 'C', True)
            pdf.cell(30, 10, "Qte", 1, 0, 'C', True)
            pdf.cell(35, 10, "P.U HT", 1, 0, 'C', True)
            pdf.cell(35, 10, "Total HT", 1, 1, 'C', True)
            
            for item in st.session_state.cart:
                pdf.cell(90, 10, item['Désignation'], 1)
                pdf.cell(30, 10, str(item['Qte']), 1, 0, 'C')
                pdf.cell(35, 10, f"{item['P.U']:.2f}", 1, 0, 'C')
                pdf.cell(35, 10, f"{item['Total']:.2f}", 1, 1, 'C')
            
            pdf.ln(5)
            pdf.cell(155, 10, "TOTAL TTC (DH):", 0, 0, 'R')
            pdf.cell(35, 10, f"{ttc:,.2f}", 1, 1, 'C')

            # زر التحميل
            pdf_bytes = pdf.output()
            b64 = base64.b64encode(pdf_bytes).decode()
            st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="{doc_ref}.pdf">📥 Télécharger la Facture</a>', unsafe_allow_html=True)
            st.success("Document enregistré !")
