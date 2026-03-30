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
# =========================================================
else:
    st.title("📄 Devis / Facture")
    df_c = load_data("Customers")
    df_m = load_data("Materiels")

    import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import base64

# --- دالة توليد PDF ---
def generate_pdf(client_info, items, totals, doc_type, doc_num):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"MVAC - {doc_type}", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Document N: {doc_num} | Date: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.cell(0, 10, f"Client: {client_info}", ln=True)
    pdf.ln(10)
    
    # الجدول
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(80, 10, "Designation", 1, 0, 'C', 1)
    pdf.cell(25, 10, "Unite", 1, 0, 'C', 1)
    pdf.cell(25, 10, "Qte", 1, 0, 'C', 1)
    pdf.cell(30, 10, "P.U HT", 1, 0, 'C', 1)
    pdf.cell(30, 10, "Total", 1, 1, 'C', 1)
    
    for item in items:
        pdf.cell(80, 10, str(item['Désignation']), 1)
        pdf.cell(25, 10, str(item['Unité']), 1, 0, 'C')
        pdf.cell(25, 10, str(item['Qte']), 1, 0, 'C')
        pdf.cell(30, 10, f"{item['P.U']:,.2f}", 1, 0, 'C')
        pdf.cell(30, 10, f"{item['Total_Line']:,.2f}", 1, 1, 'C')
    
    pdf.ln(5)
    pdf.cell(0, 10, f"Total HT: {totals['HT']:,.2f} DH", ln=True, align='R')
    pdf.cell(0, 10, f"Remise ({totals['Remise_P']}%): -{totals['Remise_Val']:,.2f} DH", ln=True, align='R')
    pdf.cell(0, 10, f"TVA (20%): {totals['TVA']:,.2f} DH", ln=True, align='R')
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"TOTAL TTC: {totals['TTC']:,.2f} DH", ln=True, align='R')
    
    return pdf.output(dest='S').encode('latin-1')

# --- الصفحة الرئيسية ---
def show_facturation_page():
    st.title("📄 إنشاء Devis / Facture")
    
    # 1. جلب البيانات
    df_c = load_data("Customers")
    df_m = load_data("Materiels")
    df_f = load_data("Facturations")

    if df_c.empty or df_m.empty:
        st.warning("⚠️ خاصك تعمر الكليان والسلعة هوما اللولين!")
        return

    # 2. معلومات الوثيقة
    with st.container(border=True):
        c1, c2, c3 = st.columns([1, 2, 1])
        doc_type = c1.selectbox("نوع الوثيقة", ["DEVIS", "FACTURE"])
        
        # البحث عن الكليان (Search)
        search_c = c2.text_input("🔍 قلب على كليان...")
        filtered_clients = df_c[df_c['الاسم/الشركة'].str.contains(search_c, case=False)] if search_c else df_c
        selected_client = c2.selectbox("اختار الكليان", filtered_clients['الاسم/الشركة'].tolist())
        
        doc_num = c3.text_input("رقم الوثيقة", value=f"{doc_type[:1]}{datetime.now().strftime('%y%m%d%H%M')}")

    # 3. إدارة السلع (Panier)
    if 'cart' not in st.session_state: st.session_state.cart = []

    with st.container(border=True):
        st.subheader("📦 إضافة السلعة")
        i1, i2, i3, i4 = st.columns([3, 1, 1, 1])
        
        # البحث عن السلعة
        search_m = i1.text_input("🔍 قلب على السلعة...")
        filtered_m = df_m[df_m['السلعة'].str.contains(search_m, case=False)] if search_m else df_m
        s_item_name = i1.selectbox("السلعة المختارة", filtered_m['السلعة'].tolist())
        
        # جلب معلومات السلعة المختارة تلقائياً
        item_info = df_m[df_m['السلعة'] == s_item_name].iloc[0]
        s_unit = i2.text_input("الوحدة", value=item_info['الوحدة'])
        s_qte = i3.number_input("الكمية", min_value=0.1, value=1.0, step=0.5)
        s_price = i4.number_input("الثمن HT", value=float(item_info['ثمن الوحدة']))

        if st.button("➕ إضافة للجدول", use_container_width=True):
            st.session_state.cart.append({
                "ID_Item": len(st.session_state.cart) + 1,
                "Désignation": s_item_name,
                "Unité": s_unit,
                "Qte": s_qte,
                "P.U": s_price,
                "Total_Line": s_qte * s_price
            })
            st.rerun()

    # 4. عرض الجدول والتعديل
    if st.session_state.cart:
        st.markdown("---")
        df_cart = pd.DataFrame(st.session_state.cart)
        
        # عرض الجدول مع زر المسح لكل سطر
        for idx, row in df_cart.iterrows():
            cols = st.columns([3, 1, 1, 1, 1, 0.5])
            cols[0].write(row['Désignation'])
            cols[1].write(row['Unité'])
            cols[2].write(f"x{row['Qte']}")
            cols[3].write(f"{row['P.U']} DH")
            cols[4].write(f"**{row['Total_Line']:.2f}**")
            if cols[5].button("🗑️", key=f"del_{idx}"):
                st.session_state.cart.pop(idx)
                st.rerun()

        # 5. الحسابات والعمولة (Commission/Remise)
        st.markdown("---")
        res1, res2 = st.columns([2, 1])
        
        with res2:
            remise_pct = st.selectbox("العمولة / تخفيض (%)", [0, 5, 10, 15, 20, 25, 30, 50])
            
            total_ht_raw = sum(item['Total_Line'] for item in st.session_state.cart)
            remise_val = total_ht_raw * (remise_pct / 100)
            total_ht_net = total_ht_raw - remise_val
            tva_val = total_ht_net * 0.20
            total_ttc = total_ht_net + tva_val

            st.write(f"Total HT Brut: {total_ht_raw:,.2f} DH")
            st.write(f"Remise: -{remise_val:,.2f} DH")
            st.write(f"TVA (20%): {tva_val:,.2f} DH")
            st.subheader(f"Total TTC: {total_ttc:,.2f} DH")

        # 6. الحفظ وتحميل PDF
        b1, b2, b3 = st.columns(3)
        
        if b1.button("💾 حفظ في الـ Sheet", type="primary", use_container_width=True):
            new_f = pd.DataFrame([[
                str(len(df_f)+1), datetime.now().strftime("%d/%m/%Y"), doc_num,
                selected_client, f"{total_ht_net:.2f}", f"{tva_val:.2f}", f"{total_ttc:.2f}"
            ]], columns=["ID", "Date", "Num_Facture", "Client", "HT", "TVA", "TTC"])
            
            if save_data("Facturations", pd.concat([df_f, new_f], ignore_index=True)):
                st.success("✅ تم الحفظ بنجاح!")

        if b2.button("📥 تحميل PDF", use_container_width=True):
            totals = {"HT": total_ht_net, "Remise_P": remise_pct, "Remise_Val": remise_val, "TVA": tva_val, "TTC": total_ttc}
            pdf_data = generate_pdf(selected_client, st.session_state.cart, totals, doc_type, doc_num)
            b64 = base64.b64encode(pdf_data).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="{doc_num}.pdf">إضغط هنا لتحميل الملف 📄</a>'
            st.markdown(href, unsafe_allow_html=True)
            
        if b3.button("🔄 إفراغ", use_container_width=True):
            st.session_state.cart = []
            st.rerun()

# استدعاء الصفحة
if page == "📄 Devis / Facture":
    show_facturation_page()
