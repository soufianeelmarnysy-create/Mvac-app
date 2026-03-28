import streamlit as st
import pandas as pd

# 1. إعدادات الصفحة
st.set_page_config(page_title="MVAC Control Panel", layout="wide", page_icon="❄️")

# 2. تهيئة قواعد البيانات (الزبناء والسلعة)
if 'db_clients' not in st.session_state:
    st.session_state.db_clients = pd.DataFrame(columns=["ID", "النوع", "الاسم/الشركة", "ICE", "RIB", "الهاتف", "العنوان"])

if 'db_stock' not in st.session_state:
    st.session_state.db_stock = pd.DataFrame(columns=["ID", "المنتج", "الوصف", "ثمن الشراء", "ثمن البيع HT", "الكمية"])

# 3. القائمة الجانبية
with st.sidebar:
    st.title("M-VAC Pro")
    st.markdown("---")
    choice = st.radio("اختار الصفحة:", ["🏠 الرئيسية", "👥 إدارة الزبناء", "📦 السلعة والمخزون", "📄 إنشاء فاتورة"])
    st.markdown("---")
    st.info("نظام تسيير MVAC - سفيان")

# --- منطق الصفحات ---

# 🏠 الصفحة الرئيسية
if choice == "🏠 الرئيسية":
    st.title("❄️ لوحة تحكم MVAC")
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي الزبناء", len(st.session_state.db_clients))
    col2.metric("قطع السلعة", len(st.session_state.db_stock))
    col3.metric("حالة النظام", "متصل ✅")

# 👥 صفحة إدارة الزبناء (اللي صاوبنا قبيلة)
elif choice == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    # (نفس كود الزبناء اللي جربتي وخدام مزيان)
    with st.expander("➕ إضافة زبون جديد"):
        type_c = st.radio("نوع الزبون:", ["Particulier", "Société"], horizontal=True)
        with st.form("add_client_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("الاسم الكامل / اسم الشركة")
            phone = col2.text_input("رقم الهاتف")
            ice = col1.text_input("رقم ICE") if type_c == "Société" else ""
            addr = st.text_area("العنوان الكامل")
            if st.form_submit_button("حفظ الزبون"):
                new_id = int(st.session_state.db_clients["ID"].max() + 1) if not st.session_state.db_clients.empty else 1
                new_row = {"ID": new_id, "النوع": type_c, "الاسم/الشركة": name, "ICE": ice, "RIB": "", "الهاتف": phone, "العنوان": addr}
                st.session_state.db_clients = pd.concat([st.session_state.db_clients, pd.DataFrame([new_row])], ignore_index=True)
                st.success("✅ تم الحفظ")
                st.rerun()

    st.markdown("---")
    search_c = st.text_input("🔍 ابحث عن زبون:")
    df_c = st.session_state.db_clients
    if search_c:
        df_c = df_c[df_c["الاسم/الشركة"].str.contains(search_c, case=False)]
    
    for i, r in df_c.iterrows():
        c1, c2, c3 = st.columns([4, 1, 1])
        c1.write(f"**{r['الاسم/الشركة']}** - 📞 {r['الهاتف']}")
        if c2.button("🗑️ حذف", key=f"del_c_{r['ID']}"):
            st.session_state.db_clients = st.session_state.db_clients[st.session_state.db_clients["ID"] != r['ID']]
            st.rerun()
        st.markdown("---")

# 📦 صفحة السلعة والمخزون (الجديدة)
elif choice == "📦 السلعة والمخزون":
    st.title("📦 تسيير السلعة والمخزون")
    
    # أ. إضافة منتج جديد
    with st.expander("➕ إضافة منتج/سلعة جديدة"):
        with st.form("add_stock_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            item_name = col1.text_input("اسم المنتج (مثلاً: غاز R410A)")
            item_desc = col2.text_input("وصف قصير")
            buy_price = col1.number_input("ثمن الشراء (HT)", min_value=0.0)
            sell_price = col2.number_input("ثمن البيع للزبون (HT)", min_value=0.0)
            qty = st.number_input("الكمية المتوفرة", min_value=0)
            
            if st.form_submit_button("حفظ في المخزون"):
                if item_name:
                    new_id = int(st.session_state.db_stock["ID"].max() + 1) if not st.session_state.db_stock.empty else 1
                    new_item = {
                        "ID": new_id, "المنتج": item_name, "الوصف": item_desc,
                        "ثمن الشراء": buy_price, "ثمن البيع HT": sell_price, "الكمية": qty
                    }
                    st.session_state.db_stock = pd.concat([st.session_state.db_stock, pd.DataFrame([new_item])], ignore_index=True)
                    st.success(f"✅ تم إضافة {item_name}")
                    st.rerun()

    st.markdown("---")
    
    # ب. عرض السلعة والبحث
    st.subheader("📋 قائمة السلعة المتوفرة")
    search_s = st.text_input("🔍 ابحث عن منتج:")
    df_s = st.session_state.db_stock
    if search_s:
        df_s = df_s[df_s["المنتج"].str.contains(search_s, case=False)]
    
    st.dataframe(df_s, use_container_width=True)

    # ج. حذف سلعة
    if not df_s.empty:
        with st.expander("🗑️ حذف منتج من القائمة"):
            del_id = st.selectbox("اختار ID المنتج للحذف", df_s["ID"])
            if st.button("تأكيد الحذف"):
                st.session_state.db_stock = st.session_state.db_stock[st.session_state.db_stock["ID"] != del_id]
                st.success("تم الحذف")
                st.rerun()

# 📄 صفحة الفاتورة (للمرحلة القادمة)
elif choice == "📄 إنشاء فاتورة":
    st.title("📄 نظام الفواتير")
    st.info("المرحلة الجاية: غانصاوبو الفاتورة اللي كتجمع هاد الزبناء وهاد السلعة.")
