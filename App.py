import streamlit as st
import pandas as pd
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="HVAC Manager - إدارة التكييف", layout="wide")

st.title("❄️  M-VAC للتكييف و التبريد التجاري نضام تسيير الشركةشركة ")
st.sidebar.header("لوحة التحكم")


# قاعدة بيانات وهمية (تقدر تربطها بملف Excel من بعد)
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame([
        {"القطعة": "غاز R410A (كجم)", "الكمية": 20, "الثمن": 150},
        {"القطعة": "محرر (Compressor) 12k", "الكمية": 5, "الثمن": 1200},
        {"القطعة": "أنبوب نحاس 1/4", "الكمية": 50, "الثمن": 40}
    ])

# 1. قسم الفواتير (Invoicing)
menu = st.sidebar.selectbox("اختر القسم", ["صنع فاتورة", "المخزون", "قائمة الزبناء"])

if menu == "صنع فاتورة":
    st.header("📄 إنشاء فاتورة جديدة")
    
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("اسم الزبون")
        service_type = st.selectbox("نوع الخدمة", ["تركيب جديد", "شحن غاز", "صيانة دورية", "إصلاح عطب"])
    with col2:
        date = st.date_input("التاريخ", datetime.now())
        phone = st.text_input("رقم الهاتف")

    st.subheader("التفاصيل والمصاريف")
    items = st.multiselect("اختر السلع المستعملة من المخزون", st.session_state.inventory["القطعة"])
    service_price = st.number_input("ثمن اليد العاملة (DH)", min_value=0)
    
    if st.button("حساب المجموع وصنع الفاتورة"):
        total_parts = st.session_state.inventory[st.session_state.inventory["القطعة"].isin(items)]["الثمن"].sum()
        total_all = total_parts + service_price
        st.success(f"المجموع الإجمالي هو: {total_all} درهم")
        st.info(f"الفاتورة جاهزة للزبون: {client_name}")

# 2. قسم المخزون (Inventory)
elif menu == "المخزون":
    st.header("📦 إدارة المخزون")
    st.table(st.session_state.inventory)
    
    st.subheader("تحديث السلع")
    new_item = st.text_input("إضافة قطعة جديدة")
    if st.button("إضافة"):
        st.write("تمت الإضافة بنجاح")

# 3. قائمة الزبناء
elif menu == "قائمة الزبناء":
    st.header("👥 سجل الزبناء")
    st.write("هنا ستظهر قائمة الزبناء السابقين وعناوينهم.")

import streamlit as st
import pandas as pd
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# إعدادات الصفحة
st.set_page_config(page_title="HVAC Pro Manager", layout="wide")

# تهيئة قاعدة البيانات في "ذاكرة الجلسة" (Session State)
if 'db' not in st.session_state:
    st.session_state.db = {
        'inventory': pd.DataFrame(columns=["القطعة", "الكمية", "الثمن"]),
        'clients': pd.DataFrame(columns=["النوع", "الاسم/الشركة", "ICE", "RIB", "Mail", "Tel", "Lieu"]),
        'invoices': []
    }

st.title("❄️ نظام إدارة التكييف والتبريد التجاري")

menu = st.sidebar.radio("القائمة الرئيسية", ["الزبناء", "المخزون", "الفواتير", "أرشيف PDF"])

# --- 1. قسم الزبناء (إضافة، تحديث، مسح) ---
if menu == "الزبناء":
    st.header("👥 إدارة الزبناء")
    
    with st.expander("➕ إضافة زبون جديد"):
        c_type = st.selectbox("نوع الزبون", ["فردي", "شركة"])
        name = st.text_input("الاسم الكامل / اسم الشركة")
        col1, col2 = st.columns(2)
        with col1:
            ice = st.text_input("ICE (للشركات)")
            rib = st.text_input("RIB")
            mail = st.text_input("البريد الإلكتروني")
        with col2:
            tel = st.text_input("الهاتف")
            lieu = st.text_input("العنوان / الموقع")
        
        if st.button("حفظ الزبون"):
            new_client = {"النوع": c_type, "الاسم/الشركة": name, "ICE": ice, "RIB": rib, "Mail": mail, "Tel": tel, "Lieu": lieu}
            st.session_state.db['clients'] = pd.concat([st.session_state.db['clients'], pd.DataFrame([new_client])], ignore_index=True)
            st.success("تم الحفظ!")

    st.subheader("قائمة الزبناء")
    edited_clients = st.data_editor(st.session_state.db['clients'], num_rows="dynamic")
    if st.button("تحديث قاعدة بيانات الزبناء"):
        st.session_state.db['clients'] = edited_clients
        st.success("تم التحديث!")

# --- 2. قسم المخزون (إضافة، تحديث، مسح) ---
elif menu == "المخزون":
    st.header("📦 إدارة المخزون (السلع)")
    edited_stock = st.data_editor(st.session_state.db['inventory'], num_rows="dynamic")
    if st.button("حفظ تغييرات المخزون"):
        st.session_state.db['inventory'] = edited_stock
        st.success("تم تحديث المخزون!")

# --- 3. قسم الفواتير (صنع، تعديل، PDF) ---
elif menu == "الفواتير":
    st.header("📄 إنشاء فاتورة")
    
    if st.session_state.db['clients'].empty:
        st.warning("يجب إضافة زبون أولاً!")
    else:
        client_choice = st.selectbox("اختر الزبون", st.session_state.db['clients']["الاسم/الشركة"])
        c_info = st.session_state.db['clients'][st.session_state.db['clients']["الاسم/الشركة"] == client_choice].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            service = st.text_area("وصف الإصلاحات / الخدمات")
            price = st.number_input("ثمن الخدمة (DH)", min_value=0)
        with col2:
            items_used = st.multiselect("السلع المستعملة", st.session_state.db['inventory']["القطعة"])
            
        if st.button("توليد الفاتورة PDF"):
            # منطق صنع PDF مبسط
            buf = io.BytesIO()
            c = canvas.Canvas(buf, pagesize=letter)
            c.drawString(100, 750, f"فاتورة لـ: {client_choice}")
            c.drawString(100, 730, f"الخدمة: {service}")
            c.drawString(100, 710, f"المجموع: {price} DH")
            c.save()
            
            inv_data = {"id": len(st.session_state.db['invoices'])+1, "client": client_choice, "total": price, "date": datetime.now(), "pdf": buf.getvalue()}
            st.session_state.db['invoices'].append(inv_data)
            st.success("تم توليد الفاتورة بنجاح!")
            st.download_button("تحميل PDF", buf.getvalue(), file_name=f"invoice_{client_choice}.pdf")

# --- 4. أرشيف الفواتير (تعديل ومسح وتحديث الـ PDF) ---
elif menu == "أرشيف PDF":
    st.header("📂 أرشيف الفواتير")
    for i, inv in enumerate(st.session_state.db['invoices']):
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.write(f"فاتورة {inv['id']} - {inv['client']} - {inv['total']} DH")
        if col2.button("مسح", key=f"del_{i}"):
            st.session_state.db['invoices'].pop(i)
            st.rerun()
        col3.download_button("تحميل", inv['pdf'], file_name=f"fixed_invoice_{i}.pdf", key=f"down_{i}")
import streamlit as st
import pandas as pd
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# إعدادات الصفحة
st.set_page_config(page_title="MVAC Pro Manager", layout="wide")

# الاتصال بـ Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# استبدل 'your-service-account-key.json' باسم ملف مفتاح الخدمة الخاص بك
creds = ServiceAccountCredentials.from_json_keyfile_name('your-service-account-key.json', scope)
client = gspread.authorize(creds)
# استبدل 'MVAC_Database' باسم ملف Google Sheets الخاص بك
spreadsheet = client.open('MVAC_Database')

# تحميل البيانات من Google Sheets
def load_data(sheet_name):
    sheet = spreadsheet.worksheet(sheet_name)
    return pd.DataFrame(sheet.get_all_records())

# حفظ البيانات إلى Google Sheets
def save_data(df, sheet_name):
    sheet = spreadsheet.worksheet(sheet_name)
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

# تهيئة البيانات في "ذاكرة الجلسة" (Session State)
if 'clients' not in st.session_state:
    st.session_state.clients = load_data('Clients')
if 'inventory' not in st.session_state:
    st.session_state.inventory = load_data('Inventory')
if 'invoices' not in st.session_state:
    st.session_state.invoices = [] # لفواتير الـ PDF، يفضل استخدام تخزين ملفات مثل Google Drive

st.title("❄️ نظام MVAC لإدارة التكييف والتبريد التجاري")

menu = st.sidebar.radio("القائمة الرئيسية", ["الزبناء", "المخزون", "الفواتير", "أرشيف PDF"])

# --- 1. قسم الزبناء (إضافة، تحديث، مسح) ---
if menu == "الزبناء":
    st.header("👥 إدارة الزبناء")
    
    with st.expander("➕ إضافة زبون جديد"):
        c_type = st.selectbox("نوع الزبون", ["فردي", "شركة"])
        name = st.text_input("الاسم الكامل / اسم الشركة")
        col1, col2 = st.columns(2)
        with col1:
            ice = st.text_input("ICE (للشركات)")
            rib = st.text_input("RIB")
            mail = st.text_input("البريد الإلكتروني")
        with col2:
            tel = st.text_input("الهاتف")
            lieu = st.text_input("العنوان / الموقع")
        
        if st.button("حفظ الزبون"):
            new_client = {"النوع": c_type, "الاسم/الشركة": name, "ICE": ice, "RIB": rib, "Mail": mail, "Tel": tel, "Lieu": lieu}
            st.session_state.clients = pd.concat([st.session_state.clients, pd.DataFrame([new_client])], ignore_index=True)
            save_data(st.session_state.clients, 'Clients')
            st.success("تم الحفظ في Google Sheets!")

    st.subheader("قائمة الزبناء")
    edited_clients = st.data_editor(st.session_state.clients, num_rows="dynamic")
    if st.button("تحديث قاعدة بيانات الزبناء"):
        st.session_state.clients = edited_clients
        save_data(st.session_state.clients, 'Clients')
        st.success("تم التحديث في Google Sheets!")

# --- 2. قسم المخزون (إضافة، تحديث، مسح) ---
elif menu == "المخزون":
    st.header("📦 إدارة المخزون (السلع)")
    edited_stock = st.data_editor(st.session_state.inventory, num_rows="dynamic")
    if st.button("حفظ تغييرات المخزون"):
        st.session_state.inventory = edited_stock
        save_data(st.session_state.inventory, 'Inventory')
        st.success("تم تحديث المخزون في Google Sheets!")

# --- 3. قسم الفواتير (صنع، تعديل، PDF) ---
elif menu == "الفواتير":
    st.header("📄 إنشاء فاتورة")
    
    if st.session_state.clients.empty:
        st.warning("يجب إضافة زبون أولاً!")
    else:
        client_choice = st.selectbox("اختر الزبون", st.session_state.clients["الاسم/الشركة"])
        
        col1, col2 = st.columns(2)
        with col1:
            service = st.text_area("وصف الإصلاحات / الخدمات")
            price = st.number_input("ثمن الخدمة (DH)", min_value=0)
        with col2:
            items_used = st.multiselect("السلع المستعملة", st.session_state.inventory["القطعة"])
            
        if st.button("توليد الفاتورة PDF"):
            # منطق صنع PDF مبسط
            buf = io.BytesIO()
            c = canvas.Canvas(buf, pagesize=letter)
            c.drawString(100, 750, f"فاتورة MVAC لـ: {client_choice}")
            c.drawString(100, 730, f"الخدمة: {service}")
            c.drawString(100, 710, f"المجموع: {price} DH")
            c.save()
            
            inv_data = {"id": len(st.session_state.invoices)+1, "client": client_choice, "total": price, "date": datetime.now(), "pdf": buf.getvalue()}
            st.session_state.invoices.append(inv_data)
            st.success("تم توليد الفاتورة بنجاح!")
            st.download_button("تحميل PDF", buf.getvalue(), file_name=f"MVAC_invoice_{client_choice}.pdf")

