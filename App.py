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

# --- 1. إعدادات الصفحة والذاكرة (Session State) ---
st.set_page_config(page_title="M-VAC System", layout="wide")

if 'cart' not in st.session_state: st.session_state.cart = []
if 'p_stock' not in st.session_state: st.session_state.p_stock = 0
if 'p_unit' not in st.session_state: st.session_state.p_unit = ""
if 'p_price' not in st.session_state: st.session_state.p_price = 0.0

# --- 2. دالة جلب بيانات السلعة والستوك (المرحلة 2) ---
def sync_with_stock():
    if 'p_item_select' in st.session_state and 'df_m' in st.session_state:
        sel = st.session_state.p_item_select
        df = st.session_state.df_m
        try:
            # البحث في العمود رقم 3 (Index 2)
            item_row = df[df.iloc[:, 2] == sel].iloc[0]
            
            # تحديث البيانات في الذاكرة
            st.session_state.p_unit = str(item_row.iloc[3])
            st.session_state.p_price = float(item_row.iloc[5])
            
            # جلب الستوك من العمود رقم 7 (Index 6) - تأكد أنه العمود G في Sheets
            val_stock = pd.to_numeric(item_row.iloc[6], errors='coerce')
            st.session_state.p_stock = val_stock if not pd.isna(val_stock) else 0
        except Exception as e:
            st.session_state.p_stock = 0

# --- 3. تصميم الـ PDF الاحترافي (المرحلة 4) ---
class MVAC_PDF(FPDF):
    def header(self):
        # اللوغو ومعلومات الشركة
        try:
            # يلا كان عندك لوغو سميتو logo.png حيد الكومنت من السطر التحتاني
            # self.image('logo.png', 10, 8, 30) 
            pass
        except: pass
        self.set_font('Arial', 'B', 20)
        self.set_text_color(78, 115, 223) # لون أزرق مهني
        self.cell(0, 10, 'M-VAC SARL', ln=True, align='L')
        self.set_font('Arial', 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, 'Installation et Maintenance Industrielle', ln=True, align='L')
        self.ln(10)

    def footer(self):
        self.set_y(-25)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 5, 'M-VAC SARL - ICE: 0023456780000 - RC: 45678 - CNSS: 1234567', 0, 1, 'C')
        self.cell(0, 5, 'Adresse: Fès, Maroc | Tel: +212 600 000 000', 0, 0, 'C')

# --- 4. واجهة البرنامج (الديزاين اللي بـغيتي) ---
st.markdown("""
    <style>
    .main-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 20px; border-top: 5px solid #4e73df; }
    .stMetric { background: #f8f9fc; padding: 15px; border-radius: 10px; border: 1px solid #e3e6f0; }
    </style>
    """, unsafe_allow_html=True)

