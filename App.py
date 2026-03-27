import streamlit as st
import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

st.set_page_config(page_title="MVAC App", layout="wide")

# عرض اللوغو
try:
    st.sidebar.image('mvac_logo.png', use_container_width=True)
except:
    st.sidebar.title("MVAC")

st.title("❄️ نظام MVAC لإدارة الفواتير")

menu = st.sidebar.radio("القائمة", ["الزبناء", "فاتورة جديدة"])

if 'clients' not in st.session_state:
    st.session_state.clients = []

if menu == "الزبناء":
    name = st.text_input("اسم الزبون")
    if st.button("حفظ الزبون"):
        st.session_state.clients.append(name)
        st.success(f"تم تسجيل {name}")
    st.write("قائمة الزبناء:", st.session_state.clients)

elif menu == "فاتورة جديدة":
    if not st.session_state.clients:
        st.warning("دخل الزبناء أولاً")
    else:
        c = st.selectbox("اختار الزبون", st.session_state.clients)
        amount = st.number_input("المبلغ (DH)", min_value=0)
        if st.button("تحميل الفاتورة PDF"):
            buf = io.BytesIO()
            p = canvas.Canvas(buf, pagesize=letter)
            p.drawString(100, 750, f"Facture pour: {c}")
            p.drawString(100, 730, f"Total: {amount} DH")
            p.save()
            st.download_button("اضغط هنا للتحميل", buf.getvalue(), "facture.pdf")
