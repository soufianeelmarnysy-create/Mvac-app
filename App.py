import streamlit as st
import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# 1. إعدادات الصفحة
st.set_page_config(page_title="MVAC Control Panel", layout="wide", page_icon="❄️")

# 2. تهيئة قواعد البيانات (Session State)
if 'db_clients' not in st.session_state:
    st.session_state.db_clients = pd.DataFrame(columns=["ID", "النوع", "الاسم/الشركة", "ICE", "RIB", "الهاتف", "العنوان"])

if 'db_stock' not in st.session_state:
    st.session_state.db_stock = pd.DataFrame(columns=["ID", "المنتج", "ثمن الشراء", "ثمن البيع HT", "الكمية"])

# 3. القائمة الجانبية
with st.sidebar:
    st.title("M-VAC Pro")
    st.markdown("---")
    choice = st.radio("اختار الصفحة:", ["🏠 الرئيسية", "👥 إدارة الزبناء", "📦 السلعة والمخزون", "📄 إنشاء فاتورة"])
    st.info("نظام تسيير MVAC - سفيان")

# --- 1. الصفحة الرئيسية ---
if choice == "🏠 الرئيسية":
    st.title("❄️ لوحة تحكم MVAC")
    col1, col2 = st.columns(2)
    col1.metric("إجمالي الزبناء", len(st.session_state.db_clients))
    col2.metric("قطع السلعة", len(st.session_state.db_stock))

