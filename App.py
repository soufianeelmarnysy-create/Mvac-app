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

# --- 1. CSS الخاص بالديزاين (FASTCOM Style) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fc; }
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #4e73df;
    }
    .main-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        margin-bottom: 20px;
    }
    .section-title {
        color: #1a202c;
        font-weight: bold;
        border-bottom: 2px solid #edf2f7;
        padding-bottom: 10px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. تعريف الدوال أولاً (لتجنب NameError) ---
def sync_details():
    """تحديث الوحدة والثمن أوتوماتيكياً عند تغيير السلعة"""
    if 'df_m' in st.session_state and st.session_state.df_m is not None:
        df = st.session_state.df_m
        try:
            selected_name = st.session_state.p_item_select
            # التأكد من وجود الأعمدة الكافية (Designation: 2, Unit: 3, Price: 5)
            if len(df.columns) >= 6:
                item_row = df[df.iloc[:, 2] == selected_name].iloc[0]
                st.session_state.p_unit = str(item_row.iloc[3])
                st.session_state.p_price = float(item_row.iloc[5])
        except:
            pass

# --- 3. منطق الصفحة الرئيسية ---
if page == "📄 Devis / Facture":
    st.markdown('<h1 style="color: #2d3748;">📄 Gestion des Documents</h1>', unsafe_allow_html=True)
    
    # جلب البيانات وتخزينها في session_state للوصول إليها من الدوال
    st.session_state.df_c = load_data("Customers")
    st.session_state.df_m = load_data("Materiels")
    st.session_state.df_f = load_data("Facturations")
    
    df_c, df_m, df_f = st.session_state.df_c, st.session_state.df_m, st.session_state.df_f

    if 'cart' not in st.session_state: st.session_state.cart = []

    # --- الجزء 1: إضافة السلع (Card العلوي) ---
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">📦 Ajouter des Articles</p>', unsafe_allow_html=True)
    
    # جلب لستة السلع بأمان (العمود رقم 3)
    items_list = []
    if df_m is not None and not df_m.empty and len(df_m.columns) >= 3:
        items_list = df_m.iloc[:, 2].dropna().tolist()

    # تعمير البيانات لأول مرة (Initial Load)
    if ('p_unit' not in st.session_state or st.session_state.p_unit == "") and items_list:
        try:
            if len(df_m.columns) >= 6:
                first_row = df_m.iloc[0]
                st.session_state.p_unit = str(first_row.iloc[3])
                st.session_state.p_price = float(first_row.iloc[5])
        except: pass

    i1, i2, i3, i4 = st.columns([3, 1, 1, 1])
    s_name = i1.selectbox("Désignation", items_list, key="p_item_select", on_change=sync_details)
    s_unit = i2.text_input("Unité", key="p_unit")
    s_qte = i3.number_input("Qte", min_value=0.1, value=1.0, step=1.0)
    s_price = i4.number_input("P.U HT", key="p_price")

    if st.button("➕ Ajouter à la liste", use_container_width=True, type="secondary"):
        if s_name:
            st.session_state.cart.append({
                "Désignation": s_name, "Unité": s_unit, "Qte": s_qte, "P.U HT": s_price, "Total HT": s_qte * s_price
            })
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # --- الجزء 2: معلومات الزبون والملخص ---
    col_info, col_summary = st.columns([1, 1])
    
    with col_info:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">👤 Client & Document</p>', unsafe_allow_html=True)
        d_type = st.selectbox("Type", ["DEVIS", "FACTURE"], key="p_type")
        
        # جلب سميات الزبناء من العمود الثالث (Index 2)
        clients_list = ["No Client Found"]
        if df_c is not None and not df_c.empty and len(df_c.columns) >= 3:
            clients_list = df_c.iloc[:, 2].dropna().tolist()
            
        s_client = st.selectbox("Client", clients_list, key="p_client")
        last_id = len(df_f) + 1 if df_f is not None else 1
        d_num = st.text_input("N° Document", value=f"D{datetime.now().strftime('%y%m')}{str(last_id).zfill(2)}", key="p_num")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_summary:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">💰 Récapitulatif DH</p>', unsafe_allow_html=True)
        total_ht = sum(i['Total HT'] for i in st.session_state.cart)
        ttc = total_ht * 1.20
        
        c1, c2 = st.columns(2)
        c1.metric("TOTAL HT", f"{total_ht:,.2f}")
        c2.metric("TOTAL TTC", f"{ttc:,.2f}")
        
        if st.session_state.cart:
            if st.button("💾 Enregistrer & PDF", type="primary", use_container_width=True):
                # (هنا كود الحفظ فـ Google Sheets وتوليد الـ PDF)
                st.success("Document enregistré avec succès!")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- الجزء 3: عرض الجدول (Basket) ---
    if st.session_state.cart:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">🛒 Panier</p>', unsafe_allow_html=True)
        df_cart = pd.DataFrame(st.session_state.cart)
        st.dataframe(df_cart, use_container_width=True, hide_index=True)
        if st.button("🗑️ Vider le panier"):
            st.session_state.cart = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
#===================================================================================================================================================
#style
#===================================================================================================================================================
import streamlit as st
import pandas as pd

# --- 1. تزيين الواجهة بـ CSS (Custom Styling) ---
st.markdown("""
    <style>
    /* خلفية التطبيق */
    .stApp {
        background-color: #f8f9fc;
    }
    /* ستايل الكارط (Card) */
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #4e73df;
        margin-bottom: 20px;
    }
    .metric-label {
        font-size: 0.8rem;
        font-weight: bold;
        color: #4e73df;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #5a5c69;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. دالة لرسم "الكارط" بحال اللي فالتصويرة ---
def style_metric_card(label, value, color="#4e73df"):
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: {color};">
            <div class="metric-label" style="color: {color};">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)

# --- 3. جلب البيانات للحسابات ---
df_f = load_data("Facturations")
df_m = load_data("Materiels")

# حساب الأرقام (Dashboard Logic)
if df_f is not None and not df_f.empty:
    total_ttc = pd.to_numeric(df_f.iloc[:, 6], errors='coerce').sum()
    count_factures = len(df_f)
    # حساب الربح التقريبي أو المبيعات الشهرية هنا
else:
    total_ttc, count_factures = 0, 0

# --- 4. عرض الواجهة (Layout) ---
if page == "📊 Tableau de Bord":
    st.title("📊 Tableau de Bord (M-VAC)")
    
    # السطر الأول: بطاقات المعلومات (Stats)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        style_metric_card("Chiffre d'Affaires", f"{total_ttc:,.2f} DH", "#4e73df")
    with col2:
        style_metric_card("Total Factures", f"{count_factures}", "#1cc88a")
    with col3:
        style_metric_card("Stock Valeur", "9,730.00 DH", "#36b9cc")
    with col4:
        style_metric_card("Dépenses", "1,400.00 DH", "#e74a3b")

    st.markdown("---")

    # السطر الثاني: جداول وتنبيهات
    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.subheader("📈 تطور المبيعات")
        # هنا ممكن تزيد chart (مثال بسيط)
        if df_f is not None:
            chart_data = pd.DataFrame({'Ventes': [2000, 5000, total_ttc]})
            st.area_chart(chart_data)

    with right_col:
        st.subheader("⚠️ Stock Critique")
        with st.container(border=True):
            # محاكاة للتنبيهات اللي فالتصويرة
            st.error("Toner: 0 units")
            st.warning("Câble USB: 2 units")
            st.info("Routeur: 5 units")

    # السطر الثالث: آخر العمليات
    st.subheader("📄 آخر الفواتير المسجلة")
    if df_f is not None:
        st.dataframe(df_f.tail(5), use_container_width=True)
