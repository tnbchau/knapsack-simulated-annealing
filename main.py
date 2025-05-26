from ui import InventoryManagementApp
import ttkbootstrap as ttkb

if __name__ == "__main__":
    root = ttkb.Window(themename="darkly")
    InventoryManagementApp(root)
    root.mainloop()