# --- 2. صفحة إدارة الزبناء ---
elif choice == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    
    # تحديد وضع الإضافة أو التعديل
    is_editing = 'editing_client_id' in st.session_state
    if not is_editing:
        c_title, c_btn, c_def = "➕ إضافة زبون جديد", "حفظ الزبون الجديد", None
    else:
        c_def = st.session_state.db_clients[st.session_state.db_clients["ID"] == st.session_state.editing_client_id].iloc[0]
        c_title, c_btn = f"🛠️ تعديل الزبون {st.session_state.editing_client_id}", "تحديث البيانات"

    with st.expander(c_title, expanded=is_editing):
        # النوع ديما كيبان
        type_c = st.radio("النوع:", ["Particulier", "Société"], 
                          index=0 if (not is_editing or c_def["النوع"]=="Particulier") else 1, horizontal=True)
        
        with st.form("client_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            # الخانات كتعمر فقط إلا كنا في وضع التعديل، وإلا كتبقى خاوية
            name = col1.text_input("الاسم / الشركة", value=c_def["الاسم/الشركة"] if is_editing else "")
            phone = col2.text_input("الهاتف", value=c_def["الهاتف"] if is_editing else "")
            ice = col1.text_input("ICE (للشركات)", value=c_def["ICE"] if is_editing else "") if type_c == "Société" else ""
            rib = col2.text_input("RIB (رقم الحساب)", value=c_def["RIB"] if is_editing else "")
            addr = st.text_area("العنوان", value=c_def["العنوان"] if is_editing else "")
            
            b1, b2 = st.columns(2)
            if b1.form_submit_button(c_btn):
                if name and phone:
                    if is_editing:
                        st.session_state.db_clients.loc[st.session_state.db_clients["ID"] == st.session_state.editing_client_id, 
                            ["النوع","الاسم/الشركة","الهاتف","ICE","RIB","العنوان"]] = [type_c, name, phone, ice, rib, addr]
                        del st.session_state.editing_client_id
                    else:
                        new_id = int(st.session_state.db_clients["ID"].max() + 1) if not st.session_state.db_clients.empty else 1
                        st.session_state.db_clients = pd.concat([st.session_state.db_clients, pd.DataFrame([{"ID":new_id,"النوع":type_c,"الاسم/الشركة":name,"ICE":ice,"RIB":rib,"الهاتف":phone,"العنوان":addr}])], ignore_index=True)
                    st.success("✅ تم بنجاح")
                    st.rerun() # هادي هي اللي كتخوي الخانات
            
            if b2.form_submit_button("إلغاء / تنظيف"):
                if is_editing: del st.session_state.editing_client_id
                st.rerun()

    st.markdown("---")
    # عرض الزبناء (البحث والحذف)
    search_c = st.text_input("🔍 بحث عن زبون:")
    df_c = st.session_state.db_clients
    if search_c: df_c = df_c[df_c["الاسم/الشركة"].str.contains(search_c, case=False)]
    
    for i, r in df_c.iterrows():
        col_c1, col_c2, col_c3, col_c4 = st.columns([1, 3, 1, 1])
        col_c1.write(f"`{r['ID']}`")
        col_c2.write(f"**{r['الاسم/الشركة']}** - {r['الهاتف']}")
        if col_c3.button("📝 تعديل", key=f"ec_{r['ID']}"):
            st.session_state.editing_client_id = r['ID']
            st.rerun()
        if col_c4.button("🗑️ حذف", key=f"dc_{r['ID']}"):
            st.session_state.db_clients = st.session_state.db_clients[st.session_state.db_clients["ID"] != r['ID']]
            st.rerun()

# --- 3. صفحة السلعة والمخزون ---
elif choice == "📦 السلعة والمخزون":
    st.title("📦 إدارة السلعة")
    is_editing_s = 'editing_stock_id' in st.session_state
    if not is_editing_s:
        s_title, s_btn, s_def = "➕ إضافة منتج", "حفظ المنتج", None
    else:
        s_def = st.session_state.db_stock[st.session_state.db_stock["ID"] == st.session_state.editing_stock_id].iloc[0]
        s_title, s_btn = f"🛠️ تعديل المنتج {st.session_state.editing_stock_id}", "تحديث المنتج"

    with st.expander(s_title, expanded=is_editing_s):
        with st.form("stock_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            s_item = col1.text_input("اسم المنتج", value=s_def["المنتج"] if is_editing_s else "")
            s_b_p = col1.number_input("ثمن الشراء HT", value=float(s_def["ثمن الشراء"]) if is_editing_s else 0.0)
            s_s_p = col2.number_input("ثمن البيع HT", value=float(s_def["ثمن البيع HT"]) if is_editing_s else 0.0)
            s_q = col2.number_input("الكمية", value=int(s_def["الكمية"]) if is_editing_s else 0)
            
            sb1, sb2 = st.columns(2)
            if sb1.form_submit_button(s_btn):
                if s_item:
                    if is_editing_s:
                        st.session_state.db_stock.loc[st.session_state.db_stock["ID"] == st.session_state.editing_stock_id, ["المنتج","ثمن الشراء","ثمن البيع HT","الكمية"]] = [s_item, s_b_p, s_s_p, s_q]
                        del st.session_state.editing_stock_id
                    else:
                        nid = int(st.session_state.db_stock["ID"].max() + 1) if not st.session_state.db_stock.empty else 1
                        st.session_state.db_stock = pd.concat([st.session_state.db_stock, pd.DataFrame([{"ID":nid,"المنتج":s_item,"ثمن الشراء":s_b_p,"ثمن البيع HT":s_s_p,"الكمية":s_q}])], ignore_index=True)
                    st.success("✅ تم")
                    st.rerun()
            if sb2.form_submit_button("إلغاء"):
                if is_editing_s: del st.session_state.editing_stock_id
                st.rerun()

    st.markdown("---")
    # عرض السلعة بالأزرار
    search_s = st.text_input("🔍 بحث عن منتج:")
    df_s = st.session_state.db_stock
    if search_s: df_s = df_s[df_s["المنتج"].str.contains(search_s, case=False)]
    for i, r in df_s.iterrows():
        sc1, sc2, sc3, sc4 = st.columns([1, 3, 1, 1])
        sc1.write(f"`{r['ID']}`")
        sc2.write(f"**{r['المنتج']}** | البيع: {r['ثمن البيع HT']} DH")
        if sc3.button("📝 تعديل", key=f"es_{r['ID']}"):
            st.session_state.editing_stock_id = r['ID']; st.rerun()
        if sc4.button("🗑️ حذف", key=f"ds_{r['ID']}"):
            st.session_state.db_stock = st.session_state.db_stock[st.session_state.db_stock["ID"] != r['ID']]; st.rerun()

# --- 4. صفحة إنشاء الفاتورة ---
elif choice == "📄 إنشاء فاتورة":
    st.title("📄 إنشاء فاتورة")
    if st.session_state.db_clients.empty:
        st.warning("سجل زبون أولاً.")
    else:
        c_list = st.session_state.db_clients["الاسم/الشركة"].tolist()
        sel_c = st.selectbox("اختار الزبون:", c_list)
        
        colf1, colf2 = st.columns(2)
        work = colf1.number_input("اليد العاملة HT", min_value=0.0)
        com = colf2.number_input("الكوميسيون / خصم", min_value=0.0)
        
        if st.button("توليد PDF"):
            st.success(f"فاتورة {sel_c} جاهزة (تحت التطوير للمظهر النهائي)")
