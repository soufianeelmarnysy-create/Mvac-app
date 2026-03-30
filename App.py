import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="نظام MVAC لإدارة الزبناء", layout="wide")

# رابط ملف Google Sheet الخاص بك
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit#gid=0"

# إنشاء الاتصال باستخدام Secrets التي أدخلتها
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📊 إدارة بيانات الزبناء - MVAC")

try:
    # قراءة البيانات من ورقة "Clients"
    # سيقوم الكود بجلب جميع الأعمدة (الاسم، ICE، الهاتف، العنوان، RIB) أوتوماتيكياً
    df = conn.read(spreadsheet=SHEET_URL, worksheet="Clients")
    st.success("✅ تم الاتصال بقاعدة البيانات بنجاح!")
except Exception as e:
    st.error(f"⚠️ خطأ في الاتصال: {e}")
    # جدول احتياطي في حالة فشل الاتصال الأولي لتجنب توقف التطبيق
    df = pd.DataFrame(columns=["الاسم/الشركة", "ICE", "الهاتف", "العنوان", "RIB"])

# عرض الجدول الرئيسي للزبناء
st.subheader("📋 قائمة الزبناء الحاليين")
st.dataframe(df, use_container_width=True)

# إضافة زبون جديد (نموذج إدخال)
with st.expander("➕ إضافة زبون جديد"):
    with st.form("new_client_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nom = st.text_input("الاسم أو اسم الشركة")
            tel = st.text_input("رقم الهاتف")
            addr = st.text_input("العنوان الكامل")
            
        with col2:
            ice = st.text_input("رقم ICE")
            rib = st.text_input("رقم الحساب البنكي (RIB)")
        
        submit_button = st.form_submit_button("حفظ البيانات في Google Sheet")
        
        if submit_button:
            if nom: # التأكد من إدخال الاسم على الأقل
                # إنشاء سطر جديد مطابق لتنسيق الجدول
                new_entry = pd.DataFrame([{
                    "الاسم/الشركة": nom,
                    "ICE": ice,
                    "الهاتف": tel,
                    "العنوان": addr,
                    "RIB": rib
                }])
                
                # دمج البيانات الجديدة مع البيانات القديمة
                updated_df = pd.concat([df, new_entry], ignore_index=True)
                
                # تحديث ملف Google Sheet
                conn.update(spreadsheet=SHEET_URL, worksheet="Clients", data=updated_df)
                
                st.success(f"✅ تمت إضافة {nom} بنجاح!")
                st.rerun() # إعادة تحميل الصفحة لإظهار البيانات الجديدة
            else:
                st.warning("المرجو إدخال اسم الزبون أو الشركة.")
