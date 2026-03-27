import streamlit as st
import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# 1. إعدادات الصفحة والستايل
st.set_page_config(page_title="MVAC Pro - Gestion", layout="wide", page_icon="❄️")

# 2. القائمة الجانبية مع اللوغو
with st.sidebar:
    try:
        st.image("mvac_logo.png", use_container_width=True) # اللوغو ديالك
    except:
        st.title("M-VAC")
    st.markdown("---")
    menu = st.radio("القائمة الرئيسية", ["🏠 الرئيسية", "👥 إدارة الزبناء", "📄 إنشاء فاتورة مفصلة"])
    st.markdown("---")
    st.info("تطبيق MVAC: تسيير السلعة واليد العاملة")

# 3. قاعدة البيانات في الذاكرة
if 'db_clients' not in st.session_state:
    st.session_state.db_clients = pd.DataFrame(columns=["الاسم/الشركة", "ICE", "الهاتف", "العنوان"])

# --- القسم 1: الصفحة الرئيسية ---
if menu == "🏠 الرئيسية":
    st.title("❄️ لوحة تحكم MVAC")
    st.write("مرحباً سفيان. هاد النسخة دابا مقادة ومنظمة كاع فيها المصاريف واليد العاملة.")
    col1, col2 = st.columns(2)
    col1.metric("إجمالي الزبناء", len(st.session_state.db_clients))
    col2.metric("حالة التطبيق", "جاهز ✅")

# --- القسم 2: إدارة الزبناء ---
elif menu == "👥 إدارة الزبناء":
    st.header("👤 إضافة زبون جديد")
    with st.form("client_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم الزبون أو الشركة")
        ice = c2.text_input("رقم الـ ICE")
        phone = c1.text_input("رقم الهاتف")
        address = c2.text_area("العنوان الكامل")
        if st.form_submit_button("حفظ الزبون"):
            if name:
                new_data = pd.DataFrame([{"الاسم/الشركة": name, "ICE": ice, "الهاتف": phone, "العنوان": address}])
                st.session_state.db_clients = pd.concat([st.session_state.db_clients, new_data], ignore_index=True)
                st.success(f"تم تسجيل {name} بنجاح")
    
    st.markdown("---")
    st.subheader("📋 قائمة الزبناء")
    st.dataframe(st.session_state.db_clients, use_container_width=True)

# --- القسم 3: إنشاء فاتورة مفصلة (السلعة + الخدمة) ---
elif menu == "📄 إنشاء فاتورة مفصلة":
    st.header("📝 تفاصيل الفاتورة المهنية")
    
    if st.session_state.db_clients.empty:
        st.warning("⚠️ يرجى إضافة زبون أولاً من قائمة الزبناء.")
    else:
        client_name = st.selectbox("اختار الزبون", st.session_state.db_clients["الاسم/الشركة"])
        client_info = st.session_state.db_clients[st.session_state.db_clients["الاسم/الشركة"] == client_name].iloc[0]

        col_a, col_b = st.columns(2)
        
        # الجزء الخاص بالسلعة (Matériel)
        with col_a:
            st.subheader("📦 السلعة (Matériel)")
            mat_desc = st.text_area("وصف السلعة", placeholder="مثلاً: غاز R410A، نحاس، مكيف...")
            mat_price = st.number_input("ثمن السلعة الإجمالي (HT)", min_value=0.0, format="%.2f")
            
        # الجزء الخاص باليد العاملة (Main d'œuvre)
        with col_b:
            st.subheader("👷 اليد العاملة (Main d'œuvre)")
            work_desc = st.text_area("وصف العمل", placeholder="مثلاً: تركيب، شحن، صيانة...")
            work_price = st.number_input("ثمن اليد العاملة (HT)", min_value=0.0, format="%.2f")

        st.markdown("---")
        # الكوميسيون والضريبة
        c1, c2 = st.columns(2)
        discount = c1.number_input("الخصم / الكوميسيون (Remise) بالدرهم", min_value=0.0)
        tva_check = c2.checkbox("تطبيق الضريبة (20% TVA)", value=True)

        # الحسابات النهائية
        subtotal = (mat_price + work_price) - discount
        tva_amount = subtotal * 0.20 if tva_check else 0
        total_ttc = subtotal + tva_amount

        # عرض النتائج قبل التحميل
        st.markdown(f"### **المجموع HT:** {subtotal:,.2f} DH")
        st.markdown(f"### **المبلغ الإجمالي TTC:** {total_ttc:,.2f} DH")

        if st.button("🚀 توليد وتحميل الفاتورة PDF"):
            buf = io.BytesIO()
            p = canvas.Canvas(buf, pagesize=letter)
            
            # تصميم الـ PDF
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, 750, "FACTURE MVAC")
            p.setFont("Helvetica", 11)
            p.drawString(50, 720, f"Client: {client_name}")
            p.drawString(50, 705, f"ICE: {client_info['ICE']}")
            p.drawString(50, 690, f"Adresse: {client_info['العنوان']}")
            
            p.line(50, 670, 550, 670)
            
            p.drawString(50, 650, f"Description Matériel: {mat_desc}")
            p.drawString(450, 650, f"{mat_price:,.2f} DH")
            
            p.drawString(50, 630, f"Main d'œuvre: {work_desc}")
            p.drawString(450, 630, f"{work_price:,.2f} DH")
            
            if discount > 0:
                p.drawString(50, 610, f"Remise (Commission):")
                p.drawString(450, 610, f"-{discount:,.2f} DH")
            
            p.line(50, 580, 550, 580)
            p.setFont("Helvetica-Bold", 12)
            p.drawString(350, 560, f"Total HT: {subtotal:,.2f} DH")
            p.drawString(350, 540, f"TVA (20%): {tva_amount:,.2f} DH")
            p.drawString(350, 510, f"TOTAL TTC: {total_ttc:,.2f} DH")
            
            p.save()
            st.download_button("📥 تحميل الفاتورة الآن", buf.getvalue(), f"Facture_MVAC_{client_name}.pdf")
