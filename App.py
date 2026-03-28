import streamlit as st
import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# 1. إعدادات الصفحة
st.set_page_config(page_title="MVAC Control Panel", layout="wide", page_icon="❄️")

# 2. تهيئة قواعد البيانات في الذاكرة (Session State)
if 'db_clients' not in st.session_state:
    st.session_state.db_clients = pd.DataFrame(columns=["ID", "النوع", "الاسم/الشركة", "ICE", "RIB", "الهاتف", "العنوان"])

if 'db_stock' not in st.session_state:
    st.session_state.db_stock = pd.DataFrame(columns=["ID", "المنتج", "ثمن الشراء", "ثمن البيع HT", "الكمية"])

# 3. القائمة الجانبية للتنقل
with st.sidebar:
    st.title("M-VAC Pro")
    st.markdown("---")
    choice = st.radio("اختار الصفحة:", ["🏠 الرئيسية", "👥 إدارة الزبناء", "📦 السلعة والمخزون", "📄 إنشاء فاتورة"])
    st.markdown("---")
    st.info("نظام تسيير MVAC - سفيان")

# --- 1. الصفحة الرئيسية ---
if choice == "🏠 الرئيسية":
    st.title("❄️ لوحة تحكم MVAC")
    st.write(f"مرحباً سفيان. اليوم هو: {pd.Timestamp.now().strftime('%Y-%m-%d')}")
    col1, col2 = st.columns(2)
    col1.metric("إجمالي الزبناء", len(st.session_state.db_clients))
    col2.metric("قطع السلعة في المخزن", len(st.session_state.db_stock))

# --- 2. صفحة إدارة الزبناء ---
elif choice == "👥 إدارة الزبناء":
    st.title("👥 إدارة قاعدة بيانات الزبناء")
    
    # منطق التعديل الفوقاني
    if 'editing_client_id' not in st.session_state:
        c_title, c_def_type, c_def_name, c_def_phone, c_def_ice, c_def_rib, c_def_addr = "➕ إضافة زبون جديد", "Particulier", "", "", "", "", ""
        c_btn = "حفظ الزبون الجديد"
    else:
        curr = st.session_state.db_clients[st.session_state.db_clients["ID"] == st.session_state.editing_client_id].iloc[0]
        c_title, c_def_type, c_def_name, c_def_phone, c_def_ice, c_def_rib, c_def_addr = f"🛠️ تعديل الزبون {st.session_state.editing_client_id}", curr["النوع"], curr["الاسم/الشركة"], curr["الهاتف"], curr["ICE"], curr["RIB"], curr["العنوان"]
        c_btn = "تحديث البيانات"

    with st.expander(c_title, expanded=('editing_client_id' in st.session_state)):
        type_c = st.radio("النوع:", ["Particulier", "Société"], index=0 if c_def_type=="Particulier" else 1, horizontal=True)
        with st.form("c_form"):
            col1, col2 = st.columns(2)
            name = col1.text_input("الاسم / الشركة", value=c_def_name)
            phone = col2.text_input("الهاتف", value=c_def_phone)
            ice = col1.text_input("ICE (للشركات)", value=c_def_ice) if type_c == "Société" else ""
            rib = col2.text_input("RIB (رقم الحساب)", value=c_def_rib)
            addr = st.text_area("العنوان", value=c_def_addr)
            b1, b2 = st.columns(2)
            if b1.form_submit_button(c_btn):
                if name and phone:
                    if 'editing_client_id' in st.session_state:
                        st.session_state.db_clients.loc[st.session_state.db_clients["ID"] == st.session_state.editing_client_id, ["النوع","الاسم/الشركة","الهاتف","ICE","RIB","العنوان"]] = [type_c, name, phone, ice, rib, addr]
                        del st.session_state.editing_client_id
                    else:
                        new_id = int(st.session_state.db_clients["ID"].max() + 1) if not st.session_state.db_clients.empty else 1
                        st.session_state.db_clients = pd.concat([st.session_state.db_clients, pd.DataFrame([{"ID":new_id,"النوع":type_c,"الاسم/الشركة":name,"ICE":ice,"RIB":rib,"الهاتف":phone,"العنوان":addr}])], ignore_index=True)
                    st.rerun()
            if b2.form_submit_button("إلغاء"):
                if 'editing_client_id' in st.session_state: del st.session_state.editing_client_id
                st.rerun()

    st.markdown("---")
    search_c = st.text_input("🔍 بحث عن زبون (اسم أو ID):")
    df_c = st.session_state.db_clients
    if search_c: df_c = df_c[df_c["الاسم/الشركة"].str.contains(search_c, case=False) | df_c["ID"].astype(str).str.contains(search_c)]
    
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
    if 'editing_stock_id' not in st.session_state:
        s_title, s_name, s_buy, s_sell, s_qty = "➕ إضافة منتج", "", 0.0, 0.0, 0
        s_btn = "حفظ المنتج"
    else:
        curr_s = st.session_state.db_stock[st.session_state.db_stock["ID"] == st.session_state.editing_stock_id].iloc[0]
        s_title, s_name, s_buy, s_sell, s_qty = f"🛠️ تعديل المنتج {st.session_state.editing_stock_id}", curr_s["المنتج"], float(curr_s["ثمن الشراء"]), float(curr_s["ثمن البيع HT"]), int(curr_s["الكمية"])
        s_btn = "تحديث المنتج"

    with st.expander(s_title, expanded=('editing_stock_id' in st.session_state)):
        with st.form("s_form"):
            col1, col2 = st.columns(2)
            s_item = col1.text_input("اسم المنتج", value=s_name)
            s_b_p = col1.number_input("ثمن الشراء HT", value=s_buy)
            s_s_p = col2.number_input("ثمن البيع HT", value=s_sell)
            s_q = col2.number_input("الكمية", value=s_qty)
            sb1, sb2 = st.columns(2)
            if sb1.form_submit_button(s_btn):
                if s_item:
                    if 'editing_stock_id' in st.session_state:
                        st.session_state.db_stock.loc[st.session_state.db_stock["ID"] == st.session_state.editing_stock_id, ["المنتج","ثمن الشراء","ثمن البيع HT","الكمية"]] = [s_item, s_b_p, s_s_p, s_q]
                        del st.session_state.editing_stock_id
                    else:
                        nid = int(st.session_state.db_stock["ID"].max() + 1) if not st.session_state.db_stock.empty else 1
                        st.session_state.db_stock = pd.concat([st.session_state.db_stock, pd.DataFrame([{"ID":nid,"المنتج":s_item,"ثمن الشراء":s_b_p,"ثمن البيع HT":s_s_p,"الكمية":s_q}])], ignore_index=True)
                    st.rerun()
            if sb2.form_submit_button("إلغاء"):
                if 'editing_stock_id' in st.session_state: del st.session_state.editing_stock_id
                st.rerun()

    st.markdown("---")
    search_s = st.text_input("🔍 بحث عن منتج:")
    df_s = st.session_state.db_stock
    if search_s: df_s = df_s[df_s["المنتج"].str.contains(search_s, case=False)]
    for i, r in df_s.iterrows():
        sc1, sc2, sc3, sc4 = st.columns([1, 3, 1, 1])
        sc1.write(f"`{r['ID']}`")
        sc2.write(f"**{r['المنتج']}** | البيع: {r['ثمن البيع HT']} DH | الكمية: {r['الكمية']}")
        if sc3.button("📝 تعديل", key=f"es_{r['ID']}"):
            st.session_state.editing_stock_id = r['ID']; st.rerun()
        if sc4.button("🗑️ حذف", key=f"ds_{r['ID']}"):
            st.session_state.db_stock = st.session_state.db_stock[st.session_state.db_stock["ID"] != r['ID']]; st.rerun()

