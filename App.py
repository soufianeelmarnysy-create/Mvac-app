import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. إعدادات الصفحة
st.set_page_config(page_title="MVAC Pro System", layout="wide")

# 2. الربط (استعمال الرابط اللي شفت في التصويرة ديالك)
conn = st.connection("gsheets", type=GSheetsConnection)

# هاد الرابط هو اللي شفتو عندك في المتصفح فالتصويرة
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D5ogjG53HMI791W1RfHDEk0ngom0P4uf-cCPWgBjwAs/edit"

def load_data(sheet_name, cols):
    try:
        # القراءة باستعمال الرابط الكامل
        df = conn.read(spreadsheet=SHEET_URL, worksheet=sheet_name, ttl=0)
        if df.empty: return pd.DataFrame(columns=cols)
        if "ID" in df.columns:
            df["ID"] = pd.to_numeric(df["ID"], errors='coerce').fillna(0).astype(int)
        return df
    except Exception as e:
        # إلا طاح خطأ غيوريك علاش بالظبط
        st.error(f"⚠️ مشكل في القراءة من ورقة {sheet_name}: {e}")
        return pd.DataFrame(columns=cols)

# 3. القائمة الجانبية
with st.sidebar:
    st.title("❄️ MVAC SYSTEM")
    page = st.radio("اختار الصفحة:", ["👥 إدارة الزبناء", "📦 السلعة والمخزون"])

# 4. إدارة الزبناء
if page == "👥 إدارة الزبناء":
    st.title("👥 إدارة الزبناء")
    
    # تأكد أن الورقة في Google Sheets سميتها بالظبط: Clients
    df_c = load_data("Clients", ["ID", "الاسم/الشركة", "النوع", "ICE", "الهاتف", "العنوان", "RIB"])

    if not df_c.empty:
        st.dataframe(df_c, use_container_width=True, hide_index=True)
        
        # زر تجربة الحفظ
        if st.button("💾 جرب حفظ البيانات"):
            try:
                conn.update(spreadsheet=SHEET_URL, worksheet="Clients", data=df_c)
                st.success("✅ مبروك! الحفظ داز ناضي دابا.")
            except Exception as e:
                st.error(f"❌ باقي مشكل في الحفظ: {e}")
    else:
        st.warning("⚠️ لم يتم العثور على بيانات. تأكد من اسم الورقة (Clients) في Google Sheets.")