# --- 4. أرشيف الفواتير (تعديل ومسح وتحديث الـ PDF) ---
elif menu == "أرشيف PDF":
    st.header("📂 أرشيف الفواتير")
    # ملاحظة: لحفظ الفواتير بشكل دائم، يفضل تخزين ملفات الـ PDF في مكان مثل Google Drive وربط روابطها هنا.
    for i, inv in enumerate(st.session_state.invoices):
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.write(f"فاتورة {inv['id']} - {inv['client']} - {inv['total']} DH")
        if col2.button("مسح", key=f"del_{i}"):
            st.session_state.invoices.pop(i)
            st.rerun()
        col3.download_button("تحميل", inv['pdf'], file_name=f"fixed_MVAC_invoice_{i}.pdf", key=f"down_{i}")
import streamlit as st
import pandas as pd
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- إعدادات الواجهة ---
st.set_page_config(page_title="MVAC System", layout="wide", page_icon="❄️")

# --- الاتصال بقاعدة البيانات (Google Sheets) ---
def init_connection():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
        client = gspread.authorize(creds)
        # تأكد أن اسم الملف مطابق لما في جوجل درايف
        return client.open("MVAC_Database")
    except:
        return None

db = init_connection()

def load_data(sheet_name):
    if db:
        sheet = db.worksheet(sheet_name)
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    return pd.DataFrame()

def save_data(df, sheet_name):
    if db:
        sheet = db.worksheet(sheet_name)
        sheet.clear()
        sheet.update([df.columns.values.tolist()] + df.values.tolist())

# --- تحميل البيانات في الذاكرة ---
if 'clients' not in st.session_state:
    st.session_state.clients = load_data("Clients")
if 'inventory' not in st.session_state:
    st.session_state.inventory = load_data("Inventory")
if 'invoices_list' not in st.session_state:
    st.session_state.invoices_list = []

# --- الهيكل الجانبي ---
st.sidebar.title("❄️ تطبيق MVAC")
menu = st.sidebar.radio("القائمة الرئيسية", ["👤 الزبناء", "📦 المخزون", "📄 الفواتير الجديد", "📂 أرشيف PDF"])

# --- 1. إدارة الزبناء (شركات وأفراد) ---
if menu == "👤 الزبناء":
    st.header("إدارة الزبناء (تحديث ومسح)")
    
    with st.expander("➕ إضافة زبون جديد"):
        c_type = st.selectbox("نوع الزبون", ["شركة", "زبون عادي"])
        name = st.text_input("الاسم الكامل / اسم الشركة")
        col1, col2 = st.columns(2)
        with col1:
            ice = st.text_input("ICE (خاص بالشركات)")
            rib = st.text_input("RIB")
            mail = st.text_input("البريد الإلكتروني")
        with col2:
            tel = st.text_input("رقم الهاتف")
            lieu = st.text_input("العنوان (Lieu)")
        
        if st.button("حفظ الزبون"):
            new_data = {"النوع": c_type, "الاسم/الشركة": name, "ICE": ice, "RIB": rib, "Mail": mail, "Tel": tel, "Lieu": lieu}
            st.session_state.clients = pd.concat([st.session_state.clients, pd.DataFrame([new_data])], ignore_index=True)
            save_data(st.session_state.clients, "Clients")
            st.success("تم حفظ الزبون بنجاح!")

    st.subheader("تعديل أو مسح الزبناء")
    # خاصية التعديل المباشر والمسح من الجدول
    edited_df = st.data_editor(st.session_state.clients, num_rows="dynamic", key="clients_editor")
    if st.button("تأكيد التحديثات (الزبناء)"):
        st.session_state.clients = edited_df
        save_data(st.session_state.clients, "Clients")
        st.success("تم تحديث البيانات!")

# --- 2. إدارة المخزون (السلع) ---
elif menu == "📦 المخزون":
    st.header("إدارة السلع والمخزون")
    st.write("يمكنك إضافة سلع جديدة، تحديث الثمن، أو مسح قطعة من الجدول مباشرة.")
    
    edited_stock = st.data_editor(st.session_state.inventory, num_rows="dynamic", key="stock_editor")
    if st.button("حفظ تغييرات المخزون"):
        st.session_state.inventory = edited_stock
        save_data(st.session_state.inventory, "Inventory")
        st.success("تم تحديث المخزون!")

# --- 3. صنع الفواتير (إصلاحات وإضافات) ---
elif menu == "📄 الفواتير الجديد":
    st.header("إنشاء فاتورة MVAC")
    
    if st.session_state.clients.empty:
        st.error("المرجو إضافة زبون أولاً في قسم الزبناء.")
    else:
        client_name = st.selectbox("اختر الزبون", st.session_state.clients["الاسم/الشركة"])
        client_info = st.session_state.clients[st.session_state.clients["الاسم/الشركة"] == client_name].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            details = st.text_area("تفاصيل الإصلاحات والإضافات")
            service_fee = st.number_input("ثمن اليد العاملة (DH)", min_value=0)
        with col2:
            parts = st.multiselect("السلع المستعملة من المخزون", st.session_state.inventory["القطعة"])
            
        if st.button("توليد الفاتورة PDF"):
            # صنع الـ PDF
            buf = io.BytesIO()
            c = canvas.Canvas(buf, pagesize=letter)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(250, 750, "FACTURE MVAC")
            c.setFont("Helvetica", 12)
            c.drawString(50, 700, f"Client: {client_name}")
            c.drawString(50, 680, f"Type: {client_info['النوع']}")
            c.drawString(50, 660, f"ICE: {client_info['ICE']} | TEL: {client_info['Tel']}")
            c.line(50, 640, 550, 640)
            c.drawString(50, 620, f"Details: {details}")
            c.drawString(50, 600, f"Service Price: {service_fee} DH")
            c.drawString(50, 580, f"Parts Used: {', '.join(parts)}")
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, 540, f"TOTAL: {service_fee} DH (Plus parts cost)")
            c.save()
            
            # حفظ في الأرشيف المؤقت
            st.session_state.invoices_list.append({
                "client": client_name,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "pdf": buf.getvalue()
            })
            st.success("تم صنع الفاتورة بنجاح!")
            st.download_button("تحميل الفاتورة PDF", buf.getvalue(), file_name=f"MVAC_{client_name}.pdf")

# --- 4. أرشيف الفواتير ---
elif menu == "📂 أرشيف PDF":
    st.header("أرشيف الفواتير السابقة")
    if not st.session_state.invoices_list:
        st.write("لا توجد فواتير في الأرشيف حالياً.")
    else:
        for i, inv in enumerate(st.session_state.invoices_list):
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.write(f"📄 {inv['client']} - {inv['date']}")
            col2.download_button("تحميل PDF", inv['pdf'], file_name=f"MVAC_Archived_{i}.pdf", key=f"dl_{i}")
            if col3.button("مسح الفاتورة", key=f"del_inv_{i}"):
                st.session_state.invoices_list.pop(i)
                st.rerun()

import streamlit as st
import pandas as pd
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- إعدادات الواجهة ---
st.set_page_config(page_title="MVAC System v2.0", layout="wide", page_icon="❄️")

# --- الاتصال بـ Google Sheets ---
def init_connection():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
        client = gspread.authorize(creds)
        return client.open("MVAC_Database")
    except Exception as e:
        st.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
        return None

db = init_connection()

def load_data(sheet_name):
    if db:
        try:
            sheet = db.worksheet(sheet_name)
            data = sheet.get_all_records()
            return pd.DataFrame(data)
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def save_data(df, sheet_name):
    if db:
        sheet = db.worksheet(sheet_name)
        sheet.clear()
        # إضافة العناوين ثم البيانات
        sheet.update([df.columns.values.tolist()] + df.values.tolist())

# --- تهيئة البيانات ---
if 'clients' not in st.session_state:
    st.session_state.clients = load_data("Clients")
if 'inventory' not in st.session_state:
    st.session_state.inventory = load_data("Inventory")
if 'invoices_list' not in st.session_state:
    st.session_state.invoices_list = []

# --- القائمة الجانبية ---
st.sidebar.markdown(f"<h1 style='text-align: center;'>❄️ MVAC</h1>", unsafe_ui_label=True)
menu = st.sidebar.radio("انتقل إلى:", ["👤 إدارة الزبناء", "📦 إدارة المخزون", "📄 إنشاء فاتورة", "📂 أرشيف الفواتير"])

# --- 1. إدارة الزبناء ---
if menu == "👤 إدارة الزبناء":
    st.header("إدارة الزبناء والشركات")
    
    with st.expander("➕ إضافة زبون/شركة جديد"):
        col1, col2 = st.columns(2)
        with col1:
            c_type = st.selectbox("نوع الزبون", ["شركة", "زبون عادي"])
            name = st.text_input("الاسم الكامل / اسم الشركة")
            ice = st.text_input("ICE (خاص بالشركات)")
        with col2:
            tel = st.text_input("رقم الهاتف")
            mail = st.text_input("البريد الإلكتروني")
            lieu = st.text_input("الموقع / العنوان")
        rib = st.text_input("RIB (الحساب البنكي)")
        
        if st.button("حفظ في قاعدة البيانات"):
            new_client = {"النوع": c_type, "الاسم/الشركة": name, "ICE": ice, "RIB": rib, "Mail": mail, "Tel": tel, "Lieu": lieu}
            st.session_state.clients = pd.concat([st.session_state.clients, pd.DataFrame([new_client])], ignore_index=True)
            save_data(st.session_state.clients, "Clients")
            st.success(f"تم تسجيل {name} بنجاح!")

    st.subheader("تعديل أو حذف الزبناء")
    # محرر البيانات التفاعلي
    updated_clients = st.data_editor(st.session_state.clients, num_rows="dynamic", key="cl_edit")
    if st.button("تحديث الكل"):
        st.session_state.clients = updated_clients
        save_data(updated_clients, "Clients")
        st.toast("تم التحديث!")

# --- 2. إدارة المخزون ---
elif menu == "📦 إدارة المخزون":
    st.header("تتبع السلع وقطع الغيار")
    st.info("يمكنك تعديل الكميات أو الأثمنة مباشرة من الجدول أدناه.")
    
    updated_stock = st.data_editor(st.session_state.inventory, num_rows="dynamic", key="st_edit")
    if st.button("حفظ تغييرات السلع"):
        st.session_state.inventory = updated_stock
        save_data(updated_stock, "Inventory")
        st.success("تم تحديث المخزون!")

# --- 3. إنشاء فاتورة ---
elif menu == "📄 إنشاء فاتورة":
    st.header("صناعة فاتورة احترافية")
    
    if st.session_state.clients.empty:
        st.warning("المرجو إضافة زبناء أولاً.")
    else:
        c_name = st.selectbox("اختر الزبون", st.session_state.clients["الاسم/الشركة"])
        c_info = st.session_state.clients[st.session_state.clients["الاسم/الشركة"] == c_name].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            service_desc = st.text_area("وصف الإصلاحات / الإضافات")
            labor_cost = st.number_input("ثمن اليد العاملة (DH)", min_value=0.0)
        with col2:
            selected_items = st.multiselect("السلع المستخدمة", st.session_state.inventory["القطعة"])
            
        if st.button("توليد ملف PDF"):
            # حساب إجمالي السلع
            items_df = st.session_state.inventory[st.session_state.inventory["القطعة"].isin(selected_items)]
            total_items = items_df["الثمن"].sum()
            grand_total = total_items + labor_cost
            
            # صنع PDF
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            p.setTitle(f"Invoice_{c_name}")
            
            # تصميم الفاتورة
            p.setFont("Helvetica-Bold", 20)
            p.drawString(240, 750, "FACTURE MVAC")
            p.setFont("Helvetica", 10)
            p.drawString(50, 720, f"Date: {datetime.now().strftime('%d/%m/%Y')}")
            
            p.line(50, 710, 550, 710)
            p.drawString(50, 690, f"Client: {c_name}")
            p.drawString(50, 675, f"ICE: {c_info['ICE']}")
            p.drawString(50, 660, f"Lieu: {c_info['Lieu']}")
            
            p.drawString(50, 630, "Description des travaux:")
            p.drawString(70, 615, f"- {service_desc}")
            
            p.line(50, 550, 550, 550)
            p.drawString(50, 530, f"Total Pieces: {total_items} DH")
            p.drawString(50, 515, f"Main d'oeuvre: {labor_cost} DH")
            p.setFont("Helvetica-Bold", 12)
            p.drawString(400, 480, f"TOTAL NET: {grand_total} DH")
            
            p.save()
            
            # حفظ في الأرشيف
            st.session_state.invoices_list.append({
                "client": c_name,
                "total": grand_total,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "pdf": buffer.getvalue()
            })
            st.success("تم إنشاء الفاتورة!")
            st.download_button("تحميل الفاتورة PDF", buffer.getvalue(), file_name=f"MVAC_{c_name}.pdf")

