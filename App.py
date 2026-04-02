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
import base64

# --- صفحة Devis / Facture ---
if page == "📄 Devis / Facture":
    st.title("📄 Devis / Facture")
    
    # 1. جلب البيانات
    df_c = load_data("Customers")
    df_m = load_data("Materiels")
    df_f = load_data("Facturations")

    # تهيئة الذاكرة (Session State)
    if 'cart' not in st.session_state: st.session_state.cart = []
    
    # --- دالة التحديث التلقائي (معدلة باش تخدم فـ أول لود) ---
    def sync_details():
        if df_m is not None and not df_m.empty:
            try:
                # كنقلبو على السلعة اللي كاينا دابا فـ السلكت
                selected_name = st.session_state.p_item_select
                mask = df_m.iloc[:, 2] == selected_name
                if mask.any():
                    item_row = df_m[mask].iloc[0]
                    # تحديث القيم مباشرة فـ الـ session_state
                    st.session_state.p_unit = str(item_row.iloc[3]) if pd.notnull(item_row.iloc[3]) else ""
                    st.session_state.p_price = float(item_row.iloc[5]) if pd.notnull(item_row.iloc[5]) else 0.0
            except:
                pass

    # لستة السلع (ضرورية باش نعرفو أول عنصر)
    items_list = df_m.iloc[:, 2].dropna().tolist() if df_m is not None else []

    # تصحيح الـ Load الأول: يلا كانت الذاكرة خاوية، نعمروها بأول سلعة فـ اللستة
    if 'p_unit' not in st.session_state or st.session_state.p_unit == "":
        if items_list:
            first_item = df_m[df_m.iloc[:, 2] == items_list[0]].iloc[0]
            st.session_state.p_unit = str(first_item.iloc[3])
            st.session_state.p_price = float(first_item.iloc[5])

    # --- PART 1: إضافة السلعة (هي الأولى دابا) ---
    with st.container(border=True):
        st.subheader("📦 إضافة السلع")
        i1, i2, i3, i4 = st.columns([3, 1, 1, 1])
        
        # السلكت كيعيط لـ sync_details فاش كيتبدل
        s_name = i1.selectbox("اختار السلعة", items_list, key="p_item_select", on_change=sync_details)
        
        # الحقول كياخدو القيمة من session_state مباشرة
        s_unit = i2.text_input("الوحدة", key="p_unit")
        s_qte = i3.number_input("الكمية", min_value=0.1, value=1.0, step=1.0)
        s_price = i4.number_input("الثمن HT", key="p_price")

        if st.button("➕ إضافة للسلة", use_container_width=True):
            if s_name:
                st.session_state.cart.append({
                    "Désignation": s_name, "Unité": s_unit, "Qte": s_qte, "P.U HT": s_price, "Total HT": s_qte * s_price
                })
                st.rerun()

    # --- PART 2: معلومات الوثيقة (الزبون والرقم) ---
    with st.expander("📝 معلومات الفاتورة / الزبون", expanded=True):
        c1, c2, c3 = st.columns([1, 2, 1])
        d_type = c1.selectbox("النوع", ["DEVIS", "FACTURE"], key="p_type")
        clients_list = df_c.iloc[:, 1].dropna().tolist() if df_c is not None else ["Client"]
        s_client = c2.selectbox("الزبون", clients_list, key="p_client")
        last_id = len(df_f) + 1 if df_f is not None else 1
        d_num = c3.text_input("رقم الوثيقة", value=f"D{datetime.now().strftime('%y%m')}{str(last_id).zfill(2)}", key="p_num")

    # --- PART 3: السلة والعمليات ---
    if st.session_state.cart:
        st.markdown("---")
        st.subheader("🛒 السلع المضافة")
        for idx, item in enumerate(st.session_state.cart):
            col_txt, col_del = st.columns([9, 1])
            col_txt.info(f"✅ **{item['Désignation']}** | {item['Qte']} {item['Unité']} x {item['P.U HT']} = **{item['Total HT']:.2f} DH**")
            if col_del.button("❌", key=f"del_{idx}"):
                st.session_state.cart.pop(idx)
                st.rerun()

        total_ht = sum(i['Total HT'] for i in st.session_state.cart)
        tva = total_ht * 0.20
        ttc = total_ht + tva
        st.success(f"### Total TTC: {ttc:,.2f} DH")

        # تسجيل وحفظ
        if st.button("💾 تسجيل الوثيقة وتحميل PDF 📥", type="primary", use_container_width=True):
            try:
                articles_summary = ", ".join([f"{i['Désignation']} (x{i['Qte']})" for i in st.session_state.cart])
                new_entry = [str(last_id), datetime.now().strftime("%d/%m/%Y"), d_num, s_client, 
                             f"{total_ht:.2f}", f"{tva:.2f}", f"{ttc:.2f}", d_type, articles_summary]
                
                new_row_df = pd.DataFrame([new_entry], columns=df_f.columns)
                if save_data("Facturations", pd.concat([df_f, new_row_df], ignore_index=True)):
                    
                    # إنشاء PDF
                    pdf = FPDF()
                    pdf.add_page()
                    try: pdf.image('mvac_logo.png', 10, 8, 35)
                    except: pass
                    
                    pdf.set_font("Arial", 'B', 16); pdf.set_text_color(0, 102, 204)
                    pdf.set_xy(50, 15); pdf.cell(0, 10, "STE M-VAC SARL AU", ln=True)
                    
                    pdf.set_font("Arial", 'B', 12); pdf.set_text_color(0, 0, 0)
                    pdf.set_xy(140, 35); pdf.cell(60, 7, f"{d_type} N: {d_num}", ln=True, align='R')
                    
                    pdf.set_xy(10, 55); pdf.cell(0, 10, f"Client: {s_client}", ln=True)
                    
                    pdf.ln(10); pdf.set_fill_color(230, 230, 230)
                    pdf.cell(90, 10, "Designation", 1, 0, 'C', True)
                    pdf.cell(20, 10, "U", 1, 0, 'C', True)
                    pdf.cell(20, 10, "Qte", 1, 0, 'C', True)
                    pdf.cell(30, 10, "P.U HT", 1, 0, 'C', True)
                    pdf.cell(30, 10, "Total", 1, 1, 'C', True)
                    
                    for i in st.session_state.cart:
                        pdf.cell(90, 8, str(i['Désignation']), 1)
                        pdf.cell(20, 8, str(i['Unité']), 1, 0, 'C')
                        pdf.cell(20, 8, str(i['Qte']), 1, 0, 'C')
                        pdf.cell(30, 8, f"{i['P.U HT']:.2f}", 1, 0, 'C')
                        pdf.cell(30, 8, f"{i['Total HT']:.2f}", 1, 1, 'C')
                    
                    pdf.ln(5); pdf.set_font("Arial", 'B', 12)
                    pdf.cell(130, 10, "TOTAL TTC (DH):", 0, 0, 'R')
                    pdf.cell(60, 10, f"{ttc:,.2f}", 1, 1, 'C', True)

                    pdf_bytes = pdf.output(dest='S').encode('latin-1')
                    b64 = base64.b64encode(pdf_bytes).decode()
                    href = f'<a href="data:application/pdf;base64,{b64}" download="{d_num}.pdf" style="text-decoration:none;"><button style="width:100%;background-color:#28a745;color:white;padding:15px;border-radius:10px;border:none;cursor:pointer;font-weight:bold;">📥 تحميل الملف الآن</button></a>'
                    st.markdown(href, unsafe_allow_html=True)
                    st.session_state.cart = []
                    st.success("✅ تم تسجيل الفاتورة بنجاح!")
            except Exception as e:
                st.error(f"⚠️ خطأ: {e}")
