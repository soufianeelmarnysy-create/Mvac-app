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
# استيراد مكتبة BytesIO ضروري للفيكس ديال PDF
from io import BytesIO

# =========================================================
# 📄 5. صفحة الفاتورة (نسخة الإصلاح النهائي)
# =========================================================
else:
    st.title("📄 Devis / Facture")
    
    df_c = load_data("Customers")
    df_m = load_data("Materiels")
    df_f = load_data("Facturations")

    if 'cart' not in st.session_state: 
        st.session_state.cart = []

    # 1. إعدادات الوثيقة
    with st.sidebar: # درنا هادو فـ Sidebar باش نوفروا المساحة للجدول
        st.header("⚙️ إعدادات")
        d_type = st.selectbox("النوع", ["DEVIS", "FACTURE"], key="dt")
        s_client = st.selectbox("الزبون", df_c['الاسم/الشركة'].tolist() if not df_c.empty else ["خاوي"], key="cl")
        d_num = st.text_input("رقم الوثيقة", value=f"{d_type[:1]}{datetime.now().strftime('%y%m%d%H%M')}")
        remise_pct = st.selectbox("العمولة (%)", [0, 5, 10, 15, 20, 25, 30, 50], key="rm")

    # 2. إضافة السلعة
    with st.container(border=True):
        i1, i2, i3, i4 = st.columns([3, 1, 1, 1])
        s_name = i1.selectbox("اختار السلعة", df_m['السلعة'].tolist() if not df_m.empty else ["خاوي"])
        
        if not df_m.empty:
            m_info = df_m[df_m['السلعة'] == s_name].iloc[0]
            s_unit = i2.text_input("الوحدة", value=m_info['الوحدة'])
            s_qte = i3.number_input("الكمية", min_value=0.1, value=1.0, step=0.5)
            s_price = i4.number_input("الثمن HT", value=float(m_info['ثمن الوحدة']))

            if st.button("➕ إضافة السطر", use_container_width=True):
                st.session_state.cart.append({
                    "Désignation": s_name, "Unité": s_unit, "Qte": s_qte, "P.U": s_price, "Total": s_qte * s_price
                })
                st.rerun()

    # 3. عرض الجدول والحسابات (بشكل يمنع الاختفاء)
    if st.session_state.cart:
        # عرض الجدول في مساحة محدودة (Scrollable)
        st.markdown("### 🛒 السلع المضافة")
        st.dataframe(pd.DataFrame(st.session_state.cart), use_container_width=True, height=250)

        # حساب النتائج
        raw_ht = sum(item['Total'] for item in st.session_state.cart)
        val_remise = raw_ht * (remise_pct / 100)
        net_ht = raw_ht - val_remise
        val_tva = net_ht * 0.20
        total_ttc = net_ht + val_tva

        # عرض الحسابات بشكل أفقي باش ما يهبطوش لتحت بزاف
        c_res1, c_res2, c_res3 = st.columns(3)
        c_res1.metric("Total HT Net", f"{net_ht:,.2f} DH")
        c_res2.metric("TVA (20%)", f"{val_tva:,.2f} DH")
        c_res3.error(f"**TOTAL TTC: {total_ttc:,.2f} DH**")

        # 4. أزرار التحكم والـ PDF (الإصلاح الجديد)
        st.markdown("---")
        b1, b2, b3 = st.columns(3)

        if b1.button("💾 حفظ في Sheet", type="primary", use_container_width=True):
            new_row = pd.DataFrame([[str(len(df_f)+1), datetime.now().strftime("%d/%m/%Y"), d_num, s_client, f"{net_ht:.2f}", f"{val_tva:.2f}", f"{total_ttc:.2f}"]], columns=df_f.columns)
            if save_data("Facturations", pd.concat([df_f, new_row], ignore_index=True)):
                st.success("✅ تم الحفظ!")
                st.session_state.cart = []
                st.rerun()

        if b2.button("📥 تحميل PDF", use_container_width=True):
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, f"MVAC - {d_type} {d_num}", ln=True, align='C')
                pdf.set_font("Arial", '', 12)
                pdf.ln(10)
                pdf.cell(0, 10, f"Client: {s_client} | Date: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
                pdf.ln(5)
                for item in st.session_state.cart:
                    pdf.cell(0, 8, f"- {item['Désignation']} | {item['Qte']} {item['Unité']} | {item['Total']:.2f} DH", ln=True)
                pdf.ln(10)
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, f"TOTAL TTC: {total_ttc:,.2f} DH", ln=True, align='R')
                
                # الطريقة الصحيحة لإخراج الـ PDF في Streamlit
                pdf_output = pdf.output(dest='S').encode('latin-1')
                b64 = base64.b64encode(pdf_output).decode()
                href = f'<a href="data:application/pdf;base64,{b64}" download="{d_num}.pdf" style="text-decoration:none;"><div style="background-color:green;color:white;padding:10px;text-align:center;border-radius:5px;">إضغط هنا لتحميل الفاتورة PDF 📥</div></a>'
                st.markdown(href, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error PDF: {e}")

        if b3.button("🔄 إفراغ", use_container_width=True):
            st.session_state.cart = []
            st.rerun()
