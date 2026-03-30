import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 🛠️ 1. الإعدادات الأساسية
st.set_page_config(page_title="MVAC Pro System", layout="wide", page_icon="❄️")

# الربط مع Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMl791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

# 🔄 دالة جلب البيانات وتنظيفها (حذف .0 وتحويلها لنصوص)
def load_data(sheet_name):
    try:
        st.cache_data.clear()
        df = conn.read(spreadsheet=SHEET_URL, worksheet=sheet_name, ttl=0)
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip()
            # تنظيف: رد كولشي نصوص ومسح الفاصلة زيرو من الأرقام
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
    page = st.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 إدارة السلعة"])
    st.markdown("---")
    st.info("SOUFIANE - Pro Edition v1.2")

# =========================================================
# 👥 3. صفحة إدارة الزبناء
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
# 📦 4. صفحة إدارة السلعة
# =========================================================
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 🛠️ 1. الإعدادات
st.set_page_config(page_title="إدارة السلعة - MVAC", layout="wide", page_icon="📦")

conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMl791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

# الأعمدة حسب ترتيب Google Sheets اللي عندك
COLS_M = ["ID", "المرجع", "السلعة", "الوحدة", "الكمية", "ثمن الوحدة"]

# 🔄 دالة جلب البيانات وتنقية الأرقام
def load_data():
    try:
        st.cache_data.clear()
        df = conn.read(spreadsheet=SHEET_URL, worksheet="Materiels", ttl=0)
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip()
            # تنظيف: تحويل لنصوص ومسح الفاصلة زيرو (.0)
            df = df.fillna("").astype(str).replace(r'\.0$', '', regex=True)
            return df[COLS_M]
        return pd.DataFrame(columns=COLS_M)
    except:
        return pd.DataFrame(columns=COLS_M)

# 💾 دالة الحفظ
def save_data(df):
    try:
        conn.update(spreadsheet=SHEET_URL, worksheet="Materiels", data=df)
        return True
    except Exception as e:
        st.error(f"❌ خطأ في الحفظ: {e}")
        return False

# =========================================================
# 📦 واجهة إدارة السلعة
# =========================================================
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 🛠️ 1. الإعدادات
st.set_page_config(page_title="إدارة السلعة - MVAC", layout="wide", page_icon="📦")

conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMl791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

# الأعمدة حسب الترتيب اللي عندك فـ Sheets: ID | المرجع | السلعة | الوحدة | الكمية | ثمن الوحدة
COLS_M = ["ID", "المرجع", "السلعة", "الوحدة", "الكمية", "ثمن الوحدة"]

# 🔄 دالة جلب البيانات وتنقية الأرقام
def load_data():
    try:
        st.cache_data.clear()
        df = conn.read(spreadsheet=SHEET_URL, worksheet="Materiels", ttl=0)
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip()
            # تنظيف: تحويل لنصوص ومسح الفاصلة زيرو (.0)
            df = df.fillna("").astype(str).replace(r'\.0$', '', regex=True)
            return df[COLS_M]
        return pd.DataFrame(columns=COLS_M)
    except Exception as e:
        return pd.DataFrame(columns=COLS_M)

# 💾 دالة الحفظ
def save_data(df):
    try:
        conn.update(spreadsheet=SHEET_URL, worksheet="Materiels", data=df)
        return True
    except Exception as e:
        st.error(f"❌ خطأ في الحفظ: {e}")
        return False

# =========================================================
# 📦 واجهة إدارة السلعة
# =========================================================
st.title("📦 إدارة السلعة (Materiels)")

df_m = load_data()

# --- أ: إضافة سلعة جديدة (Ajouter) ---
with st.expander("➕ إضافة سلعة جديدة"):
    with st.form("form_add_mat", clear_on_submit=True):
        m1, m2, m3 = st.columns(3)
        with m1:
            ref = st.text_input("🔢 المرجع (Ref)")
            des = st.text_input("📝 السلعة (Désignation) *")
        with m2:
            uni = st.selectbox("📏 الوحدة", ["U", "M", "M2", "ML", "Kg", "Ens"])
            qte = st.text_input("🔢 الكمية (Qte)", value="0")
        with m3:
            pri = st.text_input("💰 ثمن الوحدة (P.U)")
        
        if st.form_submit_button("حفظ السلعة ✅"):
            if des:
                # حساب ID جديد
                current_max = 0
                if not df_m.empty:
                    ids = pd.to_numeric(df_m["ID"], errors='coerce').fillna(0)
                    current_max = int(ids.max())
                new_id = str(current_max + 1)
                
                # ✅ تصحيح الخطأ هنا: استعملنا COLS_M
                new_row = pd.DataFrame([[new_id, ref, des, uni, qte, pri]], columns=COLS_M)
                df_updated = pd.concat([df_m, new_row], ignore_index=True)
                if save_data(df_updated):
                    st.success("✅ تم الحفظ بنجاح!")
                    st.rerun()
            else:
                st.warning("المرجو إدخال اسم السلعة!")

