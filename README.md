# TradeCore Enterprise
KOBI'ler Icin Otonom Finansal Karar Destek Motoru

TradeCore, KOBI statüsündeki işletmelerin fiyatlandırma stratejilerini ve maliyet yönetimlerini dijitalleştiren, veri odaklı bir Is Zekasi (BI) platformudur. Projenin temel amaci; isletmelerin maruz kaldigi gizli operasyonel maliyetleri seffaflastirmak, manuel piyasa takibini ortadan kaldirmak ve finansal surdurulebilirligi algoritmik bir zemine oturtmaktir.

Not: Bu repoda yer alan demo uygulamasinda, telif haklarini korumak amaciyla tamamen kurgusal bir isletme olan "Aura Coffee Lab" verileri kullanilarak bir is senaryosu simule edilmistir.

## Sistemin Temel Finansal Yetenekleri

- Butunlesik Tam Maliyetleme (OpEx Entegrasyonu): Geleneksel sistemlerin aksine maliyetleri sadece hammadde uzerinden hesaplamaz. Kira, fatura, personel gibi aylik sabit operasyonel yukleri (Overhead Costs) algoritmik olarak urun basina dagitarak yuzde yuz gercek net kar marjini ortaya cikarir.
- Otonom Piyasa Takibi (Web Scraping): Entegre bot mimarisi sayesinde, hammaddelerin dijital piyasalardaki anlik fiyat degisimlerini insan mudahalesi olmadan ceker ve maliyet tablolarini otomatik gunceller.
- Algoritmik Finansal Aksiyon Plani: Sistemin merkezindeki Logic Engine (Karar Motoru); hammadde artislarini ve kar daralmalarini aninda tespit eder. Hedefin altinda kalan urunler icin "Kritik", "Uyari" ve "Guvenli" statulerinde otonom fiyatlandirma tavsiyeleri ve aksiyon planlari uretir.
- Rol Bazli Multi-Tenant Mimari: Sistem, yonetici (Admin) ve musteri (Tenant) olmak uzere iki farkli rol uzerinden coklu sirket yonetimine uygun (SaaS) mimaride tasarlanmistir. Yonetici paneli uzerinden musteri kayitlari ve destek biletleri (ticket) yonetilebilmektedir.

## Kullanilan Teknolojiler

- Frontend ve UI Altyapisi: Python, Streamlit
- Veri Analizi ve Gorsellestirme: Pandas, Plotly Express
- Veritabani ve ORM: Microsoft SQL Server, SQLAlchemy, pyodbc
- Mimarisi: Multi-Tenant (SaaS), Role-Based Access Control (RBAC)

## Proje Dosya Yapisi

- Anasayfa.py : Sistemin giris, kimlik dogrulama ve rol yonetimi (Routing) modulu.
- 1_Dashboard.py : Logic Engine tarafindan uretilen verilerin gorsellestirildigi yonetici kokpiti.
- 2_Veri_Giris.py : Urun, hammadde ve recete (BOM) yonetimi.
- 4_Gider_Yonetimi.py : Operasyonel yuklerin (OpEx) sisteme tanimlandigi finans modulu.
- db_connection.py : SQL Server baglanti havuzu ve yapilandirmasi.
- logic_engine.py : Maliyet dagitimi ve aksiyon plani ureten ana is mantigi.

## Kurulum ve Calistirma

1. Repoyu bilgisayariniza klonlayin:
   git clone https://github.com/kullaniciadiniz/tradecore-enterprise.git

2. Gerekli kutuphaneleri yukleyin:
   pip install -r requirements.txt

3. SQL Server uzerinde TradeCoreDB adli veritabanini olusturun ve 'database_setup.sql' dosyasindaki betigi calistirarak tablolari/test verilerini yukleyin.

4. 'db_connection.py' icerisindeki veritabani baglanti dizesini kendi lokal sunucunuza gore duzenleyin.

5. Uygulamayi baslatin:
   streamlit run Anasayfa.py

---
