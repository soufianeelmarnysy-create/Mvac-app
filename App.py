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
    with st.expander("➕ إضافة زبون جديد"):
        with st.form("form_add", clear_on_submit=True):
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
                    new_id = int(df_c["ID"].max() + 1) if not df_c.empty else 1
                    new_row = pd.DataFrame([[new_id, t_c, n_c, i_c, r_c, a_c, te_c]], columns=COLS_C)
                    df_updated = pd.concat([df_c, new_row], ignore_index=True)
                    if save_data("Customers", df_updated):
                        st.success("✅ تم الحفظ!")
                        st.rerun()

    st.markdown("---")

    # --- ب: البحث والتحكم (Design التفاعلي) ---
    st.subheader("🔍 البحث عن الزبناء")
    search = st.text_input("اكتب اسم الزبون للبحث...", placeholder="مثال: anva")

    # فلترة البيانات
    df_c_str = df_c.copy().astype(str)
    df_filtered = df_c[df_c_str['الاسم/الشركة'].str.contains(search, case=False, na=False)]

    if not df_filtered.empty:
        for index, row in df_filtered.iterrows():
            with st.container(border=True):
                col_info, col_actions = st.columns([3, 1])
                
                with col_info:
                    st.markdown(f"### 👤 {row['الاسم/الشركة']} ({row['النوع']})")
                    st.markdown(f"🆔 **ICE:** {row['ICE']} | 📞 **Tel:** {row['الهاتف']}")
                    st.markdown(f"💳 **RIB:** {row['RIB']}")
                    st.markdown(f"📍 **Adresse:** {row['العنوان']}")
                
                with col_actions:
                    st.write("") # فراغ للتنسيق
                    # أزرار التحكم
                    if st.button(f"📝 تعديل", key=f"edit_{row['ID']}"):
                        st.session_state[f"editing_{row['ID']}"] = True
                    
                    if st.button(f"🗑️ حذف", key=f"del_{row['ID']}"):
                        st.session_state[f"deleting_{row['ID']}"] = True

                # --- نافذة التعديل (كتطلع تحت الكليان) ---
                if st.session_state.get(f"editing_{row['ID']}", False):
                    with st.form(f"edit_form_{row['ID']}"):
                        st.info(f"تعديل بيانات: {row['الاسم/الشركة']}")
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            new_t = st.selectbox("النوع", ["Particulier", "Société"], index=0 if row['النوع']=="Particulier" else 1)
                            new_n = st.text_input("الاسم", value=row['الاسم/الشركة'])
                            new_i = st.text_input("ICE", value=row['ICE'])
                        with ec2:
                            new_r = st.text_input("RIB", value=row['RIB'])
                            new_a = st.text_input("العنوان", value=row['العنوان'])
                            new_tel = st.text_input("الهاتف", value=row['الهاتف'])
                        
                        if st.form_submit_button("تحديث 💾"):
                            df_c.loc[index] = [row['ID'], new_t, new_n, new_i, new_r, new_a, new_tel]
                            if save_data("Customers", df_c):
                                st.success("تم التحديث!")
                                del st.session_state[f"editing_{row['ID']}"]
                                st.rerun()
                        if st.button("إلغاء ❌"):
                            del st.session_state[f"editing_{row['ID']}"]
                            st.rerun()

                # --- نافذة تأكيد الحذف ---
                if st.session_state.get(f"deleting_{row['ID']}", False):
                    st.warning(f"⚠️ واش متيقن بغيتي تمسح **{row['الاسم/الشركة']}**؟")
                    c_del1, c_del2 = st.columns(2)
                    with c_del1:
                        if st.button("نعم، احذف ✅", key=f"conf_del_{row['ID']}"):
                            df_updated = df_c.drop(index)
                            if save_data("Customers", df_updated):
                                st.success("تم الحذف!")
                                del st.session_state[f"deleting_{row['ID']}"]
                                st.rerun()
                    with c_del2:
                        if st.button("لا، تراجع ❌", key=f"cancel_del_{row['ID']}"):
                            del st.session_state[f"deleting_{row['ID']}"]
                            st.rerun()
    else:
        st.info("لم يتم العثور على أي زبون بهذا الاسم.")

# ===========================================================================================================================================================================
# 📦 4. صفحة السلعة
# =========================================================
elif page == "📦 السلعة":
    st.title("📦 إدارة السلعة")
    df_m = load_data("Materiels")
    st.dataframe(df_m, use_container_width=True, hide_index=True)
