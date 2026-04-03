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

# --- 1. الدوال الأساسية (توليد PDF والربط) ---
def generate_pdf_link(pdf, filename):
    """إصلاح مشكل الـ PDF وتحويله لـ Bytes بطريقة صحيحة"""
    try:
        pdf_output = pdf.output()
        # التعامل مع اختلاف نسخ المكتبة (Bytes vs String)
        if isinstance(pdf_output, str):
            pdf_bytes = pdf_output.encode('latin-1')
        else:
            pdf_bytes = pdf_output
        b64 = base64.b64encode(pdf_bytes).decode()
        return f'''
            <a href="data:application/pdf;base64,{b64}" download="{filename}" style="text-decoration:none;">
                <button style="width:100%; background-color:#28a745; color:white; padding:12px; border-radius:8px; border:none; cursor:pointer; font-weight:bold;">
                    📥 Télécharger le PDF
                </button>
            </a>'''
    except Exception as e:
        return f"Erreur PDF: {str(e)}"

def sync_item_details():
    """تجلب الثمن والوحدة من العمود الصحيح (Index 2 للسلعة، 3 للوحدة، 5 للثمن)"""
    if 'df_m' in st.session_state and st.session_state.df_m is not None:
        try:
            sel = st.session_state.p_item_select
            df = st.session_state.df_m
            # البحث في العمود رقم 3 (Index 2)
            row = df[df.iloc[:, 2] == sel].iloc[0]
            st.session_state.p_unit = str(row.iloc[3])
            st.session_state.p_price = float(row.iloc[5])
        except: pass

# --- 2. الستايل (الديزاين اللي مولف عليه) ---
st.markdown("""
    <style>
    .main-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px; }
    [data-testid="stMetric"] { background: #f8f9fc; border-left: 5px solid #4e73df; padding: 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. منطق صفحة الفواتير ---
if page == "📄 Devis / Facture":
    st.title("📄 Gestion des Documents (M-VAC)")

    # تحميل البيانات
    df_c = load_data("Customers")
    df_m = load_data("Materiels")
    df_f = load_data("Facturations")
    st.session_state.df_m = df_m # حفظ السلع للبحث

    if 'cart' not in st.session_state:
        st.session_state.cart = []

    # --- الجزء 1: إضافة السلعة (Card 1) ---
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📦 Ajouter des Articles")
    
    items_list = df_m.iloc[:, 2].dropna().tolist() if df_m is not None else []
    
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    s_name = col1.selectbox("Désignation", items_list, key="p_item_select", on_change=sync_item_details)
    s_unit = col2.text_input("Unité", key="p_unit")
    s_qte = col3.number_input("Qté", min_value=0.1, value=1.0, step=1.0)
    s_price = col4.number_input("P.U HT", key="p_price", format="%.2f")

    if st.button("➕ Ajouter à la liste", use_container_width=True):
        if s_name:
            st.session_state.cart.append({
                "Désignation": s_name, "Unité": s_unit, 
                "Qte": s_qte, "P.U HT": s_price, "Total HT": s_qte * s_price
            })
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # --- الجزء 2: معلومات الزبون والحسابات (Card 2) ---
    c_left, c_right = st.columns(2)

    with c_left:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        d_type = st.selectbox("Type", ["DEVIS", "FACTURE"])
        # تصحيح الزبناء: العمود رقم 3 (Index 2)
        clients = df_c.iloc[:, 2].dropna().tolist() if df_c is not None else ["Client Standard"]
        s_client = st.selectbox("Client", clients)
        d_num = st.text_input("Référence", value=f"REF-{datetime.now().strftime('%d%H%M')}")
        st.markdown('</div>', unsafe_allow_html=True)

    with c_right:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        # حساب المجموع دقيق
        total_ht = sum(float(item['Total HT']) for item in st.session_state.cart)
        ttc = total_ht * 1.20
        
        st.metric("TOTAL TTC (DH)", f"{ttc:,.2f}")
        st.write(f"**Total HT:** {total_ht:,.2f} DH")
        
        if st.session_state.cart:
            if st.button("💾 Enregistrer & PDF", type="primary", use_container_width=True):
                # توليد PDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, f"M-VAC : {d_type} - {d_num}", ln=True, align='C')
                pdf.ln(5)
                pdf.set_font("Arial", '', 11)
                pdf.cell(0, 10, f"Client: {s_client} | Date: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
                pdf.ln(5)
                
                # جدول بسيط في PDF
                pdf.set_fill_color(240, 240, 240)
                pdf.cell(100, 10, "Désignation", 1, 0, 'C', True)
                pdf.cell(30, 10, "Qté", 1, 0, 'C', True)
                pdf.cell(30, 10, "Total HT", 1, 1, 'C', True)
                
                for item in st.session_state.cart:
                    pdf.cell(100, 10, str(item['Désignation']), 1)
                    pdf.cell(30, 10, str(item['Qte']), 1, 0, 'C')
                    pdf.cell(30, 10, f"{item['Total HT']:.2f}", 1, 1, 'C')
                
                pdf.ln(5)
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(130, 10, "TOTAL TTC (DH):", 0)
                pdf.cell(30, 10, f"{ttc:,.2f}", 1, 1, 'C')

                # زر التحميل (الإصلاح الجديد)
                st.markdown(generate_pdf_link(pdf, f"{d_num}.pdf"), unsafe_allow_html=True)
                
                # حفظ في Google Sheets
                summary = ", ".join([str(i['Désignation']) for i in st.session_state.cart])
                new_row = [str(len(df_f)+1), datetime.now().strftime("%d/%m/%Y"), d_num, s_client, 
                           f"{total_ht:.2f}", f"{total_ht*0.2:.2f}", f"{ttc:.2f}", d_type, summary]
                save_data("Facturations", pd.concat([df_f, pd.DataFrame([new_row], columns=df_f.columns)], ignore_index=True))
                st.success("✅ Enregistré avec succès!")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- الجزء 3: عرض السلة (Card 3) ---
    if st.session_state.cart:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("🛒 Liste des Articles")
        st.table(pd.DataFrame(st.session_state.cart))
        if st.button("🗑️ Vider le panier"):
            st.session_state.cart = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
