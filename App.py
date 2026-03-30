import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# =========================================================
# 🛠️ 1. الإعدادات والربط
# =========================================================
st.set_page_config(page_title="MVAC Pro System", layout="wide", page_icon="❄️")

conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

# دالة جلب البيانات (الطريقة الرسمية والصحيحة)
def load_data(sheet_name, cols):
    try:
        # كتقرا البيانات بالرابط المباشر
        df = conn.read(spreadsheet=SHEET_URL, worksheet=sheet_name, ttl=0)
        if df.empty: return pd.DataFrame(columns=cols)
        if "ID" in df.columns:
            df["ID"] = pd.to_numeric(df["ID"], errors='coerce').fillna(0).astype(int)
        return df
    except:
        return pd.DataFrame(columns=cols)

# دالة الحفظ (باستعمال conn.update الرسمية)
def save_data(sheet_name, df):
    try:
        # هادي هي الطريقة اللي كتقبلها المكتبة بلا ما تعطيك attribute error
        conn.update(spreadsheet=SHEET_URL, worksheet=sheet_name, data=df)
        return True
    except Exception as e:
        st.error(f"خطأ في الحفظ: {e}")
        return False

# =========================================================
# 🧭 2. القائمة الجانبية
# =========================================================
with st.sidebar:
    st.title("❄️ MVAC SYSTEM")
    st.markdown("---")
    page = st.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 السلعة والمخزون", "📄 إنشاء Devis/Facture"])
    st.markdown("---")
    st.write("سفيان - نظام تسيير MVAC")

# =========================================================
# 👥 3. صـفـحـة إدارة الـزبـنـاء
# =========================================================
if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    df_c = load_data("Clients", ["ID", "الاسم/الشركة", "النوع", "ICE", "الهاتف", "العنوان", "RIB"])

    if "edit_id_c" not in st.session_state: st.session_state.edit_id_c = None

    with st.expander("📝 إضافة زبون جديد / تعديل بيانات", expanded=(st.session_state.edit_id_c is not None)):
        with st.form("form_client", clear_on_submit=True):
            # جلب بيانات السطر المختار للتعديل
            curr = df_c[df_c["ID"] == st.session_state.edit_id_c].iloc[0] if st.session_state.edit_id_c is not None and not df_c[df_c["ID"] == st.session_state.edit_id_c].empty else None
            
            c1, c2 = st.columns(2)
            name = c1.text_input("الاسم أو الشركة *", value=str(curr["الاسم/الشركة"]) if curr is not None else "")
            tel = c2.text_input("الهاتف", value=str(curr["الهاتف"]) if curr is not None else "")
            ice = c1.text_input("ICE", value=str(curr["ICE"]) if curr is not None else "")
            rib = c2.text_input("RIB", value=str(curr["RIB"]) if curr is not None else "")
            type_c = st.selectbox("النوع", ["Particulier", "Société"], index=0 if (curr is None or curr["النوع"]=="Particulier") else 1)
            addr = st.text_area("العنوان الكامل", value=str(curr["العنوان"]) if curr is not None else "")

            col_b1, col_b2 = st.columns([1, 4])
            if col_b1.form_submit_button("حفظ ✅"):
                if name:
                    if st.session_state.edit_id_c: # تعديل
                        df_c.loc[df_c["ID"] == st.session_state.edit_id_c, ["الاسم/الشركة", "الهاتف", "ICE", "RIB", "العنوان", "النوع"]] = [name, tel, ice, rib, addr, type_c]
                        st.session_state.edit_id_c = None
                    else: # إضافة
                        new_id = int(df_c["ID"].max() + 1) if not df_c.empty else 1
                        new_row = pd.DataFrame([{"ID":new_id, "الاسم/الشركة":name, "الهاتف":tel, "ICE":ice, "RIB":rib, "العنوان":addr, "النوع":type_c}])
                        df_c = pd.concat([df_c, new_row], ignore_index=True)
                    
                    if save_data("Clients", df_c):
                        st.success("تم الحفظ بنجاح!")
                        st.rerun()
            
            if st.session_state.edit_id_c and col_b2.form_submit_button("إلغاء التعديل ❌"):
                st.session_state.edit_id_c = None
                st.rerun()

    search = st.text_input("🔍 بحث عن زبون:")
    df_show = df_c[df_c["الاسم/الشركة"].astype(str).str.contains(search, case=False, na=False)] if search else df_c

    st.markdown("---")
    for i, row in df_show.iterrows():
        col_name, col_edit, col_del = st.columns([5, 1, 1])
        col_name.write(f"👤 **{row['الاسم/الشركة']}** | 📞 {row['الهاتف']}")
        if col_edit.button("📝", key=f"ed_c_{row['ID']}"):
            st.session_state.edit_id_c = row['ID']
            st.rerun()
        if col_del.button("🗑️", key=f"del_c_{row['ID']}"):
            df_c = df_c[df_c["ID"] != row['ID']]
            save_data("Clients", df_c)
            st.rerun()
    
    st.dataframe(df_show, use_container_width=True, hide_index=True)

# =========================================================
# 📦 4. صـفـحـة الـسلـعـة
# =========================================================
elif page == "📦 السلعة والمخزون":
    st.title("📦 إدارة السلعة والمخزون")
    df_m = load_data("Materiels", ["ID", "التعيين", "الوحدة", "الثمن", "الكمية"])

    with st.expander("➕ إضافة مادة جديدة"):
        with st.form("form_mat"):
            c1, c2, c3 = st.columns([3, 1, 1])
            nom = c1.text_input("اسم السلعة (Désignation)")
            unite = c2.selectbox("الوحدة", ["U", "M", "M2", "ML", "Kg"])
            price = c3.number_input("الثمن الوحدوي (DH)", min_value=0.0)
            
            if st.form_submit_button("إضافة ✅"):
                if nom:
                    new_id = int(df_m["ID"].max() + 1) if not df_m.empty else 1
                    new_m = pd.DataFrame([{"ID":new_id, "التعيين":nom, "الوحدة":unite, "الثمن":price, "الكمية":0}])
                    df_m = pd.concat([df_m, new_m], ignore_index=True)
                    save_data("Materiels", df_m)
                    st.success("تمت الإضافة!")
                    st.rerun()

    st.dataframe(df_m, use_container_width=True, hide_index=True)

# =========================================================
# 📄 5. صـفـحـة الـفـواتـيـر
# =========================================================
elif page == "📄 إنشاء Devis/Facture":
    st.title("📄 إنشاء وثيقة جديدة")
    st.warning("هذه الصفحة قيد التطوير لربط البيانات واستخراج PDF.")