# --- 4. الأرشيف ---
elif menu == "📂 أرشيف الفواتير":
    st.header("سجل العمليات السابقة")
    if not st.session_state.invoices_list:
        st.write("الأرشيف فارغ حالياً.")
    else:
        for i, inv in enumerate(st.session_state.invoices_list):
            with st.container():
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"**{inv['client']}** | {inv['total']} DH | {inv['date']}")
                c2.download_button("تحميل", inv['pdf'], file_name=f"MVAC_Old_{i}.pdf", key=f"d{i}")
                if c3.button("مسح", key=f"r{i}"):
                    st.session_state.invoices_list.pop(i)
                    st.rerun()
                st.divider()
import streamlit as st
import pandas as pd
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- إعدادات الصفحة ---
st.set_page_config(page_title="MVAC System - TVA Edition", layout="wide", page_icon="❄️")

# --- الاتصال بـ Google Sheets ---
def init_connection():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
        client = gspread.authorize(creds)
        return client.open("MVAC_Database")
    except Exception as e:
        return None

db = init_connection()

def load_data(sheet_name):
    if db:
        try:
            sheet = db.worksheet(sheet_name)
            return pd.DataFrame(sheet.get_all_records())
        except: return pd.DataFrame()
    return pd.DataFrame()

def save_data(df, sheet_name):
    if db:
        sheet = db.worksheet(sheet_name)
        sheet.clear()
        sheet.update([df.columns.values.tolist()] + df.values.tolist())

# --- تهيئة البيانات ---
if 'clients' not in st.session_state:
    st.session_state.clients = load_data("Clients")
if 'inventory' not in st.session_state:
    st.session_state.inventory = load_data("Inventory")
if 'invoices_history' not in st.session_state:
    st.session_state.invoices_history = []

# --- الواجهة الجانبية ---
st.sidebar.title("❄️ MVAC Pro")
menu = st.sidebar.radio("القائمة", ["👤 الزبناء", "📦 المخزون", "📄 فاتورة جديدة (TVA)", "📂 الأرشيف"])

