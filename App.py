import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# =========================================================
# 🛠️ 1. الإعدادات والربط (الأساس)
# =========================================================
st.set_page_config(page_title="MVAC Pro System", layout="wide", page_icon="❄️")

conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_ID = "1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs"

# دالة جلب البيانات (الطريقة الرسمية)
def load_data(sheet_name, cols):
    try:
        df = conn.read(spreadsheet=SHEET_ID, worksheet=sheet_name, ttl=0)
        if df.empty: return pd.DataFrame(columns=cols)
        # تصحيح الـ ID ليكون رقماً
        if "ID" in df.columns:
            df["ID"] = pd.to_numeric(df["ID"], errors='coerce').fillna(0).astype(int)
        return df
    except:
        return pd.DataFrame(columns=cols)

# =========================================================
# 🧭 2. القائمة الجانبية (Sidebar)
# =========================================================
with st.sidebar:
    st.title("❄️ MVAC SYSTEM")
    st.markdown("---")
    page = st.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 السلعة والمخزون", "📄 إنشاء Devis/Facture"])
    st.markdown("---")
    st.write("سفيان - نظام MVAC")

# =========================================================
# 👥 3. صـفـحـة إدارة الـزبـنـاء
# =========================================================
if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    df_c = load_data("Clients", ["ID", "الاسم/الشركة", "النوع", "ICE", "الهاتف", "العنوان", "RIB"])

    # ذاكرة التعديل
    if "edit_id_c" not in st.session_state: st.session_state.edit_id_c = None

    with st.expander("📝 إضافة / تعديل زبون", expanded=(st.session_state.edit_id_c is not None)):
        with st.form("form_client", clear_on_submit=True):
            curr = df_c[df_c["ID"] == st.session_state.edit_id_c].iloc[0] if st.session_state.edit_id_c else None
            
            c1, c2 = st.columns(2)
            name = c1.text_input("الاسم أو الشركة *", value=str(curr["الاسم/الشركة"]) if curr is not None else "")
            tel = c2.text_input("رقم الهاتف", value=str(curr["الهاتف"]) if curr is not None else "")
            ice = c1.text_input("ICE", value=str(curr["ICE"]) if curr is not None else "")
            rib = c2.text_input("RIB", value=str(curr["RIB"]) if curr is not None else "")
            type_c = st.selectbox("النوع", ["Particulier", "Société"], index=0 if (curr is None or curr["النوع"]=="Particulier") else 1)
            addr = st.text_area("العنوان", value=str(curr["العنوان"]) if curr is not None else "")

            if st.form_submit_button("حفظ البيانات ✅"):
                if name:
                    if st.session_state.edit_id_c: # تعديل
                        df_c.loc[df_c["ID"] == st.session_state.edit_id_c, ["الاسم/الشركة", "الهاتف", "ICE", "RIB", "العنوان", "النوع"]] = [name, tel, ice, rib, addr, type_c]
                        st.session_state.edit_id_c = None
                    else: # إضافة جديد
                        new_id = int(df_c["ID"].max() + 1) if not df_c.empty else 1
                        new_row = pd.DataFrame([{"ID":new_id, "الاسم/الشركة":name, "الهاتف":tel, "ICE":ice, "RIB":rib, "العنوان":addr, "النوع":type_c}])
                        df_c = pd.concat([df_c, new_row], ignore_index=True)
                    
                    # الحفظ باستعمال الطريقة الرسمية
                    conn.update(spreadsheet=SHEET_ID, worksheet="Clients", data=df_c)
                    st.success("✅ تم الحفظ بنجاح!")
                    st.rerun()

    # العرض والتحكم
    search = st.text_input("🔍 بحث عن زبون:")
    df_show = df_c[df_c["الاسم/الشركة"].astype(str).str.contains(search, case=False, na=False)] if search else df_c
    
    for i, row in df_show.iterrows():
        col1, col2, col3 = st.columns([5, 1, 1])
        col1.write(f"👤 **{row['الاسم/الشركة']}**")
        if col2.button("📝", key=f"e_{row['ID']}"):
            st.session_state.edit_id_c = row['ID']; st.rerun()
        if col3.button("🗑️", key=f"d_{row['ID']}"):
            df_c = df_c[df_c["ID"] != row['ID']]
            conn.update(spreadsheet=SHEET_ID, worksheet="Clients", data=df_c)
            st.rerun()
    st.dataframe(df_show, use_container_width=True, hide_index=True)

# =========================================================
# 📦 4. صـفـحـة الـسـلـعـة والمخزون
# =========================================================
elif page == "📦 السلعة والمخزون":
    st.title("📦 إدارة السلعة")
    df_m = load_data("Materiels", ["ID", "التعيين", "الوحدة", "الثمن", "الكمية"])

    with st.expander("➕ إضافة مادة"):
        with st.form("f_mat"):
            c1, c2, c3 = st.columns([3, 1, 1])
            nom = c1.text_input("اسم السلعة")
            un = c2.selectbox("الوحدة", ["U", "M", "M2", "Kg"])
            pr = c3.number_input("الثمن", min_value=0.0)
            if st.form_submit_button("إضافة ✅"):
                new_id = int(df_m["ID"].max() + 1) if not df_m.empty else 1
                new_row = pd.DataFrame([{"ID":new_id, "التعيين":nom, "الوحدة":un, "الثمن":pr, "الكمية":0}])
                df_m = pd.concat([df_m, new_row], ignore_index=True)
                conn.update(spreadsheet=SHEET_ID, worksheet="Materiels", data=df_m)
                st.success("تمت الإضافة!"); st.rerun()
    st.dataframe(df_m, use_container_width=True, hide_index=True)

# =========================================================
# 📄 5. صـفـحـة الـفـواتـيـر
# =========================================================
else:
    st.title("📄 إنشاء Devis / Facture")
    st.info("السيستيم جاهز. واش بغيتي نزيدو دابا خاصية الـ PDF؟")
