import tkinter as tk
from tkinter import ttk
from PIL import Image
import PyPDF2
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from tkinterdnd2 import *
from tkinter import messagebox
from tkinter import filedialog
import csv
from decimal import Decimal  # 用于精确计算金额

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
        
        # 修改为列表存储
        self.payment_paths = []
        self.invoice_paths = []
        
        # 添加列表视图
        self.payment_listbox = tk.Listbox(self.payment_frame, width=50, height=10)
        self.payment_listbox.grid(row=1, column=0, pady=5)
        
        self.invoice_listbox = tk.Listbox(self.invoice_frame, width=50, height=10)
        self.invoice_listbox.grid(row=1, column=0, pady=5)
        
        # 添加合并模式选择框架
        self.mode_frame = ttk.LabelFrame(self.main_frame, text="合并模式", padding="10")
        self.mode_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # 添加单选按钮变量
        self.merge_mode = tk.StringVar(value="new")
        
        # 添加单选按钮
        self.new_radio = ttk.Radiobutton(
            self.mode_frame, 
            text="创建新文件", 
            variable=self.merge_mode, 
            value="new"
        )
        self.new_radio.grid(row=0, column=0, padx=5)
        
        self.append_radio = ttk.Radiobutton(
            self.mode_frame, 
            text="追加到现有文件", 
            variable=self.merge_mode, 
            value="append"
        )
        self.append_radio.grid(row=0, column=1, padx=5)
        
        # 选择现有PDF按钮
        self.select_pdf_button = ttk.Button(
            self.mode_frame, 
            text="选择现有PDF", 
            command=self.select_existing_pdf
        )
        self.select_pdf_button.grid(row=0, column=2, padx=5)
        
        # 存储选中的PDF路径
        self.existing_pdf_path = None
        
        # 添加清除按钮
        self.clear_button = ttk.Button(self.main_frame, text="清除所有", command=self.clear_all)
        self.clear_button.grid(row=2, column=0, columnspan=2, pady=5)
        
        # 合并按钮移到最下面
        self.merge_button = ttk.Button(self.main_frame, text="合并文件", command=self.merge_files)
        self.merge_button.grid(row=3, column=0, columnspan=2, pady=5)
        
        # 启用拖放功能
        self.root.drop_target_register(DND_FILES)
        self.payment_frame.drop_target_register(DND_FILES)
        self.invoice_frame.drop_target_register(DND_FILES)
        
        # 绑定拖放事件到框架而不是标签
        self.payment_frame.dnd_bind('<<Drop>>', self.drop_payment)
        self.invoice_frame.dnd_bind('<<Drop>>', self.drop_invoice)
        
        # 添加列表框架
        self.list_frame = ttk.LabelFrame(self.main_frame, text="记录详情", padding="10")
        self.list_frame.grid(row=0, column=2, rowspan=2, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加表头
        ttk.Label(self.list_frame, text="物品名称").grid(row=0, column=0, padx=5)
        ttk.Label(self.list_frame, text="金额").grid(row=0, column=1, padx=5)
        
        # 创建记录列表
        self.records_frame = ttk.Frame(self.list_frame)
        self.records_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # 存储记录的列表
        self.records = []
        
        # 添加总金额显示
        self.total_label = ttk.Label(self.list_frame, text="总金额: ¥0.00")
        self.total_label.grid(row=2, column=0, columnspan=2, pady=5)
        
        # 添加导出CSV按钮
        self.export_button = ttk.Button(self.list_frame, text="导出CSV", command=self.export_csv)
        self.export_button.grid(row=3, column=0, columnspan=2, pady=5)
        
        # 添加CSV模式选择框架
        self.csv_frame = ttk.LabelFrame(self.list_frame, text="CSV导出模式", padding="10")
        self.csv_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # 添加CSV单选按钮变量
        self.csv_mode = tk.StringVar(value="new")
        
        # 添加CSV单选按钮
        self.csv_new_radio = ttk.Radiobutton(
            self.csv_frame, 
            text="创建新文件", 
            variable=self.csv_mode, 
            value="new"
        )
        self.csv_new_radio.grid(row=0, column=0, padx=5)
        
        self.csv_append_radio = ttk.Radiobutton(
            self.csv_frame, 
            text="追加到现有文件", 
            variable=self.csv_mode, 
            value="append"
        )
        self.csv_append_radio.grid(row=0, column=1, padx=5)
        
        # 选择现有CSV按钮
        self.select_csv_button = ttk.Button(
            self.csv_frame, 
            text="选择现有CSV", 
            command=self.select_existing_csv
        )
        self.select_csv_button.grid(row=0, column=2, padx=5)
        
        # 存储选中的CSV路径
        self.existing_csv_path = None
        
        # 导出CSV按钮移到最下面
        self.export_button.grid(row=4, column=0, columnspan=2, pady=5)

    def drop_payment(self, event):
        # 获取拖拽的文件路径并处理成列表
        files = event.data.strip('{}').split('} {')
        
        # 遍历所有文件
        for path in files:
            # 添加到路径列表
            self.payment_paths.append(path)
            # 添加到显示列表
            self.payment_listbox.insert(tk.END, path)
            # 为每个文件添加一行记录输入
            self.add_record_row()
        
        # 更新标签显示
        self.payment_label.config(text=f"已选择: {len(self.payment_paths)} 个文件")

    def drop_invoice(self, event):
        # 获取拖拽的文件路径并处理成列表
        files = event.data.strip('{}').split('} {')
        
        # 遍历所有文件
        for path in files:
            # 添加到路径列表
            self.invoice_paths.append(path)
            # 添加到显示列表
            self.invoice_listbox.insert(tk.END, path)
        
        # 更新标签显示
        self.invoice_label.config(text=f"已选择: {len(self.invoice_paths)} 个文件")

    def clear_all(self):
        self.payment_paths.clear()
        self.invoice_paths.clear()
        self.payment_listbox.delete(0, tk.END)
        self.invoice_listbox.delete(0, tk.END)
        self.payment_label.config(text="拖拽支付记录到这里")
        self.invoice_label.config(text="拖拽发票到这里")
        
        # 清除记录
        for frame in self.records_frame.winfo_children():
            frame.destroy()
        self.records.clear()
        self.update_total()

    def select_existing_pdf(self):
        file_path = filedialog.askopenfilename(
            title="选择PDF文件",
            filetypes=[("PDF文件", "*.pdf")]
        )
        if file_path:
            self.existing_pdf_path = file_path
            self.merge_mode.set("append")
            messagebox.showinfo("成功", f"已选择文件：{file_path}")

    def add_record_row(self):
        """添加一行记录输入"""
        record_frame = ttk.Frame(self.records_frame)
        record_frame.pack(fill=tk.X, pady=2)
        
        name_entry = ttk.Entry(record_frame)
        name_entry.pack(side=tk.LEFT, padx=2)
        
        amount_entry = ttk.Entry(record_frame, width=15)
        amount_entry.pack(side=tk.LEFT, padx=2)
        
        # 将输入框添加到记录列表
        self.records.append((name_entry, amount_entry))
        
        # 绑定金额输入框的验证
        amount_entry.bind('<KeyRelease>', self.update_total)

    def update_total(self, event=None):
        """更新总金额"""
        total = Decimal('0.00')
        for _, amount_entry in self.records:
            try:
                amount = Decimal(amount_entry.get() or '0')
                total += amount
            except:
                pass
        self.total_label.config(text=f"总金额: ¥{total:.2f}")

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

    def export_csv(self):
        """导出记录到CSV文件"""
        try:
            if self.csv_mode.get() == "append" and self.existing_csv_path:
                filename = self.existing_csv_path
                mode = 'a'  # 追加模式
            else:
                filename = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV 文件", "*.csv")],
                    title="保存记录"
                )
                if not filename:
                    return
                mode = 'w'  # 新建模式
            
            # 计算总金额
            total = Decimal('0.00')
            for _, amount_entry in self.records:
                try:
                    amount = Decimal(amount_entry.get() or '0')
                    total += amount
                except:
                    pass
            
            # 写入CSV
            with open(filename, mode, newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # 如果是新建模式，写入表头
                if mode == 'w':
                    writer.writerow(["物品名称", "金额"])
                
                # 写入记录
                for name_entry, amount_entry in self.records:
                    if name_entry.get() and amount_entry.get():  # 只写入有内容的记录
                        writer.writerow([
                            name_entry.get(),
                            amount_entry.get()
                        ])
                
                # 写入总计行
                writer.writerow(["总计", f"{total:.2f}"])
            
            messagebox.showinfo("成功", f"记录已{'追加' if mode == 'a' else '导出'}至: {filename}")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出CSV时出错: {str(e)}")

    def merge_files(self):
        if not self.payment_paths or not self.invoice_paths:
            messagebox.showerror("错误", "请先选择支付记录和发票文件")
            return
            
        if len(self.payment_paths) != len(self.invoice_paths):
            messagebox.showerror("错误", "支付记录和发票数量不匹配")
            return
            
        try:
            pdf_merger = PyPDF2.PdfMerger()
            
            # 如果是追加模式且已选择现有PDF
            if self.merge_mode.get() == "append" and self.existing_pdf_path:
                # 使用 with 语句安全打开现有PDF
                with open(self.existing_pdf_path, 'rb') as existing_pdf:
                    pdf_merger.append(existing_pdf)
                output_path = self.existing_pdf_path
            else:
                output_path = "merged_invoice.pdf"
            
            # 按顺序合并每组文件
            for payment_path, invoice_path in zip(self.payment_paths, self.invoice_paths):
                # 转换支付记录图片为PDF
                image = Image.open(payment_path)
                pdf_buffer = io.BytesIO()
                image.save(pdf_buffer, format='PDF', resolution=200.0)
                
                # 添加发票
                with open(invoice_path, 'rb') as invoice_file:
                    pdf_merger.append(invoice_file)
                
                # 添加支付记录
                pdf_buffer.seek(0)
                pdf_merger.append(pdf_buffer)
            
            # 保存合并后的PDF
            with open(output_path, 'wb') as output_file:
                pdf_merger.write(output_file)
            
            messagebox.showinfo("成功", f"PDF文件已合并保存至: {output_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"合并过程中出现错误: {str(e)}")
        finally:
            # 确保资源被释放
            if 'pdf_merger' in locals():
                pdf_merger.close()

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = InvoiceMergerApp(root)
    root.mainloop() 