# --- 1. إدارة الزبناء ---
if menu == "👤 الزبناء":
    st.header("إدارة الزبناء والشركات")
    with st.expander("➕ إضافة زبون"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("الاسم / الشركة")
            c_type = st.selectbox("النوع", ["شركة", "فرد"])
            ice = st.text_input("ICE")
        with col2:
            tel = st.text_input("الهاتف")
            lieu = st.text_input("العنوان")
            rib = st.text_input("RIB")
        
        if st.button("حفظ الزبون"):
            new_c = {"النوع": c_type, "الاسم/الشركة": name, "ICE": ice, "RIB": rib, "Tel": tel, "Lieu": lieu}
            st.session_state.clients = pd.concat([st.session_state.clients, pd.DataFrame([new_c])], ignore_index=True)
            save_data(st.session_state.clients, "Clients")
            st.success("تم الحفظ!")

    edited_clients = st.data_editor(st.session_state.clients, num_rows="dynamic")
    if st.button("تحديث قاعدة البيانات"):
        save_data(edited_clients, "Clients")
        st.success("تم التحديث!")

# --- 2. إدارة المخزون ---
elif menu == "📦 المخزون":
    st.header("إدارة السلع")
    edited_stock = st.data_editor(st.session_state.inventory, num_rows="dynamic")
    if st.button("تحديث المخزون"):
        save_data(edited_stock, "Inventory")
        st.success("تم التحديث!")

# --- 3. فاتورة جديدة مع TVA ---
elif menu == "📄 فاتورة جديدة (TVA)":
    st.header("إنشاء فاتورة احترافية")
    
    if st.session_state.clients.empty:
        st.error("أضف زبوناً أولاً!")
    else:
        client_name = st.selectbox("اختر الزبون", st.session_state.clients["الاسم/الشركة"])
        c_info = st.session_state.clients[st.session_state.clients["الاسم/الشركة"] == client_name].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            service = st.text_area("وصف العمل (Désignation)")
            base_price = st.number_input("ثمن الخدمة (HT)", min_value=0.0)
            tva_rate = st.selectbox("نسبة الضريبة TVA %", [20, 14, 10, 7, 0])
        with col2:
            selected_parts = st.multiselect("القطع المستعملة", st.session_state.inventory["القطعة"])
            
        # الحسابات
        parts_total = st.session_state.inventory[st.session_state.inventory["القطعة"].isin(selected_parts)]["الثمن"].sum()
        total_ht = base_price + parts_total
        tva_amount = total_ht * (tva_rate / 100)
        total_ttc = total_ht + tva_amount

        st.divider()
        st.write(f"**Total HT:** {total_ht:.2f} DH")
        st.write(f"**TVA ({tva_rate}%):** {tva_amount:.2f} DH")
        st.write(f"### **Total TTC: {total_ttc:.2f} DH**")

        if st.button("توليد الفاتورة وتحميلها"):
            buf = io.BytesIO()
            p = canvas.Canvas(buf, pagesize=letter)
            
            # رأس الفاتورة
            p.setFont("Helvetica-Bold", 22)
            p.drawCentredString(300, 750, "FACTURE MVAC")
            p.setFont("Helvetica", 10)
            p.drawString(50, 710, f"Date: {datetime.now().strftime('%d/%m/%Y')}")
            p.drawString(50, 695, f"Client: {client_name}")
            p.drawString(50, 680, f"ICE: {c_info['ICE']}")
            p.drawString(400, 695, f"Lieu: {c_info['Lieu']}")
            
            # الجدول
            p.line(50, 660, 550, 660)
            p.drawString(60, 645, "Designation")
            p.drawString(450, 645, "Total HT")
            p.line(50, 640, 550, 640)
            
            p.drawString(60, 620, f"Service: {service[:50]}...")
            p.drawString(60, 605, f"Pieces: {', '.join(selected_parts)[:50]}...")
            p.drawString(450, 615, f"{total_ht:.2f} DH")
            
            # حسابات النهاية
            p.line(350, 550, 550, 550)
            p.drawString(360, 535, f"Total HT:")
            p.drawRightString(540, 535, f"{total_ht:.2f} DH")
            p.drawString(360, 520, f"TVA ({tva_rate}%):")
            p.drawRightString(540, 520, f"{tva_amount:.2f} DH")
            p.setFont("Helvetica-Bold", 12)
            p.drawString(360, 495, f"TOTAL TTC:")
            p.drawRightString(540, 495, f"{total_ttc:.2f} DH")
            
            # تذييل
            p.setFont("Helvetica-Oblique", 8)
            p.drawString(50, 100, f"RIB: {c_info['RIB']}")
            p.save()
            
            st.session_state.invoices_history.append({"client": client_name, "total": total_ttc, "pdf": buf.getvalue()})
            st.download_button("اضغط هنا لتحميل الفاتورة PDF", buf.getvalue(), file_name=f"MVAC_{client_name}.pdf", mime="application/pdf")

# --- 4. الأرشيف ---
elif menu == "📂 الأرشيف":
    st.header("سجل الفواتير")
    for i, inv in enumerate(st.session_state.invoices_history):
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.write(f"📄 {inv['client']} - {inv['total']:.2f} TTC")
        col2.download_button("تحميل", inv['pdf'], file_name=f"MVAC_Archived_{i}.pdf", key=f"d{i}")
        if col3.button("حذف", key=f"del{i}"):
            st.session_state.invoices_history.pop(i)
            st.rerun()
import streamlit as st
import pandas as pd
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
# مكتبات إضافية للتعامل مع الصور والعربية
from PIL import Image
from arabic_reshaper import reshape
from bidi.algorithm import get_display
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- إعدادات الصفحة ---
st.set_page_config(page_title="MVAC System Pro - v4.0", layout="wide", page_icon="❄️")

# --- محاولة تثبيت الخطوط العربية ---
# ملاحظة: لظهور العربية بشكل صحيح في PDF، يجب وضع ملف خط يدعم العربية (مثل Sakkal_Majalla.ttf) في مجلد التطبيق.
# إذا لم يتوفر، سيتم استخدام التنسيق اللاتيني فقط.
try:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    # pdfmetrics.registerFont(TTFont('Arabic', 'Sakkal_Majalla.ttf')) # فعل هذا السطر عند توفر ملف الخط
    font_setup = True
except:
    font_setup = False

# --- الاتصال بـ Google Sheets ---
def init_connection():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # تأكد من اسم ملف الـ JSON
        creds = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
        client = gspread.authorize(creds)
        # تأكد من اسم ملف الـ Google Sheets
        return client.open("MVAC_Database")
    except Exception as e:
        st.error(f"خطأ في الاتصال: {e}")
        return None

db = init_connection()

def load_data(sheet_name):
    if db:
        try:
            sheet = db.worksheet(sheet_name)
            return pd.DataFrame(sheet.get_all_records())
        except: return pd.DataFrame()
    return pd.DataFrame()

def save_data(df, sheet_name):
    if db:
        try:
            sheet = db.worksheet(sheet_name)
            sheet.clear()
            sheet.update([df.columns.values.tolist()] + df.values.tolist())
        except Exception as e:
            st.error(f"خطأ في حفظ البيانات: {e}")

# --- تهيئة البيانات ---
if 'clients' not in st.session_state:
    st.session_state.clients = load_data("Clients")
if 'inventory' not in st.session_state:
    st.session_state.inventory = load_data("Inventory")
if 'invoices_history' not in st.session_state:
    st.session_state.invoices_history = []

# --- دوال مساعدة للعربية (اختيارية) ---
def format_arabic(text):
    if not font_setup or not text: return text
    try:
        reshaped_text = reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except:
        return text

# --- الواجهة الجانبية ---
# عرض اللوغو في القائمة الجانبية
try:
    logo_image = Image.open('mvac_logo.png')
    st.sidebar.image(logo_image, use_column_width=True)
except:
    st.sidebar.title("❄️ MVAC Pro")

menu = st.sidebar.radio("القائمة", ["👤 الزبناء", "📦 المخزون", "📄 فاتورة جديدة (TVA)", "📂 الأرشيف"])

# --- 1. إدارة الزبناء ---
if menu == "👤 الزبناء":
    st.header("إدارة الزبناء والشركات")
    with st.expander("➕ إضافة زبون"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("الاسم / الشركة")
            c_type = st.selectbox("النوع", ["شركة", "فرد"])
            ice = st.text_input("ICE")
        with col2:
            tel = st.text_input("الهاتف")
            lieu = st.text_input("العنوان")
            rib = st.text_input("RIB")
        
        if st.button("حفظ الزبون"):
            new_c = {"النوع": c_type, "الاسم/الشركة": name, "ICE": ice, "RIB": rib, "Tel": tel, "Lieu": lieu}
            st.session_state.clients = pd.concat([st.session_state.clients, pd.DataFrame([new_c])], ignore_index=True)
            save_data(st.session_state.clients, "Clients")
            st.success("تم الحفظ!")

    st.subheader("تعديل أو مسح الزبناء")
    edited_clients = st.data_editor(st.session_state.clients, num_rows="dynamic", key="cl_edit")
    if st.button("تحديث قاعدة البيانات (الزبناء)"):
        save_data(edited_clients, "Clients")
        st.success("تم التحديث!")

# --- 2. إدارة المخزون ---
elif menu == "📦 المخزون":
    st.header("إدارة السلع والمخزون")
    edited_stock = st.data_editor(st.session_state.inventory, num_rows="dynamic", key="st_edit")
    if st.button("تحديث المخزون"):
        save_data(edited_stock, "Inventory")
        st.success("تم التحديث!")

# --- 3. فاتورة جديدة مع TVA واللوغو ---
elif menu == "📄 فاتورة جديدة (TVA)":
    st.header("إنشاء فاتورة احترافية")
    
    if st.session_state.clients.empty:
        st.error("أضف زبوناً أولاً!")
    else:
        client_name = st.selectbox("اختر الزبون", st.session_state.clients["الاسم/الشركة"])
        c_info = st.session_state.clients[st.session_state.clients["الاسم/الشركة"] == client_name].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            service = st.text_area("وصف العمل (Désignation)")
            base_price = st.number_input("ثمن الخدمة (HT)", min_value=0.0)
            tva_rate = st.selectbox("نسبة الضريبة TVA %", [20, 14, 10, 7, 0])
        with col2:
            selected_parts = st.multiselect("القطع المستعملة", st.session_state.inventory["القطعة"])
            # إضافة الكميات لكل قطعة (اختياري، تبسيط الآن)
            
        # الحسابات
        parts_total = 0
        if selected_parts:
             parts_total = st.session_state.inventory[st.session_state.inventory["القطعة"].isin(selected_parts)]["الثمن"].sum()
        
        total_ht = base_price + parts_total
        tva_amount = total_ht * (tva_rate / 100)
        total_ttc = total_ht + tva_amount

        st.divider()
        st.markdown(f"**Total HT:** <span style='color:#4CAF50'>{total_ht:.2f} DH</span>", unsafe_allow_html=True)
        st.markdown(f"**TVA ({tva_rate}%):** <span style='color:#FF9800'>{tva_amount:.2f} DH</span>", unsafe_allow_html=True)
        st.write(f"### **Total TTC: <span style='color:#2196F3'>{total_ttc:.2f} DH</span>**", unsafe_allow_html=True)

        if st.button("توليد الفاتورة وتحميلها (PDF)"):
            with st.spinner("جاري صنع الفاتورة..."):
                buf = io.BytesIO()
                p = canvas.Canvas(buf, pagesize=letter)
                
                # إعداد الخطوط
                use_arabic = font_setup and False # فعل هذا إذا أردت العربية (يتطلب ملف خط)
                font_name = 'Arabic' if use_arabic else 'Helvetica'
                font_bold = 'Arabic' if use_arabic else 'Helvetica-Bold' # Helvetica-Bold لا تدعم العربية

                # 1. وضع اللوغو (أعلى الفاتورة)
                try:
                    p.drawInlineImage('mvac_logo.png', 50, 680, width=150, height=100)
                except:
                    p.setFont("Helvetica-Bold", 30)
                    p.drawCentredString(300, 750, "MVAC") # احتياط إذا لم توجد الصورة

                # 2. رأس الفاتورة
                p.setFont("Helvetica-Bold", 24)
                p.drawCentredString(350, 750, format_arabic("FACTURE"))
                p.setFont("Helvetica", 10)
                p.drawString(450, 720, f"Date: {datetime.now().strftime('%d/%m/%Y')}")
                p.drawString(450, 705, f"No: {datetime.now().strftime('%y%m%d%H%M')}")
                
                # معلومات الزبون
                p.setFont("Helvetica-Bold", 12)
                p.drawString(50, 650, format_arabic("Client Information:"))
                p.setFont("Helvetica", 10)
                p.drawString(70, 635, f"Nom/Société: {client_name}")
                p.drawString(70, 620, f"ICE: {c_info['ICE']}")
                p.drawString(70, 605, f"Lieu: {c_info['Lieu']}")
                p.drawString(70, 590, f"Tel: {c_info['Tel']}")

                # 3. الجدول
                p.setStrokeColor(colors.gray)
                p.line(50, 560, 550, 560)
                p.setFont("Helvetica-Bold", 11)
                p.drawString(60, 545, format_arabic("Désignation / description"))
                p.drawRightString(540, 545, format_arabic("Prix Total HT (DH)"))
                p.line(50, 540, 550, 540)
                
                p.setFont("Helvetica", 10)
                # خدمة اليد العاملة
                y_pos = 520
                if base_price > 0:
                    p.drawString(60, y_pos, f"Service / Main d'oeuvre: {service[:60]}...")
                    p.drawRightString(540, y_pos, f"{base_price:.2f}")
                    y_pos -= 20

                # القطع المستعملة
                if selected_parts:
                    p.drawString(60, y_pos, f"Pièces / Fournitures: {', '.join(selected_parts)[:60]}...")
                    p.drawRightString(540, y_pos, f"{parts_total:.2f}")
                    y_pos -= 30

                # 4. حسابات النهاية
                p.line(350, y_pos, 550, y_pos)
                y_pos -= 20
                p.setFont("Helvetica", 11)
                p.drawString(360, y_pos, format_arabic("Total HT:"))
                p.drawRightString(540, y_pos, f"{total_ht:.2f}")
                
                y_pos -= 15
                p.drawString(360, y_pos, f"TVA ({tva_rate}%):")
                p.drawRightString(540, y_pos, f"{tva_amount:.2f}")
                
                y_pos -= 25
                p.setFont("Helvetica-Bold", 13)
                p.drawString(360, y_pos, format_arabic("TOTAL TTC:"))
                p.drawRightString(540, y_pos, f"{total_ttc:.2f}")
                
                # 5. تذييل (معلومات قانونية وبنكية)
                p.setStrokeColor(colors.black)
                p.line(50, 150, 550, 150)
                p.setFont("Helvetica-Oblique", 9)
                p.drawCentredString(300, 135, "MVAC - Installation et Maintenance de Climatisation et Réfrigération Commerciale")
                p.drawCentredString(300, 120, f"Informations de paiement (RIB): {c_info['RIB']}")
                p.drawCentredString(300, 105, "Merci de votre confiance!")

                p.save()
                
                # حفظ في أرشيف الجلسة
                st.session_state.invoices_history.append({"client": client_name, "total": total_ttc, "pdf": buf.getvalue()})
                
                # زر التحميل
                st.download_button(f"اضغط هنا لتحميل فاتورة {client_name}", buf.getvalue(), file_name=f"MVAC_{client_name}.pdf", mime="application/pdf")

# --- 4. الأرشيف ---
elif menu == "📂 الأرشيف":
    st.header("سجل الفواتير المنشأة")
    if not st.session_state.invoices_history:
        st.write("الأرشيف فارغ حالياً.")
    else:
        for i, inv in enumerate(st.session_state.invoices_history):
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.markdown(f"**{inv['client']}** | {inv['total']:.2f} DH TTC")
                col2.download_button("تحميل PDF", inv['pdf'], file_name=f"MVAC_Archived_{i}.pdf", key=f"d{i}", mime="application/pdf")
                if col3.button("مسح من الأرشيف", key=f"del{i}"):
                    st.session_state.invoices_history.pop(i)
                    st.rerun()
                st.divider()
import streamlit as st
import pandas as pd
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from PIL import Image
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. قاموس اللغات (Translations) ---
LANGUAGES = {
    "العربية": {
        "title": "نظام MVAC لإدارة التكييف",
        "menu_clients": "👤 الزبناء",
        "menu_stock": "📦 المخزون",
        "menu_invoice": "📄 فاتورة جديدة",
        "menu_archive": "📂 الأرشيف",
        "add_client": "إضافة زبون جديد",
        "client_name": "الاسم / الشركة",
        "type": "النوع",
        "save": "حفظ",
        "update": "تحديث",
        "designation": "وصف العمل",
        "price_ht": "الثمن (HT)",
        "tva": "الضريبة TVA %",
        "generate_pdf": "توليد وتحميل PDF",
        "total": "المجموع الإجمالي",
        "lang_label": "اختر اللغة / Select Language"
    },
    "Français": {
        "title": "Système MVAC - Gestion HVAC",
        "menu_clients": "👤 Clients",
        "menu_stock": "📦 Stock",
        "menu_invoice": "📄 Nouvelle Facture",
        "menu_archive": "📂 Archives",
        "add_client": "Ajouter un client",
        "client_name": "Nom / Société",
        "type": "Type",
        "save": "Enregistrer",
        "update": "Mettre à jour",
        "designation": "Désignation",
        "price_ht": "Prix HT",
        "tva": "Taux TVA %",
        "generate_pdf": "Générer et Télécharger PDF",
        "total": "Total Global",
        "lang_label": "Choisir la langue"
    },
    "English": {
        "title": "MVAC Management System",
        "menu_clients": "👤 Clients",
        "menu_stock": "📦 Inventory",
        "menu_invoice": "📄 New Invoice",
        "menu_archive": "📂 Archive",
        "add_client": "Add New Client",
        "client_name": "Name / Company",
        "type": "Type",
        "save": "Save",
        "update": "Update",
        "designation": "Description",
        "price_ht": "Price HT",
        "tva": "VAT Rate %",
        "generate_pdf": "Generate & Download PDF",
        "total": "Grand Total",
        "lang_label": "Select Language"
    }
}

# --- إعدادات الصفحة ---
st.set_page_config(page_title="MVAC Multi-Lang", layout="wide", page_icon="❄️")

# --- اختيار اللغة (Sidebar) ---
selected_lang = st.sidebar.selectbox("🌐 Language", list(LANGUAGES.keys()))
texts = LANGUAGES[selected_lang]

# --- عرض اللوغو ---
try:
    st.sidebar.image('mvac_logo.png', use_column_width=True)
except:
    st.sidebar.title("MVAC")

# --- الاتصال بـ Google Sheets ---
def init_connection():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
        client = gspread.authorize(creds)
        return client.open("MVAC_Database")
    except: return None

db = init_connection()

def load_data(sheet):
    if db:
        try: return pd.DataFrame(db.worksheet(sheet).get_all_records())
        except: return pd.DataFrame()
    return pd.DataFrame()

# تهيئة البيانات
if 'clients' not in st.session_state: st.session_state.clients = load_data("Clients")
if 'inventory' not in st.session_state: st.session_state.inventory = load_data("Inventory")
if 'invoices' not in st.session_state: st.session_state.invoices = []

# --- القائمة الرئيسية ---
menu = st.sidebar.radio(texts["lang_label"], [texts["menu_clients"], texts["menu_stock"], texts["menu_invoice"], texts["menu_archive"]])

# --- 1. قسم الزبناء ---
if menu == texts["menu_clients"]:
    st.header(texts["menu_clients"])
    with st.expander(texts["add_client"]):
        name = st.text_input(texts["client_name"])
        ice = st.text_input("ICE")
        tel = st.text_input("Tel")
        if st.button(texts["save"]):
            st.success("Saved / تم الحفظ")

    st.subheader(texts["update"])
    st.data_editor(st.session_state.clients, num_rows="dynamic")

# --- 2. قسم المخزون ---
elif menu == texts["menu_stock"]:
    st.header(texts["menu_stock"])
    st.data_editor(st.session_state.inventory, num_rows="dynamic")

# --- 3. قسم الفاتورة ---
elif menu == texts["menu_invoice"]:
    st.header(texts["menu_invoice"])
    if not st.session_state.clients.empty:
        c_choice = st.selectbox(texts["client_name"], st.session_state.clients["الاسم/الشركة"])
        desc = st.text_area(texts["designation"])
        price = st.number_input(texts["price_ht"], min_value=0.0)
        tax = st.selectbox(texts["tva"], [20, 14, 10, 0])
        
        total_ttc = price + (price * tax / 100)
        st.write(f"### {texts['total']}: {total_ttc:.2f} DH")
        
        if st.button(texts["generate_pdf"]):
            buf = io.BytesIO()
            p = canvas.Canvas(buf, pagesize=letter)
            # إضافة اللوغو للفاتورة
            try: p.drawInlineImage('mvac_logo.png', 50, 700, width=100, height=60)
            except: pass
            
            p.setFont("Helvetica-Bold", 16)
            p.drawString(250, 720, "INVOICE / FACTURE")
            p.setFont("Helvetica", 10)
            p.drawString(50, 650, f"Client: {c_choice}")
            p.drawString(50, 630, f"Description: {desc}")
            p.drawString(400, 600, f"TOTAL TTC: {total_ttc:.2f} DH")
            p.save()
            
            st.session_state.invoices.append({"client": c_choice, "pdf": buf.getvalue()})
            st.download_button(texts["generate_pdf"], buf.getvalue(), file_name=f"MVAC_{c_choice}.pdf")

# --- 4. الأرشيف ---
elif menu == texts["menu_archive"]:
    st.header(texts["menu_archive"])
    for i, inv in enumerate(st.session_state.invoices):
        st.write(f"📄 {inv['client']}")
        st.download_button("Download", inv['pdf'], file_name=f"MVAC_{i}.pdf", key=f"ar_{i}")
import streamlit as st
import pandas as pd
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from PIL import Image
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. قاموس اللغات (Translations Dictionary) ---
LANGUAGES = {
    "العربية": {
        "title": "نظام MVAC لإدارة التكييف والتبريد",
        "menu_clients": "👤 الزبناء والشركات",
        "menu_stock": "📦 إدارة المخزون",
        "menu_invoice": "📄 فاتورة جديدة (TVA)",
        "menu_archive": "📂 أرشيف الفواتير",
        "add_client": "إضافة زبون جديد",
        "client_name": "الاسم الكامل / الشركة",
        "client_type": "نوع الزبون",
        "ice_label": "رقم (ICE)",
        "save_btn": "حفظ البيانات",
        "update_btn": "تحديث الكل",
        "designation": "وصف الإصلاحات / الخدمات",
        "price_ht": "الثمن الإجمالي (HT)",
        "tva_label": "نسبة الضريبة TVA %",
        "generate_pdf": "توليد وتحميل الفاتورة PDF",
        "total_ttc": "المجموع المؤدى (TTC)",
        "lang_select": "اختر لغة الواجهة",
        "history_msg": "سجل العمليات السابقة",
        "delete": "حذف",
        "download": "تحميل"
    },
    "Français": {
        "title": "Système MVAC - Gestion HVAC",
        "menu_clients": "👤 Clients & Sociétés",
        "menu_stock": "📦 Gestion de Stock",
        "menu_invoice": "📄 Nouvelle Facture (TVA)",
        "menu_archive": "📂 Archives des Factures",
        "add_client": "Ajouter un Client",
        "client_name": "Nom / Raison Sociale",
        "client_type": "Type de Client",
        "ice_label": "ICE",
        "save_btn": "Enregistrer",
        "update_btn": "Mettre à jour",
        "designation": "Désignation des Travaux",
        "price_ht": "Montant Total HT",
        "tva_label": "Taux de TVA %",
        "generate_pdf": "Générer & Télécharger PDF",
        "total_ttc": "Total à Payer (TTC)",
        "lang_select": "Choisir la Langue",
        "history_msg": "Historique des opérations",
        "delete": "Supprimer",
        "download": "Télécharger"
    },
    "English": {
        "title": "MVAC Management System",
        "menu_clients": "👤 Clients & Companies",
        "menu_stock": "📦 Inventory Management",
        "menu_invoice": "📄 New Invoice (VAT)",
        "menu_archive": "📂 Invoices Archive",
        "add_client": "Add New Client",
        "client_name": "Name / Company Name",
        "client_type": "Client Type",
        "ice_label": "ICE / Tax ID",
        "save_btn": "Save Data",
        "update_btn": "Update All",
        "designation": "Service Description",
        "price_ht": "Total Price (Excl. Tax)",
        "tva_label": "VAT Rate %",
        "generate_pdf": "Generate & Download PDF",
        "total_ttc": "Total Amount (Incl. Tax)",
        "lang_select": "Select Language",
        "history_msg": "Previous Operations History",
        "delete": "Delete",
        "download": "Download"
    }
}

# --- إعدادات الصفحة ---
st.set_page_config(page_title="MVAC Pro v5.0", layout="wide", page_icon="❄️")

# --- اختيار اللغة (Sidebar) ---
st.sidebar.markdown("### 🌐 Language / اللغة")
lang_choice = st.sidebar.selectbox("", list(LANGUAGES.keys()))
T = LANGUAGES[lang_choice]

# --- عرض اللوغو في القائمة الجانبية ---
try:
    logo = Image.open('mvac_logo.png')
    st.sidebar.image(logo, use_column_width=True)
except:
    st.sidebar.header("MVAC")

# --- الاتصال بـ Google Sheets ---
def init_db():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
        client = gspread.authorize(creds)
        return client.open("MVAC_Database")
    except: return None

db_conn = init_db()

def fetch_data(sheet_name):
    if db_conn:
        try: return pd.DataFrame(db_conn.worksheet(sheet_name).get_all_records())
        except: return pd.DataFrame()
    return pd.DataFrame()

def commit_data(df, sheet_name):
    if db_conn:
        sheet = db_conn.worksheet(sheet_name)
        sheet.clear()
        sheet.update([df.columns.values.tolist()] + df.values.tolist())

# تهيئة الذاكرة (Session State)
if 'clients' not in st.session_state: st.session_state.clients = fetch_data("Clients")
if 'inventory' not in st.session_state: st.session_state.inventory = fetch_data("Inventory")
if 'pdf_archive' not in st.session_state: st.session_state.pdf_archive = []

# --- توزيع المهام (Main Menu) ---
st.sidebar.divider()
choice = st.sidebar.radio(T["lang_select"], [T["menu_clients"], T["menu_stock"], T["menu_invoice"], T["menu_archive"]])

# --- 1. إدارة الزبناء ---
if choice == T["menu_clients"]:
    st.header(T["menu_clients"])
    with st.expander(T["add_client"]):
        c1, c2 = st.columns(2)
        with c1:
            c_name = st.text_input(T["client_name"])
            c_type = st.selectbox(T["client_type"], ["Société / شركة", "Particulier / فرد"])
            c_ice = st.text_input(T["ice_label"])
        with c2:
            c_tel = st.text_input("Tel / الهاتف")
            c_mail = st.text_input("Email / البريد")
            c_lieu = st.text_input("Lieu / العنوان")
        c_rib = st.text_input("RIB / الحساب البنكي")
        
        if st.button(T["save_btn"]):
            new_row = {"النوع": c_type, "الاسم/الشركة": c_name, "ICE": c_ice, "RIB": c_rib, "Mail": c_mail, "Tel": c_tel, "Lieu": c_lieu}
            st.session_state.clients = pd.concat([st.session_state.clients, pd.DataFrame([new_row])], ignore_index=True)
            commit_data(st.session_state.clients, "Clients")
            st.success("Success!")

    st.subheader(T["update_btn"])
    updated_cl = st.data_editor(st.session_state.clients, num_rows="dynamic", key="cl_editor")
    if st.button(T["update_btn"], key="cl_save"):
        commit_data(updated_cl, "Clients")
        st.rerun()

# --- 2. إدارة المخزون ---
elif choice == T["menu_stock"]:
    st.header(T["menu_stock"])
    updated_st = st.data_editor(st.session_state.inventory, num_rows="dynamic", key="st_editor")
    if st.button(T["update_btn"], key="st_save"):
        commit_data(updated_st, "Inventory")
        st.rerun()

# --- 3. الفاتورة الجديدة ---
elif choice == T["menu_invoice"]:
    st.header(T["menu_invoice"])
    if st.session_state.clients.empty:
        st.warning("Please add a client first!")
    else:
        target_client = st.selectbox(T["client_name"], st.session_state.clients["الاسم/الشركة"])
        c_meta = st.session_state.clients[st.session_state.clients["الاسم/الشركة"] == target_client].iloc[0]
        
        col_a, col_b = st.columns(2)
        with col_a:
            work_desc = st.text_area(T["designation"])
            h_price = st.number_input(T["price_ht"], min_value=0.0)
            v_tax = st.selectbox(T["tva_label"], [20, 14, 10, 0])
        with col_b:
            used_parts = st.multiselect("Parts / السلع", st.session_state.inventory["القطعة"])
        
        # العملية الحسابية
        parts_val = st.session_state.inventory[st.session_state.inventory["القطعة"].isin(used_parts)]["الثمن"].sum()
        subtotal = h_price + parts_val
        tax_val = subtotal * (v_tax / 100)
        final_total = subtotal + tax_val
        
        st.markdown(f"### {T['total_ttc']}: {final_total:.2f} DH")
        
        if st.button(T["generate_pdf"]):
            buffer = io.BytesIO()
            can = canvas.Canvas(buffer, pagesize=letter)
            # رسم اللوغو
            try: can.drawInlineImage('mvac_logo.png', 50, 680, width=120, height=80)
            except: pass
            
            can.setFont("Helvetica-Bold", 18)
            can.drawCentredString(300, 720, "FACTURE / INVOICE")
            can.setFont("Helvetica", 10)
            can.drawString(50, 650, f"Client: {target_client}")
            can.drawString(50, 635, f"ICE: {c_meta['ICE']}")
            can.line(50, 610, 550, 610)
            can.drawString(60, 580, f"Work: {work_desc[:100]}...")
            can.drawString(400, 540, f"Sub-Total HT: {subtotal:.2f} DH")
            can.drawString(400, 520, f"Tax ({v_tax}%): {tax_val:.2f} DH")
            can.setFont("Helvetica-Bold", 12)
            can.drawString(400, 490, f"TOTAL TTC: {final_total:.2f} DH")
            can.save()
            
            st.session_state.pdf_archive.append({"client": target_client, "data": buffer.getvalue(), "date": datetime.now().strftime("%d/%m %H:%M")})
            st.download_button(T["download"], buffer.getvalue(), file_name=f"MVAC_{target_client}.pdf")

# --- 4. الأرشيف ---
elif choice == T["menu_archive"]:
    st.header(T["menu_archive"])
    for i, item in enumerate(st.session_state.pdf_archive):
        c1, c2, c3 = st.columns([3, 1, 1])
        c1.write(f"📄 {item['client']} | {item['date']}")
        c2.download_button(T["download"], item['data'], file_name=f"Archive_{i}.pdf", key=f"btn_{i}")
        if c3.button(T["delete"], key=f"del_{i}"):
            st.session_state.pdf_archive.pop(i)
            st.rerun()
import streamlit as st
import pandas as pd
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image

# --- إعدادات الواجهة ---
st.set_page_config(page_title="MVAC Pro - Quick Start", layout="wide", page_icon="❄️")

# لغات التطبيق
LANGS = {
    "العربية": {"client": "الزبناء", "stock": "المخزون", "invoice": "فاتورة", "total": "المجموع"},
    "Français": {"client": "Clients", "stock": "Stock", "invoice": "Facture", "total": "Total"}
}

# اختيار اللغة
lang = st.sidebar.selectbox("🌐 Language", ["العربية", "Français"])
T = LANGS[lang]

# عرض اللوغو
try:
    st.sidebar.image('mvac_logo.png', use_column_width=True)
except:
    st.sidebar.header("MVAC")

# --- تخزين البيانات مؤقتاً ---
if 'clients' not in st.session_state:
    st.session_state.clients = pd.DataFrame(columns=["الاسم/الشركة", "ICE", "Tel"])
if 'invoices' not in st.session_state:
    st.session_state.invoices = []

menu = st.sidebar.radio("Menu", [T["client"], T["stock"], T["invoice"]])

# --- 1. الزبناء ---
if menu == T["client"]:
    st.header(T["client"])
    name = st.text_input("Nom / الاسم")
    ice = st.text_input("ICE")
    if st.button("Save"):
        new_c = pd.DataFrame([{"الاسم/الشركة": name, "ICE": ice}])
        st.session_state.clients = pd.concat([st.session_state.clients, new_c], ignore_index=True)
        st.success("OK!")
    st.table(st.session_state.clients)

# --- 2. الفاتورة ---
elif menu == T["invoice"]:
    st.header(T["invoice"])
    if st.session_state.clients.empty:
        st.error("Add client first!")
    else:
        c_name = st.selectbox("Client", st.session_state.clients["الاسم/الشركة"])
        price = st.number_input("HT", min_value=0.0)
        tva = st.selectbox("TVA", [20, 14, 0])
        total = price + (price * tva / 100)
        
        st.write(f"### Total: {total:.2f} DH")
        
        if st.button("Generate PDF"):
            buf = io.BytesIO()
            p = canvas.Canvas(buf, pagesize=letter)
            p.setFont("Helvetica-Bold", 16)
            p.drawString(250, 750, "FACTURE MVAC")
            p.setFont("Helvetica", 12)
            p.drawString(50, 700, f"Client: {c_name}")
            p.drawString(50, 680, f"TOTAL: {total:.2f} DH")
            p.save()
            st.download_button("Download PDF", buf.getvalue(), file_name="mvac.pdf")
import streamlit as st
import pandas as pd
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image

# إعدادات الصفحة
st.set_page_config(page_title="MVAC Pro", layout="wide")

# اللغات
LANGS = {
    "العربية": {"client": "الزبناء", "invoice": "فاتورة جديدة", "save": "حفظ", "total": "المجموع"},
    "Français": {"client": "Clients", "invoice": "Nouvelle Facture", "save": "Enregistrer", "total": "Total TTC"}
}

lang = st.sidebar.selectbox("🌐 Language", ["العربية", "Français"])
T = LANGS[lang]

# عرض اللوغو اللي رفعتي
try:
    st.sidebar.image('mvac_logo.png', use_column_width=True)
except:
    st.sidebar.header("M-VAC")

# مخزن مؤقت
if 'clients' not in st.session_state:
    st.session_state.clients = pd.DataFrame(columns=["الاسم/الشركة", "ICE"])

menu = st.sidebar.radio("القائمة", [T["client"], T["invoice"]])

if menu == T["client"]:
    st.header(T["client"])
    name = st.text_input("الاسم / Nom")
    ice = st.text_input("ICE")
    if st.button(T["save"]):
        new_data = pd.DataFrame([{"الاسم/الشركة": name, "ICE": ice}])
        st.session_state.clients = pd.concat([st.session_state.clients, new_data], ignore_index=True)
        st.success("تم الحفظ!")
    st.table(st.session_state.clients)

elif menu == T["invoice"]:
    st.header(T["invoice"])
    if st.session_state.clients.empty:
        st.warning("دخل شي زبون أولاً.")
    else:
        c_choice = st.selectbox("الزبون", st.session_state.clients["الاسم/الشركة"])
        price = st.number_input("الثمن HT", min_value=0.0)
        total = price * 1.20 # إضافة 20% ضريبة تلقائياً
        st.write(f"### {T['total']}: {total:.2f} DH")
        
        if st.button("تحميل الفاتورة PDF"):
            buf = io.BytesIO()
            p = canvas.Canvas(buf, pagesize=letter)
            p.setFont("Helvetica-Bold", 16)
            p.drawString(200, 750, f"FACTURE MVAC - {c_choice}")
            p.drawString(50, 700, f"Total a payer: {total:.2f} DH")
            p.save()
            st.download_button("Download PDF", buf.getvalue(), file_name="mvac_facture.pdf")
import streamlit as st
import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# إعداد واجهة MVAC
st.set_page_config(page_title="MVAC App", layout="wide")

# عرض اللوغو اللي رفعتي
try:
    st.sidebar.image('mvac_logo.png', use_column_width=True)
except:
    st.sidebar.title("MVAC")

st.title("❄️ نظام MVAC لإدارة الفواتير")

# قائمة بسيطة
menu = st.sidebar.radio("القائمة", ["الزبناء", "فاتورة جديدة"])

if 'clients' not in st.session_state:
    st.session_state.clients = []

if menu == "الزبناء":
    name = st.text_input("اسم الزبون")
    if st.button("حفظ الزبون"):
        st.session_state.clients.append(name)
        st.success(f"تم تسجيل {name}")

elif menu == "فاتورة جديدة":
    if not st.session_state.clients:
        st.warning("دخل الزبناء أولاً")
    else:
        c = st.selectbox("اختار الزبون", st.session_state.clients)
        amount = st.number_input("المبلغ (DH)", min_value=0)
        if st.button("تحميل الفاتورة PDF"):
            buf = io.BytesIO()
            p = canvas.Canvas(buf, pagesize=letter)
            p.drawString(100, 750, f"Facture pour: {c}")
            p.drawString(100, 730, f"Total: {amount} DH")
            p.save()
            st.download_button("اضغط هنا للتحميل", buf.getvalue(), "facture.pdf")
import streamlit as st
import pandas as pd
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image

# إعدادات الواجهة
st.set_page_config(page_title="MVAC Pro", layout="wide")

# عرض اللوغو
try:
    st.sidebar.image('mvac_logo.png', use_column_width=True)
except:
    st.sidebar.title("M-VAC")

st.sidebar.markdown("---")
menu = st.sidebar.radio("القائمة", ["👤 الزبناء", "📄 فاتورة جديدة"])

if 'clients' not in st.session_state:
    st.session_state.clients = pd.DataFrame(columns=["الاسم/الشركة", "ICE"])

if menu == "👤 الزبناء":
    st.header("إدارة الزبناء")
    name = st.text_input("اسم الزبون / الشركة")
    ice = st.text_input("رقم ICE")
    if st.button("حفظ"):
        new_row = pd.DataFrame([{"الاسم/الشركة": name, "ICE": ice}])
        st.session_state.clients = pd.concat([st.session_state.clients, new_row], ignore_index=True)
        st.success("تم الحفظ بنجاح!")
    st.table(st.session_state.clients)

elif menu == "📄 فاتورة جديدة":
    st.header("توليد فاتورة")
    if st.session_state.clients.empty:
        st.warning("يرجى إضافة زبون أولاً.")
    else:
        client = st.selectbox("اختار الزبون", st.session_state.clients["الاسم/الشركة"])
        amount = st.number_input("المبلغ الإجمالي (DH)", min_value=0.0)
        if st.button("تحميل PDF"):
            buf = io.BytesIO()
            can = canvas.Canvas(buf, pagesize=letter)
            can.setFont("Helvetica-Bold", 16)
            can.drawString(200, 750, f"FACTURE MVAC - {client}")
            can.drawString(100, 700, f"Montant: {amount:.2f} DH")
            can.save()
            st.download_button("تحميل الفاتورة", buf.getvalue(), file_name="facture.pdf")
import streamlit as st
import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

st.set_page_config(page_title="MVAC App", layout="wide")

# عرض اللوغو
try:
    st.sidebar.image('mvac_logo.png', use_container_width=True)
except:
    st.sidebar.title("MVAC")

st.title("❄️ نظام MVAC لإدارة الفواتير")

menu = st.sidebar.radio("القائمة", ["الزبناء", "فاتورة جديدة"])

if 'clients' not in st.session_state:
    st.session_state.clients = []

if menu == "الزبناء":
    name = st.text_input("اسم الزبون")
    if st.button("حفظ الزبون"):
        st.session_state.clients.append(name)
        st.success(f"تم تسجيل {name}")
    st.write("قائمة الزبناء:", st.session_state.clients)

elif menu == "فاتورة جديدة":
    if not st.session_state.clients:
        st.warning("دخل الزبناء أولاً")
    else:
        c = st.selectbox("اختار الزبون", st.session_state.clients)
        amount = st.number_input("المبلغ (DH)", min_value=0)
        if st.button("تحميل الفاتورة PDF"):
            buf = io.BytesIO()
            p = canvas.Canvas(buf, pagesize=letter)
            p.drawString(100, 750, f"Facture pour: {c}")
            p.drawString(100, 730, f"Total: {amount} DH")
            p.save()
            st.download_button("اضغط هنا للتحميل", buf.getvalue(), "facture.pdf")
import streamlit as st
import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# إعداد واجهة MVAC
st.set_page_config(page_title="MVAC App", layout="wide")

# عرض اللوغو اللي رفعتي
try:
    st.sidebar.image('mvac_logo.png', use_container_width=True)
except:
    st.sidebar.title("MVAC")

st.title("❄️ نظام MVAC لإدارة الفواتير")

menu = st.sidebar.radio("القائمة", ["الزبناء", "فاتورة جديدة"])

if 'clients' not in st.session_state:
    st.session_state.clients = []

if menu == "الزبناء":
    name = st.text_input("اسم الزبون")
    if st.button("حفظ الزبون"):
        st.session_state.clients.append(name)
        st.success(f"تم تسجيل {name}")
    st.write("قائمة الزبناء:", st.session_state.clients)

elif menu == "فاتورة جديدة":
    if not st.session_state.clients:
        st.warning("دخل الزبناء أولاً")
    else:
        c = st.selectbox("اختار الزبون", st.session_state.clients)
        amount = st.number_input("المبلغ (DH)", min_value=0)
        if st.button("تحميل الفاتورة PDF"):
            buf = io.BytesIO()
            p = canvas.Canvas(buf, pagesize=letter)
            p.drawString(100, 750, f"Facture pour: {c}")
            p.drawString(100, 730, f"Total: {amount} DH")
            p.save()
            st.download_button("اضغط هنا للتحميل", buf.getvalue(), "facture.pdf")
import streamlit as st
import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

st.set_page_config(page_title="MVAC App", layout="wide")

# عرض اللوغو
try:
    st.sidebar.image('mvac_logo.png', use_container_width=True)
except:
    st.sidebar.title("MVAC")

st.title("❄️ نظام MVAC لإدارة الفواتير")

menu = st.sidebar.radio("القائمة", ["الزبناء", "فاتورة جديدة"])

if 'clients' not in st.session_state:
    st.session_state.clients = []

if menu == "الزبناء":
    name = st.text_input("اسم الزبون")
    if st.button("حفظ الزبون"):
        st.session_state.clients.append(name)
        st.success(f"تم تسجيل {name}")
    st.write("قائمة الزبناء:", st.session_state.clients)

elif menu == "فاتورة جديدة":
    if not st.session_state.clients:
        st.warning("دخل الزبناء أولاً")
    else:
        c = st.selectbox("اختار الزبون", st.session_state.clients)
        amount = st.number_input("المبلغ (DH)", min_value=0)
        if st.button("تحميل الفاتورة PDF"):
            buf = io.BytesIO()
            p = canvas.Canvas(buf, pagesize=letter)
            p.drawString(100, 750, f"Facture pour: {c}")
            p.drawString(100, 730, f"Total: {amount} DH")
            p.save()
            st.download_button("اضغط هنا للتحميل", buf.getvalue(), "facture.pdf")
import streamlit as st
import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# إعدادات الصفحة
st.set_page_config(page_title="MVAC Pro", page_icon="❄️")

# تحسين عرض اللوغو في الجنب
with st.sidebar:
    try:
        # تأكد أن السمية هي نفس اللي في GitHub
        st.image("mvac_logo.png", use_container_width=True)
    except:
        st.title("M-VAC")
    st.markdown("---")
    menu = st.radio("القائمة الرئيسية", ["🏠 الرئيسية", "👤 إدارة الزبناء", "📄 إنشاء فاتورة"])

# الصفحة الرئيسية
if menu == "🏠 الرئيسية":
    st.title("❄️ مرحباً بك في نظام MVAC")
    st.info("استخدم القائمة الجانبية للتنقل بين الأقسام.")

# الأقسام الأخرى (الزبناء والفواتير)
if 'clients' not in st.session_state:
    st.session_state.clients = []

if menu == "👤 إدارة الزبناء":
    st.header("إضافة زبون جديد")
    name = st.text_input("اسم الزبون")
    if st.button("حفظ"):
        if name:
            st.session_state.clients.append(name)
            st.success(f"تم تسجيل {name}")
    st.write("الزبناء الحاليين:", st.session_state.clients)

elif menu == "📄 إنشاء فاتورة":
    st.header("توليد فاتورة PDF")
    if not st.session_state.clients:
        st.warning("يرجى إضافة زبون أولاً.")
    else:
        c = st.selectbox("اختار الزبون", st.session_state.clients)
        amount = st.number_input("المبلغ (DH)", min_value=0)
        if st.button("تحميل الفاتورة"):
            buf = io.BytesIO()
            p = canvas.Canvas(buf, pagesize=letter)
            p.drawString(100, 750, f"FACTURE MVAC")
            p.drawString(100, 730, f"Client: {c}")
            p.drawString(100, 710, f"Total: {amount} DH")
            p.save()
            st.download_button("اضغط للتحميل", buf.getvalue(), f"facture_{c}.pdf")
import streamlit as st
import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# 1. إعدادات واجهة التطبيق
st.set_page_config(page_title="MVAC - Système de Facturation", layout="wide", page_icon="❄️")

# 2. تحميل اللوغو وتنسيق القائمة الجانبية
with st.sidebar:
    try:
        st.image("mvac_logo.png", use_container_width=True) #
    except:
        st.title("M-VAC")
    st.markdown("---")
    menu = st.sidebar.selectbox("القائمة الرئيسية", ["🏠 الصفحة الرئيسية", "👥 إدارة الزبناء", "📄 إنشاء فاتورة جديدة"])
    st.sidebar.info("تطبيق MVAC لإدارة التبريد والتهوية")

# 3. قاعدة بيانات مؤقتة (في ذاكرة المتصفح)
if 'db_clients' not in st.session_state:
    st.session_state.db_clients = pd.DataFrame(columns=["الاسم/الشركة", "ICE", "الهاتف", "العنوان"])

# --- القسم 1: الصفحة الرئيسية ---
if menu == "🏠 الصفحة الرئيسية":
    st.title("❄️ نظام MVAC للإدارة")
    st.write("مرحباً بك سفيان. هذا النظام مخصص لتسهيل عملية تسيير الزبناء وتوليد الفواتير الخاصة بـ MVAC.")
    
    col1, col2 = st.columns(2)
    col1.metric("عدد الزبناء", len(st.session_state.db_clients))
    col2.metric("الحالة", "متصل ✅")

# --- القسم 2: إدارة الزبناء ---
elif menu == "👥 إدارة الزبناء":
    st.header("👤 إضافة زبون جديد")
    with st.form("client_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم الزبون أو الشركة")
        ice = c2.text_input("رقم ICE")
        phone = c1.text_input("رقم الهاتف")
        address = c2.text_area("العنوان")
        submit = st.form_submit_button("حفظ الزبون")
        
    if submit and name:
        new_data = pd.DataFrame([{"الاسم/الشركة": name, "ICE": ice, "الهاتف": phone, "العنوان": address}])
        st.session_state.db_clients = pd.concat([st.session_state.db_clients, new_data], ignore_index=True)
        st.success(f"تم تسجيل الزبون {name} بنجاح!")

    st.markdown("---")
    st.subheader("📋 قائمة الزبناء المسجلين")
    st.table(st.session_state.db_clients)

# --- القسم 3: إنشاء الفاتورة ---
elif menu == "📄 إنشاء فاتورة جديدة":
    st.header("📝 تفاصيل الفاتورة")
    
    if st.session_state.db_clients.empty:
        st.warning("⚠️ يجب إضافة زبون واحد على الأقل قبل إنشاء فاتورة.")
    else:
        client_name = st.selectbox("اختار الزبون", st.session_state.db_clients["الاسم/الشركة"])
        client_info = st.session_state.db_clients[st.session_state.db_clients["الاسم/الشركة"] == client_name].iloc[0]
        
        description = st.text_area("وصف الخدمة (مثلاً: تركيب مكيف هواء)")
        amount = st.number_input("المبلغ الإجمالي بدون ضريبة (HT) بالدرهم", min_value=0.0)
        tva = amount * 0.20
        total = amount + tva
        
        st.write(f"**الضريبة (20%):** {tva:.2f} DH")
        st.write(f"**المبلغ الإجمالي المؤدى (TTC):** {total:.2f} DH")

        if st.button("توليد وتحميل الفاتورة PDF"):
            buf = io.BytesIO()
            p = canvas.Canvas(buf, pagesize=letter)
            
            # تصميم الفاتورة PDF
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, 750, "FACTURE MVAC")
            p.line(50, 745, 550, 745)
            
            p.setFont("Helvetica", 12)
            p.drawString(50, 700, f"Client: {client_name}")
            p.drawString(50, 680, f"ICE: {client_info['ICE']}")
            p.drawString(50, 660, f"Adresse: {client_info['العنوان']}")
            
            p.drawString(50, 600, "Description de Service:")
            p.drawString(70, 580, f"- {description}")
            
            p.line(50, 500, 550, 500)
            p.drawString(350, 480, f"Total HT: {amount:.2f} DH")
            p.drawString(350, 460, f"TVA (20%): {tva:.2f} DH")
            p.setFont("Helvetica-Bold", 12)
            p.drawString(350, 440, f"TOTAL TTC: {total:.2f} DH")
            
            p.showPage()
            p.save()
            
            st.download_button(
                label="📥 تحميل الفاتورة الآن",
                data=buf.getvalue(),
                file_name=f"Facture_{client_name}.pdf",
                mime="application/pdf"
            )
import streamlit as st
import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# 1. إعدادات الصفحة كاملة
st.set_page_config(page_title="MVAC Pro - Système de Gestion", layout="wide", page_icon="❄️")

# 2. القائمة الجانبية مع اللوغو
with st.sidebar:
    try:
        # كيحاول يقرأ اللوغو اللي رفعتي في GitHub
        st.image("mvac_logo.png", use_container_width=True) 
    except:
        st.title("M-VAC")
    st.markdown("---")
    menu = st.radio("القائمة الرئيسية", ["🏠 الصفحة الرئيسية", "👥 إدارة الزبناء", "📄 إنشاء فاتورة جديدة"])
    st.markdown("---")
    st.info("تطبيق MVAC لإدارة خدمات التبريد والتهوية")

# 3. تخزين البيانات (كتسجل مؤقتاً في الجلسة)
if 'db_clients' not in st.session_state:
    st.session_state.db_clients = pd.DataFrame(columns=["الاسم/الشركة", "ICE", "الهاتف", "العنوان"])

# --- القسم 1: الصفحة الرئيسية ---
if menu == "🏠 الصفحة الرئيسية":
    st.title("❄️ نظام MVAC للإدارة المتكاملة")
    st.write("مرحباً بك سفيان. هاد النظام كيسهل عليك تسيير الزبناء وتصاوب فواتير احترافية لشركة MVAC.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("عدد الزبناء", len(st.session_state.db_clients))
    col2.metric("حالة السيرفر", "متصل ✅")
    col3.metric("النسخة", "1.0 PRO")

# --- القسم 2: إدارة الزبناء ---
elif menu == "👥 إدارة الزبناء":
    st.header("👤 إضافة زبون أو شركة جديدة")
    with st.form("client_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم الزبون الكامل أو اسم الشركة")
        ice = c2.text_input("رقم الـ ICE (اختياري)")
        phone = c1.text_input("رقم الهاتف")
        address = c2.text_area("العنوان الكامل")
        submit = st.form_submit_button("حفظ الزبون في القاعدة")
        
    if submit and name:
        new_row = {"الاسم/الشركة": name, "ICE": ice, "الهاتف": phone, "العنوان": address}
        st.session_state.db_clients = pd.concat([st.session_state.db_clients, pd.DataFrame([new_row])], ignore_index=True)
        st.success(f"✅ تم تسجيل {name} بنجاح!")

    st.markdown("---")
    st.subheader("📋 قائمة الزبناء المسجلين")
    if not st.session_state.db_clients.empty:
        st.dataframe(st.session_state.db_clients, use_container_width=True)
    else:
        st.write("لا يوجد زبناء مسجلين حالياً.")

# --- القسم 3: إنشاء الفاتورة ---
elif menu == "📄 إنشاء فاتورة جديدة":
    st.header("📝 تفاصيل الفاتورة المهنية")
    
    if st.session_state.db_clients.empty:
        st.warning("⚠️ خاصك تزيد زبون واحد على الأقل في قسم 'إدارة الزبناء' قبل ما تصاوب فاتورة.")
    else:
        # اختيار الزبون والمعلومات ديالو
        client_name = st.selectbox("اختار الزبون المستهدف", st.session_state.db_clients["الاسم/الشركة"])
        client_info = st.session_state.db_clients[st.session_state.db_clients["الاسم/الشركة"] == client_name].iloc[0]
        
        st.markdown("### معلومات الخدمة")
        col_a, col_b = st.columns(2)
        description = col_a.text_area("وصف الخدمة المقدمة", placeholder="مثال: إصلاح مكيف هواء بقوة 12000 BTU")
        date_facture = col_b.date_input("تاريخ الفاتورة")
        
        amount_ht = st.number_input("المبلغ الإجمالي بدون ضريبة (HT) بالدرهم", min_value=0.0, step=100.0)
        
        # حسابات الضريبة
        tva_rate = 0.20 # 20% ضريبة
        tva_amount = amount_ht * tva_rate
        total_ttc = amount_ht + tva_amount
        
        st.markdown("---")
        res1, res2, res3 = st.columns(3)
        res1.write(f"**المبلغ (HT):** {amount_ht:,.2f} DH")
        res2.write(f"**الضريبة (20%):** {tva_amount:,.2f} DH")
        res3.write(f"### **الإجمالي (TTC):** {total_ttc:,.2f} DH")

        if st.button("🚀 توليد وتحميل الفاتورة PDF"):
            buf = io.BytesIO()
            p = canvas.Canvas(buf, pagesize=letter)
            
            # تصميم رأس الفاتورة
            p.setFont("Helvetica-Bold", 20)
            p.drawCentredString(300, 750, "FACTURE MVAC")
            
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, 710, "Informations Client:")
            p.setFont("Helvetica", 11)
            p.drawString(60, 690, f"Nom: {client_name}")
            p.drawString(60, 675, f"ICE: {client_info['ICE']}")
            p.drawString(60, 660, f"Adresse: {client_info['العنوان']}")
            p.drawString(60, 645, f"Date: {date_facture}")
            
            p.line(50, 630, 550, 630)
            
            # تفاصيل الخدمة
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, 610, "Description du Service:")
            p.setFont("Helvetica", 11)
            # تقسيم النص إذا كان طويلاً
            text_object = p.beginText(60, 590)
            text_object.textLines(description)
            p.drawText(text_object)
            
            # جدول المبالغ
            p.line(50, 500, 550, 500)
            p.drawString(380, 480, f"Total HT: {amount_ht:,.2f} DH")
            p.drawString(380, 460, f"TVA (20%): {tva_amount:,.2f} DH")
            p.setFont("Helvetica-Bold", 13)
            p.drawString(380, 430, f"TOTAL TTC: {total_ttc:,.2f} DH")
            
            p.setFont("Helvetica-Oblique", 9)
            p.drawCentredString(300, 50, "Merci pour votre confiance - MVAC Service Froid et Climatisation")
            
            p.showPage()
            p.save()
            
            st.download_button(
                label="📥 اضغط هنا لتحميل الفاتورة",
                data=buf.getvalue(),
                file_name=f"Facture_MVAC_{client_name}_{date_facture}.pdf",
                mime="application/pdf"
            )
