import streamlit as st

# 1. إعدادات الصفحة (العنوان والأيقونة)
st.set_page_config(page_title="MVAC Control Panel", layout="wide", page_icon="❄️")

# 2. القائمة الجانبية (Sidebar) - هادي هي اللي كتديك لكل صفحة
with st.sidebar:
    st.title("M-VAC Pro")
    st.markdown("---")
    # هنا كتحط الاختيارات ديالك
    choice = st.radio(
        "اختار الصفحة:",
        ["🏠 الصفحة الرئيسية", "👥 إدارة الزبناء", "📦 السلعة والمخزون", "📄 إنشاء فاتورة"]
    )
    st.markdown("---")
    st.info("نظام تسيير شركة MVAC")

# 3. المنطق ديال التنقل (بناءً على الاختيار، كتبان الصفحة)
if choice == "🏠 الصفحة الرئيسية":
    st.title("مرحباً بك في MVAC")
    st.write("هادي هي لوحة التحكم الرئيسية. اختار من القائمة على اليسار باش تبدا الخدمة.")

elif choice == "👥 إدارة الزبناء":
    st.title("قائمة الزبناء")
    st.write("هنا غادي نزيدو من بعد الفورم (Form) باش تسجل كاع الشركات والناس اللي خدام معاهم.")
    import streamlit as st
import pandas as pd

# 1. إعداد قاعدة بيانات الزبناء في الذاكرة (إلا مكانتش موجودة)
if 'db_clients' not in st.session_state:
    # أعمدة شاملة للنوعين معاً
    st.session_state.db_clients = pd.DataFrame(columns=[
        "ID", "النوع", "الاسم/الشركة", "ICE", "RIB", "الهاتف", "العنوان"
    ])

st.title("👥 إدارة قاعدة بيانات الزبناء")

# --- الجزء 1: إضافة زبون جديد ---
st.subheader("➕ إضافة زبون جديد")
with st.expander("اضغط هنا لفتح استمارة التسجيل"):
    type_client = st.radio("نوع الزبون:", ["Particulier (فرد)", "Société (شركة)"], horizontal=True)
    
    with st.form("add_client_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        if type_client == "Particulier (فرد)":
            name = col1.text_input("الاسم والنسب")
            client_id_card = col2.text_input("رقم البطاقة الوطنية (ID)")
            ice = "" # خاوي للفرد
            rib = ""
        else:
            name = col1.text_input("اسم الشركة (Nom Ste)")
            ice = col2.text_input("رقم الـ ICE")
            rib = col1.text_input("رقم الحساب البنكي (RIB)")
            client_id_card = "" # خاوي للشركة

        phone = col2.text_input("رقم الهاتف")
        address = st.text_area("العنوان الكامل")
        
        submit = st.form_submit_button("حفظ الزبون")
        
        if submit:
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
                st.session_state.db_clients = pd.concat([st.session_state.db_clients, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"✅ تم تسجيل {name} بنجاح!")
            else:
                st.error("⚠️ يرجى إدخال الاسم والهاتف على الأقل.")

st.markdown("---")

# --- الجزء 2: البحث والتعديل ---
st.subheader("🔍 البحث والتعديل")
col_search, col_edit = st.columns([2, 1])

search_name = col_search.text_input("ابحث عن زبون بالاسم:")
if search_name:
    results = st.session_state.db_clients[st.session_state.db_clients["الاسم/الشركة"].str.contains(search_name, case=False, na=False)]
    st.dataframe(results, use_container_width=True)
    
    if not results.empty:
        st.info(f"💡 هنا غايظهروا مستقبلاً كاع الفواتير الخاصة بـ {search_name}")
        # (ملاحظة: فاش غانصاوبو صفحة الفواتير، غانربطوها هنا آلياً)
else:
    st.dataframe(st.session_state.db_clients, use_container_width=True)

# --- الجزء 3: خاصية التعديل (Modifier) ---
with st.expander("🛠️ تعديل معلومات زبون"):
    if not st.session_state.db_clients.empty:
        selected_client_id = st.selectbox("اختار ID الزبون المراد تعديله:", st.session_state.db_clients["ID"])
        client_data = st.session_state.db_clients[st.session_state.db_clients["ID"] == selected_client_id].iloc[0]
        
        with st.form("edit_form"):
            new_phone = st.text_input("تعديل الهاتف:", value=client_data["الهاتف"])
            new_addr = st.text_area("تعديل العنوان:", value=client_data["العنوان"])
            
            if st.form_submit_button("تحديث البيانات"):
                st.session_state.db_clients.loc[st.session_state.db_clients["ID"] == selected_client_id, ["الهاتف", "العنوان"]] = [new_phone, new_addr]
                st.success("✅ تم التحديث!")
                st.rerun()
    else:
        st.write("لا يوجد زبناء لتعديلهم.")

elif choice == "📦 السلعة والمخزون":
    st.title("تسيير السلعة")
    st.write("هنا غادي نديرو جدول فيه السلعة (نحاس، غاز، مكيفات...) والثمن ديال كل حاجة.")

elif choice == "📄 إنشاء فاتورة":
    st.title("المحاسبة والفواتير")
    st.write("هنا فين غادي نجمعو السلعة واليد العاملة والكوميسيون باش نخرجو PDF.")
