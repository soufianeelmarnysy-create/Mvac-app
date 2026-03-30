import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. إعداد الصفحة
st.set_page_config(page_title="نظام MVAC Pro", layout="wide")

# 2. الربط (تأكد أن SHEET_ID صحيح)
conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_ID = "1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs"

# 3. دالة جلب البيانات (معدلة باش ما تعطيناش Response 200)
def load_data():
    try:
        # استنعمال query للوصول المباشر للبيانات
        return conn.read(spreadsheet=SHEET_ID, worksheet="Clients", ttl=0)
    except Exception as e:
        # إلى كان الـ Sheet خاوي، كنصاوبو جدول جديد
        return pd.DataFrame(columns=["ID", "الاسم/الشركة", "النوع", "ICE", "الهاتف", "العنوان", "RIB"])

df = load_data()

# تأكد أن ID هو رقم ماشي نص
if not df.empty:
    df["ID"] = pd.to_numeric(df["ID"], errors='coerce').fillna(0).astype(int)

st.title("👥 إدارة زبناء MVAC")

# --- البحث ---
search_query = st.text_input("🔍 بحث عن زبون (بالاسم):")
display_df = df[df["الاسم/الشركة"].astype(str).str.contains(search_query, case=False, na=False)] if search_query else df

# --- نظام التعديل والإضافة ---
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

with st.expander("➕ إضافة / 🛠️ تعديل بيانات زبون", expanded=(st.session_state.edit_id is not None)):
    with st.form("client_form", clear_on_submit=True):
        current_row = df[df["ID"] == st.session_state.edit_id].iloc[0] if st.session_state.edit_id is not None and not df.empty else None
        
        col1, col2 = st.columns(2)
        name = col1.text_input("الاسم / الشركة", value=current_row["الاسم/الشركة"] if current_row is not None else "")
        phone = col2.text_input("الهاتف", value=current_row["الهاتف"] if current_row is not None else "")
        ice = col1.text_input("ICE", value=current_row["ICE"] if current_row is not None else "")
        rib = col2.text_input("RIB", value=current_row["RIB"] if current_row is not None else "")
        addr = st.text_area("العنوان", value=current_row["العنوان"] if current_row is not None else "")
        type_c = st.selectbox("النوع", ["Particulier", "Société"], index=0 if (current_row is None or current_row["النوع"]=="Particulier") else 1)

        if st.form_submit_button("حفظ"):
            if name:
                if st.session_state.edit_id is not None:
                    df.loc[df["ID"] == st.session_state.edit_id, ["الاسم/الشركة", "الهاتف", "ICE", "RIB", "العنوان", "النوع"]] = [name, phone, ice, rib, addr, type_c]
                    st.session_state.edit_id = None
                else:
                    new_id = int(df["ID"].max() + 1) if not df.empty else 1
                    new_line = pd.DataFrame([{"ID": new_id, "الاسم/الشركة": name, "النوع": type_c, "ICE": ice, "الهاتف": phone, "العنوان": addr, "RIB": rib}])
                    df = pd.concat([df, new_line], ignore_index=True)
                
                conn.update(spreadsheet=SHEET_ID, worksheet="Clients", data=df)
                st.success("✅ تم التحديث!")
                st.rerun()

# --- العرض ---
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
else:
    st.info("الجدول خاوي، زيد أول كليان!")
