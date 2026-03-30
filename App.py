import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. إعداد الصفحة
st.set_page_config(page_title="نظام MVAC Pro", layout="wide", page_icon="❄️")

# 2. الربط باستخدام ID الملف مباشرة (هذا هو الساروت الصحيح)
conn = st.connection("gsheets", type=GSheetsConnection)
# هاد الـ ID جبناه من الرابط ديالك وهو اللي كيهنينا من كاع المشاكل
SHEET_ID = "1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs"

# 3. دالة لجلب البيانات (استخدام الـ ID عوض الرابط)
def load_data():
    try:
        # استعملنا SHEET_ID هنا باش يلقى الملف نيشان
        return conn.read(spreadsheet=SHEET_ID, worksheet="Clients", ttl=0)
    except Exception as e:
        st.error(f"خطأ في قراءة البيانات: {e}")
        return pd.DataFrame(columns=["ID", "الاسم/الشركة", "النوع", "ICE", "الهاتف", "العنوان", "RIB"])

df = load_data()

st.title("👥 إدارة زبناء MVAC")

# --- محرك البحث ---
search_query = st.text_input("🔍 بحث عن زبون (بالاسم):", "")

if search_query:
    display_df = df[df["الاسم/الشركة"].astype(str).str.contains(search_query, case=False, na=False)]
else:
    display_df = df

# --- نظام التعديل والإضافة ---
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

with st.expander("➕ إضافة / 🛠️ تعديل بيانات زبون", expanded=(st.session_state.edit_id is not None)):
    with st.form("client_form"):
        if st.session_state.edit_id is not None:
            # كنقلبو على السطر اللي بغينا نعدلو
            try:
                current_row = df[df["ID"].astype(str) == str(st.session_state.edit_id)].iloc[0]
                st.info(f"تعديل: {current_row['الاسم/الشركة']}")
            except:
                current_row = None
        else:
            current_row = None

        col1, col2 = st.columns(2)
        name = col1.text_input("الاسم / الشركة", value=current_row["الاسم/الشركة"] if current_row is not None else "")
        phone = col2.text_input("الهاتف", value=current_row["الهاتف"] if current_row is not None else "")
        ice = col1.text_input("ICE", value=current_row["ICE"] if current_row is not None else "")
        rib = col2.text_input("RIB", value=current_row["RIB"] if current_row is not None else "")
        addr = st.text_area("العنوان", value=current_row["العنوان"] if current_row is not None else "")
        type_c = st.selectbox("النوع", ["Particulier", "Société"], index=0 if (current_row is None or current_row["النوع"]=="Particulier") else 1)

        submitted = st.form_submit_button("حفظ")
        
        if submitted:
            if name:
                if st.session_state.edit_id is not None:
                    # تعديل سطر موجود
                    df.loc[df["ID"].astype(str) == str(st.session_state.edit_id), ["الاسم/الشركة", "الهاتف", "ICE", "RIB", "العنوان", "النوع"]] = [name, phone, ice, rib, addr, type_c]
                    st.session_state.edit_id = None
                else:
                    # إضافة سطر جديد
                    new_id = int(df["ID"].astype(float).max() + 1) if not df.empty else 1
                    new_line = pd.DataFrame([{"ID": new_id, "الاسم/الشركة": name, "النوع": type_c, "ICE": ice, "الهاتف": phone, "العنوان": addr, "RIB": rib}])
                    df = pd.concat([df, new_line], ignore_index=True)
                
                # تحديث الـ Sheet باستخدام الـ ID
                conn.update(spreadsheet=SHEET_ID, worksheet="Clients", data=df)
                st.success("✅ تم التحديث!")
                st.rerun()

# --- عرض الأزرار للتحكم ---
st.markdown("---")
if not display_df.empty:
    for i, row in display_df.iterrows():
        c1, c2, c3 = st.columns([4, 1, 1])
        c1.write(f"**{row['الاسم/الشركة']}**")
        if c2.button("📝", key=f"ed_{row['ID']}"):
            st.session_state.edit_id = row['ID']
            st.rerun()
        if c3.button("🗑️", key=f"de_{row['ID']}"):
            df = df[df["ID"] != row['ID']]
            conn.update(spreadsheet=SHEET_ID, worksheet="Clients", data=df)
            st.rerun()
    
    st.dataframe(display_df, use_container_width=True)
