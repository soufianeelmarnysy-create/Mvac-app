import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from fpdf import FPDF
import base64

# ==========================================
# ⚙️ 1. الإعدادات والربط (مرة واحدة فقط)
# ==========================================
st.set_page_config(page_title="MVAC Pro System", layout="wide", page_icon="❄️")

conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMl791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

# أسماء الأعمدة الموحدة
COLS_C = ["ID", "النوع", "الاسم/الشركة", "ICE", "RIB", "العنوان", "الهاتف"]
COLS_M = ["ID", "المرجع", "السلعة", "الوحدة", "الكمية", "ثمن الوحدة"]

def load_data(sheet_name):
    try:
        st.cache_data.clear()
        df = conn.read(spreadsheet=SHEET_URL, worksheet=sheet_name, ttl=0)
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip()
            df = df.fillna("").astype(str).replace(r'\.0$', '', regex=True)
            return df
        return pd.DataFrame()
    except: return pd.DataFrame()

def save_data(sheet_name, df):
    try:
        conn.update(spreadsheet=SHEET_URL, worksheet=sheet_name, data=df)
        return True
    except Exception as e:
        st.error(f"❌ عطب في الحفظ: {e}")
        return False

# ==========================================
# 🧭 2. المنيو الجانبي
# ==========================================
with st.sidebar:
    st.title("❄️ MVAC SYSTEM")
    page = st.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 إدارة السلعة", "📄 إنشاء Devis/Facture"])
    st.markdown("---")
    st.info("SOUFIANE - Pro Edition v2.5")

# ==========================================
# 👥 3. صفحة إدارة الزبناء
# ==========================================
if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء (Customers)")
    df_c = load_data("Customers")

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
                    if save_data("Customers", pd.concat([df_c, new_row], ignore_index=True)):
                        st.success("✅ تم الحفظ!"); st.rerun()

    search = st.text_input("🔍 قلب على كليان...")
    df_f = df_c[df_c['الاسم/الشركة'].str.contains(search, case=False, na=False)] if not df_c.empty else df_c
    st.dataframe(df_f, use_container_width=True)

# ==========================================
# 📦 4. صفحة إدارة السلعة
# ==========================================
elif page == "📦 إدارة السلعة":
    st.title("📦 إدارة السلعة (Materiels)")
   st.title("📦 إدارة السلعة (Materiels)")

df_m = load_data()

# --- أ: إضافة سلعة جديدة (Ajouter) ---
with st.expander("➕ إضافة سلعة جديدة"):
    with st.form("form_add_mat", clear_on_submit=True):
        m1, m2, m3 = st.columns(3)
        with m1:
            ref = st.text_input("🔢 المرجع (Ref)")
            des = st.text_input("📝 السلعة (Désignation) *")
        with m2:
            uni = st.selectbox("📏 الوحدة", ["U", "M", "M2", "ML", "Kg", "Ens"])
            qte = st.text_input("🔢 الكمية (Qte)", value="0")
        with m3:
            pri = st.text_input("💰 ثمن الوحدة (P.U)")
        
        if st.form_submit_button("حفظ السلعة ✅"):
            if des:
                # حساب ID جديد
                current_max = 0
                if not df_m.empty:
                    ids = pd.to_numeric(df_m["ID"], errors='coerce').fillna(0)
                    current_max = int(ids.max())
                new_id = str(current_max + 1)
                
                # ✅ تصحيح الخطأ هنا: استعملنا COLS_M
                new_row = pd.DataFrame([[new_id, ref, des, uni, qte, pri]], columns=COLS_M)
                df_updated = pd.concat([df_m, new_row], ignore_index=True)
                if save_data(df_updated):
                    st.success("✅ تم الحفظ بنجاح!")
                    st.rerun()
            else:
                st.warning("المرجو إدخال اسم السلعة!")

st.markdown("---")

# --- ب: البحث (Recherche) ---
search = st.text_input("🔍 قلب بسمية السلعة أو المرجع...", placeholder="مثال: Tube, Climatiseur...")
df_filtered = df_m[df_m['السلعة'].str.contains(search, case=False, na=False) | 
                   df_m['المرجع'].str.contains(search, case=False, na=False)]

