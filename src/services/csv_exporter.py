import csv
from decimal import Decimal

class CSVExporter:
    @staticmethod
    def export_records(filename, records, mode='w'):
        try:
            total = Decimal('0.00')
            for _, amount_entry in records:
                try:
                    amount = Decimal(amount_entry.get() or '0')
                    total += amount
                except:
                    pass
            
            with open(filename, mode, newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                if mode == 'w':
                    writer.writerow(["物品名称", "金额"])
                
                for name_entry, amount_entry in records:
                    if name_entry.get() and amount_entry.get():
                        writer.writerow([
                            name_entry.get(),
                            amount_entry.get()
                        ])
                
                writer.writerow(["总计", f"{total:.2f}"])
            
            return True, None
        except Exception as e:
            return False, str(e) 