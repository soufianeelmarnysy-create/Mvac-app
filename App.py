import streamlit as st
import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# 1. إعدادات الصفحة كاملة
st.set_page_config(page_title="MVAC Pro - Système de Gestion", layout="wide", page_icon="❄️")

# 2. القائمة الجانبية (Sidebar) مع اللوغو
with st.sidebar:
    try:
        # كيحاول يقرأ اللوغو اللي رفعتي في GitHub
        st.image("mvac_logo.png", use_container_width=True) 
    except:
        # في حالة ما لقاش اللوغو كيبان العنوان
        st.title("M-VAC")
    st.markdown("---")
    # هادي هي اللي كتحكم في الصفحات
    menu = st.radio("القائمة الرئيسية", ["🏠 الصفحة الرئيسية", "👥 إدارة الزبناء", "📄 إنشاء فاتورة جديدة"])
    st.markdown("---")
    st.info("تطبيق MVAC لإدارة خدمات التبريد والتهوية")

# 3. تخزين البيانات (كتسجل مؤقتاً في الجلسة)
if 'db_clients' not in st.session_state:
    st.session_state.db_clients = pd.DataFrame(columns=["الاسم/الشركة", "ICE", "الهاتف", "العنوان"])

# --- القسم 1: الصفحة الرئيسية ---
if menu == "🏠 الصفحة الرئيسية":
    st.title("❄️ نظام MVAC للإدارة المتكاملة")
    st.write("مرحباً بك سفيان. هاد النظام كيسهل عليك تسيير الزبناء وتصاوب فواتير احترافية لشركة MVAC.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("عدد الزبناء", len(st.session_state.db_clients))
    col2.metric("حالة السيرفر", "متصل ✅")
    col3.metric("النسخة", "1.0 PRO")

# --- القسم 2: إدارة الزبناء ---
elif menu == "👥 إدارة الزبناء":
    st.header("👤 إضافة زبون أو شركة جديدة")
    with st.form("client_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم الزبون الكامل أو اسم الشركة")
        ice = c2.text_input("رقم الـ ICE (اختياري)")
        phone = c1.text_input("رقم الهاتف")
        address = c2.text_area("العنوان الكامل")
        submit = st.form_submit_button("حفظ الزبون في القاعدة")
        
    if submit and name:
        new_row = {"الاسم/الشركة": name, "ICE": ice, "الهاتف": phone, "العنوان": address}
        st.session_state.db_clients = pd.concat([st.session_state.db_clients, pd.DataFrame([new_row])], ignore_index=True)
        st.success(f"✅ تم تسجيل {name} بنجاح!")

    st.markdown("---")
    st.subheader("📋 قائمة الزبناء المسجلين")
    if not st.session_state.db_clients.empty:
        st.dataframe(st.session_state.db_clients, use_container_width=True)
    else:
        st.write("لا يوجد زبناء مسجلين حالياً.")

# --- القسم 3: إنشاء الفاتورة ---
elif menu == "📄 إنشاء فاتورة جديدة":
    st.header("📝 تفاصيل الفاتورة المهنية")
    
    if st.session_state.db_clients.empty:
        st.warning("⚠️ خاصك تزيد زبون واحد على الأقل في قسم 'إدارة الزبناء' قبل ما تصاوب فاتورة.")
    else:
        # اختيار الزبون والمعلومات ديالو
        client_name = st.selectbox("اختار الزبون المستهدف", st.session_state.db_clients["الاسم/الشركة"])
        client_info = st.session_state.db_clients[st.session_state.db_clients["الاسم/الشركة"] == client_name].iloc[0]
        
        st.markdown("### معلومات الخدمة")
        col_a, col_b = st.columns(2)
        description = col_a.text_area("وصف الخدمة المقدمة", placeholder="مثال: إصلاح مكيف هواء بقوة 12000 BTU")
        date_facture = col_b.date_input("تاريخ الفاتورة")
        
        amount_ht = st.number_input("المبلغ الإجمالي بدون ضريبة (HT) بالدرهم", min_value=0.0, step=100.0)
        
        # حسابات الضريبة
        tva_rate = 0.20 # 20% ضريبة
        tva_amount = amount_ht * tva_rate
        total_ttc = amount_ht + tva_amount
        
        st.markdown("---")
        res1, res2, res3 = st.columns(3)
        res1.write(f"**المبلغ (HT):** {amount_ht:,.2f} DH")
        res2.write(f"**الضريبة (20%):** {tva_amount:,.2f} DH")
        res3.write(f"### **الإجمالي (TTC):** {total_ttc:,.2f} DH")

        if st.button("🚀 توليد وتحميل الفاتورة PDF"):
            buf = io.BytesIO()
            p = canvas.Canvas(buf, pagesize=letter)
            
            # تصميم رأس الفاتورة
            p.setFont("Helvetica-Bold", 20)
            p.drawCentredString(300, 750, "FACTURE MVAC")
            
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, 710, "Informations Client:")
            p.setFont("Helvetica", 11)
            p.drawString(60, 690, f"Nom: {client_name}")
            p.drawString(60, 675, f"ICE: {client_info['ICE']}")
            p.drawString(60, 660, f"Adresse: {client_info['العنوان']}")
            p.drawString(60, 645, f"Date: {date_facture}")
            
            p.line(50, 630, 550, 630)
            
            # تفاصيل الخدمة
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, 610, "Description du Service:")
            p.setFont("Helvetica", 11)
            # تقسيم النص إذا كان طويلاً
            text_object = p.beginText(60, 590)
            text_object.textLines(description)
            p.drawText(text_object)
            
            # جدول المبالغ
            p.line(50, 500, 550, 500)
            p.drawString(380, 480, f"Total HT: {amount_ht:,.2f} DH")
            p.drawString(380, 460, f"TVA (20%): {tva_amount:,.2f} DH")
            p.setFont("Helvetica-Bold", 13)
            p.drawString(380, 430, f"TOTAL TTC: {total_ttc:,.2f} DH")
            
            p.setFont("Helvetica-Oblique", 9)
            p.drawCentredString(300, 50, "Merci pour votre confiance - MVAC Service Froid et Climatisation")
            
            p.showPage()
            p.save()
            
            st.download_button(
                label="📥 اضغط هنا لتحميل الفاتورة",
                data=buf.getvalue(),
                file_name=f"Facture_MVAC_{client_name}_{date_facture}.pdf",
                mime="application/pdf"
            )