# --- ج: عرض السلعة (Cards) ---
if not df_filtered.empty:
    for index, row in df_filtered.iterrows():
        with st.container(border=True):
            col_info, col_btns = st.columns([3, 1])
            
            with col_info:
                st.markdown(f"### 📦 {row['السلعة']}")
                st.write(f"🔢 **Ref:** `{row['المرجع']}` | 📏 **Unité:** `{row['الوحدة']}` | 🔢 **Qte:** `{row['الكمية']}`")
                st.markdown(f"💰 **Prix Unit:** <span style='color:#00ff00; font-size:18px; font-weight:bold;'>{row['ثمن الوحدة']} DH</span>", unsafe_allow_html=True)
            
            with col_btns:
                st.write("")
                if st.button(f"📝 تعديل", key=f"ed_{row['ID']}"):
                    st.session_state[f"edit_m_{row['ID']}"] = True
                if st.button(f"🗑️ حذف", key=f"dl_{row['ID']}"):
                    st.session_state[f"del_m_{row['ID']}"] = True

            # --- نافذة التعديل ---
            if st.session_state.get(f"edit_m_{row['ID']}", False):
                with st.container(border=True):
                    st.info(f"📝 تعديل: {row['السلعة']}")
                    e1, e2, e3 = st.columns(3)
                    with e1:
                        n_ref = st.text_input("المرجع", value=row['المرجع'], key=f"r_{row['ID']}")
                        n_des = st.text_input("السلعة", value=row['السلعة'], key=f"s_{row['ID']}")
                    with e2:
                        n_uni = st.selectbox("الوحدة", ["U", "M", "M2", "ML", "Kg", "Ens"], 
                                             index=["U", "M", "M2", "ML", "Kg", "Ens"].index(row['الوحدة']) if row['الوحدة'] in ["U", "M", "M2", "ML", "Kg", "Ens"] else 0,
                                             key=f"u_{row['ID']}")
                        n_qte = st.text_input("الكمية", value=row['الكمية'], key=f"q_{row['ID']}")
                    with e3:
                        n_pri = st.text_input("ثمن الوحدة", value=row['ثمن الوحدة'], key=f"p_{row['ID']}")
                    
                    be1, be2 = st.columns(2)
                    with be1:
                        if st.button("تحديث 💾", key=f"up_{row['ID']}", type="primary"):
                            df_m.loc[index] = [row['ID'], n_ref, n_des, n_uni, n_qte, n_pri]
                            if save_data(df_m):
                                st.session_state[f"edit_m_{row['ID']}"] = False
                                st.rerun()
                    with be2:
                        if st.button("إلغاء ❌", key=f"cn_{row['ID']}"):
                            st.session_state[f"edit_m_{row['ID']}"] = False
                            st.rerun()

            # --- نافذة الحذف ---
            if st.session_state.get(f"del_m_{row['ID']}", False):
                st.warning(f"⚠️ واش بغيتي تمسح **{row['السلعة']}**؟")
                b_del1, b_del2 = st.columns(2)
                with b_del1:
                    if st.button("نعم، مسح ✅", key=f"y_{row['ID']}"):
                        df_m = df_m.drop(index)
                        if save_data(df_m):
                            st.session_state[f"del_m_{row['ID']}"] = False
                            st.rerun()
                with b_del2:
                    if st.button("لا ❌", key=f"n_{row['ID']}"):
                        st.session_state[f"del_m_{row['ID']}"] = False
                        st.rerun()
else:
    st.info("ماكاين حتى سلعة بهاد السمية.")

    st.dataframe(df_m, use_container_width=True)

# ==========================================
# 📄 5. صفحة إنشاء الفاتورة (الجديدة)
# ==========================================
else:
    st.title("📄 إنشاء Devis / Facture")
    df_c = load_data("Customers")
    df_m = load_data("Materiels")

    if not df_c.empty and not df_m.empty:
        # 1. الرأس
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 2, 1])
            d_type = col1.selectbox("النوع:", ["DEVIS", "FACTURE"])
            client_name = col2.selectbox("اختار الزبون:", df_c["الاسم/الشركة"].unique())
            d_num = col3.text_input("N° الوثيقة:", value="A0045")

        # 2. إضافة الأسطر
        if 'items' not in st.session_state: st.session_state.items = []

        with st.container(border=True):
            st.subheader("🛒 إضافة سلعة")
            i1, i2, i3 = st.columns([3, 1, 1])
            sel_mat = i1.selectbox("اختار السلعة من المخزن:", df_m["السلعة"].unique())
            qte_in = i2.number_input("الكمية:", min_value=1, value=1)
            if i3.button("➕ إضافة للجدول"):
                m_info = df_m[df_m["السلعة"] == sel_mat].iloc[0]
                p_u = float(str(m_info["ثمن الوحدة"]).replace(',', '.').strip() or 0)
                st.session_state.items.append({
                    "Désignation": sel_mat, "Unité": m_info["الوحدة"],
                    "Qte": qte_in, "P.U HT": p_u, "Total": qte_in * p_u
                })
                st.rerun()

        # 3. عرض الجدول
        if st.session_state.items:
            df_inv = pd.DataFrame(st.session_state.items)
            st.table(df_inv)
            
            if st.button("🗑️ مسح الجدول"):
                st.session_state.items = []; st.rerun()

            # 4. الحسابات
            brut_ht = df_inv["Total"].sum()
            tva = brut_ht * 0.20
            ttc = brut_ht + tva

            c_total1, c_total2 = st.columns([2, 1])
            with c_total2:
                st.write(f"Total HT: **{brut_ht:,.2f} DH**")
                st.write(f"TVA (20%): **{tva:,.2f} DH**")
                st.error(f"### TOTAL TTC: {ttc:,.2f} DH")

            # 5. زر تحميل PDF (بسيط)
            if st.button("📥 تحميل PDF"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, f"MVAC - {d_type} N {d_num}", ln=True, align='C')
                pdf.set_font("Arial", '', 12)
                pdf.cell(0, 10, f"Client: {client_name}", ln=True)
                pdf.cell(0, 10, f"Date: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
                pdf.ln(10)
                for item in st.session_state.items:
                    pdf.cell(0, 10, f"- {item['Désignation']}: {item['Qte']} x {item['P.U HT']} = {item['Total']} DH", ln=True)
                
                pdf_output = pdf.output(dest='S').encode('latin-1')
                b64 = base64.b64encode(pdf_output).decode()
                href = f'<a href="data:application/pdf;base64,{b64}" download="{d_type}_{d_num}.pdf">اضغط هنا لتحميل الملف 📄</a>'
                st.markdown(href, unsafe_allow_html=True)
    else:
        st.warning("⚠️ دخل الزبناء والسلعة هو الأول!")
