import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# إعداد الصفحة
st.set_page_config(page_title="MVAC Control Panel", layout="wide", page_icon="❄️")

# الربط مع Google Sheets (الرابط النقي)
conn = st.connection("gsheets", type=GSheetsConnection)
# هاد الرابط "نقي" ما فيه لا gid لا #
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMl791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

# دالة لجلب البيانات مع الأعمدة اللي في الصورة ديالك
def get_data(worksheet_name):
    try:
        return conn.read(spreadsheet=SHEET_URL, worksheet=worksheet_name)
    except:
        # ترتيب الأعمدة كما في صورتك: ID, الاسم/الشركة, النوع, ICE, الهاتف, العنوان, RIB
        return pd.DataFrame(columns=["ID", "الاسم/الشركة", "النوع", "ICE", "الهاتف", "العنوان", "RIB"])

# القائمة الجانبية
with st.sidebar:
    st.title("M-VAC Pro")
    choice = st.radio("اختار الصفحة:", ["🏠 الرئيسية", "👥 إدارة الزبناء", "📦 السلعة والمخزون"])
    st.info("نظام تسيير MVAC - سفيان")

# --- صفحة إدارة الزبناء ---
if choice == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    db_clients = get_data("Clients")
    
    is_editing = 'editing_client_id' in st.session_state
    
    with st.expander("➕ إضافة / 🛠️ تعديل زبون", expanded=is_editing):
        with st.form("client_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            # تعبئة البيانات تلقائياً لو كنا في وضع التعديل
            c_def = db_clients[db_clients["ID"] == st.session_state.editing_client_id].iloc[0] if is_editing else None
            
            name = col1.text_input("الاسم / الشركة", value=c_def["الاسم/الشركة"] if is_editing else "")
            type_c = col2.selectbox("النوع", ["Particulier", "Société"], index=0 if (not is_editing or c_def["النوع"]=="Particulier") else 1)
            phone = col1.text_input("الهاتف", value=c_def["الهاتف"] if is_editing else "")
            ice = col2.text_input("ICE", value=c_def["ICE"] if is_editing else "")
            addr = col1.text_input("العنوان", value=c_def["العنوان"] if is_editing else "")
            rib = col2.text_input("RIB", value=c_def["RIB"] if is_editing else "")
            
            if st.form_submit_button("حفظ البيانات"):
                if name:
                    if is_editing:
                        db_clients.loc[db_clients["ID"] == st.session_state.editing_client_id, 
                                     ["الاسم/الشركة","النوع","الهاتف","ICE","العنوان","RIB"]] = [name, type_c, phone, ice, addr, rib]
                        del st.session_state.editing_client_id
                    else:
                        # تحويل ID لرقم والزيادة عليه
                        new_id = int(db_clients["ID"].astype(float).max() + 1) if not db_clients.empty else 1
                        new_row = pd.DataFrame([{"ID":new_id,"الاسم/الشركة":name,"النوع":type_c,"ICE":ice,"الهاتف":phone,"العنوان":addr,"RIB":rib}])
                        db_clients = pd.concat([db_clients, new_row], ignore_index=True)
                    
                    conn.update(spreadsheet=SHEET_URL, worksheet="Clients", data=db_clients)
                    st.success("✅ تم الحفظ بنجاح!")
                    st.rerun()

    # عرض البيانات
    st.markdown("---")
    st.dataframe(db_clients, use_container_width=True)

    # أزرار التعديل والحذف
    for i, r in db_clients.iterrows():
        c1, c2, c3 = st.columns([4, 1, 1])
        c1.write(f"**{r['الاسم/الشركة']}**")
        if c2.button("📝", key=f"edit_{r['ID']}"):
            st.session_state.editing_client_id = r['ID']
            st.rerun()
        if c3.button("🗑️", key=f"del_{r['ID']}"):
            db_clients = db_clients[db_clients["ID"] != r['ID']]
            conn.update(spreadsheet=SHEET_URL, worksheet="Clients", data=db_clients)
            st.rerun()

else:
    st.write("الصفحة قيد التفعيل...")
