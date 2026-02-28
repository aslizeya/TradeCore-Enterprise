import streamlit as st
import pandas as pd
from db_connection import DatabaseConnection
from sqlalchemy import text

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Ayarlar | TradeCore", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# BEYAZ DASHBOARD TEMASI (GÖRSEL aa17c7 UYUMLU)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    /* GENEL ARKA PLAN (BEMBEYAZ) */
    html, body, [data-testid="stAppViewContainer"] { 
        font-family: 'Outfit', sans-serif; 
        background-color: #ffffff !important; 
        background-image: none !important; /* Mor gradyan kaldırıldı */
        color: #1e293b;
    }
    
    /* Yazı Renkleri (Koyu Lacivert/Gri ve Yüksek Kontrast) */
    h1, h2, h3 { color: #1e3a8a !important; font-weight: 800; }
    p, .stMarkdown p, label { color: #1e293b !important; }

    /* Üst Bar Tasarımı (Lacivert Çerçeveli Beyaz Kutu) */
    .navbar-container { 
        background-color: #ffffff; 
        padding: 15px 30px; 
        border-radius: 12px; 
        border: 2px solid #1e3a8a; /* Lacivert çerçeve */
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
        margin-bottom: 30px; 
    }
    .navbar-container h3 { color: #1e3a8a !important; margin: 0; }
    
    /* Sekme (Tabs) Tasarımı (Beyaz Tema Uyumlu) */
    .stTabs [data-baseweb="tab-list"] { gap: 0; background-color: transparent; }
    .stTabs [data-baseweb="tab"] { 
        background-color: transparent !important; 
        color: #1e293b !important; 
        padding: 10px 20px !important;
    }
    .stTabs [aria-selected="true"] { 
        border-bottom: 3px solid #1e3a8a !important; 
    }
    .stTabs [aria-selected="true"] p { 
        color: #1e3a8a !important; 
        font-weight: 800 !important; 
    }

    /* --- FORM KUTULARI VE BİLGİ ALANLARI (GÖLGELİ VE RENKLİ SOL KENARLIKLI) --- */
    div[data-testid="stForm"], div.stAlert {
        background-color: #ffffff !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        border-left: 6px solid #1e3a8a !important; /* Lacivert Sol Kenarlık */
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
        margin-bottom: 20px !important;
        padding: 20px !important;
    }
    
    /* Bilgi Kutuları İçin Mavi Kenarlık */
    div.stAlert {
        border-left: 6px solid #3b82f6 !important;
    }
    div.stAlert p { color: #1e293b !important; font-weight: 500; }

    /* Giriş Alanları (Inputlar) */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #f8fafc !important;
        color: #1e293b !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }

    /* Buton Tasarımları (Dashboard Mavi) */
    .stButton>button { 
        background-color: #1e3a8a !important; 
        color: #ffffff !important; 
        border: none !important; 
        border-radius: 8px !important; 
        font-weight: 600 !important; 
        padding: 10px 20px !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button:hover { background-color: #162a60 !important; transform: translateY(-1px); }
    
    /* Tablo Tasarımı */
    .stTable { 
        background-color: white; 
        border-radius: 12px; 
        overflow: hidden; 
        border: 1px solid #e2e8f0; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }
    </style>
    """, unsafe_allow_html=True)

# --- GÜVENLİK KONTROLÜ ---
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("⚠️ Lütfen önce ana sayfadan giriş yapınız.")
    st.stop()

db = DatabaseConnection()
engine = db.get_engine()
tenant_id = st.session_state.get("tenant_id", 1)
company_name = st.session_state.get("company_name", "Şirketiniz")

# ==========================================
# NAVBAR BÖLÜMÜ (GÖRSEL aa17c7 UYUMLU)
# ==========================================
nav1, nav2 = st.columns([6, 1.5])
with nav1: 
    st.markdown(f'<div class="navbar-container"><h3 style="margin:0;">TradeCore <span style="font-weight:400; color:#64748b;">| {company_name}</span></h3></div>', unsafe_allow_html=True)
with nav2:
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    if st.button("🏠 Ana Sayfaya Dön", use_container_width=True):
        st.switch_page("Anasayfa.py")

st.title("⚙️ Kurumsal Ayarlar ve Bot Yönetimi")
st.markdown("<p style='color: #475569; margin-bottom: 25px;'>Şirket profilinizi düzenleyin ve otonom piyasa takip botlarını yapılandırın.</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🏢 Şirket Profili", "🤖 Bot Yapılandırma"])

# --- TAB 1: ŞİRKET PROFİLİ ---
with tab1:
    st.markdown("### Kurumsal Bilgiler")
    try:
        query = text(f"""
            SELECT t.CompanyName, r.RegionName 
            FROM Tenants t 
            JOIN Regions r ON t.BaseRegionID = r.RegionID 
            WHERE t.TenantID = {tenant_id}
        """)
        with engine.connect() as conn:
            tenant_info = pd.read_sql(query, conn)
        
        if not tenant_info.empty:
            # Bilgi alanları da gölgeli ve sol kenarlıklı hale getirildi
            st.info(f"**Kayıtlı Şirket Adı:** {tenant_info['CompanyName'][0]}")
            st.info(f"**Operasyonel Merkez Bölge:** {tenant_info['RegionName'][0]}")
        
        st.write("---")
        st.markdown("<p style='color: #475569;'>Abonelik Tipi: <b>Kurumsal (Enterprise)</b></p>", unsafe_allow_html=True)
        st.markdown("<p style='color: #475569;'>Sistem Durumu: <span style='color: #10b981; font-weight:bold;'>Aktif</span></p>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Kurumsal bilgiler çekilemedi: {e}")

# --- TAB 2: BOT YAPILANDIRMA ---
with tab2:
    st.markdown("### Piyasa Takip Linkleri")
    st.write("Botun hangi hammaddeyi hangi dijital kaynaktan takip edeceğini buradan belirleyin.")

    try:
        # Seçim kutuları için verileri çek
        materials = pd.read_sql(text(f"SELECT MaterialID, MaterialName FROM Materials WHERE TenantID = {tenant_id}"), engine)
        regions = pd.read_sql(text("SELECT RegionID, RegionName FROM Regions"), engine)

        if not materials.empty:
            with st.form("bot_config_form"):
                col1, col2 = st.columns(2)
                with col1:
                    mat_id = st.selectbox("Takip Edilecek Hammadde", 
                                          options=materials['MaterialID'].tolist(),
                                          format_func=lambda x: materials[materials['MaterialID']==x]['MaterialName'].values[0])
                with col2:
                    reg_id = st.selectbox("Hedef Bölge Fiyatı", 
                                          options=regions['RegionID'].tolist(),
                                          format_func=lambda x: regions[regions['RegionID']==x]['RegionName'].values[0])
                
                target_url = st.text_input("Web Sitesi URL (Kaynak)", placeholder="https://tedarikci.com/urun-fiyati")
                selector = st.text_input("CSS Seçici (Fiyat Alanı)", placeholder=".price-value veya #current-price")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit_bot = st.form_submit_button("Bot Görevini Sisteme Kaydet")
                
                if submit_bot:
                    if target_url and selector:
                        insert_query = text("""
                            INSERT INTO ScraperSources (MaterialID, RegionID, TargetURL, CssSelector) 
                            VALUES (:m_id, :r_id, :url, :sel)
                        """)
                        with engine.connect() as conn:
                            conn.execute(insert_query, {"m_id": mat_id, "r_id": reg_id, "url": target_url, "sel": selector})
                            conn.commit()
                        st.success("✅ Bot görev listesine başarıyla eklendi. Bir sonraki otonom taramada veriler çekilecektir.")
                    else:
                        st.warning("Lütfen URL ve CSS seçici alanlarını boş bırakmayınız.")
        else:
            st.info("Bot yapılandırmak için önce 'Veri Yönetimi' sayfasından hammadde tanımlamalısınız.")

        # Mevcut Botları Listele
        st.write("---")
        st.markdown("### Aktif Takip Listesi")
        sources_df = pd.read_sql(text(f"""
            SELECT m.MaterialName AS 'Hammadde', r.RegionName AS 'Bölge', s.TargetURL AS 'Kaynak URL', 
                   CASE WHEN s.IsActive = 1 THEN 'Aktif' ELSE 'Pasif' END AS 'Durum'
            FROM ScraperSources s
            JOIN Materials m ON s.MaterialID = m.MaterialID
            JOIN Regions r ON s.RegionID = r.RegionID
            WHERE m.TenantID = {tenant_id}
        """), engine)
        
        if not sources_df.empty:
            st.table(sources_df)
        else:
            st.caption("Henüz aktif bir bot görevi tanımlanmamış.")

    except Exception as e:
        st.error(f"Bot listesi yüklenemedi: {e}")

st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("<center style='color: #475569;'>TradeCore Kurumsal v1.2 | Gazi YBS Laboratuvarı 2026</center>", unsafe_allow_html=True)