import streamlit as st
import pandas as pd
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# إعدادات الصفحة
st.set_page_config(page_title="HVAC Pro Manager", layout="wide")

# تهيئة قاعدة البيانات في "ذاكرة الجلسة" (Session State)
if 'db' not in st.session_state:
    st.session_state.db = {
        'inventory': pd.DataFrame(columns=["القطعة", "الكمية", "الثمن"]),
        'clients': pd.DataFrame(columns=["النوع", "الاسم/الشركة", "ICE", "RIB", "Mail", "Tel", "Lieu"]),
        'invoices': []
    }

st.title("❄️ نظام إدارة التكييف والتبريد التجاري")

menu = st.sidebar.radio("القائمة الرئيسية", ["الزبناء", "المخزون", "الفواتير", "أرشيف PDF"])

# --- 1. قسم الزبناء (إضافة، تحديث، مسح) ---
if menu == "الزبناء":
    st.header("👥 إدارة الزبناء")
    
    with st.expander("➕ إضافة زبون جديد"):
        c_type = st.selectbox("نوع الزبون", ["فردي", "شركة"])
        name = st.text_input("الاسم الكامل / اسم الشركة")
        col1, col2 = st.columns(2)
        with col1:
            ice = st.text_input("ICE (للشركات)")
            rib = st.text_input("RIB")
            mail = st.text_input("البريد الإلكتروني")
        with col2:
            tel = st.text_input("الهاتف")
            lieu = st.text_input("العنوان / الموقع")
        
        if st.button("حفظ الزبون"):
            new_client = {"النوع": c_type, "الاسم/الشركة": name, "ICE": ice, "RIB": rib, "Mail": mail, "Tel": tel, "Lieu": lieu}
            st.session_state.db['clients'] = pd.concat([st.session_state.db['clients'], pd.DataFrame([new_client])], ignore_index=True)
            st.success("تم الحفظ!")

    st.subheader("قائمة الزبناء")
    edited_clients = st.data_editor(st.session_state.db['clients'], num_rows="dynamic")
    if st.button("تحديث قاعدة بيانات الزبناء"):
        st.session_state.db['clients'] = edited_clients
        st.success("تم التحديث!")

# --- 2. قسم المخزون (إضافة، تحديث، مسح) ---
elif menu == "المخزون":
    st.header("📦 إدارة المخزون (السلع)")
    edited_stock = st.data_editor(st.session_state.db['inventory'], num_rows="dynamic")
    if st.button("حفظ تغييرات المخزون"):
        st.session_state.db['inventory'] = edited_stock
        st.success("تم تحديث المخزون!")

# --- 3. قسم الفواتير (صنع، تعديل، PDF) ---
elif menu == "الفواتير":
    st.header("📄 إنشاء فاتورة")
    
    if st.session_state.db['clients'].empty:
        st.warning("يجب إضافة زبون أولاً!")
    else:
        client_choice = st.selectbox("اختر الزبون", st.session_state.db['clients']["الاسم/الشركة"])
        c_info = st.session_state.db['clients'][st.session_state.db['clients']["الاسم/الشركة"] == client_choice].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            service = st.text_area("وصف الإصلاحات / الخدمات")
            price = st.number_input("ثمن الخدمة (DH)", min_value=0)
        with col2:
            items_used = st.multiselect("السلع المستعملة", st.session_state.db['inventory']["القطعة"])
            
        if st.button("توليد الفاتورة PDF"):
            # منطق صنع PDF مبسط
            buf = io.BytesIO()
            c = canvas.Canvas(buf, pagesize=letter)
            c.drawString(100, 750, f"فاتورة لـ: {client_choice}")
            c.drawString(100, 730, f"الخدمة: {service}")
            c.drawString(100, 710, f"المجموع: {price} DH")
            c.save()
            
            inv_data = {"id": len(st.session_state.db['invoices'])+1, "client": client_choice, "total": price, "date": datetime.now(), "pdf": buf.getvalue()}
            st.session_state.db['invoices'].append(inv_data)
            st.success("تم توليد الفاتورة بنجاح!")
            st.download_button("تحميل PDF", buf.getvalue(), file_name=f"invoice_{client_choice}.pdf")

# --- 4. أرشيف الفواتير (تعديل ومسح وتحديث الـ PDF) ---
elif menu == "أرشيف PDF":
    st.header("📂 أرشيف الفواتير")
    for i, inv in enumerate(st.session_state.db['invoices']):
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.write(f"فاتورة {inv['id']} - {inv['client']} - {inv['total']} DH")
        if col2.button("مسح", key=f"del_{i}"):
            st.session_state.db['invoices'].pop(i)
            st.rerun()
        col3.download_button("تحميل", inv['pdf'], file_name=f"fixed_invoice_{i}.pdf", key=f"down_{i}")
