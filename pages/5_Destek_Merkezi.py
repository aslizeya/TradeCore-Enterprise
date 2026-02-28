import streamlit as st
import pandas as pd
from db_connection import DatabaseConnection
from sqlalchemy import text

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Destek Merkezi | TradeCore", layout="wide", initial_sidebar_state="collapsed")

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
        background-image: none !important; /* Gradyan kaldırıldı */
        color: #1e293b; /* Koyu metin temeli */
    }
    
    /* Yazı Renkleri (Koyu Lacivert/Gri ve Yüksek Kontrast) */
    h1, h2, h3 { color: #1e3a8a !important; font-weight: 800; }
    p, .stMarkdown p { color: #1e293b !important; } /* Paragraf ve markdown yazıları koyu */

    /* Üst Bar Tasarımı (Görseldeki gibi Lacivert Çerçeveli Beyaz Kutular) */
    .navbar-container { 
        background-color: #ffffff; 
        padding: 15px 30px; 
        border-radius: 12px; /* Görsele uygun köşeler */
        border: 2px solid #1e3a8a; /* Lacivert çerçeve */
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); /* Hafif gölge */
        margin-bottom: 30px; 
    }
    .navbar-container h3 { color: #1e3a8a !important; margin: 0; }
    
    /* --- FORM KUTULARI (GÖLGELİ VE RENKLİ SOL KENARLIKLI) --- */
    /* Etiketler (Koyu Yazı, Kutu Üstünde) */
    label[data-testid="stWidgetLabel"] p { 
        color: #1e293b !important; /* Koyu metin */
        font-weight: 600 !important; 
        background-color: transparent !important; /* Blok kaldırıldı */
        padding: 0 !important; 
        font-size: 1rem !important;
    }
    
    /* Giriş Kutuları (Beyaz, Gölceli, Sol Kenarlıklı) */
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea {
        background-color: #ffffff !important; 
        color: #1e293b !important;
        border: 1px solid #e2e8f0 !important; /* Standart ince çerçeve */
        border-radius: 8px !important; /* Köşeler */
        box-shadow: 0 2px 5px rgba(0,0,0,0.02); /* Hafif gölge */
        border-left: 5px solid #1e3a8a !important; /* Lacivert Sol Kenarlık */
        height: auto !important; /* Yükseklik standarda çekildi */
    }
    /* TextArea yükseklik ayarı */
    div[data-testid="stTextArea"] textarea { height: 150px !important; }

    /* Buton Tasarımları (Dashboard Uyumlu) */
    .stButton>button { 
        background-color: #1e3a8a !important; /* Lacivert arka plan */
        color: #ffffff !important; /* Beyaz yazı */
        border: none !important; 
        border-radius: 8px !important; 
        font-weight: 600 !important; 
        padding: 10px 20px !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button:hover { background-color: #162a60 !important; transform: translateY(-1px); }
    
    /* Sekme (Tabs) Tasarımı (Beyaz Tema Uyumlu) */
    .stTabs [data-baseweb="tab-list"] { gap: 0; background-color: transparent; }
    .stTabs [data-baseweb="tab"] { 
        background-color: transparent !important; 
        color: #1e293b !important; /* Koyu yazı */
        padding: 10px 20px !important;
        border-radius: 0 !important;
    }
    .stTabs [aria-selected="true"] { 
        border-bottom: 2px solid #1e3a8a !important; /* Lacivert alt çizgi */
    }
    .stTabs [aria-selected="true"] p { 
        color: #1e3a8a !important; 
        font-weight: 700 !important; 
    }

    /* Expander/Talepler (Gölgeli Beyaz Kart Görünümü) */
    div[data-testid="stExpander"] { 
        background-color: white !important; 
        border-radius: 12px !important; 
        margin-bottom: 15px !important; 
        border: 1px solid #e2e8f0 !important; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); /* Gölge */
    }
    div[data-testid="stExpander"] details summary p { 
        color: #1e3a8a !important; 
        font-weight: 800 !important; 
    }
    div[data-testid="stExpander"] details div[data-testid="stExpanderDetails"] p, 
    div[data-testid="stExpander"] details div[data-testid="stExpanderDetails"] b { 
        color: #1e293b !important; /* Koyu metin */
    }
    </style>
    """, unsafe_allow_html=True)

# --- GÜVENLİK KONTROLÜ ---
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("⚠️ Lütfen önce ana sayfadan giriş yapınız.")
    st.stop()
    
if st.session_state.get("role") != "tenant":
    st.error("Bu sayfa sadece TradeCore KOBİ müşterileri içindir.")
    st.stop()

# --- BAĞLANTI & OTURUM ---
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
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True) # Hizalama için boşluk
    if st.button("🏠 Ana Sayfaya Dön", use_container_width=True):
        st.switch_page("Anasayfa.py")

# ==========================================
# SAYFA İÇERİĞİ
# ==========================================
st.title("Destek ve Bildirim Merkezi")
# Altyazı rengi koyulaştırıldı
st.markdown("<p style='color: #475569; margin-bottom: 20px;'>Yönetim ekibiyle doğrudan iletişime geçin, talep ve şikâyetlerinizi buradan iletin.</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝 Yeni Talep / Şikâyet Oluştur", "📂 Geçmiş Taleplerim ve Yanıtlar"])

# --- TAB 1: YENİ TALEP OLUŞTURMA ---
with tab1:
    st.markdown("### Bize Ulaşın")
    with st.form("new_ticket_form", clear_on_submit=True):
        # Konu Alanı (Standard beyaz kutu, lacivert sol kenarlık, koyu etiket)
        subject = st.text_input("Konu", placeholder="Örn: Sisteme yeni bir hammadde ölçü birimi eklenmesi hk.")
        message = st.text_area("Mesajınız / Şikâyetiniz", placeholder="Lütfen talebinizi veya yaşadığınız sorunu detaylıca açıklayın...", height=150)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("Talebi Güvenli Bir Şekilde Gönder"):
            if subject and message:
                try:
                    query = text("""
                        INSERT INTO SupportTickets (TenantID, Subject, Message, Status) 
                        VALUES (:t_id, :subj, :msg, 'Açık')
                    """)
                    with engine.connect() as conn:
                        conn.execute(query, {"t_id": tenant_id, "subj": subject, "msg": message})
                        conn.commit()
                    st.success("Talebiniz başarıyla alındı. Yönetim ekibi (Admin) en kısa sürede size dönüş yapacaktır.")
                except Exception as e:
                    st.error(f"Veritabanı Hatası: {e}")
            else:
                st.warning("Lütfen Konu ve Mesaj alanlarını eksiksiz doldurunuz.")

# --- TAB 2: GEÇMİŞ TALEPLER VE YANITLAR ---
with tab2:
    st.markdown("### Taleplerimin Durumu")
    try:
        query = text("""
            SELECT TicketID, Subject, Message, Status, AdminReply, FORMAT(CreatedAt, 'dd.MM.yyyy HH:mm') as CreatedTime
            FROM SupportTickets 
            WHERE TenantID = :t_id
            ORDER BY CreatedAt DESC
        """)
        with engine.connect() as conn:
            tickets_df = pd.read_sql(query, conn, params={"t_id": tenant_id})
            
        if tickets_df.empty:
            st.info("💡 Henüz oluşturulmuş bir destek talebiniz bulunmuyor.")
        else:
            for index, row in tickets_df.iterrows():
                # Duruma göre statü ikonu
                status_icon = "🔴" if row['Status'] == 'Açık' else ("🟡" if row['Status'] == 'İnceleniyor' else "🟢")
                
                # Expander'lar gölgeli beyaz kart oldu
                with st.expander(f"{status_icon} {row['Subject']} ({row['CreatedTime']}) - Durum: {row['Status']}"):
                    st.markdown(f"**Sizin Mesajınız:**\n\n{row['Message']}")
                    st.markdown("<hr style='border: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
                    
                    if pd.isna(row['AdminReply']) or row['AdminReply'] == "":
                        st.info("⏳ Yönetim ekibi talebinizi inceliyor, henüz yanıt verilmedi.")
                    else:
                        # Yanıt koyu yazılı yeşil kutu
                        st.success(f"**Yönetici Yanıtı:**\n\n{row['AdminReply']}")
    except Exception as e:
        st.error(f"Talepler yüklenirken hata oluştu: {e}")

st.markdown("<br><br><br>", unsafe_allow_html=True)
# Alt bilgi yazısı koyulaştırıldı
st.markdown("<center style='color: #475569;'>TradeCore Kurumsal v1.2 | Gazi YBS Laboratuvarı 2026</center>", unsafe_allow_html=True)