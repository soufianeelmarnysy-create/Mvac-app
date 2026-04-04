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
import os

# -------------------------------
# 1. INIT FILES (auto create)
# -------------------------------
def init_files():
    if not os.path.exists("Materiels.csv"):
        df = pd.DataFrame([
            [1, "M001", "Climatiseur", "U", 10, 2500],
            [2, "M002", "Compresseur", "U", 5, 1800],
        ], columns=["ID","Ref","Designation","Unite","Stock","Prix"])
        df.to_csv("Materiels.csv", index=False)

    if not os.path.exists("Customers.csv"):
        df = pd.DataFrame([
            [1, "C001", "Client Standard"]
        ], columns=["ID","Ref","Nom"])
        df.to_csv("Customers.csv", index=False)

    if not os.path.exists("Facturations.csv"):
        df = pd.DataFrame(columns=["ID","Date","Ref","Client","HT","TVA","TTC","Type"])
        df.to_csv("Facturations.csv", index=False)

init_files()

# -------------------------------
# 2. LOAD / SAVE
# -------------------------------
def load_data(name):
    return pd.read_csv(f"{name}.csv")

def save_data(name, df):
    df.to_csv(f"{name}.csv", index=False)

# -------------------------------
# 3. SESSION
# -------------------------------
if 'cart' not in st.session_state:
    st.session_state.cart = []

# -------------------------------
# 4. UPDATE STOCK
# -------------------------------
def update_stock(cart_items):
    df_m = load_data("Materiels")

    for item in cart_items:
        mask = df_m["Designation"] == item['Désignation']
        idx = df_m[mask].index

        if not idx.empty:
            current = float(df_m.loc[idx[0], "Stock"])
            df_m.loc[idx[0], "Stock"] = current - item['Qte']

    save_data("Materiels", df_m)

# -------------------------------
# 5. UI
# -------------------------------
st.title("📄 M-VAC PRO : Gestion Commerciale")

df_m = load_data("Materiels")
df_c = load_data("Customers")
df_f = load_data("Facturations")

# -------------------------------
# 6. ADD PRODUCT
# -------------------------------
st.subheader("🛒 Ajouter Article")

items = df_m["Designation"].tolist()
s_item = st.selectbox("Article", items)

row = df_m[df_m["Designation"] == s_item].iloc[0]

stock = float(row["Stock"])
price = float(row["Prix"])
unit = row["Unite"]

col1, col2 = st.columns([3,1])

with col1:
    p = st.number_input("Prix HT", value=price)
    q = st.number_input("Quantité", min_value=0.1, max_value=stock, value=1.0)

with col2:
    color = "green" if stock > 0 else "red"
    st.markdown(f"### Stock\n<span style='color:{color}'>{stock}</span>", unsafe_allow_html=True)

if st.button("➕ Ajouter au panier"):

    if q > stock:
        st.error("❌ Stock insuffisant")
    else:
        found = False
        for i in st.session_state.cart:
            if i["Désignation"] == s_item:
                i["Qte"] += q
                i["Total"] = i["Qte"] * i["P.U"]
                found = True
                break

        if not found:
            st.session_state.cart.append({
                "Désignation": s_item,
                "Unité": unit,
                "Qte": q,
                "P.U": p,
                "Total": q * p
            })

        st.rerun()

# -------------------------------
# 7. CART + PDF
# -------------------------------
if st.session_state.cart:

    st.subheader("🧾 Panier")
    st.table(pd.DataFrame(st.session_state.cart))

    clients = df_c["Nom"].tolist()

    col1, col2 = st.columns(2)

    with col1:
        d_type = st.radio("Type", ["DEVIS", "FACTURE"])
        client = st.selectbox("Client", clients)

    with col2:
        total_ht = sum(i['Total'] for i in st.session_state.cart)
        tva = total_ht * 0.2
        ttc = total_ht + tva
        st.metric("Total TTC", f"{ttc:.2f} DH")

    ref = f"MVAC-{datetime.now().strftime('%y%m%d%H%M%S')}"

    # PDF
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 10, f"{d_type} - M-VAC", ln=True, align="C")

    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f"Ref: {ref} | Client: {client}", ln=True)

    pdf.ln(5)

    for item in st.session_state.cart:
        pdf.cell(0, 8, f"{item['Désignation']} | {item['Qte']} x {item['P.U']} = {item['Total']:.2f}", ln=True)

    pdf.ln(5)
    pdf.cell(0, 10, f"TOTAL TTC: {ttc:.2f} DH", ln=True)

    pdf_data = pdf.output(dest='S')

try:
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
except:
    pdf_bytes = pdf.output(dest='S')

    if st.download_button("💾 Télécharger PDF", data=pdf_bytes, file_name=f"{ref}.pdf"):

        new_row = [
            len(df_f)+1,
            datetime.now().strftime("%d/%m/%Y"),
            ref,
            client,
            total_ht,
            tva,
            ttc,
            d_type
        ]

        df_f = pd.concat([df_f, pd.DataFrame([new_row], columns=df_f.columns)], ignore_index=True)
        save_data("Facturations", df_f)

        if d_type == "FACTURE":
            update_stock(st.session_state.cart)

        st.session_state.cart = []
        st.success("✅ تم بنجاح")
        st.rerun()
