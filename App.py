import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from fpdf import FPDF
import base64

# ==========================================
# ⚙️ 1. الإعدادات والربط
# ==========================================
st.set_page_config(page_title="MVAC Pro System", layout="wide", page_icon="❄️")

conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMl791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

COLS_C = ["ID", "النوع", "الاسم/الشركة", "ICE", "RIB", "العنوان", "الهاتف"]
COLS_M = ["ID", "المرجع", "السلعة", "الوحدة", "الكمية", "ثمن الوحدة"]

def load_data(sheet_name, columns):
    try:
        st.cache_data.clear()
        df = conn.read(spreadsheet=SHEET_URL, worksheet=sheet_name, ttl=0)
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip()
            df = df.fillna("").astype(str).replace(r'\.0$', '', regex=True)
            return df[columns]
        return pd.DataFrame(columns=columns)
    except: return pd.DataFrame(columns=columns)

def save_data(sheet_name, df):
    try:
        conn.update(spreadsheet=SHEET_URL, worksheet=sheet_name, data=df)
        return True
    except Exception as e:
        st.error(f"❌ عطب في الحفظ: {e}"); return False

# ==========================================
# 🧭 2. المنيو الجانبي
# ==========================================
with st.sidebar:
    st.title("❄️ MVAC SYSTEM")
    page = st.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 إدارة السلعة", "📄 Devis / Facture"])
    st.info("SOUFIANE - Pro v3.5")

# ==========================================
# 👥 3. صفحة إدارة الزبناء (Full CRUD)
# ==========================================
if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    df_c = load_data("Customers", COLS_C)

    # 1. إضافة (Ajouter)
    with st.expander("➕ إضافة زبون جديد"):
        with st.form("add_client"):
            c1, c2 = st.columns(2)
            with c1:
                t_c = st.selectbox("النوع", ["Société", "Particulier"])
                n_c = st.text_input("الاسم أو الشركة *")
                i_c = st.text_input("ICE")
            with c2:
                te_c = st.text_input("الهاتف")
                a_c = st.text_input("العنوان")
            if st.form_submit_button("حفظ ✅"):
                new_id = str(int(pd.to_numeric(df_c["ID"], errors='coerce').max() + 1)) if not df_c.empty else "1"
                new_row = pd.DataFrame([[new_id, t_c, n_c, i_c, "", a_c, te_c]], columns=COLS_C)
                if save_data("Customers", pd.concat([df_c, new_row], ignore_index=True)): st.rerun()

    # 2. بحث (Recherche)
    search_c = st.text_input("🔍 قلب على كليان بالسمية...")
    df_f = df_c[df_c['الاسم/الشركة'].str.contains(search_c, case=False, na=False)] if search_c else df_c

    # 3. عرض وتعديل وحذف (Update/Delete)
    for idx, row in df_f.iterrows():
        with st.container(border=True):
            col_txt, col_btn = st.columns([4, 1.2])
            col_txt.write(f"👤 **{row['الاسم/الشركة']}** | 📞 {row['الهاتف']} | 🆔 ICE: {row['ICE']}")
            
            b1, b2 = col_btn.columns(2)
            if b1.button("📝 تعديل", key=f"ed_c_{row['ID']}"): st.session_state[f"edit_mode_c_{row['ID']}"] = True
            if b2.button("🗑️ حذف", key=f"del_c_{row['ID']}"):
                if save_data("Customers", df_c.drop(idx)): st.rerun()

            # نافذة التعديل (Modification)
            if st.session_state.get(f"edit_mode_c_{row['ID']}", False):
                with st.form(f"f_ed_c_{row['ID']}"):
                    en = st.text_input("الاسم", value=row['الاسم/الشركة'])
                    et = st.text_input("الهاتف", value=row['الهاتف'])
                    ei = st.text_input("ICE", value=row['ICE'])
                    if st.form_submit_button("تحديث 💾"):
                        df_c.loc[idx, ["الاسم/الشركة", "الهاتف", "ICE"]] = [en, et, ei]
                        if save_data("Customers", df_c):
                            st.session_state[f"edit_mode_c_{row['ID']}"] = False
                            st.rerun()