import streamlit as st
import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# 1. إعدادات الصفحة
st.set_page_config(page_title="MVAC Pro - Gestion", layout="wide", page_icon="❄️")

# 2. القائمة الجانبية (Sidebar) مع اللوغو
with st.sidebar:
    try:
        st.image("mvac_logo.png", use_container_width=True)
    except:
        st.title("MVAC")
    st.markdown("---")
    # هادي هي اللي كتحكم في الصفحات
    menu = st.radio("القائمة الرئيسية", ["🏠 الصفحة الرئيسية", "👥 إدارة الزبناء", "📄 إنشاء فاتورة جديدة"])
    st.markdown("---")
    st.info("تطبيق MVAC لإدارة التبريد والتهوية")

# 3. قاعدة البيانات (مؤقتة في الجلسة)
if 'db_clients' not in st.session_state:
    st.session_state.db_clients = pd.DataFrame(columns=["الاسم/الشركة", "ICE", "الهاتف", "العنوان"])

# --- الصفحة 1: الرئيسية ---
if menu == "🏠 الصفحة الرئيسية":
    st.title("❄️ نظام MVAC للإدارة")
    st.write(f"مرحباً بك سفيان. هاد التطبيق واجد باش ينظم ليك الخدمة.")
    
    col1, col2 = st.columns(2)
    col1.metric("عدد الزبناء المسجلين", len(st.session_state.db_clients))
    col2.metric("الحالة", "متصل ✅")

