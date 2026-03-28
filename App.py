import streamlit as st
import pandas as pd

# 1. إعدادات الصفحة
st.set_page_config(page_title="MVAC Control Panel", layout="wide", page_icon="❄️")

# 2. تهيئة قاعدة بيانات الزبناء في الذاكرة
if 'db_clients' not in st.session_state:
    st.session_state.db_clients = pd.DataFrame(columns=[
        "ID", "النوع", "الاسم/الشركة", "ICE", "RIB", "الهاتف", "العنوان"
    ])

# 3. القائمة الجانبية للتنقل
with st.sidebar:
    st.title("M-VAC Pro")
    st.markdown("---")
    choice = st.radio(
        "اختار الصفحة:",
        ["🏠 الصفحة الرئيسية", "👥 إدارة الزبناء", "📦 السلعة والمخزون", "📄 إنشاء فاتورة"]
    )
    st.markdown("---")
    st.info("نظام تسيير MVAC - سفيان")

# --- منطق الصفحات ---

# 🏠 الصفحة الرئيسية
if choice == "🏠 الصفحة الرئيسية":
    st.title("❄️ لوحة تحكم MVAC")
    st.write("مرحباً سفيان، التطبيق جاهز للعمل.")
    col1, col2 = st.columns(2)
    col1.metric("إجمالي الزبناء", len(st.session_state.db_clients))
    col2.metric("حالة النظام", "متصل ✅")

# 👥 صفحة إدارة الزبناء (المطورة)
elif choice == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")

    # أ. إضافة زبون جديد
    with st.expander("➕ إضافة زبون جديد (فرد أو شركة)"):
        type_c = st.radio("نوع الزبون:", ["Particulier", "Société"], horizontal=True)
        with st.form("add_client_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("الاسم الكامل / اسم الشركة")
            phone = col2.text_input("رقم الهاتف")
            
            if type_c == "Société":
                ice = col1.text_input("رقم ICE")
                rib = col2.text_input("رقم RIB")
            else:
                ice, rib = "", ""
                
            addr = st.text_area("العنوان الكامل")
            
            if st.form_submit_button("حفظ الزبون"):
                if name and phone:
                    # توليد ID جديد
                    new_id = int(st.session_state.db_clients["ID"].max() + 1) if not st.session_state.db_clients.empty else 1
                    new_row = {
                        "ID": new_id, "النوع": type_c, "الاسم/الشركة": name,
                        "ICE": ice, "RIB": rib, "الهاتف": phone, "العنوان": addr
                    }
                    st.session_state.db_clients = pd.concat([st.session_state.db_clients, pd.DataFrame([new_row])], ignore_index=True)
                    st.success(f"✅ تم حفظ {name}")
                    st.rerun()
                else:
                    st.error("⚠️ يرجى إدخال الاسم والهاتف")

    st.markdown("---")

    # ب. البحث والتحكم (تعديل/حذف)
    st.subheader("🔍 البحث والتحكم في الزبناء")
    search_term = st.text_input("ابحث عن زبون بالاسم:")

    if not st.session_state.db_clients.empty:
        df_display = st.session_state.db_clients
        if search_term:
            df_display = df_display[df_display["الاسم/الشركة"].str.contains(search_term, case=False, na=False)]

        # عرض الزبناء مع الأزرار
        for index, row in df_display.iterrows():
            with st.container():
                c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
                c1.write(f"**{row['الاسم/الشركة']}** ({row['النوع']})")
                c2.write(f"📞 {row['الهاتف']}")
                
                # زر التعديل
                if c3.button("📝 تعديل", key=f"edit_{row['ID']}"):
                    st.session_state.editing_id = row['ID']
                
                # زر الحذف
                if c4.button("🗑️ حذف", key=f"del_{row['ID']}"):
                    st.session_state.db_clients = st.session_state.db_clients[st.session_state.db_clients["ID"] != row['ID']]
                    st.warning("تم الحذف بنجاح")
                    st.rerun()
                st.markdown("---")

        # نافذة التعديل المنبثقة
        if 'editing_id' in st.session_state:
            st.markdown("### 🛠️ تعديل البيانات")
            curr = st.session_state.db_clients[st.session_state.db_clients["ID"] == st.session_state.editing_id].iloc[0]
            with st.form("edit_form"):
                new_n = st.text_input("الاسم", value=curr["الاسم/الشركة"])
                new_p = st.text_input("الهاتف", value=curr["الهاتف"])
                new_a = st.text_area("العنوان", value=curr["العنوان"])
                
                col_btn1, col_btn2 = st.columns(2)
                if col_btn1.form_submit_button("✅ حفظ"):
                    st.session_state.db_clients.loc[st.session_state.db_clients["ID"] == st.session_state.editing_id, ["الاسم/الشركة", "الهاتف", "العنوان"]] = [new_n, new_p, new_a]
                    del st.session_state.editing_id
                    st.success("تم التحديث!")
                    st.rerun()
                if col_btn2.form_submit_button("❌ إلغاء"):
                    del st.session_state.editing_id
                    st.rerun()
    else:
        st.info("لا يوجد زبناء مسجلين حالياً.")

# 📦 صفحة السلعة (للمرحلة القادمة)
elif choice == "📦 السلعة والمخزون":
    st.title("📦 تسيير السلعة")
    st.info("هاد القسم هو اللي غانقادو فيه الماتيريال (نحاس، غاز...) والأثمنة.")

# 📄 صفحة الفاتورة (للمرحلة القادمة)
elif choice == "📄 إنشاء فاتورة":
    st.title("📄 الفواتير")
    st.info("هنا غانجمعو الزبون مع السلعة باش تخرج الفاتورة PDF.")
