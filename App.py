import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# =========================================================
# 🛠️ 1. الإعدادات والربط
# =========================================================
st.set_page_config(page_title="MVAC Pro System", layout="wide", page_icon="❄️")

conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_ID = "1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs"

# دالة جلب البيانات المضمونة
def load_data(sheet_name, cols):
    try:
        # الوصول للـ client الحقيقي لـ gspread
        client = conn._instance.client
        sh = client.open_by_key(SHEET_ID)
        ws = sh.worksheet(sheet_name)
        data = ws.get_all_records()
        df = pd.DataFrame(data)
        if df.empty: return pd.DataFrame(columns=cols)
        if "ID" in df.columns:
            df["ID"] = pd.to_numeric(df["ID"], errors='coerce').fillna(0).astype(int)
        return df
    except Exception as e:
        # st.error(f"Error loading: {e}")
        return pd.DataFrame(columns=cols)

# دالة الحفظ المضمونة
def save_data(sheet_name, df):
    try:
        client = conn._instance.client
        sh = client.open_by_key(SHEET_ID)
        ws = sh.worksheet(sheet_name)
        ws.clear()
        # تحويل البيانات لـ List ووضعها في Sheet
        ws.update([df.columns.values.tolist()] + df.values.tolist())
        return True
    except Exception as e:
        st.error(f"خطأ في الحفظ: {e}")
        return False

# =========================================================
# 🧭 2. القائمة الجانبية
# =========================================================
with st.sidebar:
    st.title("❄️ MVAC SYSTEM")
    page = st.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 السلعة والمخزون", "📄 إنشاء Devis/Facture"])
    st.markdown("---")
    st.write("سفيان - نظام MVAC")

# =========================================================
# 👥 3. صفحة الزبناء
# =========================================================
if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    df_c = load_data("Clients", ["ID", "الاسم/الشركة", "النوع", "ICE", "الهاتف", "العنوان", "RIB"])

    if "edit_id_c" not in st.session_state: st.session_state.edit_id_c = None

    with st.expander("📝 إضافة / تعديل زبون", expanded=(st.session_state.edit_id_c is not None)):
        with st.form("form_client", clear_on_submit=True):
            curr = df_c[df_c["ID"] == st.session_state.edit_id_c].iloc[0] if st.session_state.edit_id_c else None
            
            c1, c2 = st.columns(2)
            name = c1.text_input("الاسم أو الشركة *", value=str(curr["الاسم/الشركة"]) if curr is not None else "")
            tel = c2.text_input("رقم الهاتف", value=str(curr["الهاتف"]) if curr is not None else "")
            ice = c1.text_input("ICE", value=str(curr["ICE"]) if curr is not None else "")
            rib = c2.text_input("RIB", value=str(curr["RIB"]) if curr is not None else "")
            type_c = st.selectbox("نوع الزبون", ["Particulier", "Société"], index=0 if (curr is None or curr["النوع"]=="Particulier") else 1)
            addr = st.text_area("العنوان", value=str(curr["العنوان"]) if curr is not None else "")

            sub = st.form_submit_button("حفظ ✅")
            if sub and name:
                if st.session_state.edit_id_c:
                    df_c.loc[df_c["ID"] == st.session_state.edit_id_c, ["الاسم/الشركة", "الهاتف", "ICE", "RIB", "العنوان", "النوع"]] = [name, tel, ice, rib, addr, type_c]
                    st.session_state.edit_id_c = None
                else:
                    new_id = int(df_c["ID"].max() + 1) if not df_c.empty else 1
                    new_row = pd.DataFrame([{"ID":new_id, "الاسم/الشركة":name, "الهاتف":tel, "ICE":ice, "RIB":rib, "العنوان":addr, "النوع":type_c}])
                    df_c = pd.concat([df_c, new_row], ignore_index=True)
                
                if save_data("Clients", df_c):
                    st.success("تم الحفظ!")
                    st.rerun()

    # البحث والعرض
    search = st.text_input("🔍 بحث:")
    df_show = df_c[df_c["الاسم/الشركة"].astype(str).str.contains(search, case=False, na=False)] if search else df_c
    
    for i, row in df_show.iterrows():
        col1, colEdit, colDel = st.columns([5, 1, 1])
        col1.write(f"👤 **{row['الاسم/الشركة']}**")
        if colEdit.button("📝", key=f"e_{row['ID']}"):
            st.session_state.edit_id_c = row['ID']
            st.rerun()
        if colDel.button("🗑️", key=f"d_{row['ID']}"):
            df_c = df_c[df_c["ID"] != row['ID']]
            save_data("Clients", df_c)
            st.rerun()
    st.dataframe(df_show, use_container_width=True, hide_index=True)

# =========================================================
# 📦 4. صفحة السلعة
# =========================================================
elif page == "📦 السلعة والمخزون":
    st.title("📦 إدارة السلعة")
    df_m = load_data("Materiels", ["ID", "التعيين", "الوحدة", "الثمن", "الكمية"])

    with st.expander("➕ إضافة مادة"):
        with st.form("f_mat"):
            c1, c2, c3 = st.columns([3, 1, 1])
            nom = c1.text_input("اسم المادة")
            un = c2.selectbox("الوحدة", ["U", "M", "M2", "Kg"])
            pr = c3.number_input("الثمن", min_value=0.0)
            if st.form_submit_button("إضافة"):
                new_id = int(df_m["ID"].max() + 1) if not df_m.empty else 1
                new_row = pd.DataFrame([{"ID":new_id, "التعيين":nom, "الوحدة":un, "الثمن":pr, "الكمية":0}])
                df_m = pd.concat([df_m, new_row], ignore_index=True)
                save_data("Materiels", df_m)
                st.rerun()
    st.dataframe(df_m, use_container_width=True, hide_index=True)

# =========================================================
# 📄 5. صفحة الفاتورة
# =========================================================
else:
    st.title("📄 إنشاء Devis / Facture")
    st.write("السيستيم جاهز لربط الفواتير.")
