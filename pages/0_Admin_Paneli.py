import streamlit as st
import pandas as pd
from db_connection import DatabaseConnection
from sqlalchemy import text

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Sistem Yönetimi | TradeCore", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# BEYAZ DASHBOARD TEMASI (GÖRSEL 132d9e UYUMLU)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    /* GENEL ARKA PLAN (BEMBEYAZ) */
    html, body, [data-testid="stAppViewContainer"] { 
        font-family: 'Outfit', sans-serif; 
        background-color: #f8fafc !important; 
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
    
    /* Beyaz Kart Yapıları (Yetkisiz Erişim Ekranı) */
    .white-card {
        background-color: #ffffff; 
        padding: 40px; 
        border-radius: 12px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
        border: 1px solid #e2e8f0; 
        border-left: 6px solid #1e3a8a;
    }
    .white-card h2, .white-card p { color: #1e293b !important; }

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

    /* --- FORM KUTULARI VE EXPANDER'LAR (GÖLGELİ VE RENKLİ SOL KENARLIKLI) --- */
    div[data-testid="stExpander"], div[data-testid="stForm"] {
        background-color: #ffffff !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        border-left: 6px solid #1e3a8a !important; /* Lacivert Sol Kenarlık */
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
        margin-bottom: 20px !important;
        padding: 10px !important;
    }
    
    /* Expander Başlık Yazısı */
    div[data-testid="stExpander"] details summary p {
        color: #1e3a8a !important;
        font-weight: 800 !important;
    }
    div[data-testid="stExpander"] p, div[data-testid="stExpander"] b {
        color: #1e293b !important;
    }

    /* Giriş Alanları (Inputlar) */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stTextArea textarea {
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
    
    /* Tablo Düzenlemeleri */
    .stDataFrame { background-color: white; border-radius: 12px; border: 1px solid #e2e8f0; padding: 10px; }
    
    /* Bilgi Kutuları İçin Mavi Kenarlık */
    div.stAlert {
        border-radius: 12px !important;
        border-left: 6px solid #3b82f6 !important;
    }
    div.stAlert p { color: #1e293b !important; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

# --- MERKEZİ GÜVENLİK DUVARI ---
if st.session_state.get("role") != "admin":
    st.markdown("""<style>[data-testid="stSidebar"] {display: none;}</style>""", unsafe_allow_html=True)
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, lock_col, _ = st.columns([1, 1.5, 1])
    with lock_col:
        st.markdown('<div class="white-card">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center;'>🛡️ Yetkisiz Erişim</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; margin-bottom:20px;'>Bu sayfa sadece TradeCore Sistem Yöneticilerine özeldir. Lütfen yönetici anahtarını giriniz.</p>", unsafe_allow_html=True)
        
        admin_key = st.text_input("Yönetici Anahtarı", type="password", placeholder="••••••••")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Doğrula ve Giriş Yap", use_container_width=True):
            if admin_key == "gazi123":
                st.session_state["authenticated"] = True
                st.session_state["role"] = "admin"
                st.session_state["company_name"] = "TradeCore Yönetim Merkezi"
                st.rerun()
            else:
                st.error("Hatalı anahtar! Erişim reddedildi.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- BAĞLANTI & OTURUM ---
db = DatabaseConnection()
engine = db.get_engine()
company_name = st.session_state.get("company_name", "Yönetim Merkezi")

# ==========================================
# NAVBAR BÖLÜMÜ (GÖRSEL 132d9e UYUMLU)
# ==========================================
nav1, nav2 = st.columns([6, 1.5])
with nav1:
    st.markdown(f'<div class="navbar-container"><h3 style="margin:0;">TradeCore <span style="font-weight:400; color:#64748b;">| {company_name}</span></h3></div>', unsafe_allow_html=True)
with nav2:
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    if st.button("🏠 Ana Sayfaya Dön", use_container_width=True):
        st.switch_page("Anasayfa.py")

# ==========================================
# SAYFA İÇERİĞİ
# ==========================================
st.title("Süper Yönetici Paneli")
# Alt yazı rengi lacivert/gri tona uyarlandı
st.markdown("<p style='color: #475569; margin-bottom: 25px;'>Sistemdeki tüm KOBİ'leri yönetin ve destek biletlerini cevaplayın.</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["✨ Yeni Şirket Kaydı", "📋 Mevcut Portföy", "💬 Müşteri Talepleri (Biletler)"])

# --- TAB 1: YENİ ŞİRKET EKLE ---
with tab1:
    st.markdown("### Kurumsal Müşteri Oryantasyonu")
    with st.form("new_tenant_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            new_company_name = st.text_input("Şirket Adı", placeholder="Örn: Gazi Lojistik A.Ş.")
            tenant_password = st.text_input("Müşteri Giriş Şifresi", placeholder="Örn: gazi2026") 
        with col2:
            try:
                regions = pd.read_sql("SELECT * FROM Regions ORDER BY RegionName", engine)
                base_region = st.selectbox("Operasyon Merkezi (Şehir)", options=regions['RegionID'].tolist(), 
                                           format_func=lambda x: regions[regions['RegionID']==x]['RegionName'].values[0])
            except:
                st.error("Veritabanından şehirler çekilemedi. Bölge tablosunu kontrol edin.")
                base_region = 1
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("Şirketi Sisteme Tanımla"):
            if new_company_name and tenant_password:
                try:
                    query = text("INSERT INTO Tenants (CompanyName, BaseRegionID, AccessPassword) VALUES (:name, :reg, :pw)")
                    with engine.connect() as conn:
                        conn.execute(query, {"name": new_company_name, "reg": base_region, "pw": tenant_password})
                        conn.commit()
                    st.success(f"✅ {new_company_name} başarıyla eklendi! Şifre: {tenant_password}")
                except Exception as e:
                    st.error(f"Kayıt Hatası: {e}")
            else:
                st.error("Şirket adı ve şifre zorunludur.")

# --- TAB 2: PORTFÖY TABLOSU ---
with tab2:
    st.markdown("### Kayıtlı Şirketler (Müşteriler)")
    try:
        tenants_df = pd.read_sql("""
            SELECT t.TenantID as 'ID', t.CompanyName as 'Şirket Adı', r.RegionName as 'Merkez Şehir', 
                   t.AccessPassword as 'Giriş Şifresi', FORMAT(t.CreatedAt, 'dd.MM.yyyy') as 'Kayıt Tarihi'
            FROM Tenants t
            LEFT JOIN Regions r ON t.BaseRegionID = r.RegionID
        """, engine)
        st.dataframe(tenants_df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Tablo yüklenirken hata oluştu: {e}")

# --- TAB 3: DESTEK BİLETLERİ YANITLAMA ---
with tab3:
    st.markdown("### Gelen Müşteri Biletleri (Destek Talepleri)")
    try:
        tickets_query = text("""
            SELECT tk.TicketID, tn.CompanyName, tk.Subject, tk.Message, tk.Status, tk.AdminReply, FORMAT(tk.CreatedAt, 'dd.MM.yyyy HH:mm') as CreatedTime
            FROM SupportTickets tk
            JOIN Tenants tn ON tk.TenantID = tn.TenantID
            ORDER BY CASE WHEN tk.Status = 'Çözüldü' THEN 2 ELSE 1 END, tk.CreatedAt DESC
        """)
        
        with engine.connect() as conn:
            tickets_df = pd.read_sql(tickets_query, conn)
            
        if tickets_df.empty:
            st.info("💡 Sistemde henüz bir müşteri talebi bulunmuyor.")
        else:
            for index, row in tickets_df.iterrows():
                icon = "🔴" if row['Status'] == 'Açık' else ("🟡" if row['Status'] == 'İnceleniyor' else "🟢")
                
                with st.expander(f"{icon} [Talep #{row['TicketID']}] {row['CompanyName']} - {row['Subject']}"):
                    st.markdown(f"**Tarih:** {row['CreatedTime']} | **Mevcut Durum:** {row['Status']}")
                    st.markdown(f"**Müşteri Mesajı:**\n> {row['Message']}")
                    
                    st.markdown("<hr style='border:1px solid #e2e8f0; margin:10px 0;'>", unsafe_allow_html=True)
                    
                    with st.form(f"reply_form_{row['TicketID']}"):
                        new_status = st.selectbox("Durumu Güncelle", ["Açık", "İnceleniyor", "Çözüldü"], index=["Açık", "İnceleniyor", "Çözüldü"].index(row['Status']))
                        reply_msg = st.text_area("Müşteriye Yanıtınız", value=row['AdminReply'] if row['AdminReply'] else "")
                        
                        if st.form_submit_button("Yanıtı Gönder ve Güncelle"):
                            update_query = text("""
                                UPDATE SupportTickets 
                                SET Status = :status, AdminReply = :reply, UpdatedAt = GETDATE()
                                WHERE TicketID = :t_id
                            """)
                            with engine.connect() as conn:
                                conn.execute(update_query, {"status": new_status, "reply": reply_msg, "t_id": row['TicketID']})
                                conn.commit()
                            st.success(f"Talep #{row['TicketID']} güncellendi!")
                            st.rerun()
                            
    except Exception as e:
        st.error(f"Biletler çekilirken hata oluştu: {e}")

st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("<center style='color: #64748b;'>TradeCore Kurumsal v1.2 | Gazi YBS Laboratuvarı 2026</center>", unsafe_allow_html=True)