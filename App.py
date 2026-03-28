import streamlit as st
import pandas as pd

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="MVAC Control Panel", layout="wide", page_icon="❄️")

# 2. إنشاء قاعدة بيانات الزبناء في الذاكرة (Session State)
# هادي هي اللي كتخلي البيانات تبقى مسجلة طول ما المتصفح مفتوح
if 'db_clients' not in st.session_state:
    st.session_state.db_clients = pd.DataFrame(columns=[
        "ID", "النوع", "الاسم/الشركة", "ICE", "RIB", "الهاتف", "العنوان"
    ])

# 3. القائمة الجانبية (Navigation Sidebar)
with st.sidebar:
    st.title("M-VAC Pro")
    st.markdown("---")
    # المحرك اللي كيبدل الصفحات
    choice = st.radio(
        "اختار الصفحة:",
        ["🏠 الصفحة الرئيسية", "👥 إدارة الزبناء", "📦 السلعة والمخزون", "📄 إنشاء فاتورة"]
    )
    st.markdown("---")
    st.info("نظام تسيير MVAC - سفيان")

# --- الجزء الخاص بالمنطق (Logic) لكل صفحة ---

# الصفحة 1: الرئيسية
if choice == "🏠 الصفحة الرئيسية":
    st.title("❄️ مرحباً بك في نظام MVAC")
    st.write("هادي هي لوحة التحكم. اختار القسم اللي بغيتي تخدم فيه من القائمة على اليسار.")
    
    # إحصائيات سريعة
    col1, col2 = st.columns(2)
    col1.metric("إجمالي الزبناء المسجلين", len(st.session_state.db_clients))
    col2.metric("حالة النظام", "متصل ✅")

# الصفحة 2: إدارة الزبناء (هادي هي اللي دمجنا دابا)
elif choice == "👥 إدارة الزبناء":
    st.title("👥 إدارة قاعدة بيانات الزبناء")

    # --- أ: إضافة زبون جديد ---
    st.subheader("➕ إضافة زبون جديد")
    with st.expander("فتح استمارة التسجيل"):
        # اختيار النوع باش تتبدل الخانات آلياً
        type_client = st.radio("نوع الزبون:", ["Particulier (فرد)", "Société (شركة)"], horizontal=True)
        
        with st.form("add_client_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            if type_client == "Particulier (فرد)":
                name = col1.text_input("الاسم والنسب الكامل")
                client_id_card = col2.text_input("رقم البطاقة الوطنية (CIN/ID)")
                ice, rib = "", "" # خانات خاوية حيت ماشي شركة
            else:
                name = col1.text_input("اسم الشركة (Nom Ste)")
                ice = col2.text_input("رقم الـ ICE")
                rib = col1.text_input("رقم الحساب البنكي (RIB)")
                client_id_card = "" # خاوية حيت ماشي فرد

            phone = col2.text_input("رقم الهاتف")
            address = st.text_area("العنوان الكامل")
            
            if st.form_submit_button("حفظ الزبون"):
                if name and phone:
                    new_id = len(st.session_state.db_clients) + 1
                    new_row = {
                        "ID": new_id, 
                        "النوع": type_client, 
                        "الاسم/الشركة": name,
                        "ICE": ice, 
                        "RIB": rib, 
                        "الهاتف": phone, 
                        "العنوان": address
                    }
                    # إضافة السطر الجديد للجدول
                    st.session_state.db_clients = pd.concat([st.session_state.db_clients, pd.DataFrame([new_row])], ignore_index=True)
                    st.success(f"✅ تم تسجيل {name} بنجاح!")
                    st.rerun() # تحديث الصفحة باش يبان في الجدول
                else:
                    st.error("⚠️ ضروري تدخل الاسم والهاتف.")

    st.markdown("---")
    
    # --- ب: البحث والجدول ---
    st.subheader("📋 قائمة الزبناء والبحث")
    search_query = st.text_input("بحث عن زبون بالاسم:")
    
    if search_query:
        # تصفية الجدول بناءً على البحث
        filtered_df = st.session_state.db_clients[st.session_state.db_clients["الاسم/الشركة"].str.contains(search_query, case=False, na=False)]
        st.dataframe(filtered_df, use_container_width=True)
    else:
        # عرض الجدول كامل
        st.dataframe(st.session_state.db_clients, use_container_width=True)

    # --- ج: التعديل (Modifier) ---
    with st.expander("🛠️ تعديل معلومات زبون"):
        if not st.session_state.db_clients.empty:
            client_to_edit = st.selectbox("اختار ID الزبون:", st.session_state.db_clients["ID"])
            # كيجيب البيانات القديمة باش تبان ليك قبل ما تبدلها
            old_data = st.session_state.db_clients[st.session_state.db_clients["ID"] == client_to_edit].iloc[0]
            
            with st.form("edit_client"):
                new_phone = st.text_input("تعديل الهاتف", value=old_data["الهاتف"])
                new_addr = st.text_area("تعديل العنوان", value=old_data["العنوان"])
                if st.form_submit_button("تحديث"):
                    st.session_state.db_clients.loc[st.session_state.db_clients["ID"] == client_to_edit, ["الهاتف", "العنوان"]] = [new_phone, new_addr]
                    st.success("تم التحديث!")
                    st.rerun()

# الصفحة 3: السلعة (خاوية حالياً)
elif choice == "📦 السلعة والمخزون":
    st.title("📦 تسيير السلعة والمخزون")
    st.info("هاد القسم هو المرحلة الجاية: غانقادو فيه جدول السلعة والأثمنة.")

# الصفحة 4: الفاتورة (خاوية حالياً)
elif choice == "📄 إنشاء فاتورة":
    st.title("📄 نظام الفواتير")
    st.info("هنا غانجمعو كلشي باش نخرجو الفاتورة PDF.")
