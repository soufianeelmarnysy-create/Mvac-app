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
from streamlit_gsheets import GSheetsConnection

# 1. إعدادات الصفحة
st.set_page_config(page_title="M-VAC PRO", layout="wide")

st.title("📄 M-VAC PRO : Gestion Commerciale")

# 2. الربط مع Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"❌ مشكل في الاتصال بـ Google Sheets: {e}")

# دالة جلب البيانات مع معالجة الأخطاء باش متبقاش الصفحة بيضاء
def load_data(sheet_name):
    try:
        # ttl=0 باش يجيب البيانات دقة بدقة
        df = conn.read(worksheet=sheet_name, ttl="0m")
        if df is empty or df is None:
            return pd.DataFrame()
        return df
    except Exception as e:
        st.warning(f"⚠️ تنبيه: تعذر قراءة ورقة '{sheet_name}'. تأكد من وجودها.")
        return pd.DataFrame()

# دالة حفظ البيانات
def save_data(sheet_name, df):
    try:
        conn.update(worksheet=sheet_name, data=df)
        st.cache_data.clear()
    except Exception as e:
        st.error(f"❌ فشل حفظ البيانات في {sheet_name}: {e}")

# 3. إدارة سلة التسوق (Session State)
if 'cart' not in st.session_state:
    st.session_state.cart = []

# 4. دالة تحديث المخزون (Update Stock)
def update_gsheets_stock(cart_items):
    df_m = load_data("Materiels")
    if not df_m.empty:
        df_m = df_m.copy().astype(object)
        for item in cart_items:
            # البحث بالسلعة في العمود الثالث (index 2)
            mask = df_m.iloc[:, 2] == item['Désignation']
            idx = df_m[mask].index
            if not idx.empty:
                # تحديث الستوك في العمود الخامس (index 4)
                current_stock = pd.to_numeric(df_m.iloc[idx[0], 4], errors='coerce')
                new_stock = float(current_stock if not pd.isna(current_stock) else 0) - float(item['Qte'])
                df_m.iloc[idx[0], 4] = max(0, new_stock)
        save_data("Materiels", df_m)

# 5. جلب البيانات الأساسية
df_m = load_data("Materiels")
df_c = load_data("Customers")
df_f = load_data("Facturations")

# --- واجهة إضافة السلع ---
st.subheader("🛒 Ajouter Article")

if not df_m.empty:
    # جلب قائمة السلع من العمود C (index 2)
    items_list = df_m.iloc[:, 2].dropna().unique().tolist()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        s_item = st.selectbox("Sélectionner l'Article", items_list)
        # جلب معلومات السلعة المختارة
        row = df_m[df_m.iloc[:, 2] == s_item].iloc[0]
        
        # Stock: E (4), Price: F (5), Unit: D (3)
        p_stock = pd.to_numeric(row.iloc[4], errors='coerce')
        p_price = float(row.iloc[5]) if not pd.isna(row.iloc[5]) else 0.0
        p_unit = str(row.iloc[3])
        
        q = st.number_input("Quantité", min_value=0.1, value=1.0, step=1.0)
        p = st.number_input("Prix HT (DH)", value=p_price)

    with col2:
        st_color = "green" if p_stock > 0 else "red"
        st.markdown(f"""
            <div style='text-align:center; padding:15px; border:2px solid {st_color}; border-radius:15px;'>
                Stock الحالي<br><h2 style='color:{st_color};'>{p_stock}</h2><small>{p_unit}</small>
            </div>
            """, unsafe_allow_html=True)

    if st.button("➕ Ajouter au Panier", use_container_width=True):
        if q > p_stock:
            st.error("❌ Stock insuffisant!")
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
                    "Désignation": s_item, "Unité": p_unit, "Qte": q, "P.U": p, "Total": q * p
                })
            st.rerun()
else:
    st.info("💡 في انتظار تحميل بيانات السلع من Google Sheets...")