if page == "📄 Devis / Facture":
    st.title("📄 Gestion des Ventes & Stock")
    
    # تحميل البيانات
    df_c = load_data("Customers")
    df_m = load_data("Materiels")
    df_f = load_data("Facturations")
    st.session_state.df_m = df_m # مهم للـ Sync

    # --- PART 1: اختيار السلعة والستوك ---
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📦 Recherche Article & État du Stock")
    
    if df_m is not None:
        items = df_m.iloc[:, 2].dropna().tolist()
        col_s1, col_s2 = st.columns([3, 1])
        
        s_name = col_s1.selectbox("Sélectionner un article", items, key="p_item_select", on_change=sync_with_stock)
        
        # عرض الستوك بـ ديزاين واضح
        st_val = st.session_state.p_stock
        st_color = "#1cc88a" if st_val > 0 else "#e74a3b"
        col_s2.markdown(f"""
            <div style="text-align:center; padding:10px; background:{st_color}10; border:2px solid {st_color}; border-radius:10px;">
                <p style="margin:0; color:{st_color}; font-weight:bold;">Stock Disponible</p>
                <h2 style="margin:0; color:{st_color};">{st_val}</h2>
            </div>
        """, unsafe_allow_html=True)

        with st.form("mvac_add_form"):
            c1, c2, c3 = st.columns(3)
            u = c1.text_input("Unité", key="p_unit")
            p = c2.number_input("Prix HT (DH)", key="p_price", format="%.2f")
            q = c3.number_input("Quantité voulue", min_value=0.1, value=1.0)
            
            if st.form_submit_button("➕ Ajouter au Panier", use_container_width=True):
                if q > st.session_state.p_stock:
                    st.error(f"❌ المخزون غير كافي! متوفر فقط {st.session_state.p_stock}")
                else:
                    st.session_state.cart.append({"Désignation": s_name, "Unité": u, "Qte": q, "P.U": p, "Total": q*p})
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # --- PART 2: الحسابات والزبون ---
    if st.session_state.cart:
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            st.markdown('<div class="main-card">', unsafe_allow_html=True)
            st.subheader("👤 Infos Document")
            d_type = st.radio("Type de document", ["DEVIS", "FACTURE"], horizontal=True)
            clients = df_c.iloc[:, 2].dropna().tolist() if df_c is not None else ["Standard"]
            s_client = st.selectbox("Client", clients)
            d_ref = st.text_input("Référence N°", value=f"MVAC-{datetime.now().strftime('%y%m%d%H%M')}")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_right:
            st.markdown('<div class="main-card">', unsafe_allow_html=True)
            st.subheader("💰 Récapitulatif")
            total_ht = sum(item['Total'] for item in st.session_state.cart)
            tva = total_ht * 0.20
            ttc = total_ht + tva
            
            st.metric("TOTAL TTC", f"{ttc:,.2f} DH", delta=f"TVA (20%): {tva:,.2f}")
            
            if st.button("💾 Enregistrer & Générer PDF", type="primary", use_container_width=True):
                # 1. الحفظ في Google Sheets (المختصر - المرحلة 3)
                new_row = [len(df_f)+1, datetime.now().strftime("%d/%m/%Y"), d_ref, s_client, total_ht, tva, ttc, d_type]
                save_data("Facturations", pd.concat([df_f, pd.DataFrame([new_row], columns=df_f.columns[:8])], ignore_index=True))
                
                # 2. إنشاء الـ PDF الاحترافي (المرحلة 4)
                pdf = MVAC_PDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, f"{d_type} N°: {d_ref}", ln=True)
                pdf.cell(0, 10, f"Date: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
                pdf.cell(0, 10, f"Doit à: {s_client}", ln=True)
                pdf.ln(5)
                
                # جدول السلع
                pdf.set_fill_color(78, 115, 223); pdf.set_text_color(255, 255, 255)
                pdf.cell(90, 10, "Désignation", 1, 0, 'C', True)
                pdf.cell(20, 10, "Qté", 1, 0, 'C', True)
                pdf.cell(35, 10, "P.U HT", 1, 0, 'C', True)
                pdf.cell(35, 10, "Total HT", 1, 1, 'C', True)
                
                pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", '', 10)
                for item in st.session_state.cart:
                    pdf.cell(90, 10, str(item['Désignation']), 1)
                    pdf.cell(20, 10, str(item['Qte']), 1, 0, 'C')
                    pdf.cell(35, 10, f"{item['P.U']:.2f}", 1, 0, 'C')
                    pdf.cell(35, 10, f"{item['Total']:.2f}", 1, 1, 'C')
                
                pdf.ln(5)
                pdf.set_font("Arial", 'B', 11)
                pdf.cell(145, 10, "Total Hors Taxe (DH) : ", 0, 0, 'R')
                pdf.cell(35, 10, f"{total_ht:,.2f}", 1, 1, 'C')
                pdf.cell(145, 10, "TVA (20%) (DH) : ", 0, 0, 'R')
                pdf.cell(35, 10, f"{tva:,.2f}", 1, 1, 'C')
                pdf.set_fill_color(248, 249, 252)
                pdf.cell(145, 10, "NET A PAYER TTC (DH) : ", 0, 0, 'R', True)
                pdf.cell(35, 10, f"{ttc:,.2f}", 1, 1, 'C', True)

                # زر التحميل
                pdf_output = pdf.output()
                pdf_bytes = pdf_output.encode('latin-1') if isinstance(pdf_output, str) else pdf_output
                b64 = base64.b64encode(pdf_bytes).decode()
                st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="{d_ref}.pdf" style="text-decoration:none;"><button style="width:100%; background-color:#28a745; color:white; padding:12px; border:none; border-radius:10px; cursor:pointer; font-weight:bold;">📥 Télécharger le Document (PDF)</button></a>', unsafe_allow_html=True)
                st.success("✅ Enregistré avec succès !")
                
            if st.button("🗑️ Vider le Panier", use_container_width=True):
                st.session_state.cart = []
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # عرض الجدول في الصفحة
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.table(pd.DataFrame(st.session_state.cart))
        st.markdown('</div>', unsafe_allow_html=True)
