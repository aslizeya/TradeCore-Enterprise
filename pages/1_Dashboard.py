import streamlit as st
import pandas as pd
import plotly.express as px
from db_connection import DatabaseConnection
from logic_engine import TradeCoreLogic

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Yönetici Kokpiti | TradeCore", layout="wide")

# --- KURUMSAL CSS (BEYAZ DASHBOARD TASARIMI) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] { 
        font-family: 'Outfit', sans-serif; 
        background-color: #f8fafc; /* Görseldeki açık gri/beyaz arka plan */
    }
    
    /* Üstteki Şirket Bilgi Kartı */
    .navbar-container { 
        background-color: #ffffff; 
        padding: 20px 30px; 
        border-radius: 12px; 
        border: 2px solid #1e3a8a; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
        margin-bottom: 25px; 
    }
    
    h1, h2, h3 { color: #1e3a8a; font-weight: 800; }
    
    /* KPI Kartları */
    .kpi-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
        border-left: 5px solid #1e3a8a;
        text-align: center;
    }
    .kpi-title { color: #64748b; font-size: 1.1rem; font-weight: 600; margin-bottom: 10px; }
    .kpi-value { color: #1e3a8a; font-size: 2.2rem; font-weight: 800; }
    
    .stButton>button { 
        background-color: #1e3a8a !important; 
        color: white !important; 
        border-radius: 8px; 
        font-weight: 600; 
        width: 100%; 
    }
    .stButton>button:hover { background-color: #172554 !important; }
    .stDataFrame { border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

# --- GÜVENLİK VE ROL KONTROLÜ ---
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("Lütfen önce ana sayfadan giriş yapınız.")
    st.stop()
    
if st.session_state.get("role") != "tenant":
    st.error("Bu sayfa sadece TradeCore KOBİ müşterileri içindir.")
    st.stop()

tenant_id = st.session_state.get("tenant_id", 1)
company_name = st.session_state.get("company_name", "Şirketiniz")

# ==========================================
# NAVBAR BÖLÜMÜ (GÖRSEL UYUMLU)
# ==========================================
nav_col1, nav_col2 = st.columns([6, 1.2])
with nav_col1:
    st.markdown(f'<div class="navbar-container"><h3 style="margin:0;">TradeCore <span style="font-weight:400; color:#64748b;">| {company_name}</span></h3></div>', unsafe_allow_html=True)
with nav_col2:
    st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
    if st.button("Oturumu Kapat"):
        st.session_state.clear()
        st.switch_page("Anasayfa.py")

# ==========================================
# VERİ ÇEKME (LOGIC ENGINE)
# ==========================================
# Başlık görsele uygun şekilde güncellendi
st.title("📊 Yönetici Kokpiti (Gösterge Paneli)")
st.markdown("<p style='color: #64748b; margin-bottom: 30px;'>İşletmenizin düzenli finansal sistemi, tam maliyet analiziyle (OpEx dâhil) takip edin.</p>", unsafe_allow_html=True)

try:
    logic = TradeCoreLogic()
    df = logic.calculate_product_analysis(tenant_id)
except Exception as e:
    st.error(f"Sistem Motoru Hatası: {e}")
    st.stop()

if df.empty:
    st.info("💡 Sisteme henüz aktif ürün veya reçete eklemediniz. Lütfen 'Ürün ve Reçete' sayfasından veri giriniz.")
    st.stop()

# ==========================================
# KPI KARTLARI (ÖZET) - İkonlar ve Başlıklar
# ==========================================
col1, col2, col3, col4 = st.columns(4)

total_products = len(df)
avg_margin = df['CurrentMargin'].mean()
critical_products = len(df[df['CurrentMargin'] < df['TargetMarginPercentage']])
avg_overhead = df['OverheadCost'].mean()

with col1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">📦 Aktif Ürün</div><div class="kpi-value">{total_products}</div></div>', unsafe_allow_html=True)
with col2:
    # Görseldeki yeşil tonu
    color = "#28a745" if avg_margin >= 20 else "#dc3545"
    st.markdown(f'<div class="kpi-card" style="border-left-color: {color};"><div class="kpi-title">📈 Net Kâr Marjı</div><div class="kpi-value" style="color:{color};">%{avg_margin:.1f}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="kpi-card" style="border-left-color: #dc3545;"><div class="kpi-title">⚠️ Riskli Ürün Sayısı</div><div class="kpi-value" style="color:#dc3545;">{critical_products}</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">💸 Ürün Başına Düşen Sabit Gider</div><div class="kpi-value">{avg_overhead:.2f} ₺</div></div>', unsafe_allow_html=True)

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# ==========================================
# GRAFİKLER (GÖRSELLEŞTİRME)
# ==========================================
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("### 💰 Maliyet Kırılımı (Hammadde vs Operasyonel)")
    st.caption("Ürün maliyetinin ne kadarını desteklediği, ne kadarı kira/faturadan geliyor?")
    
    # Yığılmış (Stacked) Bar Grafik için veriyi hazırlama
    df_melted = pd.melt(df, id_vars=['ProductName'], value_vars=['MaterialCost', 'OverheadCost'], 
                        var_name='Maliyet Türü', value_name='Tutar (TL)')
    
    df_melted['Maliyet Türü'] = df_melted['Maliyet Türü'].replace({'MaterialCost': 'Hammadde Maliyeti', 'OverheadCost': 'Sabit Gider (OpEx) Payı'})
    
    fig_cost = px.bar(df_melted, x='ProductName', y='Tutar (TL)', color='Maliyet Türü', 
                      color_discrete_map={'Hammadde Maliyeti': '#3b82f6', 'Sabit Gider (OpEx) Payı': '#1e3a8a'},
                      barmode='stack')
    fig_cost.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_cost, use_container_width=True)

with chart_col2:
    st.markdown("### 🎯 Hedef Kâr vs Gerçekleşen Net Kâr")
    st.caption("Hedefinizin (Kırmızı Çizgi) altında kalan ürünleri tespit edin.")
    
    fig_margin = px.bar(df, x='ProductName', y='CurrentMargin', text_auto='.1f',
                        color='CurrentMargin', color_continuous_scale=['#ef4444', '#10b981'])
    
    # Hedef Kâr Marjını Çizgi Olarak Ekleme (Ortalama Hedef)
    avg_target = df['TargetMarginPercentage'].mean()
    fig_margin.add_hline(y=avg_target, line_dash="dash", line_color="red", annotation_text="Ortalama Hedef")
    fig_margin.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False)
    st.plotly_chart(fig_margin, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# YAPAY ZEKA AKSİYON PLANI TABLOSU
# ==========================================
st.markdown("### 🤖 TradeCore Finansal Aksiyon Planı")
st.write("Sistem Motoru (Logic Engine), güncel hammadde fiyatlarını ve işletme giderlerinizi analiz ederek aşağıdaki tavsiyeleri oluşturdu:")

# Tablo sütun isimlerini Türkçeleştirelim
display_df = df[['ProductName', 'CurrentSalePrice', 'MaterialCost', 'OverheadCost', 'TotalCost', 'CurrentMargin', 'ActionPlan']].copy()
display_df.columns = ['Ürün Adı', 'Satış Fiyatı (TL)', 'Hammadde Maliyeti (TL)', 'Sabit Gider Payı (TL)', 'TOPLAM MALİYET (TL)', 'Net Kâr Marjı (%)', 'Sistem Tavsiyesi']

# Yuvarlama işlemleri
display_df['Satış Fiyatı (TL)'] = display_df['Satış Fiyatı (TL)'].round(2)
display_df['Hammadde Maliyeti (TL)'] = display_df['Hammadde Maliyeti (TL)'].round(2)
display_df['Sabit Gider Payı (TL)'] = display_df['Sabit Gider Payı (TL)'].round(2)
display_df['TOPLAM MALİYET (TL)'] = display_df['TOPLAM MALİYET (TL)'].round(2)
display_df['Net Kâr Marjı (%)'] = display_df['Net Kâr Marjı (%)'].round(1)

# Tablo renklendirme
def color_action(val):
    if "KRİTİK" in str(val) or "UYARI" in str(val):
        return 'color: #ef4444; font-weight: bold; background-color: #fee2e2;'
    return 'color: #059669; font-weight: bold; background-color: #d1fae5;'

styled_df = display_df.style.map(color_action, subset=['Sistem Tavsiyesi'])
st.dataframe(styled_df, use_container_width=True, hide_index=True)

st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("<center style='color: #64748b;'>TradeCore Enterprise v1.2 | Gazi YBS Laboratuvarı 2026</center>", unsafe_allow_html=True)