import pyodbc
from sqlalchemy import create_engine
import urllib

class DatabaseConnection:
    """
    TradeCore Enterprise - Veritabanı Bağlantı Yönetimi
    Mimar: Aslı Zeynep
    """
    def __init__(self):
        # --- BURAYI KENDİ BİLGİLERİNE GÖRE DÜZENLE ---
        self.server = r'localhost\SQLEXPRESS'  
        self.database = 'TradeCore'
        self.driver = 'ODBC Driver 17 for SQL Server' # Bilgisayarındaki driver sürümü
        
        # Windows Authentication (SSMS'e şifresiz giriyorsan bu kullanılır)
        self.connection_string = (
            f"Driver={{{self.driver}}};"
            f"Server={self.server};"
            f"Database={self.database};"
            f"Trusted_Connection=yes;"
        )

    def get_engine(self):
        """SQLAlchemy motoru oluşturur (Pandas ve analizler için)"""
        params = urllib.parse.quote_plus(self.connection_string)
        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
        return engine

    def test_connection(self):
        """Bağlantının sağlıklı olup olmadığını kontrol eder"""
        try:
            engine = self.get_engine()
            connection = engine.connect()
            print("✅ TradeCore: Veritabanı bağlantısı başarıyla kuruldu!")
            connection.close()
            return True
        except Exception as e:
            print(f"❌ Hata: Bağlantı kurulamadı. \nDetay: {e}")
            return False

# Test etmek için alt kısım (Sadece bu dosya çalıştırıldığında aktif olur)
if __name__ == "__main__":
    db = DatabaseConnection()
    db.test_connection()