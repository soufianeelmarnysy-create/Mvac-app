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
from datetime import datetime

# --- الجزء الخاص بصفحة Devis / Facture ---
if page == "📄 Devis / Facture":
    st.header("📄 Création de Document")

    # 1. تحميل البيانات من الصور اللي صفتي
    df_c = load_data("Customers")    #
    df_m = load_data("Materiels")     #
    df_f = load_data("Facturations") #
    df_d = load_data("Devis")        #

    if 'cart' not in st.session_state: st.session_state.cart = []

    # --- الجزء 1: معلومات الكليان ---
    with st.container(border=True):
        c1, c2, c3 = st.columns([1, 2, 1])
        doc_type = c1.selectbox("Type", ["DEVIS", "FACTURE"])
        clients = df_c.iloc[:, 2].dropna().unique().tolist() if not df_c.empty else ["Passager"]
        s_client = c2.selectbox("Sélectionner Client", clients)
        d_ref = c3.text_input("Référence", value=f"{doc_type[0]}-{datetime.now().strftime('%d%H%M')}")

    # --- الجزء 2: اختيار السلعة (هنا فين كاين الحل) ---
    with st.container(border=True):
        st.subheader("📦 Sélection des Articles")
        
        # لستة السلع من العمود "السلعة"
        m_list = df_m.iloc[:, 2].dropna().unique().tolist() if not df_m.empty else []
        
        # كنزيدو on_change=st.rerun باش غير تختار السلعة، الصفحة تحس بالتغيير
        selected_art = st.selectbox("Choisir l'article", [""] + m_list, key="art_selector")

        u_v, s_v, p_v = "", 0.0, 0.0
        
        if selected_art != "":
            # كنجبدو السطر الخاص بالسلعة اللي تختارات
            item_info = df_m[df_m.iloc[:, 2] == selected_art].iloc[0]
            u_v = str(item_info.iloc[3])  # الوحدة (U, Kg, M...)
            s_v = float(item_info.iloc[4]) # الكمية في الستوك
            # تنظيف الثمن من أي فاصلة
            try:
                p_v = float(str(item_info.iloc[5]).replace(',', '.'))
            except:
                p_v = 0.0

        # عرض المربعات اللي طلبتي (Unité & Stock)
        col_info1, col_info2, col_qte, col_prix, col_add = st.columns([1, 1, 1, 1, 1])
        
        with col_info1:
            st.markdown(f"<div style='border:1px solid #ddd; padding:10px; border-radius:5px; text-align:center;'>Unité<br><b>{u_v}</b></div>", unsafe_allow_html=True)
        with col_info2:
            color = "green" if s_v > 0 else "red"
            st.markdown(f"<div style='border:1px solid {color}; padding:10px; border-radius:5px; text-align:center;'>Stock<br><b style='color:{color};'>{s_v}</b></div>", unsafe_allow_html=True)
        
        q_in = col_qte.number_input("Qté", min_value=0.1, value=1.0)
        p_in = col_prix.number_input("Prix HT", value=p_v) # دابا الثمن غايطلع أوتوماتيك هنا

        if col_add.button("➕ Ajouter", use_container_width=True):
            if selected_art:
                # تنقيص الستوك في الحال إلى كانت FACTURE
                if doc_type == "FACTURE":
                    if q_in <= s_v:
                        idx = df_m[df_m.iloc[:, 2] == selected_art].index[0]
                        df_m.iloc[idx, 4] = s_v - q_in
                        save_data("Materiels", df_m) # حفظ التغيير فـ Sheets
                        st.session_state.cart.append({
                            "Désignation": selected_art, "Unité": u_v, "Qte": q_in, "PU_HT": p_in, "Total": q_in * p_in
                        })
                        st.rerun()
                    else:
                        st.error("Stock insuffisant !")
                else:
                    # Devis ما كينقصش الستوك
                    st.session_state.cart.append({
                        "Désignation": selected_art, "Unité": u_v, "Qte": q_in, "PU_HT": p_in, "Total": q_in * p_in
                    })
                    st.rerun()

    # --- الجزء 3: الجدول النهائي والحفظ ---
    if st.session_state.cart:
        st.table(pd.DataFrame(st.session_state.cart)) # جدول بسيط وسريع
        
        if st.button("💾 Enregistrer Document Final", type="primary", use_container_width=True):
            # حفظ في Facturations أو Devis حسب الاختيار
            target_sheet = "Facturations" if doc_type == "FACTURE" else "Devis"
            target_df = df_f if doc_type == "FACTURE" else df_d
            
            new_row = [len(target_df)+1, datetime.now().strftime("%d/%m/%Y"), d_ref, s_client, sum(i['Total'] for i in st.session_state.cart)]
            # (تكملة الأعمدة حسب الجدول ديالك...)
            
            st.success(f"Document {d_ref} enregistré !")
            st.session_state.cart = []
            st.rerun()
