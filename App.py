import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# =========================================================
# 1. إعدادات الصفحة والربط (الأساس)
# =========================================================
st.set_page_config(page_title="MVAC Pro System", layout="wide", page_icon="❄️")

conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_ID = "1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs"

# دالة ذكية لجلب البيانات وتصحيح أنواع الجداول
def load_data(sheet_name, cols):
    try:
        df = conn.read(spreadsheet=SHEET_ID, worksheet=sheet_name, ttl=0)
        if df.empty: return pd.DataFrame(columns=cols)
        if "ID" in df.columns:
            df["ID"] = pd.to_numeric(df["ID"], errors='coerce').fillna(0).astype(int)
        return df
    except:
        return pd.DataFrame(columns=cols)

# =========================================================
# 2. القائمة الجانبية (Sidebar) - هادي هي اللي فيها المنيو
# =========================================================
with st.sidebar:
    st.title("❄️ MVAC SYSTEM")
    page = st.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 السلعة والمخزون", "📄 إنشاء Devis/Facture"])
    st.markdown("---")
    st.write("سفيان - نظام تسيير MVAC")

# =========================================================
# 3. صـفـحـة إدارة الـزبـنـاء (Clients)
# =========================================================
if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    df_c = load_data("Clients", ["ID", "الاسم/الشركة", "النوع", "ICE", "الهاتف", "العنوان", "RIB"])

    # --- الجزء الخاص بـ (AJOUTER / MODIFIER) ---
    if "edit_id_c" not in st.session_state: st.session_state.edit_id_c = None

    with st.expander("➕ إضافة / 🛠️ تعديل بيانات زبون", expanded=(st.session_state.edit_id_c is not None)):
        with st.form("form_client", clear_on_submit=True):
            # إلى كنا فوضع التعديل، كنجبدو البيانات القديمة
            curr = df_c[df_c["ID"] == st.session_state.edit_id_c].iloc[0] if st.session_state.edit_id_c else None
            
            c1, c2 = st.columns(2)
            name = c1.text_input("الاسم/الشركة *", value=curr["الاسم/الشركة"] if curr is not None else "")
            tel = c2.text_input("الهاتف", value=curr["الهاتف"] if curr is not None else "")
            ice = c1.text_input("ICE", value=curr["ICE"] if curr is not None else "")
            rib = c2.text_input("RIB", value=curr["RIB"] if curr is not None else "")
            type_c = st.selectbox("النوع", ["Particulier", "Société"], index=0 if (curr is None or curr["النوع"]=="Particulier") else 1)
            addr = st.text_area("العنوان", value=curr["العنوان"] if curr is not None else "")

            if st.form_submit_button("حفظ التغييرات"):
                if name:
                    if st.session_state.edit_id_c: # تعديل
                        df_c.loc[df_c["ID"] == st.session_state.edit_id_c, ["الاسم/الشركة", "الهاتف", "ICE", "RIB", "العنوان", "النوع"]] = [name, tel, ice, rib, addr, type_c]
                        st.session_state.edit_id_c = None
                    else: # إضافة جديد
                        new_id = int(df_c["ID"].max() + 1) if not df_c.empty else 1
                        new_row = pd.DataFrame([{"ID":new_id, "الاسم/الشركة":name, "الهاتف":tel, "ICE":ice, "RIB":rib, "العنوان":addr, "النوع":type_c}])
                        df_c = pd.concat([df_c, new_row], ignore_index=True)
                    
                    conn.update(spreadsheet=SHEET_ID, worksheet="Clients", data=df_c)
                    st.success("✅ تم الحفظ بنجاح!"); st.rerun()

    # --- الجزء الخاص بـ (RECHERCHE / SUPPRIMER) ---
    search = st.text_input("🔍 بحث ساريع عن زبون:")
    disp_c = df_c[df_c["الاسم/الشركة"].astype(str).str.contains(search, case=False, na=False)] if search else df_c

    st.markdown("### قائمة الزبناء")
    for i, row in disp_c.iterrows():
        col1, col2, col3 = st.columns([6, 1, 1])
        col1.write(f"👤 **{row['الاسم/الشركة']}** | 📞 {row['الهاتف']}")
        # زر التعديل
        if col2.button("📝", key=f"edit_c_{row['ID']}"):
            st.session_state.edit_id_c = row['ID']; st.rerun()
        # زر الحذف
        if col3.button("🗑️", key=f"del_c_{row['ID']}"):
            df_c = df_c[df_c["ID"] != row['ID']]
            conn.update(spreadsheet=SHEET_ID, worksheet="Clients", data=df_c); st.rerun()
    
    st.dataframe(disp_c, use_container_width=True, hide_index=True)

# =========================================================
# 4. صـفـحـة الـسـلـعـة (Materiels)
# =========================================================
elif page == "📦 السلعة والمخزون":
    st.title("📦 إدارة السلعة والمخزون")
    df_m = load_data("Materiels", ["ID", "التعيين", "الوحدة", "الثمن", "الكمية"])

    with st.expander("➕ إضافة مادة (Article) جديدة للمخزن"):
        with st.form("form_mat"):
            c1, c2, c3 = st.columns([3, 1, 1])
            designation = c1.text_input("اسم السلعة (Désignation)")
            unite = c2.selectbox("الوحدة", ["U", "M", "M2", "ML", "Kg"])
            prix = c3.number_input("الثمن الوحدوي (DH)", min_value=0.0)
            if st.form_submit_button("إضافة للمخزن"):
                if designation:
                    new_id = int(df_m["ID"].max() + 1) if not df_m.empty else 1
                    new_row = pd.DataFrame([{"ID":new_id, "التعيين":designation, "الوحدة":unite, "الثمن":prix, "الكمية":0}])
                    df_m = pd.concat([df_m, new_row], ignore_index=True)
                    conn.update(spreadsheet=SHEET_ID, worksheet="Materiels", data=df_m)
                    st.success("✅ تمت إضافة السلعة!"); st.rerun()

    st.dataframe(df_m, use_container_width=True, hide_index=True)

# =========================================================
# 5. صـفـحـة الـفـواتـيـر (Devis/Facture)
# =========================================================
elif page == "📄 إنشاء Devis/Facture":
    st.title("📄 إنشاء وثيقة جديدة")
    st.info("هنا كنجمعو بين الزبناء والسلعة باش نحسبو الفاتورة.")
    # (قريباً غنزيدو هنا PDF generator)