# --- عرض السلة والتحكم في الفاتورة ---
if st.session_state.cart:
    st.divider()
    st.subheader("🧾 Panier & Validation")
    st.table(pd.DataFrame(st.session_state.cart))

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        d_type = st.radio("Type de Document", ["DEVIS", "FACTURE"], horizontal=True)
        
        # جلب الزبناء من العمود C (index 2) في ورقة Customers
        list_c = df_c.iloc[:, 2].dropna().unique().tolist() if not df_c.empty else ["Client Standard"]
        s_client = st.selectbox("Choisir le Client", list_c)
        d_ref = st.text_input("Référence", value=f"MVAC-{datetime.now().strftime('%y%m%d%H%M')}")

    with col_v2:
        total_ht = sum(i['Total'] for i in st.session_state.cart)
        ttc = total_ht * 1.2
        st.metric("Total TTC à Payer", f"{ttc:,.2f} DH")

        # --- توليد الـ PDF ---
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(41, 128, 185)
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_font("Arial", 'B', 24)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 20, txt=f"M-VAC SARL - {d_type}", ln=True, align='C')
        
        pdf.ln(25)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, txt=f"Date: {datetime.now().strftime('%d/%m/%Y')} | Ref: {d_ref}", ln=True)
        pdf.cell(0, 8, txt=f"Client: {s_client}", ln=True)
        pdf.ln(10)

        # Header الجدول
        pdf.set_fill_color(41, 128, 185); pdf.set_text_color(255, 255, 255)
        pdf.cell(90, 10, "Designation", 1, 0, 'C', 1)
        pdf.cell(30, 10, "Qte", 1, 0, 'C', 1)
        pdf.cell(30, 10, "P.U", 1, 0, 'C', 1)
        pdf.cell(40, 10, "Total HT", 1, 1, 'C', 1)

        pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", '', 11)
        for item in st.session_state.cart:
            # تنظيف الاسم من أي رموز غريبة
            clean_name = str(item['Désignation']).encode('ascii', 'ignore').decode('ascii')
            pdf.cell(90, 10, clean_name, 1)
            pdf.cell(30, 10, str(item['Qte']), 1, 0, 'C')
            pdf.cell(30, 10, f"{item['P.U']:.2f}", 1, 0, 'C')
            pdf.cell(40, 10, f"{item['Total']:.2f}", 1, 1, 'R')

        pdf.ln(5)
        pdf.set_font("Arial", 'B', 13)
        pdf.cell(150, 12, "TOTAL TTC (TVA 20%) :", 1, 0, 'R')
        pdf.cell(40, 12, f"{ttc:,.2f} DH", 1, 1, 'C')

        # استخراج الـ Bytes بطريقة آمنة لـ Streamlit
        p_out = pdf.output()
        p_bytes = bytes(p_out) if isinstance(p_out, (bytearray, bytes)) else p_out.encode('latin-1')

        if st.download_button(
            label="💾 Valider & Télécharger PDF", 
            data=p_bytes, 
            file_name=f"{d_ref}.pdf", 
            mime="application/pdf", 
            type="primary", 
            use_container_width=True
        ):
            # 1. تحديث سجل الفواتير (Facturations)
            if not df_f.empty:
                new_f = [len(df_f)+1, datetime.now().strftime("%d/%m/%Y"), d_ref, s_client, total_ht, total_ht*0.2, ttc, d_type]
                df_f.loc[len(df_f)] = new_f
                save_data("Facturations", df_f)
            
            # 2. تحديث الستوك (فقط في حالة الفاتورة)
            if d_type == "FACTURE":
                update_gsheets_stock(st.session_state.cart)
            
            st.session_state.cart = []
            st.success("✅ العملية تمت بنجاح!")
            st.rerun()

    if st.button("🗑️ Vider le panier", use_container_width=True):
        st.session_state.cart = []
        st.rerun()

    # SAFE PDF
    pdf_data = pdf.output(dest='S')
    pdf_bytes = pdf_data if isinstance(pdf_data, bytes) else pdf_data.encode('latin-1')

    st.download_button("📥 Télécharger PDF", pdf_bytes, file_name=f"{ref}.pdf")
