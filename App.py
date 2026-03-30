import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. إعداد الصفحة
st.set_page_config(page_title="MVAC Pro System", layout="wide", page_icon="❄️")

# 2. الربط
conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_ID = "1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs"

# 3. دالة جلب البيانات
def load_data(sheet_name, cols):
    try:
        df = conn.read(spreadsheet=SHEET_ID, worksheet=sheet_name, ttl=0)
        if df.empty: return pd.DataFrame(columns=cols)
        # توحيد نوع البيانات في العمود ID
        if "ID" in df.columns:
            df["ID"] = pd.to_numeric(df["ID"], errors='coerce').fillna(0).astype(int)
        return df
    except: return pd.DataFrame(columns=cols)

# --- القائمة الجانبية للتنقل ---
with st.sidebar:
    st.title("❄️ MVAC SYSTEM")
    st.image("https://cdn-icons-png.flaticon.com/512/906/906334.png", width=100) # أيقونة افتراضية
    page = st.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 السلعة والمخزون", "📄 إنشاء Devis/Facture"])
    st.markdown("---")
    st.write("سفيان - نظام تسيير MVAC")

# --- 1. صفحة الزبناء ---
if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    df_c = load_data("Clients", ["ID", "الاسم/الشركة", "النوع", "ICE", "الهاتف", "العنوان", "RIB"])
    
    # (هنا حط كود الزبناء اللي عطيتك في الأول باش تقدر تزيد وتعدل)
    st.dataframe(df_c, use_container_width=True, hide_index=True)

# --- 2. صفحة السلعة والمخزون ---
elif page == "📦 السلعة والمخزون":
    st.title("📦 إدارة السلعة والمخزون")
    df_m = load_data("Materiels", ["ID", "التعيين", "الوحدة", "الثمن", "الكمية"])
    
    with st.expander("➕ إضافة مادة (Article) جديدة"):
        with st.form("add_materiel"):
            c1, c2, c3 = st.columns([3, 1, 1])
            nom = c1.text_input("تعيين المادة (Désignation)")
            unit = c2.selectbox("الوحدة", ["U", "M", "M2", "ML", "Kg"])
            price = c3.number_input("الثمن الوحدوي (DH)", min_value=0.0)
            
            if st.form_submit_button("حفظ المادة"):
                if nom:
                    new_id = int(df_m["ID"].max() + 1) if not df_m.empty else 1
                    new_row = pd.DataFrame([{"ID":new_id, "التعيين":nom, "الوحدة":unit, "الثمن":price, "الكمية": 0}])
                    df_m = pd.concat([df_m, new_row], ignore_index=True)
                    conn.update(spreadsheet=SHEET_ID, worksheet="Materiels", data=df_m)
                    st.success("✅ تمت إضافة المادة!")
                    st.rerun()

    st.dataframe(df_m, use_container_width=True, hide_index=True)

# --- 3. صفحة إنشاء Devis / Facture ---
elif page == "📄 إنشاء Devis/Facture":
    st.title("📄 محاكي إنشاء الوثائق")
    
    df_c = load_data("Clients", ["الاسم/الشركة"])
    df_m = load_data("Materiels", ["التعيين", "الثمن", "الوحدة"])
    
    col1, col2, col3 = st.columns(3)
    client = col1.selectbox("الزبون:", df_c["الاسم/الشركة"].unique())
    doc_type = col2.radio("نوع الوثيقة:", ["Devis", "Facture"])
    tva_rate = col3.selectbox("الضريبة TVA:", [20, 0, 14, 7])

    st.markdown("---")
    
    # اختيار السلعة والحساب
    sel_item = st.selectbox("اختار المادة من المخزون:", df_m["التعيين"].unique())
    if sel_item:
        item_data = df_m[df_m["التعيين"] == sel_item].iloc[0]
        c1, c2, c3 = st.columns(3)
        unit_price = c1.number_input("الثمن (DH):", value=float(item_data["الثمن"]))
        qte = c2.number_input("الكمية:", min_value=1, value=1)
        
        total_ht = unit_price * qte
        tva_amount = total_ht * (tva_rate / 100)
        total_ttc = total_ht + tva_amount
        
        st.metric("إجمالي السطر (TTC)", f"{total_ttc:,.2} DH", delta=f"TVA: {tva_amount:,.2f}")
        
        if st.button("💾 حفظ السطر في الفاتورة"):
            st.success(f"تم تسجيل {sel_item} في قائمة {doc_type}")
            # الخطوة الجاية: نصاوبو PDF كيشبه للفواتير الحقيقية
