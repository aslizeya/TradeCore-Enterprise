import streamlit as st
from db_connection import DatabaseConnection
from sqlalchemy import text

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="TradeCore | Anasayfa", layout="wide", initial_sidebar_state="collapsed")

db = DatabaseConnection()
engine = db.get_engine()

# Oturum Yönetimi
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["role"] = None 

# ==========================================
# KURUMSAL TASARIM CSS (GÖRSEL UYUMLU)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    /* Arka Plan: Görseldeki Düz Mor Tonu */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Outfit', sans-serif;
        background-color: #6b21a8; 
    }
    
    .hero-title { color: #ffffff !important; text-align: center; font-weight: 800; font-size: 3.5rem; margin-bottom: 5px; }
    .hero-subtitle { color: #cbd5e1 !important; text-align: center; font-size: 1.2rem; margin-bottom: 40px; }
    
    /* Özellik Kartları (Beyaz Kutular) */
    .feature-box { 
        background-color: #ffffff; 
        padding: 30px; 
        border-radius: 16px; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.1); 
        text-align: center; 
        height: 100%; 
    }
    .feature-box h3 { color: #1e3a8a !important; font-weight: 800;}
    .feature-box p { color: #475569 !important; }

    /* Hızlı Rehber (Expander) Düzenlemesi */
    div[data-testid="stExpander"] {
        background-color: rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        border: none !important;
    }
    div[data-testid="stExpander"] details summary {
        background-color: #ffffff !important;
        border-radius: 10px !important;
        padding: 12px !important;
    }
    div[data-testid="stExpander"] details summary p {
        color: #1e3a8a !important;
        font-weight: 700 !important;
    }
    div[data-testid="stExpander"] details div[data-testid="stExpanderDetails"] p {
        color: #ffffff !important; /* Arka planda beyaz yazı */
        line-height: 1.6;
    }
    
    /* Login Ekranı ve Inputlar */
    label[data-testid="stWidgetLabel"] p { color: #ffffff !important; font-weight: 600 !important; }
    
    /* Sekmeler (Tabs) */
    .stTabs [data-baseweb="tab"] { background-color: rgba(255,255,255,0.1); color: #ffffff; border-radius: 8px 8px 0 0; }
    .stTabs [aria-selected="true"] { background-color: #ffffff !important; }
    .stTabs [aria-selected="true"] p { color: #1e3a8a !important; font-weight: 800 !important; }

    /* Buton Tasarımları */
    [data-testid="stButton"] button {
        background-color: #ffffff !important; 
        border-radius: 12px !important; 
        border: none !important;
        transition: 0.3s;
    }
    [data-testid="stButton"] button p { color: #1e3a8a !important; font-weight: 800 !important; }
    [data-testid="stButton"] button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }

    /* Sidebar Çıkış Butonu Özel Renk */
    [data-testid="stSidebar"] [data-testid="stButton"] button { background-color: #6b21a8 !important; }
    [data-testid="stSidebar"] [data-testid="stButton"] button p { color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# DURUM 1: ZİYARETÇİ EKRANI (LOGİN)
# ==========================================
if not st.session_state["authenticated"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="hero-title">TradeCore Enterprise</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">İşletmenizin Yeni Nesil Karar Destek Merkezi</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown('<div class="feature-box"><h3>Otonom Piyasa</h3><p>Türkiye genelindeki fiyatları izleyin.</p></div>', unsafe_allow_html=True)
    with col2: st.markdown('<div class="feature-box"><h3>Tam Maliyet</h3><p>Hammadde, kira ve personel yönetimi.</p></div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="feature-box"><h3>Aktif İletişim</h3><p>Yönetimle anında iletişime geçin.</p></div>', unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Hızlı Başlangıç Rehberi
    _, guide_col, _ = st.columns([1, 2, 1])
    with guide_col:
        with st.expander("TradeCore Nasıl Kullanılır? (Hızlı Başlangıç Rehberi)"):
            st.markdown("""
            **1. Sisteme Giriş:** Size tanımlanan Şirket Kodu ve Şifre ile sisteme giriş yapın.
            
            **2. Veri ve Reçete Tanımlama:** 'Ürün ve Reçete' panelinden kullandığınız hammaddeleri, güncel fiyatları ve sattığınız ürünler için reçeteleri sisteme işleyin.
            
            **3. Sabit Giderlerin Kaydı:** İşletmenizin aylık kira, fatura ve personel maaşı gibi operasyonel yüklerini kaydedin.
            
            **4. Akıllı Analiz:** 'Yönetici Kokpiti'ne geçtiğinizde sistem; girdiğiniz tüm verileri hesaplayarak ürün başına düşen gerçek maliyetinizi çıkarır ve zarar ettiğiniz ürünler için size net fiyatlandırma tavsiyeleri sunar.
            """)
            
    st.markdown("<br><h2 style='color:#ffffff; text-align:center; font-weight: 800; margin-bottom:20px;'>Sisteme Giriş</h2>", unsafe_allow_html=True)
    
    _, login_col, _ = st.columns([1, 1.2, 1])
    with login_col:
        tab_kobi, tab_admin = st.tabs(["Şirket Girişi", "Sistem Yöneticisi"])
        
        with tab_kobi:
            tenant = st.text_input("Şirket Kodu (Tenant ID)", placeholder="Örn: 1")
            pw = st.text_input("Şifre", type="password", key="pw_tenant")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Şirket Hesabına Bağlan", use_container_width=True):
                if tenant and pw:
                    query = text("SELECT TenantID, CompanyName FROM Tenants WHERE TenantID = :t_id AND AccessPassword = :pw")
                    with engine.connect() as conn:
                        user_check = conn.execute(query, {"t_id": tenant, "pw": pw}).fetchone()
                        if user_check:
                            st.session_state.update({"authenticated": True, "role": "tenant", "tenant_id": tenant, "company_name": user_check[1]})
                            st.rerun() 
                        else:
                            st.error("Giriş bilgileri hatalı.")
            
        with tab_admin:
            admin_user = st.text_input("Yönetici Adı", placeholder="admin")
            admin_pw = st.text_input("Şifre", type="password", key="pw_admin")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Yönetici Paneline Bağlan", use_container_width=True):
                if admin_user == "admin" and admin_pw == "gazi123":
                    st.session_state.update({"authenticated": True, "role": "admin", "company_name": "TradeCore Yönetim Merkezi"})
                    st.rerun()
                else:
                    st.error("Yönetici bilgileri hatalı.")

# ==========================================
# DURUM 2: KULLANICI EKRANI (PORTAL)
# ==========================================
else:
    company = st.session_state.get("company_name", "TradeCore")
    user_role = st.session_state.get("role", "tenant")
    
    with st.sidebar:
        st.markdown(f"<h2 style='color: #1e3a8a; font-weight: 800; margin-bottom: 0;'>TradeCore</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #64748b; font-weight: 600; margin-bottom: 30px;'>{company}</p>", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("Oturumu Kapat", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    _, main_col, _ = st.columns([1, 2, 1])
    
    with main_col:
        if user_role == "tenant":
            st.markdown(f'<div style="text-align:center; color:white;"><h1>Merhaba, {company}</h1><p>Tüm operasyonlarınızı aşağıdaki panellerden hızlıca yönetebilirsiniz.</p></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            r1_c1, r1_c2 = st.columns(2)
            with r1_c1:
                if st.button("Yönetici Kokpiti\n\nKâr Marjları ve Alarmlar", use_container_width=True):
                    st.switch_page("pages/1_Dashboard.py")
            with r1_c2:
                if st.button("Ürün ve Reçete\n\nHammadde ve Fiyatlar", use_container_width=True):
                    st.switch_page("pages/2_Veri_Giris.py")
                
            st.markdown("<br>", unsafe_allow_html=True)
            r2_c1, r2_c2 = st.columns(2)
            with r2_c1:
                if st.button("Sabit Giderler\n\nKira, Maaş ve Faturalar", use_container_width=True):
                    st.switch_page("pages/4_Gider_Yonetimi.py")
            with r2_c2:
                if st.button("Destek Merkezi\n\nŞikâyet ve Bildirimler", use_container_width=True):
                    st.switch_page("pages/5_Destek_Merkezi.py")
        
        elif user_role == "admin":
            st.markdown('<div style="text-align:center; color:white;"><h1>Sistem Yönetim Paneli</h1><p>Müşterileri ve destek biletlerini yönetin.</p></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            admin_c1, admin_c2 = st.columns(2)
            with admin_c1:
                if st.button("Müşteri Şirketleri Yönet\n\nYeni Kayıt ve Yetkiler", use_container_width=True):
                    st.switch_page("pages/0_Admin_Paneli.py")
            with admin_c2:
                if st.button("Gelen Destek Biletleri\n\nMüşteri Taleplerini Yanıtla", use_container_width=True):
                    st.switch_page("pages/0_Admin_Paneli.py")

st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("<center style='color: #cbd5e1;'>TradeCore Enterprise v1.2 | Gazi YBS Laboratuvarı 2026</center>", unsafe_allow_html=True)