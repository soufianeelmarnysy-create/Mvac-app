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
elif page == "📦 إدارة السلعة":
    st.title("📦 إدارة السلعة (Materials)")
    COLS_M = ["ID", "المرجع", "التعريف", "الوحدة", "الثمن"] # تأكد من هاد الأسماء فـ Sheets
    df_m = load_data("Materiels")

    # --- إضافة سلعة جديدة ---
    with st.expander("➕ إضافة سلعة جديدة"):
        with st.form("form_add_mat", clear_on_submit=True):
            m1, m2 = st.columns(2)
            with m1:
                ref = st.text_input("المرجع (Ref)")
                des = st.text_input("التعريف (Désignation) *")
            with m2:
                uni = st.selectbox("الوحدة", ["U", "M", "M2", "ML", "Kg"])
                pri = st.text_input("الثمن (Prix)")
            
            if st.form_submit_button("حفظ السلعة ✅"):
                if des:
                    new_id_m = str(int(pd.to_numeric(df_m["ID"], errors='coerce').max() + 1)) if not df_m.empty else "1"
                    new_row_m = pd.DataFrame([[new_id_m, ref, des, uni, pri]], columns=COLS_M)
                    df_m_updated = pd.concat([df_m, new_row_m], ignore_index=True)
                    if save_data("Materiels", df_m_updated):
                        st.success("✅ تم الحفظ!")
                        st.rerun()

    st.markdown("---")
    search_m = st.text_input("🔍 قلب على سلعة...", placeholder="مثال: climatiseur")
    df_m_filt = df_m[df_m['التعريف'].str.contains(search_m, case=False, na=False)] if not df_m.empty else df_m

    if not df_m_filt.empty:
        for idx_m, row_m in df_m_filt.iterrows():
            with st.container(border=True):
                mc1, mc2 = st.columns([3, 1])
                with mc1:
                    st.markdown(f"### 📦 {row_m['التعريف']}")
                    st.write(f"🔢 Ref: `{row_m['المرجع']}` | 💰 Prix: `{row_m['الثمن']} DH` | 📏 Unité: `{row_m['الوحدة']}`")
                with mc2:
                    st.write(" ")
                    if st.button(f"📝 تعديل", key=f"em_{row_m['ID']}"): st.session_state[f"edit_m_{row_m['ID']}"] = True
                    if st.button(f"🗑️ حذف", key=f"dm_{row_m['ID']}"): st.session_state[f"del_m_{row_m['ID']}"] = True

                # تعديل السلعة
                if st.session_state.get(f"edit_m_{row_m['ID']}", False):
                    with st.container(border=True):
                        me1, me2 = st.columns(2)
                        with me1:
                            n_ref = st.text_input("المرجع", value=row_m['المرجع'], key=f"ref_{row_m['ID']}")
                            n_des = st.text_input("التعريف", value=row_m['التعريف'], key=f"des_{row_m['ID']}")
                        with me2:
                            n_pri = st.text_input("الثمن", value=row_m['الثمن'], key=f"pri_{row_m['ID']}")
                        if st.button("تحديث 💾", key=f"up_m_{row_m['ID']}", type="primary"):
                            df_m.loc[idx_m, ['المرجع', 'التعريف', 'الثمن']] = [n_ref, n_des, n_pri]
                            if save_data("Materiels", df_m): st.rerun()
                        if st.button("إلغاء ❌", key=f"can_m_{row_m['ID']}"):
                            st.session_state[f"edit_m_{row_m['ID']}"] = False
                            st.rerun()
    else: st.info("لا توجد سلعة.")
