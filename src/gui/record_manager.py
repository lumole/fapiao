import tkinter as tk
from tkinter import ttk
from decimal import Decimal

class RecordManager:
    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="记录详情", padding="10")
        
        # 添加表头
        ttk.Label(self.frame, text="物品名称").grid(row=0, column=0, padx=5)
        ttk.Label(self.frame, text="金额").grid(row=0, column=1, padx=5)
        
        # 创建记录列表
        self.records_frame = ttk.Frame(self.frame)
        self.records_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.records = []
        
        # 添加总金额显示
        self.total_label = ttk.Label(self.frame, text="总金额: ¥0.00")
        self.total_label.grid(row=2, column=0, columnspan=2, pady=5)
    
    def add_record_row(self):
        record_frame = ttk.Frame(self.records_frame)
        record_frame.pack(fill=tk.X, pady=2)
        
        name_entry = ttk.Entry(record_frame)
        name_entry.pack(side=tk.LEFT, padx=2)
        
        amount_entry = ttk.Entry(record_frame, width=15)
        amount_entry.pack(side=tk.LEFT, padx=2)
        
        self.records.append((name_entry, amount_entry))
        amount_entry.bind('<KeyRelease>', self.update_total)
    
    def update_total(self, event=None):
        total = Decimal('0.00')
        for _, amount_entry in self.records:
            try:
                amount = Decimal(amount_entry.get() or '0')
                total += amount
            except:
                pass
        self.total_label.config(text=f"总金额: ¥{total:.2f}")
    
    def clear(self):
        for frame in self.records_frame.winfo_children():
            frame.destroy()
        self.records.clear()
        self.update_total() 