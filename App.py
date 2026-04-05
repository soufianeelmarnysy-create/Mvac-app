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

# CSS باش نرجعو الواجهة بحال Fastcom (مربعات بيضاء، ظل، وألوان متناسقة)
st.markdown("""
    <style>
        .main { background-color: #f0f2f6; }
        .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #2980b9; color: white; }
        .metric-container {
            background-color: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-top: 5px solid #2980b9;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2️⃣ الربط المباشر مع Google Sheets
# ==========================================
@st.cache_resource
def connect_to_gsheets():
    # ⚠️ حط المعلومات ديالك هنا كاملة كيفما كاينين في ملف JSON
    SERVICE_ACCOUNT_INFO = {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_KEY_HERE\n-----END PRIVATE KEY-----\n",
        "client_email": "your-email@project.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "your-cert-url"
    }
    
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(SERVICE_ACCOUNT_INFO, scope)
    return gspread.authorize(creds)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMl791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

try:
    gc = connect_to_gsheets()
    sh = gc.open_by_url(SHEET_URL)
except Exception as e:
    st.error(f"❌ خطأ في الربط: {e}")
    st.stop()

# دالات جلب وحفظ البيانات (التعامل مع جداولك)
def load_data(sheet_name):
    ws = sh.worksheet(sheet_name)
    return pd.DataFrame(ws.get_all_records())

def save_data(sheet_name, df):
    ws = sh.worksheet(sheet_name)
    ws.clear()
    # كتحول الجدول لليست باش Google Sheets يفهمها
    ws.update([df.columns.values.tolist()] + df.values.tolist())

# ==========================================
# 3️⃣ جلب البيانات وتحضير الواجهة
# ==========================================
df_m = load_data("Materiels")
df_c = load_data("Customers")
df_f = load_data("Facturations")

# Sidebar
with st.sidebar:
    st.title("📦 M-VAC PRO")
    menu = st.radio("القائمة الرئيسية", ["📊 Dashboard", "🛒 Ventes", "📦 Stock"])

# ------------------------------------------
# 📊 الجزء 1: Dashboard (الإحصائيات)
# ------------------------------------------
if menu == "📊 Dashboard":
    st.subheader("إحصائيات عامة")
    
    # حساب القيم
    total_ca = pd.to_numeric(df_f['Total_TTC'], errors='coerce').sum()
    count_factures = len(df_f)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-container'><b>CHIFFRE D'AFFAIRES</b><br><h2>{total_ca:,.2f} DH</h2></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-container'><b>FACTURES TOTAL</b><br><h2>{count_factures}</h2></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-container'><b>CLIENTS</b><br><h2>{len(df_c)}</h2></div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("📉 مبيان المبيعات")
    if not df_f.empty:
        st.line_chart(df_f.set_index('Date')['Total_HT'])

# ------------------------------------------
# 🛒 الجزء 2: Ventes (إنشاء الفاتورة)
# ------------------------------------------
elif menu == "🛒 Ventes":
    if 'cart' not in st.session_state: st.session_state.cart = []
    
    st.subheader("إنشاء فاتورة / دوكري")
    
    col_in1, col_in2 = st.columns([2, 1])
    with col_in1:
        s_item = st.selectbox("اختار السلعة", df_m['Désignation'].unique())
        row = df_m[df_m['Désignation'] == s_item].iloc[0]
        qte = st.number_input("الكمية", min_value=0.1, value=1.0)
    
    with col_in2:
        prix = st.number_input("الثمن HT", value=float(row['Prix_HT']))
        st.write(f"**Stock:** {row['Stock']} {row['Unité']}")
        
    if st.button("➕ إضافة إلى السلة"):
        if qte > float(row['Stock']):
            st.error("الكمية كثر من اللي كاين في الستوك!")
        else:
            st.session_state.cart.append({
                "Désignation": s_item, "Unité": row['Unité'], 
                "Qte": qte, "P.U": prix, "Total": qte * prix
            })
            st.rerun()

    # عرض السلة
    if st.session_state.cart:
        st.divider()
        df_cart = pd.DataFrame(st.session_state.cart)
        st.table(df_cart)
        
        total_ht = df_cart['Total'].sum()
        total_ttc = total_ht * 1.2
        
        c_f1, c_f2 = st.columns(2)
        with c_f1:
            type_doc = st.radio("نوع الوثيقة", ["DEVIS", "FACTURE"], horizontal=True)
            client_name = st.selectbox("اختار الزبون", df_c['Nom'].unique())
        
        with c_f2:
            st.metric("Total TTC", f"{total_ttc:,.2f} DH")
            st.write(f"**المبلغ بالحروف:** {num2words(total_ttc, lang='fr').upper()} DH")

        if st.button("💾 حفظ العملية وتحديث الستوك", type="primary"):
            # 1. تحديث الستوك (Boucle)
            if type_doc == "FACTURE":
                for item in st.session_state.cart:
                    idx = df_m[df_m['Désignation'] == item['Désignation']].index[0]
                    df_m.at[idx, 'Stock'] = float(df_m.at[idx, 'Stock']) - item['Qte']
                save_data("Materiels", df_m)
            
            # 2. تسجيل الفاتورة
            new_f = [len(df_f)+1, datetime.now().strftime("%d/%m/%Y"), "REF-"+datetime.now().strftime("%H%M"), client_name, total_ht, total_ht*0.2, total_ttc, type_doc]
            # تحويل السطر لـ DataFrame وزيادته
            df_f = pd.concat([df_f, pd.DataFrame([new_f], columns=df_f.columns[:8])], ignore_index=True)
            save_data("Facturations", df_f)
            
            st.session_state.cart = []
            st.success("✅ تمت العملية بنجاح!")
            st.rerun()
