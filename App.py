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
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from fpdf import FPDF
from datetime import datetime

# -------------------------------
# GOOGLE SHEETS
# -------------------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

sheet = client.open("MVAC_Data")

ws_m = sheet.worksheet("Materiels")
ws_c = sheet.worksheet("Customers")
ws_f = sheet.worksheet("Facturations")

# -------------------------------
# LOAD
# -------------------------------
def load(ws):
    return pd.DataFrame(ws.get_all_records())

def save_fact(row):
    ws_f.append_row(row)

def update_stock(cart):
    df = load(ws_m)
    for item in cart:
        idx = df[df["السلعة"] == item["Désignation"]].index
        if not idx.empty:
            current = float(df.loc[idx[0], "الكمية"])
            new = current - item["Qte"]
            ws_m.update_cell(idx[0]+2, 5, new)

# -------------------------------
# SESSION
# -------------------------------
if "cart" not in st.session_state:
    st.session_state.cart = []

if "saved" not in st.session_state:
    st.session_state.saved = False

# -------------------------------
# UI
# -------------------------------
st.title("🔥 M-VAC PRO MAX")

df_m = load(ws_m)
df_c = load(ws_c)
df_f = load(ws_f)

# -------------------------------
# CLIENT
# -------------------------------
clients = df_c["الاسم/الشركة"].tolist()
client = st.selectbox("👤 Client", clients)

# commission
commission = st.number_input("💰 Commission (%)", 0, 100, 0)

# auto num facture
count_client = len(df_f[df_f["Client"] == client]) + 1
ref = f"{client[:3].upper()}-{count_client:03d}"

st.info(f"📄 Numéro: {ref}")

# -------------------------------
# PRODUIT
# -------------------------------
items = df_m["السلعة"].tolist()
prod = st.selectbox("📦 Produit", items)

row = df_m[df_m["السلعة"] == prod].iloc[0]

stock = float(row["الكمية"])
price = float(row["ثمن الوحدة"])
unit = row["الوحدة"]

st.write(f"📏 Unité: {unit} | 💵 Prix: {price} DH | 📦 Stock: {stock}")

q = st.number_input("Quantité", 0.1, stock, 1.0)

if st.button("➕ Ajouter"):

    found = False
    for i in st.session_state.cart:
        if i["Désignation"] == prod:
            i["Qte"] += q
            i["Total"] = i["Qte"] * i["P.U"]
            found = True

    if not found:
        st.session_state.cart.append({
            "Désignation": prod,
            "Qte": q,
            "P.U": price,
            "Total": q * price
        })

    st.rerun()

# -------------------------------
# PANIER EDIT
# -------------------------------
if st.session_state.cart:

    st.subheader("🧾 Panier")

    for i, item in enumerate(st.session_state.cart):
        col1, col2, col3, col4 = st.columns([3,1,1,1])

        col1.write(item["Désignation"])
        new_qte = col2.number_input(f"Qte {i}", value=item["Qte"], key=i)
        
        if col3.button("❌", key=f"del{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

        if new_qte != item["Qte"]:
            item["Qte"] = new_qte
            item["Total"] = new_qte * item["P.U"]

    total_ht = sum(i["Total"] for i in st.session_state.cart)
    com = total_ht * (commission / 100)
    tva = total_ht * 0.2
    ttc = total_ht + tva + com

    st.success(f"HT: {total_ht} | TVA: {tva} | Commission: {com} | TTC: {ttc}")

    # -------------------------------
    # SAVE BUTTON
    # -------------------------------
    if st.button("💾 Enregistrer"):

        row = [
            len(df_f)+1,
            datetime.now().strftime("%d/%m/%Y"),
            ref,
            client,
            total_ht,
            tva,
            ttc,
            "FACTURE"
        ]

        save_fact(row)
        update_stock(st.session_state.cart)

        st.session_state.saved = True
        st.success("✅ Enregistré")

# -------------------------------
# PDF BUTTON
# -------------------------------
if st.session_state.saved:

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"FACTURE - {ref}", ln=True, align="C")

    pdf.cell(0, 8, f"Client: {client}", ln=True)

    pdf.ln(5)

    for item in st.session_state.cart:
        pdf.cell(0, 8, f"{item['Désignation']} | {item['Qte']} x {item['P.U']} = {item['Total']:.2f}", ln=True)

    pdf.ln(5)
    pdf.cell(0, 10, f"TTC: {ttc:.2f} DH", ln=True)

    pdf_data = pdf.output(dest='S')
    pdf_bytes = pdf_data if isinstance(pdf_data, bytes) else pdf_data.encode('latin-1')

    st.download_button("📥 Télécharger PDF", pdf_bytes, file_name=f"{ref}.pdf")
