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

# --- منطق صفحة إدارة الزبناء ---
if choice == "👥 إدارة الزبناء":
    st.title("👥 إدارة قاعدة بيانات الزبناء")

    # تحديد وضع الإضافة أو التعديل للزبون
    if 'editing_client_id' not in st.session_state:
        c_title_form = "➕ إضافة زبون جديد"
        c_def_type = "Particulier"
        c_def_name = ""
        c_def_phone = ""
        c_def_ice = ""
        c_def_addr = ""
        c_btn_label = "حفظ الزبون الجديد"
    else:
        curr_c = st.session_state.db_clients[st.session_state.db_clients["ID"] == st.session_state.editing_client_id].iloc[0]
        c_title_form = f"🛠️ تعديل بيانات الزبون رقم {st.session_state.editing_client_id}"
        c_def_type = curr_c["النوع"]
        c_def_name = curr_c["الاسم/الشركة"]
        c_def_phone = curr_c["الهاتف"]
        c_def_ice = curr_c["ICE"]
        c_def_addr = curr_c["العنوان"]
        c_btn_label = "تحديث بيانات الزبون"

    # الفورم (ديما الفوق)
    with st.expander(c_title_form, expanded=('editing_client_id' in st.session_state)):
        type_c = st.radio("النوع:", ["Particulier", "Société"], index=0 if c_def_type=="Particulier" else 1, horizontal=True)
        with st.form("client_form_top", clear_on_submit=True):
            col1, col2 = st.columns(2)
            c_name = col1.text_input("الاسم الكامل / اسم الشركة", value=c_def_name)
            c_phone = col2.text_input("رقم الهاتف", value=c_def_phone)
            c_ice = col1.text_input("رقم ICE (اختياري)", value=c_def_ice) if type_c == "Société" else ""
            c_addr = st.text_area("العنوان الكامل", value=c_def_addr)
            
            cb1, cb2 = st.columns(2)
            c_submit = cb1.form_submit_button(c_btn_label)
            c_cancel = cb2.form_submit_button("إلغاء / تنظيف")

            if c_submit:
                if 'editing_client_id' in st.session_state:
                    st.session_state.db_clients.loc[st.session_state.db_clients["ID"] == st.session_state.editing_client_id, 
                        ["النوع", "الاسم/الشركة", "الهاتف", "ICE", "العنوان"]] = [type_c, c_name, c_phone, c_ice, c_addr]
                    del st.session_state.editing_client_id
                    st.success("✅ تم تحديث بيانات الزبون")
                else:
                    new_id = int(st.session_state.db_clients["ID"].max() + 1) if not st.session_state.db_clients.empty else 1
                    new_row = {"ID": new_id, "النوع": type_c, "الاسم/الشركة": c_name, "ICE": c_ice, "RIB": "", "الهاتف": c_phone, "العنوان": c_addr}
                    st.session_state.db_clients = pd.concat([st.session_state.db_clients, pd.DataFrame([new_row])], ignore_index=True)
                    st.success("✅ تم حفظ الزبون الجديد")
                st.rerun()
            
            if c_cancel:
                if 'editing_client_id' in st.session_state: del st.session_state.editing_client_id
                st.rerun()

    st.markdown("---")
    # البحث والعرض بالأزرار
    search_c = st.text_input("🔍 ابحث عن زبون (ID أو اسم):")
    df_c = st.session_state.db_clients
    if search_c:
        df_c = df_c[df_c["الاسم/الشركة"].str.contains(search_c, case=False) | df_c["ID"].astype(str).str.contains(search_c)]
    
    for i, r in df_c.iterrows():
        col_c1, col_c2, col_c3, col_c4 = st.columns([1, 3, 1, 1])
        col_c1.write(f"`{r['ID']}`")
        col_c2.write(f"**{r['الاسم/الشركة']}** ({r['النوع']}) - 📞 {r['الهاتف']}")
        if col_c3.button("📝 تعديل", key=f"edit_c_{r['ID']}"):
            st.session_state.editing_client_id = r['ID']
            st.rerun()
        if col_c4.button("🗑️ حذف", key=f"del_c_{r['ID']}"):
            st.session_state.db_clients = st.session_state.db_clients[st.session_state.db_clients["ID"] != r['ID']]
            st.rerun()
        st.markdown("---")

