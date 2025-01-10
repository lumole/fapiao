import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinterdnd2 import *
from .frames import DragDropFrame
from .record_manager import RecordManager
from services.file_merger import FileMerger
from services.csv_exporter import CSVExporter

class InvoiceMergerApp:
    def __init__(self, root):
        self.root = root
        if not isinstance(self.root, TkinterDnD.Tk):
            self.root = TkinterDnD.Tk()
        self.root.title("发票整理工具")
        
        self.setup_ui()
        
    def setup_ui(self):
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建拖拽区域
        self.payment_frame = DragDropFrame(self.main_frame, "支付记录（图片）", self.on_files_dropped)
        self.payment_frame.grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.invoice_frame = DragDropFrame(self.main_frame, "发票（PDF）", self.on_files_dropped)
        self.invoice_frame.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 设置记录管理器
        self.record_manager = RecordManager(self.main_frame)
        self.record_manager.frame.grid(row=0, column=2, rowspan=2, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.record_manager.set_invoice_frame(self.invoice_frame)
        
        # 设置其他UI组件...
        self.setup_mode_frame()
        self.setup_buttons()
        self.setup_csv_frame()
        
    def setup_mode_frame(self):
        # 添加合并模式选择框架
        self.mode_frame = ttk.LabelFrame(self.main_frame, text="合并模式", padding="10")
        self.mode_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        self.merge_mode = tk.StringVar(value="new")
        
        ttk.Radiobutton(
            self.mode_frame, 
            text="创建新文件", 
            variable=self.merge_mode, 
            value="new"
        ).grid(row=0, column=0, padx=5)
        
        ttk.Radiobutton(
            self.mode_frame, 
            text="追加到现有文件", 
            variable=self.merge_mode, 
            value="append"
        ).grid(row=0, column=1, padx=5)
        
        ttk.Button(
            self.mode_frame, 
            text="选择现有PDF", 
            command=self.select_existing_pdf
        ).grid(row=0, column=2, padx=5)
        
        self.existing_pdf_path = None
        
        # ... 其余方法的实现 ... 

    def setup_buttons(self):
        """设置按钮"""
        # 添加清除按钮
        self.clear_button = ttk.Button(
            self.main_frame, 
            text="清除所有", 
            command=self.clear_all
        )
        self.clear_button.grid(row=2, column=0, columnspan=2, pady=5)
        
        # 合并按钮
        self.merge_button = ttk.Button(
            self.main_frame, 
            text="合并文件", 
            command=self.merge_files
        )
        self.merge_button.grid(row=3, column=0, columnspan=2, pady=5)

    def setup_csv_frame(self):
        """设置CSV导出相关的UI"""
        # CSV模式选择框架
        self.csv_frame = ttk.LabelFrame(
            self.record_manager.frame, 
            text="CSV导出模式", 
            padding="10"
        )
        self.csv_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # CSV模式选择
        self.csv_mode = tk.StringVar(value="new")
        
        ttk.Radiobutton(
            self.csv_frame, 
            text="创建新文件", 
            variable=self.csv_mode, 
            value="new"
        ).grid(row=0, column=0, padx=5)
        
        ttk.Radiobutton(
            self.csv_frame, 
            text="追加到现有文件", 
            variable=self.csv_mode, 
            value="append"
        ).grid(row=0, column=1, padx=5)
        
        # 选择现有CSV按钮
        ttk.Button(
            self.csv_frame, 
            text="选择现有CSV", 
            command=self.select_existing_csv
        ).grid(row=0, column=2, padx=5)
        
        self.existing_csv_path = None
        
        # 导出CSV按钮
        self.export_button = ttk.Button(
            self.record_manager.frame, 
            text="导出CSV", 
            command=self.export_csv
        )
        self.export_button.grid(row=4, column=0, columnspan=2, pady=5)

    def on_files_dropped(self):
        """当文件被拖放时的回调"""
        # 确保支付记录和发票数量匹配
        if len(self.payment_frame.paths) > len(self.record_manager.records):
            # 添加新的记录行
            for _ in range(len(self.payment_frame.paths) - len(self.record_manager.records)):
                self.record_manager.add_record_row()

    def clear_all(self):
        """清除所有数据"""
        self.payment_frame.clear()
        self.invoice_frame.clear()
        self.record_manager.clear()
        self.existing_pdf_path = None
        self.existing_csv_path = None

    def select_existing_pdf(self):
        """选择现有PDF文件"""
        file_path = filedialog.askopenfilename(
            title="选择PDF文件",
            filetypes=[("PDF文件", "*.pdf")]
        )
        if file_path:
            self.existing_pdf_path = file_path
            self.merge_mode.set("append")
            messagebox.showinfo("成功", f"已选择文件：{file_path}")

    def select_existing_csv(self):
        """选择现有CSV文件"""
        file_path = filedialog.askopenfilename(
            title="选择CSV文件",
            filetypes=[("CSV文件", "*.csv")]
        )
        if file_path:
            self.existing_csv_path = file_path
            self.csv_mode.set("append")
            messagebox.showinfo("成功", f"已选择文件：{file_path}")

    def merge_files(self):
        """合并文件"""
        if not self.payment_frame.paths or not self.invoice_frame.paths:
            messagebox.showerror("错误", "请先选择支付记录和发票文件")
            return
        
        if len(self.payment_frame.paths) != len(self.invoice_frame.paths):
            messagebox.showerror("错误", "支付记录和发票数量不匹配")
            return
        
        try:
            output_path = self.existing_pdf_path if self.merge_mode.get() == "append" else "merged_invoice.pdf"
            
            success, error = FileMerger.merge_files(
                self.payment_frame.paths,
                self.invoice_frame.paths,
                output_path,
                self.existing_pdf_path if self.merge_mode.get() == "append" else None
            )
            
            if success:
                messagebox.showinfo("成功", f"PDF文件已合并保存至: {output_path}")
            else:
                messagebox.showerror("错误", f"合并过程中出现错误: {error}")
            
        except Exception as e:
            messagebox.showerror("错误", f"合并过程中出现错误: {str(e)}")

    def export_csv(self):
        """导出CSV文件"""
        try:
            if self.csv_mode.get() == "append" and self.existing_csv_path:
                filename = self.existing_csv_path
            else:
                filename = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV 文件", "*.csv")],
                    title="保存记录"
                )
                if not filename:
                    return
            
            success, error = CSVExporter.export_records(
                filename,
                self.record_manager.records,
                'a' if self.csv_mode.get() == "append" else 'w'
            )
            
            if success:
                messagebox.showinfo(
                    "成功", 
                    f"记录已{'追加' if self.csv_mode.get() == 'append' else '导出'}至: {filename}"
                )
            else:
                messagebox.showerror("错误", f"导出CSV时出错: {error}")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出CSV时出错: {str(e)}") 