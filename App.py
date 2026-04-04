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
import io

# --- 1. إعدادات الذاكرة (للحفاظ على السلة) ---
if 'cart' not in st.session_state: st.session_state.cart = []

# --- 2. دالة تنقيص الستوك (العمود E هو Index 4) ---
def update_gsheets_stock(cart_items):
    df_m = load_data("Materiels")
    if df_m is not None:
        df_m = df_m.copy()
        # تحويل عمود الكمية لرقمي بزز لتفادي TypeError
        df_m.iloc[:, 4] = pd.to_numeric(df_m.iloc[:, 4], errors='coerce').fillna(0)
        
        for item in cart_items:
            # البحث بالاسم في العمود C
            idx = df_m[df_m.iloc[:, 2] == item['Désignation']].index
            if not idx.empty:
                current_s = float(df_m.iloc[idx[0], 4])
                new_s = current_s - float(item['Qte'])
                # التعديل باستعمال .at لضمان الدقة
                df_m.at[idx[0], df_m.columns[4]] = new_s
        save_data("Materiels", df_m)

# --- 3. واجهة اختيار السلعة ---
st.title("📄 M-VAC PRO : Gestion Commerciale")

df_m = load_data("Materiels")
df_c = load_data("Customers")
df_f = load_data("Facturations")

# التأكد من أن جدول السلع مقروء وفيه الأعمدة الكافية
if df_m is not None and len(df_m.columns) >= 6:
    items_list = df_m.iloc[:, 2].dropna().unique().tolist()
    
    st.markdown('<div style="background:#f9f9f9; padding:20px; border-radius:15px; border:1px solid #ddd;">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    
    with col1:
        s_item = st.selectbox("Sélectionner l'Article", items_list)
        row = df_m[df_m.iloc[:, 2] == s_item].iloc[0]
        # جلب الستوك (E) والثمن (F)
        st.session_state.p_stock = pd.to_numeric(row.iloc[4], errors='coerce')
        st.session_state.p_price = float(row.iloc[5])
        st.session_state.p_unit = str(row.iloc[3])
    
    with col2:
        st_color = "green" if st.session_state.p_stock > 0 else "red"
        st.markdown(f"<div style='text-align:center;'>Stock<br><h2 style='color:{st_color};'>{st.session_state.p_stock}</h2></div>", unsafe_allow_html=True)

    with st.form("add_to_cart"):
        c1, c2, c3 = st.columns(3)
        u = c1.text_input("Unité", value=st.session_state.p_unit, disabled=True)
        p = c2.number_input("Prix HT (DH)", value=st.session_state.p_price)
        q = c3.number_input("Quantité", min_value=0.1, value=1.0)
        
        if st.form_submit_button("➕ Ajouter au Panier", use_container_width=True):
            if q > st.session_state.p_stock:
                st.error(f"❌ Stock insuffisant! (Max: {st.session_state.p_stock})")
            else:
                st.session_state.cart.append({
                    "Désignation": s_item, "Unité": u, "Qte": q, "P.U": p, "Total": q * p
                })
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. معالجة السلة والـ PDF والـ Valider ---
if st.session_state.cart:
    st.write("### 🛒 Votre Panier")
    st.table(pd.DataFrame(st.session_state.cart))
    
    # جلب الزبناء من العمود C (Index 2)
    if df_c is not None and len(df_c.columns) >= 3:
        list_clients = df_c.iloc[:, 2].dropna().unique().tolist()
    else:
        list_clients = ["Client Standard"]

    col_a, col_b = st.columns(2)
    with col_a:
        d_type = st.radio("Type", ["DEVIS", "FACTURE"], horizontal=True)
        s_client = st.selectbox("Client", list_clients)
        d_ref = st.text_input("Référence", value=f"MVAC-{datetime.now().strftime('%y%m%H%M')}")
    
    with col_b:
        total_ht = sum(i['Total'] for i in st.session_state.cart)
        ttc = total_ht * 1.20
        st.metric("Total à Payer (TTC)", f"{ttc:,.2f} DH")

        # صنع الـ PDF (حل مشكلة AttributeError)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt=f"M-VAC - {d_type}", ln=True, align='C')
        pdf.set_font("Arial", '', 12)
        pdf.cell(200, 10, txt=f"Client: {s_client} | Ref: {d_ref}", ln=True)
        pdf.ln(10)
        
        # جدول السلع في الـ PDF
        pdf.cell(100, 10, "Designation", 1); pdf.cell(40, 10, "Qte", 1); pdf.cell(50, 10, "Total HT", 1, 1)
        for item in st.session_state.cart:
            pdf.cell(100, 10, str(item['Désignation']), 1)
            pdf.cell(40, 10, str(item['Qte']), 1)
            pdf.cell(50, 10, f"{item['Total']:.2f}", 1, 1)
        
        pdf_raw = pdf.output()
        pdf_bytes = bytes(pdf_raw) if not isinstance(pdf_raw, str) else pdf_raw.encode('latin-1')

        # زر الحفظ والتحميل الموحد
        if st.download_button(
            label="💾 Valider & Télécharger PDF",
            data=pdf_bytes,
            file_name=f"{d_ref}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        ):
            # حفظ في سجل الفواتير
            new_f = [len(df_f)+1, datetime.now().strftime("%d/%m/%Y"), d_ref, s_client, total_ht, total_ht*0.2, ttc, d_type]
            save_data("Facturations", pd.concat([df_f, pd.DataFrame([new_f], columns=df_f.columns[:8])], ignore_index=True))
            
            # تنقيص الستوك فقط إذا اختار FACTURE
            if d_type == "FACTURE":
                update_gsheets_stock(st.session_state.cart)
            
            st.session_state.cart = [] 
            st.success("✅ Opération terminée avec succès!")
            st.rerun()

    if st.button("🗑️ Vider le panier"):
        st.session_state.cart = []
        st.rerun()
