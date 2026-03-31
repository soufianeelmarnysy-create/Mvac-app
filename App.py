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
# =========================================================================================================================================================================
# 📄 5. صفحة الفاتورة المتكاملة (Version Corrigée selon Image)
# =========================================================
else:
    st.title("📄 Gestion des Factures & Devis")
    
    # 1. جلب البيانات
    df_c = load_data("Customers")
    df_m = load_data("Materiels")
    df_f = load_data("Facturations")

    # تنظيف الأعمدة (تحسباً لأي فراغ خفي)
    for df in [df_c, df_m, df_f]:
        if not df.empty:
            df.columns = df.columns.str.strip()

    if 'cart' not in st.session_state: 
        st.session_state.cart = []

    # 🔍 2. Recherche (بناءً على عناوين الصورة: Num_Facture, Client, Date...)
    with st.expander("🔍 Recherche dans les archives"):
        if not df_f.empty and 'Num_Facture' in df_f.columns:
            search_list = df_f['Num_Facture'].tolist()[::-1]
            sf = st.selectbox("Document:", ["---"] + search_list, key="search_f_box")
            if sf != "---":
                f_row = df_f[df_f['Num_Facture'] == sf].iloc[0]
                # عرض المعلومات باستعمال أسماء الأعمدة من الصورة
                st.info(f"👤 Client: {f_row.get('Client', 'N/A')} | 📅 Date: {f_row.get('Date', 'N/A')}")
                c_ht, c_tva, c_ttc = st.columns(3)
                c_ht.metric("Total HT", f"{f_row.get('HT', 0)} DH")
                c_tva.metric("TVA", f"{f_row.get('TVA', 0)} DH")
                c_ttc.metric("Total TTC", f"{f_row.get('TTC', 0)} DH")
        else:
            st.info("Aucune donnée dans Facturations.")

    st.markdown("---")

    # 3. التحقق من صفحة السلع (Materiels)
    # ملاحظة: تأكد أن صفحة Materiels فيها أعمدة سميتها: Designation, Unite, Prix
    if df_m.empty:
        st.error("⚠️ La feuille 'Materiels' est vide !")
    else:
        # تحديد أسماء الأعمدة (حاولت نوقعهم بناءً على Facturations)
        # إذا كانت سميتهم بالعربية فـ Materiels، بدلهوم هنا:
        col_item = df_m.columns[0] # كياخد أول عمود كـ Designation
        col_unit = df_m.columns[1] if len(df_m.columns) > 1 else None
        col_price = df_m.columns[2] if len(df_m.columns) > 2 else None

        # 4. إضافة السلع
        with st.container(border=True):
            st.subheader("📦 Ajouter des articles")
            i1, i2, i3, i4 = st.columns([3, 1, 1, 1])
            
            items_list = df_m[col_item].dropna().unique().tolist()
            s_name = i1.selectbox("Article", items_list, key="item_sel")
            
            m_info = df_m[df_m[col_item] == s_name].iloc[0]
            
            s_unit = i2.text_input("Unité", value=str(m_info[col_unit]) if col_unit else "", key=f"u_{s_name}")
            s_qte = i3.number_input("Qté", min_value=0.1, value=1.0, step=1.0, key=f"q_{s_name}")
            s_price = i4.number_input("Prix HT", value=float(m_info[col_price]) if col_price else 0.0, key=f"p_{s_name}")

            if st.button("➕ Ajouter au tableau", use_container_width=True):
                st.session_state.cart.append({
                    "Désignation": s_name,
                    "Unité": s_unit,
                    "Qte": s_qte,
                    "PU_HT": s_price,
                    "Total_HT": s_qte * s_price
                })
                st.rerun()

        # 5. عرض الجدول النهائي
        if st.session_state.cart:
            st.markdown("### 🛒 Tableau Actuel")
            st.table(pd.DataFrame(st.session_state.cart))

            # الحسابات
            sum_ht = sum(item['Total_HT'] for item in st.session_state.cart)
            tva = sum_ht * 0.20
            ttc = sum_ht + tva

            st.write(f"**Total HT:** {sum_ht:,.2f} DH")
            st.error(f"### TOTAL TTC: {ttc:,.2f} DH")

            # 6. الحفظ (بناءً على ترتيب الأعمدة في صورتك)
            if st.button("💾 Enregistrer la Facture", type="primary"):
                new_data = pd.DataFrame([[
                    str(len(df_f)+1),                   # ID
                    datetime.now().strftime("%d/%m/%Y"), # Date
                    f"F{datetime.now().strftime('%y%m%d%H%M')}", # Num_Facture
                    s_client if 's_client' in locals() else "Client", # Client
                    f"{sum_ht:.2f}",                    # HT
                    f"{tva:.2f}",                       # TVA
                    f"{ttc:.2f}"                        # TTC
                ]], columns=df_f.columns.tolist())
                
                if save_data("Facturations", pd.concat([df_f, new_data], ignore_index=True)):
                    st.success("✅ Facture enregistrée !")
                    st.session_state.cart = []
                    st.rerun()



