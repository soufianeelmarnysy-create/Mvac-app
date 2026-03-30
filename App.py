import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. إعدادات الصفحة
st.set_page_config(page_title="MVAC Control Panel", layout="wide", page_icon="❄️")

# 2. الربط مع Google Sheets
# تأكد أن Secrets عندك فيها [connections.gsheets] ناضية
conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

# دالة لجلب البيانات
def get_data(worksheet_name, columns):
    try:
        return conn.read(spreadsheet=SHEET_URL, worksheet=worksheet_name)
    except:
        return pd.DataFrame(columns=columns)

# 3. القائمة الجانبية
with st.sidebar:
    st.title("M-VAC Pro")
    st.markdown("---")
    choice = st.radio("اختار الصفحة:", ["🏠 الرئيسية", "👥 إدارة الزبناء", "📦 السلعة والمخزون", "📄 إنشاء فاتورة"])
    st.info("نظام تسيير MVAC - سفيان")

# --- 1. الصفحة الرئيسية ---
if choice == "🏠 الرئيسية":
    st.title("❄️ لوحة تحكم MVAC")
    db_clients = get_data("Clients", ["ID", "النوع", "الاسم/الشركة", "ICE", "RIB", "الهاتف", "العنوان"])
    db_stock = get_data("Materiels", ["ID", "المنتج", "ثمن الشراء", "ثمن البيع HT", "الكمية"])
    
    col1, col2 = st.columns(2)
    col1.metric("إجمالي الزبناء", len(db_clients))
    col2.metric("قطع السلعة", len(db_stock))

# --- 2. صفحة إدارة الزبناء ---
elif choice == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    db_clients = get_data("Clients", ["ID", "النوع", "الاسم/الشركة", "ICE", "RIB", "الهاتف", "العنوان"])
    
    is_editing = 'editing_client_id' in st.session_state
    if is_editing:
        c_def = db_clients[db_clients["ID"] == st.session_state.editing_client_id].iloc[0]
        c_title, c_btn = f"🛠️ تعديل الزبون {st.session_state.editing_client_id}", "تحديث البيانات"
    else:
        c_title, c_btn, c_def = "➕ إضافة زبون جديد", "حفظ الزبون الجديد", None

    with st.expander(c_title, expanded=is_editing):
        type_c = st.radio("النوع:", ["Particulier", "Société"], 
                          index=0 if (not is_editing or c_def["النوع"]=="Particulier") else 1, horizontal=True)
        
        with st.form("client_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("الاسم / الشركة", value=c_def["الاسم/الشركة"] if is_editing else "")
            phone = col2.text_input("الهاتف", value=c_def["الهاتف"] if is_editing else "")
            ice = col1.text_input("ICE (للشركات)", value=c_def["ICE"] if is_editing else "") if type_c == "Société" else ""
            rib = col2.text_input("RIB (رقم الحساب)", value=c_def["RIB"] if is_editing else "")
            addr = st.text_area("العنوان", value=c_def["العنوان"] if is_editing else "")
            
            if st.form_submit_button(c_btn):
                if name and phone:
                    if is_editing:
                        db_clients.loc[db_clients["ID"] == st.session_state.editing_client_id, 
                                     ["النوع","الاسم/الشركة","الهاتف","ICE","RIB","العنوان"]] = [type_c, name, phone, ice, rib, addr]
                        del st.session_state.editing_client_id
                    else:
                        new_id = int(db_clients["ID"].max() + 1) if not db_clients.empty else 1
                        new_row = pd.DataFrame([{"ID":new_id,"النوع":type_c,"الاسم/الشركة":name,"ICE":ice,"RIB":rib,"الهاتف":phone,"العنوان":addr}])
                        db_clients = pd.concat([db_clients, new_row], ignore_index=True)
                    
                    # تحديث Google Sheet فعلياً
                    conn.update(spreadsheet=SHEET_URL, worksheet="Clients", data=db_clients)
                    st.success("✅ تم حفظ البيانات في Google Sheet")
                    st.rerun()

    st.markdown("---")
    search_c = st.text_input("🔍 بحث عن زبون:")
    df_show = db_clients
    if search_c: df_show = df_show[df_show["الاسم/الشركة"].astype(str).str.contains(search_c, case=False)]
    
    for i, r in df_show.iterrows():
        col_c1, col_c2, col_c3, col_c4 = st.columns([1, 3, 1, 1])
        col_c1.write(f"`{r['ID']}`")
        col_c2.write(f"**{r['الاسم/الشركة']}** - {r['الهاتف']}")
        if col_c3.button("📝 تعديل", key=f"ec_{r['ID']}"):
            st.session_state.editing_client_id = r['ID']
            st.rerun()
        if col_c4.button("🗑️ حذف", key=f"dc_{r['ID']}"):
            db_clients = db_clients[db_clients["ID"] != r['ID']]
            conn.update(spreadsheet=SHEET_URL, worksheet="Clients", data=db_clients)
            st.rerun()

# --- 3. صفحة السلعة والمخزون ---
elif choice == "📦 السلعة والمخزون":
    st.title("📦 إدارة السلعة")
    db_stock = get_data("Materiels", ["ID", "المنتج", "ثمن الشراء", "ثمن البيع HT", "الكمية"])
    
    # ... (نفس المنطق ديال تعديل/إضافة السلعة مع تبديل st.session_state.db_stock بـ db_stock)
    # وعند الحفظ استعمل: conn.update(spreadsheet=SHEET_URL, worksheet="Materiels", data=db_stock)
    st.info("طبق نفس منطق 'إدارة الزبناء' هنا للربط مع ورقة Materiels")

# --- 4. صفحة إنشاء الفاتورة ---
elif choice == "📄 إنشاء فاتورة":
    st.title("📄 إنشاء فاتورة")
    db_clients = get_data("Clients", ["ID", "الاسم/الشركة"])
    if db_clients.empty:
        st.warning("سجل زبون أولاً.")
    else:
        c_list = db_clients["الاسم/الشركة"].tolist()
        sel_c = st.selectbox("اختار الزبون:", c_list)
        st.button("توليد PDF (قيد التطوير)")
