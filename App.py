import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 🛠️ 1. الإعدادات والربط المضمون
# ==========================================
st.set_page_config(page_title="MVAC Pro System", layout="wide", page_icon="❄️")

# الربط باستعمال الـ ID المباشر
conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_ID = "1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs"

def load_data(sheet_name, cols):
    try:
        df = conn.read(spreadsheet=SHEET_ID, worksheet=sheet_name, ttl=0)
        if df.empty: return pd.DataFrame(columns=cols)
        return df
    except:
        return pd.DataFrame(columns=cols)

# ==========================================
# 🧭 2. القائمة الجانبية (Sidebar)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9431/9431166.png", width=100) # لوغو مؤقت
    st.title("MVAC SYSTEM")
    st.markdown("---")
    page = st.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 السلعة والمخزون", "📄 إنشاء Devis/Facture"])
    st.markdown("---")
    st.write("🔧 سفيان - نظام تسيير MVAC")

# ==========================================
# 👥 3. صفحة الزبناء (Clients)
# ==========================================
if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    df_c = load_data("Clients", ["ID", "الاسم/الشركة", "النوع", "ICE", "الهاتف", "العنوان", "RIB"])

    # فورم الإضافة والتعديل
    if "edit_id_c" not in st.session_state: st.session_state.edit_id_c = None

    with st.expander("➕ إضافة / 🛠️ تعديل زبون", expanded=(st.session_state.edit_id_c is not None)):
        with st.form("form_client"):
            curr = df_c[df_c["ID"] == st.session_state.edit_id_c].iloc[0] if st.session_state.edit_id_c else None
            c1, c2 = st.columns(2)
            name = c1.text_input("الاسم/الشركة *", value=str(curr["الاسم/الشركة"]) if curr is not None else "")
            tel = c2.text_input("الهاتف", value=str(curr["الهاتف"]) if curr is not None else "")
            ice = c1.text_input("ICE", value=str(curr["ICE"]) if curr is not None else "")
            type_c = st.selectbox("النوع", ["Société", "Particulier"], index=0 if (curr is None or curr["النوع"]=="Société") else 1)
            addr = st.text_area("العنوان", value=str(curr["العنوان"]) if curr is not None else "")
            
            if st.form_submit_button("حفظ البيانات ✅"):
                if name:
                    if st.session_state.edit_id_c:
                        df_c.loc[df_c["ID"] == st.session_state.edit_id_c, ["الاسم/الشركة", "الهاتف", "ICE", "العنوان", "النوع"]] = [name, tel, ice, addr, type_c]
                        st.session_state.edit_id_c = None
                    else:
                        new_id = int(df_c["ID"].max() + 1) if not df_c.empty else 1
                        new_row = pd.DataFrame([{"ID":new_id, "الاسم/الشركة":name, "الهاتف":tel, "ICE":ice, "العنوان":addr, "النوع":type_c}])
                        df_c = pd.concat([df_c, new_row], ignore_index=True)
                    
                    conn.update(spreadsheet=SHEET_ID, worksheet="Clients", data=df_c)
                    st.success("تم الحفظ!"); st.rerun()

    st.dataframe(df_c, use_container_width=True, hide_index=True)

# ==========================================
# 📦 4. صفحة السلعة (Materiels)
# ==========================================
elif page == "📦 السلعة والمخزون":
    st.title("📦 إدارة السلعة")
    df_m = load_data("Materiels", ["ID", "التعيين", "الوحدة", "الثمن", "الكمية"])

    with st.expander("➕ إضافة مادة جديدة"):
        with st.form("form_mat"):
            c1, c2, c3 = st.columns([3, 1, 1])
            nom = c1.text_input("Désignation")
            un = c2.selectbox("Unité", ["U", "M", "M2", "Kg", "ML"])
            pr = c3.number_input("Prix (DH)", min_value=0.0)
            if st.form_submit_button("إضافة"):
                new_id = int(df_m["ID"].max() + 1) if not df_m.empty else 1
                new_row = pd.DataFrame([{"ID":new_id, "التعيين":nom, "الوحدة":un, "الثمن":pr, "الكمية":0}])
                df_m = pd.concat([df_m, new_row], ignore_index=True)
                conn.update(spreadsheet=SHEET_ID, worksheet="Materiels", data=df_m)
                st.rerun()
    st.dataframe(df_m, use_container_width=True, hide_index=True)

# ==========================================
# 📄 5. صفحة Devis (بداية الحساب)
# ==========================================
else:
    st.title("📄 إنشاء Devis جديد")
    df_c = load_data("Clients", ["الاسم/الشركة"])
    df_m = load_data("Materiels", ["التعيين", "الثمن", "الوحدة"])

    c1, c2 = st.columns(2)
    client_sel = c1.selectbox("اختار الزبون:", df_c["الاسم/الشركة"])
    date_devis = c2.date_input("تاريخ الوثيقة")

    st.markdown("---")
    st.write("💡 الخطوة الجاية: غنزيدو هنا جدول تفاعلي فين تختار السلعة ويتحسب Total HT و TVA بحال هاديك الورقة اللي صيفطتي.")
