import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 🛠️ 1. الإعدادات والربط
st.set_page_config(page_title="MVAC Pro System", layout="wide", page_icon="❄️")

conn = st.connection("gsheets", type=GSheetsConnection)

# الرابط الصحيح (تأكد أن هاد الرابط هو اللي فيه ورقة Customers)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMl791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

# الترتيب اللي عندك فـ Sheets بالظبط: ID, النوع, الاسم/الشركة, ICE, RIB, العنوان, الهاتف
COLS_C = ["ID", "النوع", "الاسم/الشركة", "ICE", "RIB", "العنوان", "الهاتف"]

# 🔄 دالة جلب البيانات (Affichage)
def load_data(sheet_name):
    try:
        # ttl=0 باش يجيب anva وأي حاجة جديدة فالبلاصة
        df = conn.read(spreadsheet=SHEET_URL, worksheet=sheet_name, ttl=0)
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip()
            # كيجبر الكود يحترم الترتيب ديالك
            return df[COLS_C]
        return pd.DataFrame(columns=COLS_C)
    except:
        return pd.DataFrame(columns=COLS_C)

# 💾 دالة الحفظ (Enregistrement)
def save_data(sheet_name, df):
    try:
        conn.update(spreadsheet=SHEET_URL, worksheet=sheet_name, data=df)
        return True
    except Exception as e:
        st.error(f"❌ خطأ فالحفظ: {e}")
        return False

# 🧭 2. القائمة الجانبية
with st.sidebar:
    st.title("❄️ MVAC SYSTEM")
    st.markdown("---")
    page = st.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 السلعة"])
    st.markdown("---")
    st.write("سفيان - MVAC v1.0")

# ===========================================================================================================================================================================
# 👥 3. صفحة إدارة الزبناء (نسخة احترافية)
# =========================================================
if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    
    df_c = load_data("Customers")

    # --- 1. إضافة زبون جديد ---
    with st.expander("📝 إضافة زبون جديد"):
        with st.form("form_add", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                t_c = st.selectbox("النوع", ["Particulier", "Société"], key="add_type")
                n_c = st.text_input("الاسم أو الشركة *")
                i_c = st.text_input("ICE")
            with col2:
                r_c = st.text_input("RIB")
                a_c = st.text_input("العنوان")
                te_c = st.text_input("الهاتف")
            
            if st.form_submit_button("حفظ ✅"):
                if n_c:
                    new_id = int(df_c["ID"].max() + 1) if not df_c.empty else 1
                    new_row = pd.DataFrame([[new_id, t_c, n_c, i_c, r_c, a_c, te_c]], columns=COLS_C)
                    df_updated = pd.concat([df_c, new_row], ignore_index=True)
                    if save_data("Customers", df_updated):
                        st.success("تم الحفظ!")
                        st.rerun()

    st.markdown("---")

    # --- 2. البحث والتعديل والمسح ---
    if not df_c.empty:
        st.subheader("🔍 البحث والتحكم")
        
        # خانة البحث بالسمية
        search = st.text_input("قلب على كليان بالسمية أو ICE:")
        df_filtered = df_c[df_c['الاسم/الشركة'].str.contains(search, case=False, na=False) | 
                           df_c['ICE'].str.contains(search, case=False, na=False)]

        # اختيار الكليان باش نعدلوه
        selected_client_name = st.selectbox("اختار كليان باش تعدلو أو تمسحو:", ["---"] + df_filtered['الاسم/الشركة'].tolist())

        if selected_client_name != "---":
            # جلب معلومات الكليان المختار
            client_info = df_c[df_c['الاسم/الشركة'] == selected_client_name].iloc[0]
            idx = df_c[df_c['الاسم/الشركة'] == selected_client_name].index[0]

            with st.container(border=True):
                st.write(f"📝 تعديل بيانات: **{selected_client_name}**")
                c1, c2 = st.columns(2)
                with c1:
                    new_type = st.selectbox("النوع", ["Particulier", "Société"], index=0 if client_info['النوع']=="Particulier" else 1)
                    new_name = st.text_input("الاسم/الشركة", value=client_info['الاسم/الشركة'])
                    new_ice = st.text_input("ICE", value=client_info['ICE'])
                with c2:
                    new_rib = st.text_input("RIB", value=client_info['RIB'])
                    new_addr = st.text_input("العنوان", value=client_info['العنوان'])
                    new_tel = st.text_input("الهاتف", value=client_info['الهاتف'])

                col_btn1, col_btn2 = st.columns([1, 4])
                with col_btn1:
                    if st.button("تحديث 💾", type="primary"):
                        df_c.loc[idx] = [client_info['ID'], new_type, new_name, new_ice, new_rib, new_addr, new_tel]
                        if save_data("Customers", df_c):
                            st.success("تم التعديل!")
                            st.rerun()
                
                with col_btn2:
                    if st.button("حذف الكليان 🗑️"):
                        df_c = df_c.drop(idx)
                        if save_data("Customers", df_c):
                            st.warning("تم الحذف!")
                            st.rerun()

        # عرض الجدول الكامل
        st.markdown("---")
        st.write("### 📋 قائمة الزبناء الكاملة")
        st.dataframe(df_filtered, use_container_width=True, hide_index=True)
    else:
        st.info("الجدول خاوي.")
# ===========================================================================================================================================================================
# 📦 4. صفحة السلعة
# =========================================================
elif page == "📦 السلعة":
    st.title("📦 إدارة السلعة")
    df_m = load_data("Materiels")
    st.dataframe(df_m, use_container_width=True, hide_index=True)
