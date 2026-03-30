import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. إعداد الصفحة
st.set_page_config(page_title="نظام MVAC Pro", layout="wide", page_icon="❄️")

# 2. الربط مع Google Sheets (الرابط النقي)
conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

# 3. دالة لجلب البيانات (باش ديما تكون محينة)
def load_data():
    return conn.read(spreadsheet=SHEET_URL, worksheet="Clients", ttl=0) # ttl=0 باش ما يكيشيش البيانات القديمة

df = load_data()

st.title("👥 إدارة زبناء MVAC")

# --- محرك البحث ---
search_query = st.text_input("🔍 بحث عن زبون (بالاسم):", "")

# --- فلتراسيون ديال الجدول على حساب البحث ---
if search_query:
    display_df = df[df["الاسم/الشركة"].astype(str).str.contains(search_query, case=False, na=False)]
else:
    display_df = df

# --- فورم الإضافة والتعديل ---
# كنخدمو بـ session_state باش نعرفو واش بغينا نعدلو شي حد
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

with st.expander("➕ إضافة / 🛠️ تعديل بيانات زبون", expanded=(st.session_state.edit_id is not None)):
    with st.form("client_form"):
        # إلى كان كاين edit_id، كنجبدو بياناتو باش نعمرو الخانات
        if st.session_state.edit_id is not None:
            current_row = df[df["ID"] == st.session_state.edit_id].iloc[0]
            st.info(f"أنت الآن تعدل بيانات: {current_row['الاسم/الشركة']}")
        else:
            current_row = None

        col1, col2 = st.columns(2)
        name = col1.text_input("الاسم / الشركة", value=current_row["الاسم/الشركة"] if current_row is not None else "")
        phone = col2.text_input("الهاتف", value=current_row["الهاتف"] if current_row is not None else "")
        ice = col1.text_input("ICE", value=current_row["ICE"] if current_row is not None else "")
        rib = col2.text_input("RIB", value=current_row["RIB"] if current_row is not None else "")
        addr = st.text_area("العنوان", value=current_row["العنوان"] if current_row is not None else "")
        type_c = st.selectbox("النوع", ["Particulier", "Société"], index=0 if (current_row is None or current_row["النوع"]=="Particulier") else 1)

        submitted = st.form_submit_button("حفظ التغييرات")
        
        if submitted:
            if name:
                if st.session_state.edit_id is not None:
                    # عملية التعديل
                    df.loc[df["ID"] == st.session_state.edit_id, ["الاسم/الشركة", "الهاتف", "ICE", "RIB", "العنوان", "النوع"]] = [name, phone, ice, rib, addr, type_c]
                    st.session_state.edit_id = None # نرجعو لوضع الإضافة
                else:
                    # عملية إضافة جديد
                    new_id = int(df["ID"].astype(float).max() + 1) if not df.empty else 1
                    new_line = pd.DataFrame([{"ID": new_id, "الاسم/الشركة": name, "النوع": type_c, "ICE": ice, "الهاتف": phone, "العنوان": addr, "RIB": rib}])
                    df = pd.concat([df, new_line], ignore_index=True)
                
                # تحديث الـ Sheet
                conn.update(spreadsheet=SHEET_URL, worksheet="Clients", data=df)
                st.success("✅ تم التحديث بنجاح!")
                st.rerun()

# --- عرض الجدول مع أزرار التحكم ---
st.markdown("---")
st.subheader("📋 قائمة الزبناء")

if not display_df.empty:
    for i, row in display_df.iterrows():
        with st.container():
            c1, c2, c3, c4 = st.columns([4, 1, 1, 1])
            c1.write(f"**{row['الاسم/الشركة']}** | {row['الهاتف']}")
            
            # زر التعديل
            if c2.button("📝 تعديل", key=f"edit_{row['ID']}"):
                st.session_state.edit_id = row['ID']
                st.rerun()
            
            # زر الحذف
            if c3.button("🗑️ حذف", key=f"del_{row['ID']}"):
                df = df[df["ID"] != row['ID']]
                conn.update(spreadsheet=SHEET_URL, worksheet="Clients", data=df)
                st.success("تم الحذف")
                st.rerun()
    
    st.markdown("---")
    st.dataframe(display_df, use_container_width=True)
else:
    st.info("لا يوجد زبناء بهذا الاسم.")
