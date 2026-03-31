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
# =========================================================
# 📄 صفحة الفاتورة المستقرة - MVAC SYSTEM
# =========================================================
elif page == "📄 Devis / Facture":
    st.title("📄 Devis / Facture")
    
    # 1. جلب البيانات من Google Sheets
    df_c = load_data("Customers")
    df_m = load_data("Materiels")
    df_f = load_data("Facturations")

    # --- تهيئة الذاكرة (Session State) ---
    if 'cart' not in st.session_state: st.session_state.cart = []
    
    # تحذير إيلا كانت البيانات ناقصة
    if df_c.empty or df_m.empty:
        st.error("⚠️ خاصك تعمر الكليان والسلعة هما اللولين!")
    else:
        # 2. إعدادات الوثيقة (ثابتة بـ Key)
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 2, 1])
            # استعملنا key باش الاختيار ما يطرش فاش تزيد السلعة
            d_type = c1.selectbox("النوع", ["DEVIS", "FACTURE"], key="st_doc_type")
            s_client = c2.selectbox("اختار الزبون", df_c['الاسم/الشركة'].tolist(), key="st_client_name")
            d_num = c3.text_input("رقم الوثيقة", value=f"{d_type[:1]}{datetime.now().strftime('%y%m%d%H%M')}", key="st_doc_num")

        # 3. إضافة السلعة
        with st.container(border=True):
            st.subheader("📦 إضافة السلع")
            i1, i2, i3, i4 = st.columns([3, 1, 1, 1])
            s_name = i1.selectbox("اختار السلعة", df_m['السلعة'].tolist(), key="st_item_select")
            
            m_info = df_m[df_m['السلعة'] == s_name].iloc[0]
            s_unit = i2.text_input("الوحدة", value=m_info['الوحدة'], key="st_unit")
            s_qte = i3.number_input("الكمية", min_value=0.1, value=1.0, step=0.5, key="st_qte")
            s_price = i4.number_input("الثمن HT", value=float(m_info['ثمن الوحدة']), key="st_price")

            if st.button("➕ إضافة السطر", use_container_width=True):
                st.session_state.cart.append({
                    "Désignation": s_name, "Unité": s_unit, "Qte": s_qte, "P.U": s_price, "Total": s_qte * s_price
                })
                st.rerun()

        # 4. عرض الجدول + المسح (الذي طلبته)
        if st.session_state.cart:
            st.markdown("### 🛒 السلع المضافة")
            # استعملت dataframe عوض table باش ما ياكلش المساحة بزاف
            st.dataframe(pd.DataFrame(st.session_state.cart), use_container_width=True)

            with st.expander("📝 مراجعة أو مسح أسطر"):
                for idx, item in enumerate(st.session_state.cart):
                    col_t, col_b = st.columns([4, 1])
                    col_t.write(f"{item['Désignation']} ({item['Qte']} {item['Unité']})")
                    if col_b.button("❌", key=f"del_{idx}"):
                        st.session_state.cart.pop(idx)
                        st.rerun()

            # 5. الحسابات (TVA & TTC) - عرض واضح جداً
            st.markdown("---")
            res_l, res_r = st.columns([2, 1])
            with res_r:
                remise_p = st.selectbox("العمولة (%)", [0, 5, 10, 15, 20, 25, 30, 50], key="st_remise")
                
                raw_ht = sum(i['Total'] for i in st.session_state.cart)
                val_rem = raw_ht * (remise_p / 100)
                net_ht = raw_ht - val_rem
                val_tva = net_ht * 0.20
                total_ttc = net_ht + val_tva

                # عرض النتائج بألوان واضحة
                st.write(f"**Total HT Net:** {net_ht:,.2f} DH")
                st.info(f"**TVA (20%):** {val_tva:,.2f} DH")
                st.error(f"### TOTAL TTC: {total_ttc:,.2f} DH")

            # 6. أزرار التحكم (إصلاح الـ PDF)
            st.markdown("---")
            b1, b2, b3 = st.columns(3)

            if b1.button("💾 حفظ في Sheet", type="primary", use_container_width=True):
                # هنا كنعمرو الجدول اللي فيه ID, Date, Num_Facture...
                new_f = pd.DataFrame([[
                    str(len(df_f)+1), datetime.now().strftime("%d/%m/%Y"), d_num,
                    s_client, f"{net_ht:.2f}", f"{val_tva:.2f}", f"{total_ttc:.2f}"
                ]], columns=["ID", "Date", "Num_Facture", "Client", "HT", "TVA", "TTC"])
                if save_data("Facturations", pd.concat([df_f, new_f], ignore_index=True)):
                    st.success("✅ تم الحفظ بنجاح!")
                    st.session_state.cart = []
                    st.rerun()

            if b2.button("📥 تحميل PDF", use_container_width=True):
                try:
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Helvetica", 'B', 16)
                    pdf.cell(0, 10, f"MVAC SYSTEM - {d_type}", ln=True, align='C')
                    pdf.set_font("Helvetica", '', 12)
                    pdf.ln(10)
                    pdf.cell(0, 10, f"Client: {s_client} | Date: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
                    for i in st.session_state.cart:
                        pdf.cell(0, 8, f"- {i['Désignation']} | {i['Qte']} {i['Unité']} | {i['Total']:.2f} DH", ln=True)
                    pdf.ln(5)
                    pdf.set_font("Helvetica", 'B', 14)
                    pdf.cell(0, 10, f"TOTAL TTC: {total_ttc:,.2f} DH", ln=True, align='R')
                    
                    pdf_bytes = pdf.output()
                    if isinstance(pdf_bytes, str): pdf_bytes = pdf_bytes.encode('latin-1')
                    
                    b64 = base64.b64encode(pdf_bytes).decode()
                    st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="{d_num}.pdf" style="text-decoration:none;"><button style="width:100%;background-color:#28a745;color:white;border:none;padding:10px;border-radius:5px;cursor:pointer;">إضغط هنا للتحميل 📥</button></a>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error PDF: {e}")

            if b3.button("🔄 إفراغ الجدول", use_container_width=True):
                st.session_state.cart = []
                st.rerun()
