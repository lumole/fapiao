import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal
from services.pdf_reader import extract_info_from_pdf
import os

class RecordManager:
    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="记录详情", padding="10")
        
        # 添加自动识别选项
        self.auto_detect_var = tk.BooleanVar()
        self.auto_detect_frame = ttk.Frame(self.frame)
        self.auto_detect_frame.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        self.auto_detect_cb = ttk.Checkbutton(
            self.auto_detect_frame, 
            text="自动识别发票", 
            variable=self.auto_detect_var,
            command=self.handle_auto_detect
        )
        self.auto_detect_cb.pack(side=tk.LEFT, padx=5)
        
        # 添加表头
        ttk.Label(self.frame, text="物品名称").grid(row=1, column=0, padx=5)
        ttk.Label(self.frame, text="规格型号").grid(row=1, column=1, padx=5)
        ttk.Label(self.frame, text="金额").grid(row=1, column=2, padx=5)
        
        # 创建一个带滚动条的框架来容纳记录
        self.records_canvas = tk.Canvas(self.frame)
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.records_canvas.yview)
        self.records_frame = ttk.Frame(self.records_canvas)
        
        # 配置 canvas
        self.records_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # 网格布局
        self.records_canvas.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scrollbar.grid(row=2, column=3, sticky=(tk.N, tk.S))
        
        # 在 canvas 中创建窗口来显示 records_frame
        self.canvas_frame = self.records_canvas.create_window((0, 0), window=self.records_frame, anchor='nw')
        
        # 绑定事件
        self.records_frame.bind('<Configure>', self._on_frame_configure)
        self.records_canvas.bind('<Configure>', self._on_canvas_configure)
        
        # 绑定鼠标滚轮事件
        self.records_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        self.records = []
        
        # 添加总金额显示
        self.total_label = ttk.Label(
            self.frame, 
            text="总金额: ¥0.00",
            font=('Arial', 12, 'bold')  # 设置字体让它更醒目
        )
        # 使用place替代grid，固定在窗口右上角
        self.total_label.place(
            relx=1.0,  # 相对于父窗口的右边
            x=-10,     # 向左偏移10像素
            y=10,      # 向下偏移10像素
            anchor='ne'  # 右上角对齐
        )
        
        # 保存对发票框架的引用
        self.invoice_frame = None
    
    def set_invoice_frame(self, invoice_frame):
        """设置发票框架的引用"""
        self.invoice_frame = invoice_frame
    
    def add_record_row(self):
        record_frame = ttk.Frame(self.records_frame)
        record_frame.pack(fill=tk.X, pady=2)
        
        name_entry = ttk.Entry(record_frame)
        name_entry.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        
        spec_entry = ttk.Entry(record_frame)
        spec_entry.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        
        amount_entry = ttk.Entry(record_frame, width=15)
        amount_entry.pack(side=tk.LEFT, padx=2)
        
        self.records.append((name_entry, spec_entry, amount_entry))
        amount_entry.bind('<KeyRelease>', self.update_total)
    
    def update_total(self, event=None):
        total = Decimal('0.00')
        for _, _, amount_entry in self.records:
            try:
                amount = Decimal(amount_entry.get() or '0')
                total += amount
            except:
                pass
        self.total_label.config(text=f"总金额: ¥{total:.2f}")
    
    def clear(self):
        """清除所有记录"""
        for frame in self.records_frame.winfo_children():
            frame.destroy()
        self.records.clear()
        self.update_total()
        # 重置滚动区域
        self._on_frame_configure()
    
    def handle_auto_detect(self):
        """处理自动识别选项的变化"""
        if not self.invoice_frame:
            messagebox.showerror("错误", "未找到发票框架")
            return
            
        if self.auto_detect_var.get():
            if not self.invoice_frame.paths:
                messagebox.showwarning("提示", "请先拖入发票PDF文件")
                self.auto_detect_var.set(False)
                return
            self.process_pdf_files(self.invoice_frame.paths)
    
    def process_pdf_files(self, pdf_paths):
        """处理PDF文件列表"""
        # 清空现有记录
        self.clear()
        
        # 处理每个PDF文件
        for pdf_path in pdf_paths:
            results = extract_info_from_pdf(pdf_path)
            
            if results:
                for name, spec, amount in results:
                    # 添加新行
                    self.add_record_row()
                    # 获取最后一行的输入框
                    name_entry, spec_entry, amount_entry = self.records[-1]
                    # 填入信息
                    name_entry.insert(0, name)  # 保留星号
                    spec_entry.insert(0, spec)
                    amount_entry.insert(0, str(amount))
        
        # 更新总金额
        self.update_total() 
    
    def _on_frame_configure(self, event=None):
        """当记录框架大小改变时，更新画布的滚动区域"""
        self.records_canvas.configure(scrollregion=self.records_canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """当画布大小改变时，调整内部框架的宽度"""
        self.records_canvas.itemconfig(self.canvas_frame, width=event.width)
    
    def _on_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        if self.records_frame.winfo_height() > self.records_canvas.winfo_height():
            self.records_canvas.yview_scroll(int(-1*(event.delta/120)), "units") 