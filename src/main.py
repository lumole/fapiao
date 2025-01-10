from tkinterdnd2 import TkinterDnD
from gui.app import InvoiceMergerApp

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = InvoiceMergerApp(root)
    root.mainloop() 