import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. إعداد الصفحة (العنوان والأيقونة)
st.set_page_config(page_title="MVAC Pro Control", layout="wide", page_icon="❄️")

# 2. الربط مع Google Sheets باستخدام الـ ID (أضمن طريقة)
conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_ID = "1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs"

# 3. دالة جلب البيانات مع معالجة الأخطاء
def load_data():
    try:
        # قراءة البيانات من ورقة Clients
        df = conn.read(spreadsheet=SHEET_ID, worksheet="Clients", ttl=0)
        # التأكد أن عمود ID عبارة عن أرقام
        if not df.empty and "ID" in df.columns:
            df["ID"] = pd.to_numeric(df["ID"], errors='coerce').fillna(0).astype(int)
        return df
    except Exception as e:
        # في حالة كان الجدول خاوي أو أول مرة
        return pd.DataFrame(columns=["ID", "الاسم/الشركة", "النوع", "ICE", "الهاتف", "العنوان", "RIB"])

# جلب البيانات الحالية
df = load_data()

st.title("👥 إدارة زبناء MVAC")

# --- 🔍 محرك البحث ---
search_query = st.text_input("🔍 بحث عن زبون (اكتب الاسم هنا):", "")

# تصفية الجدول على حساب البحث
if search_query:
    display_df = df[df["الاسم/الشركة"].astype(str).str.contains(search_query, case=False, na=False)]
else:
    display_df = df

# --- 🛠️ نظام الإضافة والتعديل ---
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

# تفتحات الإضافة/التعديل
with st.expander("➕ إضافة / 🛠️ تعديل بيانات زبون", expanded=(st.session_state.edit_id is not None)):
    with st.form("client_form", clear_on_submit=True):
        # جلب بيانات الزبون لو كنا في وضع التعديل
        if st.session_state.edit_id is not None and not df.empty:
            current_row = df[df["ID"] == st.session_state.edit_id].iloc[0]
            st.info(f"📍 أنت الآن تعدل بيانات: {current_row['الاسم/الشركة']}")
        else:
            current_row = None

        col1, col2 = st.columns(2)
        name = col1.text_input("الاسم / الشركة *", value=current_row["الاسم/الشركة"] if current_row is not None else "")
        phone = col2.text_input("الهاتف", value=current_row["الهاتف"] if current_row is not None else "")
        ice = col1.text_input("ICE", value=current_row["ICE"] if current_row is not None else "")
        rib = col2.text_input("RIB", value=current_row["RIB"] if current_row is not None else "")
        addr = st.text_area("العنوان", value=current_row["العنوان"] if current_row is not None else "")
        type_c = st.selectbox("النوع", ["Particulier", "Société"], 
                             index=0 if (current_row is None or current_row["النوع"]=="Particulier") else 1)

        save_btn = st.form_submit_button("حفظ البيانات في Google Sheet")
        
        if save_btn:
            if name:
                if st.session_state.edit_id is not None:
                    # تحديث سطر موجود
                    df.loc[df["ID"] == st.session_state.edit_id, ["الاسم/الشركة", "الهاتف", "ICE", "RIB", "العنوان", "النوع"]] = [name, phone, ice, rib, addr, type_c]
                    st.session_state.edit_id = None
                else:
                    # إضافة سطر جديد بـ ID جديد
                    next_id = int(df["ID"].max() + 1) if not df.empty else 1
                    new_line = pd.DataFrame([{"ID": next_id, "الاسم/الشركة": name, "النوع": type_c, "ICE": ice, "الهاتف": phone, "العنوان": addr, "RIB": rib}])
                    df = pd.concat([df, new_line], ignore_index=True)
                
                # إرسال التحديث لـ Google Sheets
                conn.update(spreadsheet=SHEET_ID, worksheet="Clients", data=df)
                st.success("✅ تم الحفظ بنجاح!")
                st.rerun()
            else:
                st.error("⚠️ يرجى إدخال الاسم على الأقل.")

# --- 📋 عرض قائمة الزبناء مع أزرار التحكم ---
st.markdown("---")
st.subheader("📋 قائمة الزبناء الحالية")

if not display_df.empty:
    # عرض أسطر تفاعلية
    for i, row in display_df.iterrows():
        with st.container():
            c1, c2, c3 = st.columns([5, 1, 1])
            c1.write(f"**{row['ID']}** - {row['الاسم/الشركة']} ({row['الهاتف']})")
            
            # زر التعديل
            if c2.button("📝 تعديل", key=f"edit_btn_{row['ID']}"):
                st.session_state.edit_id = row['ID']
                st.rerun()
            
            # زر الحذف
            if c3.button("🗑️ حذف", key=f"del_btn_{row['ID']}"):
                df = df[df["ID"] != row['ID']]
                conn.update(spreadsheet=SHEET_ID, worksheet="Clients", data=df)
                st.success(f"تم حذف {row['الاسم/الشركة']}")
                st.rerun()
    
    st.markdown("---")
    # عرض الجدول الكامل للتأكد
    st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.warning("الجدول خاوي. ابدأ بإضافة أول زبون!")

# زر لإلغاء وضع التعديل إذا كان مفعلاً
if st.session_state.edit_id is not None:
    if st.button("❌ إلغاء التعديل والرجوع للإضافة"):
        st.session_state.edit_id = None
        st.rerun()
