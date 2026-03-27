import streamlit as st
import pandas as pd
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="HVAC Manager - إدارة التكييف", layout="wide")

st.title("❄️ نظام إدارة شركة التكييف والتبريد")
st.sidebar.header("لوحة التحكم")

# قاعدة بيانات وهمية (تقدر تربطها بملف Excel من بعد)
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame([
        {"القطعة": "غاز R410A (كجم)", "الكمية": 20, "الثمن": 150},
        {"القطعة": "محرر (Compressor) 12k", "الكمية": 5, "الثمن": 1200},
        {"القطعة": "أنبوب نحاس 1/4", "الكمية": 50, "الثمن": 40}
    ])

# 1. قسم الفواتير (Invoicing)
menu = st.sidebar.selectbox("اختر القسم", ["صنع فاتورة", "المخزون", "قائمة الزبناء"])

if menu == "صنع فاتورة":
    st.header("📄 إنشاء فاتورة جديدة")
    
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("اسم الزبون")
        service_type = st.selectbox("نوع الخدمة", ["تركيب جديد", "شحن غاز", "صيانة دورية", "إصلاح عطب"])
    with col2:
        date = st.date_input("التاريخ", datetime.now())
        phone = st.text_input("رقم الهاتف")

    st.subheader("التفاصيل والمصاريف")
    items = st.multiselect("اختر السلع المستعملة من المخزون", st.session_state.inventory["القطعة"])
    service_price = st.number_input("ثمن اليد العاملة (DH)", min_value=0)
    
    if st.button("حساب المجموع وصنع الفاتورة"):
        total_parts = st.session_state.inventory[st.session_state.inventory["القطعة"].isin(items)]["الثمن"].sum()
        total_all = total_parts + service_price
        st.success(f"المجموع الإجمالي هو: {total_all} درهم")
        st.info(f"الفاتورة جاهزة للزبون: {client_name}")

# 2. قسم المخزون (Inventory)
elif menu == "المخزون":
    st.header("📦 إدارة المخزون")
    st.table(st.session_state.inventory)
    
    st.subheader("تحديث السلع")
    new_item = st.text_input("إضافة قطعة جديدة")
    if st.button("إضافة"):
        st.write("تمت الإضافة بنجاح")

# 3. قائمة الزبناء
elif menu == "قائمة الزبناء":
    st.header("👥 سجل الزبناء")
    st.write("هنا ستظهر قائمة الزبناء السابقين وعناوينهم.")