# --- 4. صفحة إنشاء الفاتورة ---
elif choice == "📄 إنشاء فاتورة":
    st.title("📄 إنشاء فاتورة مهنية")
    if st.session_state.db_clients.empty:
        st.warning("⚠️ سجل زبون أولاً.")
    else:
        # اختيار الزبون
        c_list = st.session_state.db_clients["الاسم/الشركة"].tolist()
        selected_client = st.selectbox("اختار الزبون:", c_list)
        c_info = st.session_state.db_clients[st.session_state.db_clients["الاسم/الشركة"] == selected_client].iloc[0]

        col_f1, col_f2 = st.columns(2)
        # اختيار السلعة من المخزن
        if not st.session_state.db_stock.empty:
            items_list = st.session_state.db_stock["المنتج"].tolist()
            selected_item = col_f1.selectbox("اختار المنتج من المخزن:", items_list)
            item_data = st.session_state.db_stock[st.session_state.db_stock["المنتج"] == selected_item].iloc[0]
            price_from_stock = col_f2.number_input("ثمن المنتج (HT)", value=float(item_data["ثمن البيع HT"]))
        else:
            st.info("المخزن خاوي، دخل الثمن يدوياً.")
            price_from_stock = col_f2.number_input("ثمن السلعة (HT)", min_value=0.0)

        work_p = st.number_input("اليد العاملة (Main d'œuvre) HT", min_value=0.0)
        remise = st.number_input("الكوميسيون / خصم (Remise) DH", min_value=0.0)
        
        # الحسابات
        total_ht = (price_from_stock + work_p) - remise
        tva = total_ht * 0.20
        total_ttc = total_ht + tva

        st.markdown(f"### المجموع TTC: **{total_ttc:,.2f} DH**")

        if st.button("🚀 توليد وتحميل الفاتورة PDF"):
            buf = io.BytesIO()
            p = canvas.Canvas(buf, pagesize=letter)
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, 750, f"FACTURE: MVAC")
            p.setFont("Helvetica", 12)
            p.drawString(50, 720, f"Client: {selected_client}")
            p.drawString(50, 705, f"ICE: {c_info['ICE']}")
            p.drawString(50, 690, f"RIB: {c_info['RIB']}")
            p.line(50, 670, 550, 670)
            p.drawString(50, 650, f"Materiel: {price_from_stock:,.2f} DH")
            p.drawString(50, 630, f"Main d'oeuvre: {work_p:,.2f} DH")
            p.drawString(50, 610, f"Remise: -{remise:,.2f} DH")
            p.line(50, 580, 550, 580)
            p.drawString(350, 560, f"TOTAL HT: {total_ht:,.2f} DH")
            p.drawString(350, 540, f"TVA (20%): {tva:,.2f} DH")
            p.setFont("Helvetica-Bold", 14)
            p.drawString(350, 510, f"TOTAL TTC: {total_ttc:,.2f} DH")
            p.save()
            st.download_button("📥 تحميل PDF", buf.getvalue(), f"Facture_{selected_client}.pdf")
