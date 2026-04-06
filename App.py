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
# 📄 5. دالة صفحة الفاتورة المطورة (MVAC PRO EDITION)
# =========================================================

# 1. دالة التحميل السريع (باش التطبيق يولي طاير وما يتبلوكاوش ليك الطلبات)
@st.cache_data(ttl=300) # كيحفظ الداتا 5 دقائق فذاكرة التطبيق
def load_data_fast(sheet_name):
    return load_data(sheet_name)

def show_facturation_page():
    # زواق في العنوان
    st.markdown("<h1 style='text-align: center; color: #005050;'>📄 MVAC SYSTEM - DEVIS & FACTURE</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # 2. تحميل البيانات (بسرعة)
    df_c = load_data_fast("Customers").dropna(how='all')
    df_m = load_data_fast("Materiels").dropna(how='all')
    df_f = load_data_fast("Facturations").dropna(how='all')
    df_d = load_data_fast("Devis").dropna(how='all')

    if 'cart' not in st.session_state: 
        st.session_state.cart = []

    # --- القسم 1: معلومات المستند (Design Pro) ---
    with st.container(border=True):
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            doc_type = st.selectbox("📝 Type", ["DEVIS", "FACTURE"], key="doc_type_final")
        with c2:
            # جلب الكليان من العمود 2 (الاسم/الشركة)
            clients = df_c.iloc[:, 2].dropna().unique().tolist() if not df_c.empty else ["Passager"]
            s_client = st.selectbox("👤 Client", clients, key="client_final")
        with c3:
            d_ref = st.text_input("🔢 Référence", value=f"{doc_type[0]}-{datetime.now().strftime('%d%H%M')}")

    # --- القسم 2: إضافة السلع (بأوتوماتيك الأثمنة) ---
    st.subheader("🛒 Sélection des Articles")
    with st.container(border=True):
        # السلعة في العمود 2 (Index 2)
        articles = df_m.iloc[:, 2].dropna().unique().tolist() if not df_m.empty else []
        sel_art = st.selectbox("🔍 Rechercher un article", [""] + articles, key="article_final")
        
        u_v, s_v, p_v = "", 0.0, 0.0
        if sel_art:
            row = df_m[df_m.iloc[:, 2] == sel_art].iloc[0]
            u_v = str(row.iloc[3])  # الوحدة
            # تحويل آمن للأرقام لتفادي Error الأثمنة
            try:
                s_v = float(str(row.iloc[4]).replace(',', '.').strip())
                p_v = float(str(row.iloc[5]).replace(',', '.').strip())
            except:
                s_v, p_v = 0.0, 0.0

        i1, i2, i3, i4, i5 = st.columns([1, 1, 1, 1, 1.2])
        i1.markdown(f"**Unité:**\n\n{u_v}")
        # تلوين الستوك (أحمر يلا كان قليل)
        stock_color = "red" if s_v <= 5 else "green"
        i2.markdown(f"**Stock:**\n\n<span style='color:{stock_color}; font-weight:bold;'>{s_v}</span>", unsafe_allow_html=True)
        
        q_in = i3.number_input("Qté", min_value=0.1, value=1.0, step=1.0)
        p_in = i4.number_input("Prix HT (DH)", value=p_v)

        if i5.button("➕ Ajouter à la liste", use_container_width=True, type="secondary"):
            if sel_art:
                st.session_state.cart.append({
                    "Désignation": sel_art, 
                    "Unité": u_v, 
                    "Qte": q_in, 
                    "PU_HT": p_in, 
                    "Total": q_in * p_in
                })
                st.toast(f"Ajouté: {sel_art}", icon="✅")
                st.rerun()

    # --- القسم 3: عرض الجدول والحسابات ---
    if st.session_state.cart:
        st.markdown("### 📋 Détails de la commande")
        df_cart = pd.DataFrame(st.session_state.cart)
        
        # عرض الجدول مع زواق
        st.dataframe(df_cart.style.format({"PU_HT": "{:.2f}", "Total": "{:.2f}"}), use_container_width=True)

        # الحسابات الإجمالية
        t_ht = df_cart['Total'].sum()
        t_tva = t_ht * 0.2
        t_ttc = t_ht + t_tva

        col_res1, col_res2 = st.columns([2, 1])
        with col_res2:
            st.markdown(f"""
            <div style="background-color:#f0f2f6; padding:15px; border-radius:10px; border-left: 5px solid #005050;">
                <p style="margin:0;">Total HT: <b>{t_ht:,.2f} DH</b></p>
                <p style="margin:0;">TVA (20%): <b>{t_tva:,.2f} DH</b></p>
                <h3 style="margin:0; color:#005050;">TOTAL TTC: {t_ttc:,.2f} DH</h3>
            </div>
            """, unsafe_allow_html=True)

        # --- القسم 4: الحفظ و الـ PDF ---
        st.markdown("---")
        b1, b2, b3 = st.columns([1, 1, 1])
        
        with b1:
            if st.button("💾 Enregistrer & Valider", type="primary", use_container_width=True):
                target_sheet = "Facturations" if doc_type == "FACTURE" else "Devis"
                # قراءة فريش للحفظ (ماشي من الـ cache)
                existing_df = load_data(target_sheet)
                
                new_row = [len(existing_df)+1, datetime.now().strftime("%d/%m/%Y"), d_ref, s_client, t_ht, t_tva, t_ttc]
                
                # ميزان الأعمدة (Padding)
                if len(new_row) < len(existing_df.columns):
                    new_row += [""] * (len(existing_df.columns) - len(new_row))
                
                new_row_df = pd.DataFrame([new_row], columns=existing_df.columns)
                updated_df = pd.concat([existing_df, new_row_df], ignore_index=True)
                
                if save_data(target_sheet, updated_df):
                    # تحديث الستوك يلا كانت FACTURE
                    if doc_type == "FACTURE":
                        for item in st.session_state.cart:
                            m_idx = df_m[df_m.iloc[:, 2] == item['Désignation']].index[0]
                            df_m.iloc[m_idx, 4] -= item['Qte']
                        save_data("Materiels", df_m)
                    
                    st.cache_data.clear() # مسح الذاكرة باش يبانو التغييرات
                    st.balloons()
                    st.success("✅ Document enregistré avec succès !")

        with b2:
            # زر توليد الـ PDF
            pdf_data = generate_pdf(doc_type, d_ref, s_client, st.session_state.cart, t_ht, t_tva, t_ttc)
            st.download_button("📥 Télécharger PDF", data=pdf_data, file_name=f"{d_ref}.pdf", mime="application/pdf", use_container_width=True)

        with b3:
            if st.button("🔄 Nouveau", use_container_width=True):
                st.session_state.cart = []
                st.rerun()

# --- مناداة الدالة ---
if page == "📄 Devis / Facture":
    show_facturation_page()
