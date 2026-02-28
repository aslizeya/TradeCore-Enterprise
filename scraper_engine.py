import requests
from bs4 import BeautifulSoup
import re
from db_connection import DatabaseConnection
from sqlalchemy import text

class TradeCoreScraper:
    def __init__(self):
        self.db = DatabaseConnection()
        self.engine = self.db.get_engine()
        # Gerçek bir tarayıcı gibi görünmek için Headers
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def clean_price(self, price_str):
        """Metin halindeki fiyatı sayıya dönüştürür (Örn: '1.250,50 TL' -> 1250.50)"""
        try:
            # Rakamlar, virgül ve nokta dışındaki her şeyi temizle
            price_str = re.sub(r'[^\d,.]', '', price_str)
            # Binlik ayırıcıyı (nokta) kaldır, ondalık ayırıcıyı (virgül) noktaya çevir
            if ',' in price_str and '.' in price_str:
                price_str = price_str.replace('.', '').replace(',', '.')
            elif ',' in price_str:
                price_str = price_str.replace(',', '.')
            return float(price_str)
        except Exception:
            return None

    def fetch_price(self, url, selector):
        """Verilen URL ve CSS Selector ile fiyatı çeker"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                element = soup.select_one(selector)
                if element:
                    return self.clean_price(element.text.strip())
            return None
        except Exception as e:
            print(f"Scraping Hatası ({url}): {e}")
            return None

    def run_automation(self):
        """
        Veritabanındaki aktif bot görevlerini tarar ve fiyatları günceller.
        """
        print("🚀 Piyasa taraması başlatıldı...")
        
        # SQL sorgusunu 'text()' içine alarak SQLAlchemy 2.0 uyumlu hale getirdik
        get_tasks_query = text("SELECT MaterialID, RegionID, TargetURL, CssSelector FROM ScraperSources WHERE IsActive = 1")
        
        try:
            with self.engine.connect() as conn:
                # Görev listesini veritabanından al
                tasks = conn.execute(get_tasks_query).fetchall()
                
                if not tasks:
                    print("ℹ️ Takip edilecek aktif bir bot görevi bulunamadı. Ayarlar sayfasından link ekleyin.")
                    return

                for task in tasks:
                    # Veritabanından gelen sütunlar
                    mat_id, reg_id, url, selector = task
                    
                    # Web kazıma işlemini yap
                    price = self.fetch_price(url, selector)
                    
                    if price:
                        # Yeni fiyatı PriceHistory tablosuna ekle
                        insert_query = text("""
                            INSERT INTO PriceHistory (MaterialID, RegionID, UnitPrice, SourceType) 
                            VALUES (:m_id, :r_id, :price, 'Bot-Auto')
                        """)
                        
                        # Parametreleri güvenli bir şekilde gönderiyoruz
                        conn.execute(insert_query, {"m_id": mat_id, "r_id": reg_id, "price": price})
                        
                        # SQLAlchemy 2.0 için işlemi onayla (commit)
                        conn.commit() 
                        
                        print(f"✅ ID:{mat_id} için yeni fiyat: {price} TL (Bölge:{reg_id})")
                    else:
                        print(f"❌ ID:{mat_id} için fiyat çekilemedi. (URL: {url})")
                        
        except Exception as e:
            print(f"🚨 Otomasyon motorunda bir hata oluştu: {e}")

if __name__ == "__main__":
    bot = TradeCoreScraper()
    bot.run_automation()