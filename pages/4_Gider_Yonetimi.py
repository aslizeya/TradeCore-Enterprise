import streamlit as st
import pandas as pd
from db_connection import DatabaseConnection
from sqlalchemy import text

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Gider Yönetimi | TradeCore", layout="wide", initial_sidebar_state="collapsed")

db = DatabaseConnection()
engine = db.get_engine()

# Oturum Yönetimi
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["role"] = None 

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
        background-image: none !important;
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
        border: 2px solid #1e3a8a; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
        margin-bottom: 30px; 
    }
    .navbar-container h3 { color: #1e3a8a !important; margin:0; }
    
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

    /* Giriş Alanları (Inputlar) */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
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
    
    /* Tablo Görünümü */
    .stDataFrame { background-color: white; border-radius: 12px; border: 1px solid #e2e8f0; }
    
    /* Bilgilendirme Kutuları */
    div.stAlert {
        border-radius: 12px !important;
        border-left: 6px solid #3b82f6 !important;
    }
    div.stAlert p { color: #1e293b !important; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

# --- GÜVENLİK KONTROLÜ ---
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("⚠️ Lütfen önce ana sayfadan giriş yapınız.")
    st.stop()

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

# ==========================================
# SAYFA İÇERİĞİ
# ==========================================
st.title("Gider ve Operasyonel Yük Yönetimi")
st.markdown("<p style='color: #475569; margin-bottom: 25px;'>İşletmenizin sabit giderlerini tarihsel olarak yönetin ve kâr hesaplama kurallarını belirleyin.</p>", unsafe_allow_html=True)

# --- AKILLI ANALİZ KONFİGÜRASYONU ---
with st.expander("⚙️ Finansal Analiz ve Maliyetleme Ayarları", expanded=False):
    try:
        settings_query = text("SELECT IncludeOverheadInProfit, DefaultOverheadPercent FROM TenantSettings WHERE TenantID = :t_id")
        with engine.connect() as conn:
            settings = conn.execute(settings_query, {"t_id": tenant_id}).fetchone()
            
        if not settings:
            with engine.connect() as conn:
                conn.execute(text("INSERT INTO TenantSettings (TenantID) VALUES (:t_id)"), {"t_id": tenant_id})
                conn.commit()
            include_op, def_perc = False, 10.0
        else:
            include_op, def_perc = bool(settings[0]), float(settings[1])

        st.info("💡 **Bilgi:** Bu ayarlar Yönetici Kokpiti'ndeki (Dashboard) net kâr hesaplamalarını ve alarm sistemini doğrudan etkiler.")
        
        c1, c2 = st.columns([2, 1])
        with c1:
            new_include = st.toggle("Net Kâr hesabına Kira, Fatura ve Personel giderlerini dâhil et", value=include_op)
            st.caption("Açık olduğunda, ürün maliyetlerine operasyonel yük payı da eklenir (Tam Maliyetleme).")
        
        with c2:
            new_perc = st.number_input("Varsayılan Gider Payı (%)", value=def_perc, min_value=0.0, max_value=50.0, step=1.0)
            st.caption("Eğer sisteme güncel bir gider girmezseniz, satış fiyatının yüzde kaçı gider sayılsın?")
        
        if st.button("Analiz Ayarlarını Kaydet"):
            update_query = text("""
                UPDATE TenantSettings 
                SET IncludeOverheadInProfit = :inc, DefaultOverheadPercent = :perc 
                WHERE TenantID = :t_id
            """)
            with engine.connect() as conn:
                conn.execute(update_query, {"inc": 1 if new_include else 0, "perc": new_perc, "t_id": tenant_id})
                conn.commit()
            st.success("✅ Ayarlar başarıyla güncellendi. Dashboard bu yeni modele göre çalışacak.")
            st.rerun()
    except Exception as e:
        st.error(f"Ayarlar yüklenirken bir hata oluştu: {e}")

st.markdown("<br>", unsafe_allow_html=True)

# --- 3 SEKMELİ GİDER YÖNETİMİ ---
tab1, tab2, tab3 = st.tabs(["➕ Yeni Gider Ekle", "🔄 Mevcut Gideri Güncelle", "📋 Gider Tablosu ve Arşiv"])

# TAB 1: YENİ EKLE
with tab1:
    st.markdown("### Sıfırdan Yeni Bir Gider Kalemi Tanımla")
    with st.form("new_overhead_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            cost_name = st.text_input("Gider Adı", placeholder="Örn: Muhasebe Ücreti")
        with col2:
            amount = st.number_input("Tutar (TL)", min_value=0.0, format="%.2f")
        with col3:
            frequency = st.selectbox("Tekrarlanma Sıklığı", ["Aylık", "Yıllık", "Haftalık", "Günlük", "Tek Seferlik"])
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("Sisteme Aktif Olarak Kaydet"):
            if cost_name and amount > 0:
                try:
                    query = text("""
                        INSERT INTO OverheadCosts (TenantID, CostName, Amount, Frequency, Status) 
                        VALUES (:t_id, :name, :amount, :freq, 'Aktif')
                    """)
                    with engine.connect() as conn:
                        conn.execute(query, {"t_id": tenant_id, "name": cost_name, "amount": amount, "freq": frequency})
                        conn.commit()
                    st.success(f"'{cost_name}' başarıyla eklendi.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Hata: {e}")
            else:
                st.error("Lütfen bilgileri eksiksiz giriniz.")

# TAB 2: GÜNCELLE VE ARŞİVLE
with tab2:
    st.markdown("### Fiyatı Değişen Bir Gideri Güncelle")
    try:
        active_costs_df = pd.read_sql(text(f"SELECT CostID, CostName, Amount, Frequency FROM OverheadCosts WHERE TenantID = {tenant_id} AND Status = 'Aktif'"), engine)
        
        if active_costs_df.empty:
            st.info("💡 Güncellenecek aktif bir gider bulunmuyor.")
        else:
            with st.form("update_overhead_form", clear_on_submit=True):
                st.write("Aşağıdan zamlanan/düşen gideri seçip yeni fiyatını girin. Eski fiyat kaybolmaz, geçmiş tablosuna aktarılır.")
                
                selected_cost_id = st.selectbox("Güncellenecek Gider", options=active_costs_df['CostID'].tolist(),
                                               format_func=lambda x: f"{active_costs_df[active_costs_df['CostID']==x]['CostName'].values[0]} (Şu an: {active_costs_df[active_costs_df['CostID']==x]['Amount'].values[0]:,.2f} TL)")
                
                new_amount = st.number_input("YENİ Tutar (TL)", min_value=0.0, format="%.2f")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("Güncelle ve Eski Veriyi Arşivle"):
                    if new_amount > 0:
                        cost_info = active_costs_df[active_costs_df['CostID'] == selected_cost_id].iloc[0]
                        c_name = cost_info['CostName']
                        c_freq = cost_info['Frequency']
                        
                        with engine.connect() as conn:
                            conn.execute(text("UPDATE OverheadCosts SET Status = 'Geçmiş' WHERE CostID = :c_id"), {"c_id": selected_cost_id})
                            conn.execute(text("INSERT INTO OverheadCosts (TenantID, CostName, Amount, Frequency, Status) VALUES (:t_id, :name, :amount, :freq, 'Aktif')"), 
                                         {"t_id": tenant_id, "name": c_name, "amount": new_amount, "freq": c_freq})
                            conn.commit()
                            
                        st.success("✅ Gider başarıyla güncellendi! Eski veri arşive kaldırıldı.")
                        st.rerun() 
                    else:
                        st.warning("Lütfen geçerli bir yeni tutar girin.")
    except Exception as e:
        st.error(f"Hata oluştu: {e}")

# TAB 3: FİLTRELİ TABLO
with tab3:
    st.markdown("### İşletme Giderleri Listesi")
    filter_option = st.radio("Tablo Görünümü", ["Sadece Aktif Giderler", "Arşivlenmiş (Geçmiş) Giderler", "Tüm Geçmişi Göster"], horizontal=True)
    
    try:
        base_query = """
            SELECT CostName AS 'Gider Adı', Amount AS 'Tutar (TL)', Frequency AS 'Sıklık', 
                   Status AS 'Durum', FORMAT(CreatedAt, 'dd.MM.yyyy HH:mm') AS 'Kayıt Tarihi'
            FROM OverheadCosts 
            WHERE TenantID = :t_id
        """
        if filter_option == "Sadece Aktif Giderler":
            base_query += " AND Status = 'Aktif'"
        elif filter_option == "Arşivlenmiş (Geçmiş) Giderler":
            base_query += " AND Status = 'Geçmiş'"
            
        base_query += " ORDER BY CreatedAt DESC"
        
        with engine.connect() as conn:
            df_costs = pd.read_sql(text(base_query), conn, params={"t_id": tenant_id})
            
        if not df_costs.empty:
            def color_status(val):
                color = '#10b981' if val == 'Aktif' else '#ef4444' 
                return f'color: {color}; font-weight: bold'
                
            styled_df = df_costs.style.map(color_status, subset=['Durum'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            
            if filter_option in ["Sadece Aktif Giderler", "Tüm Geçmişi Göster"]:
                active_monthly_query = text("SELECT SUM(Amount) FROM OverheadCosts WHERE TenantID = :t_id AND Frequency = 'Aylık' AND Status = 'Aktif'")
                with engine.connect() as conn:
                    active_monthly = conn.execute(active_monthly_query, {"t_id": tenant_id}).scalar() or 0
                st.info(f"💡 **Şu Anki Güncel Aylık Sabit Gideriniz:** {active_monthly:,.2f} TL")
        else:
            st.info("Seçtiğiniz filtreye uygun gider kaydı bulunamadı.")
            
    except Exception as e:
        st.error(f"Tablo yüklenirken hata oluştu: {e}")

st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("<center style='color: #64748b;'>TradeCore Kurumsal v1.2 | Gazi YBS Laboratuvarı 2026</center>", unsafe_allow_html=True)