st.markdown("---")

# --- ب: البحث (Recherche) ---
search = st.text_input("🔍 قلب بسمية السلعة أو المرجع...", placeholder="مثال: Tube, Climatiseur...")
df_filtered = df_m[df_m['السلعة'].str.contains(search, case=False, na=False) | 
                   df_m['المرجع'].str.contains(search, case=False, na=False)]

# --- ج: عرض السلعة (Cards) ---
if not df_filtered.empty:
    for index, row in df_filtered.iterrows():
        with st.container(border=True):
            col_info, col_btns = st.columns([3, 1])
            
            with col_info:
                st.markdown(f"### 📦 {row['السلعة']}")
                st.write(f"🔢 **Ref:** `{row['المرجع']}` | 📏 **Unité:** `{row['الوحدة']}` | 🔢 **Qte:** `{row['الكمية']}`")
                st.markdown(f"💰 **Prix Unit:** <span style='color:#00ff00; font-size:18px; font-weight:bold;'>{row['ثمن الوحدة']} DH</span>", unsafe_allow_html=True)
            
            with col_btns:
                st.write("")
                if st.button(f"📝 تعديل", key=f"ed_{row['ID']}"):
                    st.session_state[f"edit_m_{row['ID']}"] = True
                if st.button(f"🗑️ حذف", key=f"dl_{row['ID']}"):
                    st.session_state[f"del_m_{row['ID']}"] = True

            # --- نافذة التعديل ---
            if st.session_state.get(f"edit_m_{row['ID']}", False):
                with st.container(border=True):
                    st.info(f"📝 تعديل: {row['السلعة']}")
                    e1, e2, e3 = st.columns(3)
                    with e1:
                        n_ref = st.text_input("المرجع", value=row['المرجع'], key=f"r_{row['ID']}")
                        n_des = st.text_input("السلعة", value=row['السلعة'], key=f"s_{row['ID']}")
                    with e2:
                        n_uni = st.selectbox("الوحدة", ["U", "M", "M2", "ML", "Kg", "Ens"], 
                                             index=["U", "M", "M2", "ML", "Kg", "Ens"].index(row['الوحدة']) if row['الوحدة'] in ["U", "M", "M2", "ML", "Kg", "Ens"] else 0,
                                             key=f"u_{row['ID']}")
                        n_qte = st.text_input("الكمية", value=row['الكمية'], key=f"q_{row['ID']}")
                    with e3:
                        n_pri = st.text_input("ثمن الوحدة", value=row['ثمن الوحدة'], key=f"p_{row['ID']}")
                    
                    be1, be2 = st.columns(2)
                    with be1:
                        if st.button("تحديث 💾", key=f"up_{row['ID']}", type="primary"):
                            df_m.loc[index] = [row['ID'], n_ref, n_des, n_uni, n_qte, n_pri]
                            if save_data(df_m):
                                st.session_state[f"edit_m_{row['ID']}"] = False
                                st.rerun()
                    with be2:
                        if st.button("إلغاء ❌", key=f"cn_{row['ID']}"):
                            st.session_state[f"edit_m_{row['ID']}"] = False
                            st.rerun()

            # --- نافذة الحذف ---
            if st.session_state.get(f"del_m_{row['ID']}", False):
                st.warning(f"⚠️ واش بغيتي تمسح **{row['السلعة']}**؟")
                b_del1, b_del2 = st.columns(2)
                with b_del1:
                    if st.button("نعم، مسح ✅", key=f"y_{row['ID']}"):
                        df_m = df_m.drop(index)
                        if save_data(df_m):
                            st.session_state[f"del_m_{row['ID']}"] = False
                            st.rerun()
                with b_del2:
                    if st.button("لا ❌", key=f"n_{row['ID']}"):
                        st.session_state[f"del_m_{row['ID']}"] = False
                        st.rerun()
else:
    st.info("ماكاين حتى سلعة بهاد السمية.")
    # ==================================================================================================================================================================
# 📄 5. صفحة Devis (بداية الحساب)
# ==========================================
else:
    st.title("📄 إنشاء Devis جديد")
    df_c = load_data("Clients", ["الاسم/الشركة"])
    df_m = load_data("Materiels", ["التعيين", "الثمن", "الوحدة"])

    c1, c2 = st.columns(2)
    client_sel = c1.selectbox("اختار الزبون:", df_c["الاسم/الشركة"])
    date_devis = c2.date_input("تاريخ الوثيقة")

    st.markdown("---")
    st.write("💡 الخطوة الجاية: غنزيدو هنا جدول تفاعلي فين تختار السلعة ويتحسب Total HT و TVA بحال هاديك الورقة اللي صيفطتي.")