# --- منطق صفحة السلعة والمخزون ---
elif choice == "📦 السلعة والمخزون":
    st.title("📦 إدارة السلعة والمخزون")
    
    if 'editing_stock_id' not in st.session_state:
        s_title_form, s_def_name, s_def_buy, s_def_sell, s_def_qty = "➕ إضافة منتج جديد", "", 0.0, 0.0, 0
        s_btn_label = "حفظ المنتج الجديد"
    else:
        curr_s = st.session_state.db_stock[st.session_state.db_stock["ID"] == st.session_state.editing_stock_id].iloc[0]
        s_title_form = f"🛠️ تعديل المنتج رقم {st.session_state.editing_stock_id}"
        s_def_name, s_def_buy, s_def_sell, s_def_qty = curr_s["المنتج"], float(curr_s["ثمن الشراء"]), float(curr_s["ثمن البيع HT"]), int(curr_s["الكمية"])
        s_btn_label = "تحديث البيانات"

    with st.expander(s_title_form, expanded=('editing_stock_id' in st.session_state)):
        with st.form("stock_form_top", clear_on_submit=True):
            col1, col2 = st.columns(2)
            item_name = col1.text_input("اسم المنتج", value=s_def_name)
            buy_p = col1.number_input("ثمن الشراء (HT)", min_value=0.0, value=s_def_buy)
            sell_p = col2.number_input("ثمن البيع (HT)", min_value=0.0, value=s_def_sell)
            qty = st.number_input("الكمية", min_value=0, value=s_def_qty)
            
            sb1, sb2 = st.columns(2)
            s_submit = sb1.form_submit_button(s_btn_label)
            s_cancel = sb2.form_submit_button("إلغاء / تنظيف")

            if s_submit:
                if 'editing_stock_id' in st.session_state:
                    st.session_state.db_stock.loc[st.session_state.db_stock["ID"] == st.session_state.editing_stock_id, 
                        ["المنتج", "ثمن الشراء", "ثمن البيع HT", "الكمية"]] = [item_name, buy_p, sell_p, qty]
                    del st.session_state.editing_stock_id
                    st.success("✅ تم تحديث المنتج")
                else:
                    new_id = int(st.session_state.db_stock["ID"].max() + 1) if not st.session_state.db_stock.empty else 1
                    new_item = {"ID": new_id, "المنتج": item_name, "الوصف": "", "ثمن الشراء": buy_p, "ثمن البيع HT": sell_p, "الكمية": qty}
                    st.session_state.db_stock = pd.concat([st.session_state.db_stock, pd.DataFrame([new_item])], ignore_index=True)
                    st.success("✅ تم إضافة المنتج")
                st.rerun()
            
            if s_cancel:
                if 'editing_stock_id' in st.session_state: del st.session_state.editing_stock_id
                st.rerun()

    st.markdown("---")
    search_s = st.text_input("🔍 ابحث عن منتج (ID أو اسم):")
    df_s = st.session_state.db_stock
    if search_s:
        df_s = df_s[df_s["المنتج"].str.contains(search_s, case=False) | df_s["ID"].astype(str).str.contains(search_s)]
    
    for i, r in df_s.iterrows():
        col_s1, col_s2, col_s3, col_s4 = st.columns([1, 3, 1, 1])
        col_s1.write(f"`{r['ID']}`")
        col_s2.write(f"**{r['المنتج']}** | {r['ثمن البيع HT']} DH | الكمية: {r['الكمية']}")
        if col_s3.button("📝 تعديل", key=f"edit_s_{r['ID']}"):
            st.session_state.editing_stock_id = r['ID']
            st.rerun()
        if col_s4.button("🗑️ حذف", key=f"del_s_{r['ID']}"):
            st.session_state.db_stock = st.session_state.db_stock[st.session_state.db_stock["ID"] != r['ID']]
            st.rerun()
        st.markdown("---")

# باقي الصفحات (الرئيسية والفاتورة خليهم كيف ما هما)
elif choice == "🏠 الرئيسية":
    st.title("❄️ لوحة تحكم MVAC")
    st.write("إحصائيات سريعة...")

elif choice == "📄 إنشاء فاتورة":
    st.title("📄 إنشاء الفاتورة")
    st.info("هنا غانربطو كلشي للمرحلة الجاية.")
