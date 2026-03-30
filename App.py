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
if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    
    df_c = load_data("Customers")

    # --- أ: إضافة زبون جديد ---
    with st.expander("📝 إضافة زبون جديد"):
        with st.form("form_add", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                t_c = st.selectbox("النوع", ["Particulier", "Société"])
                n_c = st.text_input("الاسم أو الشركة *")
                i_c = st.text_input("ICE")
            with c2:
                r_c = st.text_input("RIB")
                a_c = st.text_input("العنوان")
                te_c = st.text_input("الهاتف")
            
            if st.form_submit_button("حفظ فـ Google Sheets ✅"):
                if n_c:
                    new_id = int(df_c["ID"].max() + 1) if not df_c.empty else 1
                    new_row = pd.DataFrame([[new_id, t_c, n_c, i_c, r_c, a_c, te_c]], columns=COLS_C)
                    df_updated = pd.concat([df_c, new_row], ignore_index=True)
                    if save_data("Customers", df_updated):
                        st.success("✅ تم الحفظ بنجاح!")
                        st.rerun()
                else:
                    st.warning("السمية ضرورية!")

    st.markdown("---")

    # --- ب: البحث والتعديل والمسح ---
    if not df_c.empty:
        st.subheader("🔍 البحث والتحكم")
        
        search = st.text_input("قلب على كليان بالسمية أو ICE:")
        
        # تحويل الأعمدة لنصوص لتفادي AttributeError
        df_c_search = df_c.copy().astype(str)
        
        # فلترة البيانات
        df_filtered = df_c[
            df_c_search['الاسم/الشركة'].str.contains(search, case=False, na=False) | 
            df_c_search['ICE'].str.contains(search, case=False, na=False)
        ]

        # اختيار كليان من القائمة المفلترة
        client_names = ["---"] + df_filtered['الاسم/الشركة'].tolist()
        selected_client = st.selectbox("اختار كليان باش تعدلو أو تمسحو:", client_names)

        if selected_client != "---":
            # جلب معلومات الكليان
            idx = df_c[df_c['الاسم/الشركة'] == selected_client].index[0]
            row = df_c.loc[idx]

            with st.container(border=True):
                st.write(f"📝 تعديل بيانات: **{selected_client}**")
                col_edit1, col_edit2 = st.columns(2)
                with col_edit1:
                    edit_type = st.selectbox("النوع", ["Particulier", "Société"], 
                                           index=0 if row['النوع']=="Particulier" else 1)
                    edit_name = st.text_input("الاسم/الشركة", value=row['الاسم/الشركة'])
                    edit_ice = st.text_input("ICE", value=row['ICE'])
                with col_edit2:
                    edit_rib = st.text_input("RIB", value=row['RIB'])
                    edit_addr = st.text_input("العنوان", value=row['العنوان'])
                    edit_tel = st.text_input("الهاتف", value=row['الهاتف'])

                btn_edit, btn_del = st.columns([1, 4])
                with btn_edit:
                    if st.button("تحديث 💾", type="primary"):
                        df_c.loc[idx] = [row['ID'], edit_type, edit_name, edit_ice, edit_rib, edit_addr, edit_tel]
                        if save_data("Customers", df_c):
                            st.success("تم التحديث!")
                            st.rerun()
                with btn_del:
                    if st.button("حذف 🗑️"):
                        df_c = df_c.drop(idx)
                        if save_data("Customers", df_c):
                            st.warning("تم الحذف!")
                            st.rerun()

        # عرض الجدول
        st.markdown("---")
        st.write("### 📋 قائمة الزبناء")
        st.dataframe(df_filtered, use_container_width=True, hide_index=True)
    else:
        st.info("الجدول خاوي حالياً.")
# ===========================================================================================================================================================================
# 📦 4. صفحة السلعة
# =========================================================
elif page == "📦 السلعة":
    st.title("📦 إدارة السلعة")
    df_m = load_data("Materiels")
    st.dataframe(df_m, use_container_width=True, hide_index=True)