# --- الصفحة 2: إدارة الزبناء ---
elif menu == "👥 إدارة الزبناء":
    st.header("👤 إضافة زبون جديد")
    with st.form("add_client", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم الزبون / الشركة")
        ice = c2.text_input("ICE (اختياري)")
        phone = c1.text_input("الهاتف")
        address = c2.text_area("العنوان")
        if st.form_submit_button("حفظ الزبون"):
            if name:
                new_row = {"الاسم/الشركة": name, "ICE": ice, "الهاتف": phone, "العنوان": address}
                st.session_state.db_clients = pd.concat([st.session_state.db_clients, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"تم تسجيل {name} بنجاح!")

    st.subheader("📋 قائمة الزبناء")
    st.dataframe(st.session_state.db_clients, use_container_width=True)

# --- الصفحة 3: إنشاء الفاتورة (الباج لوخرا اللي بغيتي) ---
elif menu == "📄 إنشاء فاتورة جديدة":
    st.header("📝 توليد فاتورة مهنية")
    
    if st.session_state.db_clients.empty:
        st.warning("⚠️ خاصك تزيد زبون أولاً في صفحة 'إدارة الزبناء'.")
    else:
        # اختيار الزبون من القائمة
        client_name = st.selectbox("اختار الزبون", st.session_state.db_clients["الاسم/الشركة"])
        client_info = st.session_state.db_clients[st.session_state.db_clients["الاسم/الشركة"] == client_name].iloc[0]
        
        col_a, col_b = st.columns(2)
        desc = col_a.text_area("وصف الخدمة", placeholder="مثال: تركيب نظام تهوية")
        amount_ht = col_b.number_input("المبلغ (HT) بالدرهم", min_value=0.0)
        
        tva = amount_ht * 0.20
        total_ttc = amount_ht + tva
        
        st.write(f"**المبلغ HT:** {amount_ht:.2f} DH | **TVA (20%):** {tva:.2f} DH")
        st.markdown(f"### **الإجمالي (TTC): {total_ttc:.2f} DH**")
        
        if st.button("🚀 تحميل الفاتورة PDF"):
            buf = io.BytesIO()
            p = canvas.Canvas(buf, pagesize=letter)
            # تصميم بسيط للـ PDF
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, 750, "FACTURE MVAC")
            p.setFont("Helvetica", 12)
            p.drawString(50, 720, f"Client: {client_name}")
            p.drawString(50, 705, f"ICE: {client_info['ICE']}")
            p.drawString(50, 670, f"Description: {desc}")
            p.line(50, 650, 550, 650)
            p.drawString(400, 630, f"Total HT: {amount_ht:.2f}")
            p.drawString(400, 615, f"TVA (20%): {tva:.2f}")
            p.drawString(400, 590, f"TOTAL TTC: {total_ttc:.2f}")
            p.save()
            st.download_button("📥 تحميل الآن", buf.getvalue(), f"Facture_{client_name}.pdf")
import streamlit as st
import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# إعدادات الصفحة
st.set_page_config(page_title="MVAC Pro", layout="wide", page_icon="❄️")

# القائمة الجانبية
with st.sidebar:
    try:
        st.image("mvac_logo.png", use_container_width=True)
    except:
        st.title("M-VAC")
    st.markdown("---")
    menu = st.radio("القائمة", ["🏠 الرئيسية", "👥 الزبناء", "📄 الفواتير"])

# قاعدة البيانات المؤقتة
if 'db' not in st.session_state:
    st.session_state.db = []

if menu == "🏠 الرئيسية":
    st.title("❄️ نظام MVAC للإدارة")
    st.write("مرحباً سفيان، التطبيق خدام دابا بنجاح.")

elif menu == "👥 الزبناء":
    st.header("إضافة زبون")
    name = st.text_input("اسم الزبون")
    if st.button("حفظ"):
        if name:
            st.session_state.db.append(name)
            st.success(f"تم حفظ {name}")
    st.write("قائمة الزبناء:", st.session_state.db)

elif menu == "📄 الفواتير":
    st.header("إنشاء فاتورة")
    if not st.session_state.db:
        st.warning("زيد زبون أولاً.")
    else:
        user = st.selectbox("اختار الزبون", st.session_state.db)
        price = st.number_input("المبلغ (DH)", min_value=0)
        if st.button("تحميل PDF"):
            buf = io.BytesIO()
            p = canvas.Canvas(buf, pagesize=letter)
            p.drawString(100, 750, f"FACTURE MVAC - Client: {user}")
            p.drawString(100, 730, f"Total: {price} DH")
            p.save()
            st.download_button("تحميل الآن", buf.getvalue(), "facture.pdf")
import streamlit as st
import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# 1. إعدادات الصفحة كاملة
st.set_page_config(page_title="MVAC Pro - Système de Gestion", layout="wide", page_icon="❄️")

# 2. القائمة الجانبية (Sidebar) مع اللوغو
with st.sidebar:
    try:
        # كيحاول يقرأ اللوغو اللي رفعتي في GitHub
        st.image("mvac_logo.png", use_container_width=True) 
    except:
        # في حالة ما لقاش اللوغو كيبان العنوان
        st.title("M-VAC")
    st.markdown("---")
    # هادي هي اللي كتحكم في الصفحات
    menu = st.radio("القائمة الرئيسية", ["🏠 الصفحة الرئيسية", "👥 إدارة الزبناء", "📄 إنشاء فاتورة جديدة"])
    st.markdown("---")
    st.info("تطبيق MVAC لإدارة خدمات التبريد والتهوية")

# 3. تخزين البيانات (كتسجل مؤقتاً في الجلسة)
if 'db_clients' not in st.session_state:
    st.session_state.db_clients = pd.DataFrame(columns=["الاسم/الشركة", "ICE", "الهاتف", "العنوان"])

# --- القسم 1: الصفحة الرئيسية ---
if menu == "🏠 الصفحة الرئيسية":
    st.title("❄️ نظام MVAC للإدارة المتكاملة")
    st.write("مرحباً بك سفيان. هاد النظام كيسهل عليك تسيير الزبناء وتصاوب فواتير احترافية لشركة MVAC.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("عدد الزبناء", len(st.session_state.db_clients))
    col2.metric("حالة السيرفر", "متصل ✅")
    col3.metric("النسخة", "1.0 PRO")

# --- القسم 2: إدارة الزبناء ---
elif menu == "👥 إدارة الزبناء":
    st.header("👤 إضافة زبون أو شركة جديدة")
    with st.form("client_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم الزبون الكامل أو اسم الشركة")
        ice = c2.text_input("رقم الـ ICE (اختياري)")
        phone = c1.text_input("رقم الهاتف")
        address = c2.text_area("العنوان الكامل")
        submit = st.form_submit_button("حفظ الزبون في القاعدة")
        
    if submit and name:
        new_row = {"الاسم/الشركة": name, "ICE": ice, "الهاتف": phone, "العنوان": address}
        st.session_state.db_clients = pd.concat([st.session_state.db_clients, pd.DataFrame([new_row])], ignore_index=True)
        st.success(f"✅ تم تسجيل {name} بنجاح!")

    st.markdown("---")
    st.subheader("📋 قائمة الزبناء المسجلين")
    if not st.session_state.db_clients.empty:
        st.dataframe(st.session_state.db_clients, use_container_width=True)
    else:
        st.write("لا يوجد زبناء مسجلين حالياً.")

# --- القسم 3: إنشاء الفاتورة ---
elif menu == "📄 إنشاء فاتورة جديدة":
    st.header("📝 تفاصيل الفاتورة المهنية")
    
    if st.session_state.db_clients.empty:
        st.warning("⚠️ خاصك تزيد زبون واحد على الأقل في قسم 'إدارة الزبناء' قبل ما تصاوب فاتورة.")
    else:
        # اختيار الزبون والمعلومات ديالو
        client_name = st.selectbox("اختار الزبون المستهدف", st.session_state.db_clients["الاسم/الشركة"])
        client_info = st.session_state.db_clients[st.session_state.db_clients["الاسم/الشركة"] == client_name].iloc[0]
        
        st.markdown("### معلومات الخدمة")
        col_a, col_b = st.columns(2)
        description = col_a.text_area("وصف الخدمة المقدمة", placeholder="مثال: إصلاح مكيف هواء بقوة 12000 BTU")
        date_facture = col_b.date_input("تاريخ الفاتورة")
        
        amount_ht = st.number_input("المبلغ الإجمالي بدون ضريبة (HT) بالدرهم", min_value=0.0, step=100.0)
        
        # حسابات الضريبة
        tva_rate = 0.20 # 20% ضريبة
        tva_amount = amount_ht * tva_rate
        total_ttc = amount_ht + tva_amount
        
        st.markdown("---")
        res1, res2, res3 = st.columns(3)
        res1.write(f"**المبلغ (HT):** {amount_ht:,.2f} DH")
        res2.write(f"**الضريبة (20%):** {tva_amount:,.2f} DH")
        res3.write(f"### **الإجمالي (TTC):** {total_ttc:,.2f} DH")

        if st.button("🚀 توليد وتحميل الفاتورة PDF"):
            buf = io.BytesIO()
            p = canvas.Canvas(buf, pagesize=letter)
            
            # تصميم رأس الفاتورة
            p.setFont("Helvetica-Bold", 20)
            p.drawCentredString(300, 750, "FACTURE MVAC")
            
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, 710, "Informations Client:")
            p.setFont("Helvetica", 11)
            p.drawString(60, 690, f"Nom: {client_name}")
            p.drawString(60, 675, f"ICE: {client_info['ICE']}")
            p.drawString(60, 660, f"Adresse: {client_info['العنوان']}")
            p.drawString(60, 645, f"Date: {date_facture}")
            
            p.line(50, 630, 550, 630)
            
            # تفاصيل الخدمة
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, 610, "Description du Service:")
            p.setFont("Helvetica", 11)
            # تقسيم النص إذا كان طويلاً
            text_object = p.beginText(60, 590)
            text_object.textLines(description)
            p.drawText(text_object)
            
            # جدول المبالغ
            p.line(50, 500, 550, 500)
            p.drawString(380, 480, f"Total HT: {amount_ht:,.2f} DH")
            p.drawString(380, 460, f"TVA (20%): {tva_amount:,.2f} DH")
            p.setFont("Helvetica-Bold", 13)
            p.drawString(380, 430, f"TOTAL TTC: {total_ttc:,.2f} DH")
            
            p.setFont("Helvetica-Oblique", 9)
            p.drawCentredString(300, 50, "Merci pour votre confiance - MVAC Service Froid et Climatisation")
            
            p.showPage()
            p.save()
            
            st.download_button(
                label="📥 اضغط هنا لتحميل الفاتورة",
                data=buf.getvalue(),
                file_name=f"Facture_MVAC_{client_name}_{date_facture}.pdf",
                mime="application/pdf"
            )
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
