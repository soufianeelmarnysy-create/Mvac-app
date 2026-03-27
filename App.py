import streamlit as st
import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# 1. إعداد الصفحة
st.set_page_config(page_title="MVAC Pro Gestion", layout="wide", page_icon="❄️")

# 2. القائمة الجانبية
with st.sidebar:
    try:
        st.image("mvac_logo.png", use_container_width=True)
    except:
        st.title("M-VAC")
    st.markdown("---")
    menu = st.radio("القائمة الرئيسية", ["🏠 الرئيسية", "👥 إدارة الزبناء", "📄 إنشاء فاتورة مفصلة"])

# 3. تخزين البيانات
if 'db_clients' not in st.session_state:
    st.session_state.db_clients = pd.DataFrame(columns=["الاسم/الشركة", "ICE", "الهاتف", "العنوان"])

# --- إدارة الزبناء ---
if menu == "👥 إدارة الزبناء":
    st.header("👤 تسجيل زبون جديد")
    with st.form("client_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name = col1.text_input("اسم الزبون / الشركة")
        ice = col2.text_input("رقم الـ ICE")
        phone = col1.text_input("الهاتف")
        address = col2.text_area("العنوان")
        if st.form_submit_button("حفظ الزبون"):
            if name:
                new_row = {"الاسم/الشركة": name, "ICE": ice, "الهاتف": phone, "العنوان": address}
                st.session_state.db_clients = pd.concat([st.session_state.db_clients, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"تم تسجيل {name}")

# --- إنشاء الفاتورة المفصلة ---
elif menu == "📄 إنشاء فاتورة مفصلة":
    st.header("📝 إنشاء فاتورة (سلعة + يد عاملة)")
    
    if st.session_state.db_clients.empty:
        st.warning("⚠️ سجل زبون أولاً.")
    else:
        client_name = st.selectbox("اختار الزبون", st.session_state.db_clients["الاسم/الشركة"])
        
        st.markdown("### 🛠️ تفاصيل الخدمة والسلعة")
        col_main1, col_main2 = st.columns(2)
        
        with col_main1:
            st.subheader("📦 السلعة (المواد)")
            items_desc = st.text_area("وصف السلعة (مثلاً: مواسير، غاز، مكيف...)", placeholder="كل حاجة في سطر")
            items_price = st.number_input("ثمن السلعة الإجمالي (HT)", min_value=0.0)
            
        with col_main2:
            st.subheader("👷 اليد العاملة")
            work_desc = st.text_area("وصف العمل (مثلاً: تركيب، صيانة...)", placeholder="تفاصيل الخدمة")
            work_price = st.number_input("ثمن اليد العاملة (HT)", min_value=0.0)

        st.markdown("---")
        st.subheader("💰 الخصم والضرائب")
        c1, c2 = st.columns(2)
        discount = c1.number_input("الخصم / الكوميسيون (Remise) بالدرهم", min_value=0.0)
        tva_choice = c2.checkbox("تطبيق الضريبة (20% TVA)", value=True)

        # الحسابات
        total_ht = (items_price + work_price) - discount
        tva_amount = total_ht * 0.20 if tva_choice else 0
        total_ttc = total_ht + tva_amount

        # عرض النتائج
        st.info(f"إجمالي HT: {total_ht:,.2f} DH | الضريبة: {tva_amount:,.2f} DH")
        st.success(f"### المبلغ الإجمالي للأداء (TTC): {total_ttc:,.2f} DH")

        if st.button("🚀 توليد الفاتورة PDF"):
            buf = io.BytesIO()
            p = canvas.Canvas(buf, pagesize=letter)
            # الرأس
            p.setFont("Helvetica-Bold", 18)
            p.drawCentredString(300, 750, "FACTURE MVAC")
            
            p.setFont("Helvetica", 12)
            p.drawString(50, 700, f"Client: {client_name}")
            p.drawString(50, 680, f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d')}")
            
            p.line(50, 660, 550, 660)
            
            # الجداول
            p.drawString(50, 640, "Détails de la Facture:")
            p.drawString(70, 620, f"- Matériel (السلعة): {items_price:,.2f} DH")
            p.drawString(70, 600, f"- Main d'œuvre (اليد العاملة): {work_price:,.2f} DH")
            if discount > 0:
                p.drawString(70, 580, f"- Remise (خصم): -{discount:,.2f} DH")
            
            p.line(50, 560, 550, 560)
            
            # المجموع
            p.setFont("Helvetica-Bold", 12)
            p.drawString(350, 540, f"Total HT: {total_ht:,.2f} DH")
            p.drawString(350, 520, f"TVA (20%): {tva_amount:,.2f} DH")
            p.setFont("Helvetica-Bold", 14)
            p.drawString(350, 490, f"TOTAL TTC: {total_ttc:,.2f} DH")
            
            p.save()
            st.download_button("📥 تحميل الفاتورة", buf.getvalue(), f"Mvac_Facture_{client_name}.pdf")

else:
    st.title("🏠 الرئيسية")
    st.write("مرحباً سفيان في لوحة تحكم MVAC. دبا تقدر تفرق بين السلعة والخدمة وتدير الخصم للزبناء.")
