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
    st.info("نظام تسيير MVAC - سفيان")

# --- منطق الصفحات ---

# 🏠 الصفحة الرئيسية
if choice == "🏠 الرئيسية":
    st.title("❄️ لوحة تحكم MVAC")
    col1, col2 = st.columns(2)
    col1.metric("إجمالي الزبناء", len(st.session_state.db_clients))
    col2.metric("قطع السلعة في المخزن", len(st.session_state.db_stock))

# 👥 صفحة إدارة الزبناء
elif choice == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    # (كود الزبناء اللي خدام عندك مزيان)
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
        if c2.button("📝 تعديل", key=f"edit_c_{r['ID']}"): st.info("خاصية التعديل قيد التشغيل")
        if c3.button("🗑️ حذف", key=f"del_c_{r['ID']}"):
            st.session_state.db_clients = st.session_state.db_clients[st.session_state.db_clients["ID"] != r['ID']]
            st.rerun()
        st.markdown("---")

# 📦 صفحة السلعة والمخزون (المطورة بطلبك)
elif choice == "📦 السلعة والمخزون":
    st.title("📦 إدارة السلعة والمخزون")
    
    # أ. إضافة منتج جديد
    with st.expander("➕ إضافة منتج جديد للمخزن"):
        with st.form("add_stock_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            item_name = col1.text_input("اسم المنتج")
            item_desc = col2.text_input("الوصف / الماركة")
            buy_p = col1.number_input("ثمن الشراء (HT)", min_value=0.0)
            sell_p = col2.number_input("ثمن البيع (HT)", min_value=0.0)
            qty = st.number_input("الكمية", min_value=0)
            
            if st.form_submit_button("حفظ المنتج"):
                if item_name:
                    new_id = int(st.session_state.db_stock["ID"].max() + 1) if not st.session_state.db_stock.empty else 1
                    new_item = {"ID": new_id, "المنتج": item_name, "الوصف": item_desc, "ثمن الشراء": buy_p, "ثمن البيع HT": sell_p, "الكمية": qty}
                    st.session_state.db_stock = pd.concat([st.session_state.db_stock, pd.DataFrame([new_item])], ignore_index=True)
                    st.success(f"✅ تم إضافة {item_name}")
                    st.rerun()

    st.markdown("---")
    
    # ب. البحث المطور (ID أو الاسم)
    st.subheader("🔍 البحث والتحكم في السلعة")
    search_s = st.text_input("ابحث عن منتج (بواسطة الاسم أو ID):")
    
    df_s = st.session_state.db_stock
    if search_s:
        # البحث كيشوف في ID (بعد تحويله لنص) وفي اسم المنتج
        df_s = df_s[df_s["المنتج"].str.contains(search_s, case=False) | df_s["ID"].astype(str).str.contains(search_s)]
    
    if not df_s.empty:
        for i, r in df_s.iterrows():
            with st.container():
                col_i1, col_i2, col_i3, col_i4 = st.columns([1, 3, 1, 1])
                col_i1.write(f"ID: `{r['ID']}`")
                col_i2.write(f"**{r['المنتج']}** | الثمن: {r['ثمن البيع HT']} DH | الكمية: {r['الكمية']}")
                
                # زر التعديل
                if col_i3.button("📝 تعديل", key=f"edit_s_{r['ID']}"):
                    st.session_state.editing_stock_id = r['ID']
                
                # زر الحذف
                if col_i4.button("🗑️ حذف", key=f"del_s_{r['ID']}"):
                    st.session_state.db_stock = st.session_state.db_stock[st.session_state.db_stock["ID"] != r['ID']]
                    st.warning(f"تم حذف {r['المنتج']}")
                    st.rerun()
                st.markdown("---")

        # ج. نافذة تعديل السلعة
        if 'editing_stock_id' in st.session_state:
            st.markdown("### 🛠️ تعديل بيانات السلعة")
            curr_s = st.session_state.db_stock[st.session_state.db_stock["ID"] == st.session_state.editing_stock_id].iloc[0]
            with st.form("edit_stock_form"):
                u_name = st.text_input("اسم المنتج", value=curr_s["المنتج"])
                u_buy = st.number_input("ثمن الشراء", value=float(curr_s["ثمن الشراء"]))
                u_sell = st.number_input("ثمن البيع", value=float(curr_s["ثمن البيع HT"]))
                u_qty = st.number_input("الكمية", value=int(curr_s["الكمية"]))
                
                c_btn1, c_btn2 = st.columns(2)
                if c_btn1.form_submit_button("✅ حفظ التعديلات"):
                    st.session_state.db_stock.loc[st.session_state.db_stock["ID"] == st.session_state.editing_stock_id, ["المنتج", "ثمن الشراء", "ثمن البيع HT", "الكمية"]] = [u_name, u_buy, u_sell, u_qty]
                    del st.session_state.editing_stock_id
                    st.success("تم التحديث!")
                    st.rerun()
                if c_btn2.form_submit_button("❌ إلغاء"):
                    del st.session_state.editing_stock_id
                    st.rerun()
    else:
        st.info("المخزن خاوي أو لا يوجد نتائج للبحث.")

# 📄 صفحة الفاتورة
elif choice == "📄 إنشاء فاتورة":
    st.title("📄 إنشاء الفاتورة")
    st.info("المرحلة القادمة: سحب البيانات من الزبناء والسلعة لتوليد PDF.")
