import tkinter as tk
from tkinter import ttk
from PIL import Image
import PyPDF2
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from tkinterdnd2 import *
from tkinter import messagebox

class InvoiceMergerApp:
    def __init__(self, root):
        self.root = root
        if not isinstance(self.root, TkinterDnD.Tk):
            self.root = TkinterDnD.Tk()
        self.root.title("发票整理工具")
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建左右拖拽区域
        self.payment_frame = ttk.LabelFrame(self.main_frame, text="支付记录（图片）", padding="10")
        self.payment_frame.grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.invoice_frame = ttk.LabelFrame(self.main_frame, text="发票（PDF）", padding="10")
        self.invoice_frame.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建拖拽标签
        self.payment_label = ttk.Label(self.payment_frame, text="拖拽支付记录到这里")
        self.payment_label.grid(row=0, column=0, pady=50)
        
        self.invoice_label = ttk.Label(self.invoice_frame, text="拖拽发票到这里")
        self.invoice_label.grid(row=0, column=0, pady=50)
        
        # 创建合并按钮
        self.merge_button = ttk.Button(self.main_frame, text="合并文件", command=self.merge_files)
        self.merge_button.grid(row=1, column=0, columnspan=2, pady=10)
        
        # 初始化文件路径
        self.payment_path = None
        self.invoice_path = None
        
        # 启用拖放功能
        self.root.drop_target_register(DND_FILES)
        self.payment_frame.drop_target_register(DND_FILES)
        self.invoice_frame.drop_target_register(DND_FILES)
        
        # 绑定拖放事件到框架而不是标签
        self.payment_frame.dnd_bind('<<Drop>>', self.drop_payment)
        self.invoice_frame.dnd_bind('<<Drop>>', self.drop_invoice)

    def drop_payment(self, event):
        self.payment_path = event.data.strip('{}')
        self.payment_label.config(text=f"已选择: {self.payment_path}")

    def drop_invoice(self, event):
        self.invoice_path = event.data.strip('{}')
        self.invoice_label.config(text=f"已选择: {self.invoice_path}")

    def merge_files(self):
        if not self.payment_path or not self.invoice_path:
            messagebox.showerror("错误", "请先选择支付记录和发票文件")
            return
            
        try:
            # 转换支付记录图片为PDF
            image = Image.open(self.payment_path)
            pdf_buffer = io.BytesIO()
            image.save(pdf_buffer, format='PDF')
            
            # 读取原始发票PDF
            pdf_merger = PyPDF2.PdfMerger()
            pdf_merger.append(self.invoice_path)
            
            # 添加支付记录
            pdf_buffer.seek(0)
            pdf_merger.append(pdf_buffer)
            
            # 保存合并后的PDF
            output_path = "merged_invoice.pdf"
            with open(output_path, 'wb') as output_file:
                pdf_merger.write(output_file)
            
            messagebox.showinfo("成功", f"文件已合并保存至: {output_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"合并过程中出现错误: {str(e)}")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = InvoiceMergerApp(root)
    root.mainloop() 