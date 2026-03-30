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
# 👤 واجهة إدارة الزبناء
# =========================================================
st.title("👥 إدارة الزبناء (Customers)")

df_c = load_data()

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
                current_max = 0
                if not df_c.empty:
                    ids = pd.to_numeric(df_c["ID"], errors='coerce').fillna(0)
                    current_max = int(ids.max())
                new_id = str(current_max + 1)
                
                new_row = pd.DataFrame([[new_id, t_c, n_c, i_c, r_c, a_c, te_c]], columns=COLS_C)
                df_updated = pd.concat([df_c, new_row], ignore_index=True)
                if save_data(df_updated):
                    st.success("✅ تم الحفظ!")
                    st.rerun()

st.markdown("---")

# --- ب: البحث بـ Design الـ Cards ---
st.subheader("🔍 البحث السريع")
search_query = st.text_input("قلب بسمية الكليان...", placeholder="مثال: anva")

df_filtered = df_c[df_c['الاسم/الشركة'].str.contains(search_query, case=False, na=False)]

if not df_filtered.empty:
    for index, row in df_filtered.iterrows():
        with st.container(border=True):
            col_info, col_btns = st.columns([3, 1])
            
            with col_info:
                # عرض البيانات مع الأيقونات
                st.markdown(f"### 👤 {row['الاسم/الشركة']} ({row['النوع']})")
                st.write(f"🆔 **ICE:** `{row['ICE']}` | 📞 **Tel:** `{row['الهاتف']}`")
                st.write(f"💳 **RIB:** `{row['RIB']}`")
                st.write(f"📍 **Adresse:** {row['العنوان']}")
            
            with col_btns:
                st.write(" ")
                if st.button(f"📝 تعديل", key=f"edit_{row['ID']}"):
                    st.session_state[f"edit_mode_{row['ID']}"] = True
                
                if st.button(f"🗑️ حذف", key=f"del_{row['ID']}"):
                    st.session_state[f"del_mode_{row['ID']}"] = True

            # نافذة التعديل
            if st.session_state.get(f"edit_mode_{row['ID']}", False):
                with st.container(border=True):
                    st.info(f"تعديل: {row['الاسم/الشركة']}")
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        new_type = st.selectbox("النوع", ["Particulier", "Société"], index=0 if row['النوع']=="Particulier" else 1, key=f"et_{row['ID']}")
                        new_name = st.text_input("الاسم", value=row['الاسم/الشركة'], key=f"en_{row['ID']}")
                        new_ice = st.text_input("ICE", value=row['ICE'], key=f"ei_{row['ID']}")
                    with ec2:
                        new_rib = st.text_input("RIB", value=row['RIB'], key=f"er_{row['ID']}")
                        new_addr = st.text_input("العنوان", value=row['العنوان'], key=f"ea_{row['ID']}")
                        new_tel = st.text_input("الهاتف", value=row['الهاتف'], key=f"etex_{row['ID']}")
                    
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("تحديث 💾", key=f"up_{row['ID']}", type="primary"):
                            df_c.loc[index] = [row['ID'], new_type, new_name, new_ice, new_rib, new_addr, new_tel]
                            if save_data(df_c):
                                st.session_state[f"edit_mode_{row['ID']}"] = False
                                st.rerun()
                    with b2:
                        if st.button("إلغاء ❌", key=f"can_{row['ID']}"):
                            st.session_state[f"edit_mode_{row['ID']}"] = False
                            st.rerun()

            # نافذة الحذف
            if st.session_state.get(f"del_mode_{row['ID']}", False):
                st.error(f"⚠️ واش بصح بغيتي تمسح **{row['الاسم/الشركة']}**؟")
                if st.button("نعم، احذف ✅", key=f"conf_{row['ID']}"):
                    df_new = df_c.drop(index)
                    if save_data(df_new):
                        st.session_state[f"del_mode_{row['ID']}"] = False
                        st.rerun()
                if st.button("لا، تراجع ❌", key=f"stop_{row['ID']}"):
                    st.session_state[f"del_mode_{row['ID']}"] = False
                    st.rerun()
else:
    st.info("لم يتم العثور على أي نتائج.")

# ===========================================================================================================================================================================
# 📦 4. صفحة السلعة
# =========================================================
elif page == "📦 السلعة":
    st.title("📦 إدارة السلعة")
    df_m = load_data("Materiels")
    st.dataframe(df_m, use_container_width=True, hide_index=True)