# ==========================================
# 📦 4. صفحة إدارة السلعة (Full CRUD)
# ==========================================
elif page == "📦 إدارة السلعة":
    st.title("📦 إدارة السلعة")
    df_m = load_data("Materiels", COLS_M)

    # 1. إضافة
    with st.expander("➕ إضافة سلعة"):
        with st.form("add_mat"):
            m1, m2 = st.columns(2)
            with m1:
                ref = st.text_input("المرجع (Ref)")
                des = st.text_input("السلعة *")
            with m2:
                qte = st.text_input("الكمية", value="0")
                pri = st.text_input("الثمن (HT)")
            if st.form_submit_button("حفظ ✅"):
                new_id = str(int(pd.to_numeric(df_m["ID"], errors='coerce').max() + 1)) if not df_m.empty else "1"
                new_row = pd.DataFrame([[new_id, ref, des, "U", qte, pri]], columns=COLS_M)
                if save_data("Materiels", pd.concat([df_m, new_row], ignore_index=True)): st.rerun()

    # 2. بحث
    search_m = st.text_input("🔍 قلب بسمية السلعة...")
    df_fm = df_m[df_m['السلعة'].str.contains(search_m, case=False, na=False)] if search_m else df_m

    # 3. تعديل وحذف السلعة
    for idx, row in df_fm.iterrows():
        with st.container(border=True):
            c_info, c_action = st.columns([4, 1.2])
            c_info.write(f"📦 **{row['السلعة']}** | 🔢 Qte: {row['الكمية']} | 💰 {row['ثمن الوحدة']} DH")
            
            eb, db = c_action.columns(2)
            if eb.button("📝 تعديل", key=f"ed_m_{row['ID']}"): st.session_state[f"edit_mode_m_{row['ID']}"] = True
            if db.button("🗑️ حذف", key=f"del_m_{row['ID']}"):
                if save_data("Materiels", df_m.drop(idx)): st.rerun()

            if st.session_state.get(f"edit_mode_m_{row['ID']}", False):
                with st.form(f"f_ed_m_{row['ID']}"):
                    en_des = st.text_input("السلعة", value=row['السلعة'])
                    en_qte = st.text_input("الكمية", value=row['الكمية'])
                    en_pri = st.text_input("الثمن", value=row['ثمن الوحدة'])
                    if st.form_submit_button("تحديث 💾"):
                        df_m.loc[idx, ["السلعة", "الكمية", "ثمن الوحدة"]] = [en_des, en_qte, en_pri]
                        if save_data("Materiels", df_m):
                            st.session_state[f"edit_mode_m_{row['ID']}"] = False
                            st.rerun()

# ==========================================
# 📄 5. صفحة Devis / Facture
# ==========================================
else:
    st.title("📄 Devis / Facture")
    df_c = load_data("Customers", COLS_C)
    df_m = load_data("Materiels", COLS_M)

    if not df_c.empty and not df_m.empty:
        col_h1, col_h2 = st.columns(2)
        c_name = col_h1.selectbox("الزبون", df_c["الاسم/الشركة"].tolist())
        d_type = col_h2.selectbox("النوع", ["DEVIS", "FACTURE"])

        if 'cart' not in st.session_state: st.session_state.cart = []

        with st.container(border=True):
            i1, i2, i3 = st.columns([3, 1, 1])
            s_item = i1.selectbox("السلعة", df_m["السلعة"].tolist())
            s_qte = i2.number_input("الكمية", min_value=1, value=1)
            if i3.button("➕"):
                it = df_m[df_m["السلعة"] == s_item].iloc[0]
                p_u = float(it["ثمن الوحدة"] or 0)
                st.session_state.cart.append({"Désignation": s_item, "Qte": s_qte, "P.U": p_u, "Total": s_qte * p_u})
                st.rerun()

        if st.session_state.cart:
            df_inv = pd.DataFrame(st.session_state.cart)
            st.table(df_inv)
            ttc = df_inv["Total"].sum() * 1.2
            st.error(f"TOTAL TTC (20% TVA): {ttc:,.2f} DH")
            
            if st.button("📥 PDF"):
                st.write("PDF Generating...") # هنا كود الـ PDF اللي عطيتهولك فالمثال السابق
            if st.button("🗑️ إفراغ"):
                st.session_state.cart = []; st.rerun()
