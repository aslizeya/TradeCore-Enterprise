import pandas as pd
from db_connection import DatabaseConnection
from sqlalchemy import text

class TradeCoreLogic:
    def __init__(self):
        self.db = DatabaseConnection()
        self.engine = self.db.get_engine()

    def calculate_product_analysis(self, tenant_id):
        with self.engine.connect() as conn:
            # 1. KULLANICI AYARLARINI ÇEK
            settings_query = text("SELECT IncludeOverheadInProfit, DefaultOverheadPercent FROM TenantSettings WHERE TenantID = :t_id")
            settings = conn.execute(settings_query, {"t_id": tenant_id}).fetchone()
            
            include_overhead = False
            default_percent = 10.0
            
            if settings:
                include_overhead = bool(settings[0])
                default_percent = float(settings[1])

            # 2. GERÇEK GİDERLERİ ÇEK
            total_monthly_overhead = 0.0
            if include_overhead:
                overhead_query = text("SELECT ISNULL(SUM(Amount), 0) FROM OverheadCosts WHERE TenantID = :t_id AND Status = 'Aktif' AND Frequency = 'Aylık'")
                total_monthly_overhead = float(conn.execute(overhead_query, {"t_id": tenant_id}).scalar() or 0.0)

            # 3. ÜRÜNLERİ, SATIŞ HACİMLERİNİ VE HAMMADDE MALİYETLERİNİ HESAPLA
            product_query = text("""
                SELECT p.ProductID, p.ProductName, p.CurrentSalePrice, p.TargetMarginPercentage, p.EstimatedMonthlySales,
                       ISNULL(SUM(r.QuantityNeeded * ph.UnitPrice), 0) as MaterialCost
                FROM Products p
                LEFT JOIN ProductRecipes r ON p.ProductID = r.ProductID
                LEFT JOIN Materials m ON r.MaterialID = m.MaterialID AND m.Status = 'Aktif'
                OUTER APPLY (
                    SELECT TOP 1 UnitPrice FROM PriceHistory WHERE MaterialID = m.MaterialID ORDER BY UpdateDate DESC
                ) ph
                WHERE p.TenantID = :t_id AND p.Status = 'Aktif'
                GROUP BY p.ProductID, p.ProductName, p.CurrentSalePrice, p.TargetMarginPercentage, p.EstimatedMonthlySales
            """)
            df = pd.read_sql(product_query, conn, params={"t_id": tenant_id})

            if df.empty:
                return df

            # 4. YENİ ZEKÂ: HACİM TABANLI MALİYET DAĞITIMI (Volume-Based Costing)
            total_sales_volume = df['EstimatedMonthlySales'].sum()
            
            # Tüm şirketin aylık toplam giderini, satılan toplam ürün sayısına bölüyoruz
            # Bu bize satılan her 1 adet ürünün yüklenmesi gereken sabit gider payını verir.
            overhead_per_unit = (total_monthly_overhead / total_sales_volume) if total_sales_volume > 0 else 0.0

            def calculate_overhead_share(row):
                if not include_overhead:
                    return 0.0 
                
                if total_monthly_overhead > 0:
                    # Artık ürün çeşidine değil, 1 adet ürünün sırtlaması gereken sabit payı ekliyoruz
                    return overhead_per_unit
                else:
                    return row['CurrentSalePrice'] * (default_percent / 100.0)

            df['OverheadCost'] = df.apply(calculate_overhead_share, axis=1)
            
            # 5. GERÇEK (NET) MALİYET VE KÂR MARJI
            df['TotalCost'] = df['MaterialCost'] + df['OverheadCost']
            
            def calculate_margin(row):
                if row['CurrentSalePrice'] > 0:
                    return ((row['CurrentSalePrice'] - row['TotalCost']) / row['CurrentSalePrice']) * 100
                return 0.0

            df['CurrentMargin'] = df.apply(calculate_margin, axis=1)
            
            # 6. YAPAY ZEKA AKSİYON PLANI
            def decide_action(row):
                if row['CurrentMargin'] < row['TargetMarginPercentage']:
                    needed_price = row['TotalCost'] / (1 - (row['TargetMarginPercentage'] / 100.0))
                    if row['OverheadCost'] > 0:
                        return f"⚠️ KRİTİK: Sabit gider payı ({row['OverheadCost']:.2f} TL) eklendiğinde zarar ediyorsunuz! Fiyatı en az {needed_price:.2f} TL yapın."
                    else:
                        return f"⚠️ UYARI: Hammadde pahalı! Fiyatı {needed_price:.2f} TL yapın."
                return "✅ Karlılık Mükemmel"

            df['ActionPlan'] = df.apply(decide_action, axis=1)
            return df