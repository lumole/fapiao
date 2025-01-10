import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import *

class DragDropFrame(ttk.LabelFrame):
    def __init__(self, parent, title, drop_callback):
        super().__init__(parent, text=title, padding="10")
        
        self.paths = []
        self.drop_callback = drop_callback
        
        # 创建拖拽标签
        self.label = ttk.Label(self, text=f"拖拽{title}到这里")
        self.label.grid(row=0, column=0, pady=50)
        
        # 创建列表视图
        self.listbox = tk.Listbox(self, width=50, height=10)
        self.listbox.grid(row=1, column=0, pady=5)
        
        # 启用拖放功能
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.on_drop)
    
    def on_drop(self, event):
        files = event.data.strip('{}').split('} {')
        for path in files:
            self.paths.append(path)
            self.listbox.insert(tk.END, path)
        self.label.config(text=f"已选择: {len(self.paths)} 个文件")
        if self.drop_callback:
            self.drop_callback()
    
    def clear(self):
        self.paths.clear()
        self.listbox.delete(0, tk.END)
        self.label.config(text=f"拖拽{self['text']}到这里") 