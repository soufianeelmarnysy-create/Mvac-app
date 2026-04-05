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
from num2words import num2words
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ==========================================
# 1️⃣ الإعدادات والستايل (التصميم الاحترافي)
# ==========================================
st.set_page_config(page_title="M-VAC PRO", layout="wide")

st.markdown("""
    <style>
        .main { background-color: #f8f9fa; }
        .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .article-card { 
            background: white; padding: 20px; border-radius: 15px; 
            border-left: 5px solid #2980b9; margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2️⃣ الربط مع Google Sheets (SERVICE_ACCOUNT)
# ==========================================
# نصيحة: تأكد أن SERVICE_ACCOUNT_INFO فيه كاع السطور (بما فيهم private_key_id)
@st.cache_resource
def connect_gsheets():
    # حط الـ JSON ديالك كامل هنا وسط الأقواس {}
    SERVICE_ACCOUNT_INFO = st.secrets["gcp_service_account"] # هادي أحسن طريقة فـ Streamlit Cloud
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(SERVICE_ACCOUNT_INFO, scope)
    return gspread.authorize(creds)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMl791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

try:
    client = connect_gsheets()
    sh = client.open_by_url(SHEET_URL)
except Exception as e:
    st.error(f"❌ مشكل في الاتصال: {e}")
    st.stop()

# دالات جلب وحفظ البيانات
def load_data(sheet_name):
    worksheet = sh.worksheet(sheet_name)
    return pd.DataFrame(worksheet.get_all_records())

def save_data(sheet_name, df):
    worksheet = sh.worksheet(sheet_name)
    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

# ==========================================
# 3️⃣ واجهة البرنامج (Sidebar)
# ==========================================
with st.sidebar:
    st.title("M-VAC PRO 📦")
    menu = st.radio("Navigation", ["📊 Dashboard", "🛒 Ventes & Factures", "👥 Clients"])
    st.info(f"Connecté à: {sh.title}")

# جلب البيانات الأساسية
df_m = load_data("Materiels")
df_c = load_data("Customers")
df_f = load_data("Facturations")

# ==========================================
# 📊 الجزء 1: Dashboard (لوحة التحكم)
# ==========================================
if menu == "📊 Dashboard":
    st.subheader("Tableau de Bord")
    
    # حسابات سريعة
    total_ca = pd.to_numeric(df_f['Total_TTC'], errors='coerce').sum() if not df_f.empty else 0
    nb_ventes = len(df_f)
    stock_alerte = len(df_m[pd.to_numeric(df_m['Stock'], errors='coerce') < 5])

    c1, c2, c3 = st.columns(3)
    c1.metric("Chiffre d'Affaires", f"{total_ca:,.2f} DH")
    c2.metric("Nombre de Ventes", nb_ventes)
    c3.metric("Articles en Alerte Stock", stock_alerte, delta_color="inverse")

    st.divider()
    st.subheader("📈 Évolution des Ventes")
    if not df_f.empty:
        st.line_chart(df_f.set_index('Date')['Total_HT'])

# ==========================================
# 🛒 الجزء 2: Ventes & Factures (الخدمة ديالك)
# ==========================================
elif menu == "🛒 Ventes & Factures":
    if 'cart' not in st.session_state: st.session_state.cart = []

    st.markdown("<div class='article-card'><h3>➕ Ajouter un Article</h3></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        s_item = st.selectbox("Sélectionner l'Article", df_m['Désignation'].unique())
        row = df_m[df_m['Désignation'] == s_item].iloc[0]
        
        q = st.number_input("Quantité", min_value=0.1, value=1.0)
        p = st.number_input("Prix Unitaire HT (DH)", value=float(row['Prix_HT']))
    
    with col2:
        current_stock = float(row['Stock'])
        st.write(f"**Stock disponible:** {current_stock} {row['Unité']}")
        if st.button("➕ Ajouter au Panier", use_container_width=True):
            if q > current_stock:
                st.error("❌ الكمية المطلوبة كثر من الستوك!")
            else:
                st.session_state.cart.append({
                    "Désignation": s_item, "Unité": row['Unité'], 
                    "Qte": q, "P.U": p, "Total": q*p
                })
                st.rerun()

    # عرض السلة والتحكم
    if st.session_state.cart:
        st.subheader("🧾 Récapitulatif de la Commande")
        df_cart = pd.DataFrame(st.session_state.cart)
        st.table(df_cart)
        
        total_ht = df_cart['Total'].sum()
        total_ttc = total_ht * 1.2
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            d_type = st.radio("Document", ["DEVIS", "FACTURE"], horizontal=True)
            s_client = st.selectbox("Client", df_c['Nom'].unique() if not df_c.empty else ["Client Standard"])
        
        with col_f2:
            st.metric("TOTAL TTC", f"{total_ttc:,.2f} DH")
            st.write(f"**En lettres:** {num2words(total_ttc, lang='fr').upper()} DH")

        if st.button("💾 Valider et Enregistrer la Transaction", type="primary", use_container_width=True):
            # 1. تحديث الستوك في جدول Materiels (فقط للفاتورة)
            if d_type == "FACTURE":
                for item in st.session_state.cart:
                    idx = df_m[df_m['Désignation'] == item['Désignation']].index[0]
                    df_m.at[idx, 'Stock'] = float(df_m.at[idx, 'Stock']) - item['Qte']
                save_data("Materiels", df_m)

            # 2. تسجيل الفاتورة في جدول Facturations
            new_ref = f"MVAC-{datetime.now().strftime('%y%m%d%H%M')}"
            new_row = {
                "ID": len(df_f)+1, "Date": datetime.now().strftime("%d/%m/%Y"),
                "Référence": new_ref, "Client": s_client,
                "Total_HT": total_ht, "TVA": total_ht*0.2,
                "Total_TTC": total_ttc, "Type": d_type
            }
            df_f = pd.concat([df_f, pd.DataFrame([new_row])], ignore_index=True)
            save_data("Facturations", df_f)

            st.session_state.cart = []
            st.success(f"✅ تم تسجيل {d_type} بنجاح!")
            st.rerun()

        if st.button("🗑️ Vider le panier"):
            st.session_state.cart = []
            st.rerun()
