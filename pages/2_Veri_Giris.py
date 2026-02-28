import streamlit as st
import pandas as pd
from db_connection import DatabaseConnection
from sqlalchemy import text

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Veri Yönetimi | TradeCore", layout="wide", initial_sidebar_state="collapsed")

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
        border: 2px solid #1e3a8a; /* Lacivert çerçeve */
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

    /* --- FORM KUTULARI VE EXPANDER'LAR (GÖLGELİ VE LACİVERT SOL KENARLIKLI) --- */
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
    
    /* İnfografik Şeritler */
    .info-strip {
        background-color: #f1f5f9;
        padding: 12px;
        border-radius: 10px;
        color: #1e3a8a;
        font-weight: 700;
        margin-bottom: 10px;
        border-left: 4px solid #1e3a8a;
    }
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

st.title("Operasyon ve Veri Yönetimi")
st.markdown("<p style='color: #475569; margin-bottom: 25px;'>Ürünlerinizi, hammaddelerinizi ve reçetelerinizi <b>güncel arşivleriyle</b> yönetin.</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["➕ Yeni Tanımlamalar", "🔄 Fiyat Güncelle & Arşivle", "📋 Envanter Arşivi"])

# --- TAB 1: YENİ TANIMLAMALAR ---
with tab1:
    st.markdown("### Sisteme Sıfırdan Veri Ekle")
    c1, c2 = st.columns(2)
    with c1:
        with st.expander("1️⃣ Yeni Hammadde Ekle", expanded=True):
            with st.form("new_material_form", clear_on_submit=True):
                mat_name = st.text_input("Hammadde Adı")
                mat_unit = st.selectbox("Ölçü Birimi", ["kg", "Litre", "Adet", "Gram", "Kutu", "Çuval"])
                mat_price = st.number_input("Güncel Birim Fiyatı (TL)", min_value=0.01, format="%.2f", step=1.0)
                
                if st.form_submit_button("Hammaddeyi Kaydet"):
                    if mat_name:
                        try:
                            with engine.connect() as conn:
                                mat_query = text("""
                                    INSERT INTO Materials (TenantID, MaterialName, Unit, Status) 
                                    OUTPUT INSERTED.MaterialID
                                    VALUES (:t_id, :name, :unit, 'Aktif')
                                """)
                                result = conn.execute(mat_query, {"t_id": tenant_id, "name": mat_name, "unit": mat_unit})
                                new_mat_id = result.fetchone()[0]
                                
                                price_query = text("""
                                    INSERT INTO PriceHistory (MaterialID, UnitPrice, UpdateDate) 
                                    VALUES (:m_id, :price, GETDATE())
                                """)
                                conn.execute(price_query, {"m_id": new_mat_id, "price": mat_price})
                                
                                conn.commit()
                            st.success(f"'{mat_name}' ({mat_price} TL) başarıyla eklendi.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Hata: {e}")
                    else:
                        st.warning("Lütfen hammadde adını giriniz.")
    
    with c2:
        with st.expander("2️⃣ Yeni Ürün (Satış) Ekle", expanded=True):
            with st.form("new_product_form", clear_on_submit=True):
                prod_name = st.text_input("Ürün Adı")
                prod_price = st.number_input("Satış Fiyatı (TL)", min_value=0.0, format="%.2f")
                prod_margin = st.number_input("Hedef Kâr Marjı (%)", min_value=0.0, max_value=100.0, value=60.0)
                prod_sales = st.number_input("Aylık Tahmini Satış (Adet)", min_value=1, value=100)
                
                if st.form_submit_button("Ürünü Kaydet"):
                    if prod_name:
                        query = text("INSERT INTO Products (TenantID, ProductName, CurrentSalePrice, TargetMarginPercentage, EstimatedMonthlySales, Status) VALUES (:t_id, :name, :price, :margin, :sales, 'Aktif')")
                        with engine.connect() as conn:
                            conn.execute(query, {"t_id": tenant_id, "name": prod_name, "price": prod_price, "margin": prod_margin, "sales": prod_sales})
                            conn.commit()
                        st.success(f"'{prod_name}' başarıyla eklendi.")
                        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("3️⃣ Ürün Reçetesi (BOM) Bağla", expanded=False):
        try:
            prod_df = pd.read_sql(text(f"SELECT ProductID, ProductName FROM Products WHERE TenantID = {tenant_id} AND Status = 'Aktif'"), engine)
            mat_df = pd.read_sql(text(f"SELECT MaterialID, MaterialName FROM Materials WHERE TenantID = {tenant_id} AND Status = 'Aktif'"), engine)
            if not prod_df.empty and not mat_df.empty:
                with st.form("recipe_form", clear_on_submit=True):
                    r1, r2, r3 = st.columns(3)
                    with r1: sel_prod = st.selectbox("Hangi Ürün İçin?", options=prod_df['ProductID'].tolist(), format_func=lambda x: prod_df[prod_df['ProductID']==x]['ProductName'].values[0])
                    with r2: sel_mat = st.selectbox("İçindeki Hammadde", options=mat_df['MaterialID'].tolist(), format_func=lambda x: mat_df[mat_df['MaterialID']==x]['MaterialName'].values[0])
                    with r3: qty = st.number_input("Kullanım Miktarı", min_value=0.001, format="%.3f", step=0.010)
                    if st.form_submit_button("Reçeteye Ekle"):
                        query = text("INSERT INTO ProductRecipes (ProductID, MaterialID, QuantityNeeded) VALUES (:p_id, :m_id, :qty)")
                        with engine.connect() as conn:
                            conn.execute(query, {"p_id": sel_prod, "m_id": sel_mat, "qty": qty})
                            conn.commit()
                        st.success("Reçete başarıyla bağlandı!")
            else:
                st.info("Reçete bağlamak için önce en az bir ürün ve bir hammadde eklemelisiniz.")
        except Exception as e:
            st.error(f"Hata: {e}")

# --- TAB 2: GÜNCELLE VE ARŞİVLE ---
with tab2:
    st.markdown("### Veri Güncelleme Merkezi")
    colA, colB = st.columns(2)
    with colA:
        st.markdown('<div class="info-strip">📉 Hammadde Fiyatı Güncelle</div>', unsafe_allow_html=True)
        try:
            active_mats = pd.read_sql(text(f"SELECT MaterialID, MaterialName FROM Materials WHERE TenantID = {tenant_id} AND Status = 'Aktif'"), engine)
            if not active_mats.empty:
                with st.form("price_entry_form", clear_on_submit=True):
                    st.write("Mevcut bir hammaddenin piyasa fiyatı değiştiyse buradan güncelleyin. Eski fiyatlar maliyet geçmişi için saklanır.")
                    selected_mat = st.selectbox("Hammadde Seçin", options=active_mats['MaterialID'].tolist(), format_func=lambda x: active_mats[active_mats['MaterialID']==x]['MaterialName'].values[0])
                    new_price = st.number_input("YENİ Birim Fiyat (TL)", min_value=0.01, step=0.1, format="%.2f")
                    if st.form_submit_button("Fiyatı Sisteme İşle"):
                        query = text("INSERT INTO PriceHistory (MaterialID, UnitPrice, UpdateDate) VALUES (:mat, :price, GETDATE())")
                        with engine.connect() as conn:
                            conn.execute(query, {"mat": selected_mat, "price": new_price})
                            conn.commit()
                        st.success("✅ Hammadde fiyatı başarıyla güncellendi!")
            else:
                st.info("Güncellenecek aktif hammadde bulunamadı.")
        except Exception as e: st.error(e)

    with colB:
        st.markdown('<div class="info-strip">🏷️ Ürün Fiyatı & Satış Hacmi Güncelle</div>', unsafe_allow_html=True)
        try:
            active_prods = pd.read_sql(text(f"SELECT ProductID, ProductName, CurrentSalePrice, TargetMarginPercentage, EstimatedMonthlySales FROM Products WHERE TenantID = {tenant_id} AND Status = 'Aktif'"), engine)
            if not active_prods.empty:
                with st.form("update_product_form", clear_on_submit=True):
                    sel_p_id = st.selectbox("Güncellenecek Ürün", options=active_prods['ProductID'].tolist(), format_func=lambda x: f"{active_prods[active_prods['ProductID']==x]['ProductName'].values[0]} ({active_prods[active_prods['ProductID']==x]['CurrentSalePrice'].values[0]} TL)")
                    new_sale_price = st.number_input("YENİ Satış Fiyatı (TL)", min_value=0.01, format="%.2f")
                    new_sales_vol = st.number_input("YENİ Tahmini Satış (Adet)", min_value=1)
                    
                    if st.form_submit_button("Güncelle ve Arşivle"):
                        p_info = active_prods[active_prods['ProductID'] == sel_p_id].iloc[0]
                        p_name, p_margin = p_info['ProductName'], p_info['TargetMarginPercentage']
                        
                        with engine.connect() as conn:
                            conn.execute(text("UPDATE Products SET Status = 'Geçmiş' WHERE ProductID = :p_id"), {"p_id": sel_p_id})
                            result = conn.execute(text("INSERT INTO Products (TenantID, ProductName, CurrentSalePrice, TargetMarginPercentage, EstimatedMonthlySales, Status) OUTPUT INSERTED.ProductID VALUES (:t_id, :name, :price, :margin, :sales, 'Aktif')"), 
                                                  {"t_id": tenant_id, "name": p_name, "price": new_sale_price, "margin": p_margin, "sales": new_sales_vol})
                            new_prod_id = result.fetchone()[0]
                            recipes = conn.execute(text("SELECT MaterialID, QuantityNeeded FROM ProductRecipes WHERE ProductID = :old_id"), {"old_id": sel_p_id}).fetchall()
                            for r in recipes:
                                conn.execute(text("INSERT INTO ProductRecipes (ProductID, MaterialID, QuantityNeeded) VALUES (:new_id, :m_id, :qty)"), {"new_id": new_prod_id, "m_id": r[0], "qty": r[1]})
                            conn.commit()
                        st.success("✅ Ürün güncellendi, eski fiyat arşivlendi ve reçete korundu!")
                        st.rerun()
            else:
                st.info("Güncellenecek aktif ürün bulunamadı.")
        except Exception as e: st.error(e)

# --- TAB 3: FİLTRELİ TABLO ---
with tab3:
    st.markdown("### Envanter ve Arşiv Tabloları")
    filter_option = st.radio("Görünüm Filtresi", ["Sadece Aktif Veriler", "Arşivlenmiş (Geçmiş) Veriler"], horizontal=True)
    status_filter = "AND Status = 'Aktif'" if filter_option == "Sadece Aktif Veriler" else "AND Status = 'Geçmiş'"
    
    try:
        df_p = pd.read_sql(text(f"SELECT ProductName AS 'Ürün Adı', CurrentSalePrice AS 'Satış Fiyatı (TL)', EstimatedMonthlySales AS 'Aylık Satış (Adet)', Status AS 'Durum' FROM Products WHERE TenantID = {tenant_id} {status_filter}"), engine)
        if not df_p.empty:
            def color_status(val):
                color = '#10b981' if val == 'Aktif' else '#ef4444' 
                return f'color: {color}; font-weight: bold'
                
            styled_df = df_p.style.map(color_status, subset=['Durum'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
        else:
            st.info("Seçilen filtreye uygun kayıt bulunamadı.")
    except Exception as e: st.error(e)

st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("<center style='color: #64748b;'>TradeCore Kurumsal v1.2 | Gazi YBS Laboratuvarı 2026</center>", unsafe_allow_html=True)