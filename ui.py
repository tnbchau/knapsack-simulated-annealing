import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from tkinter import messagebox, Text, filedialog
import csv
from knapsack_algorithm import knapsack_simulated_annealing, generate_knapsack_data

class InventoryManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title(" Quản lý Ba lô - Simulated Annealing")
        self.root.geometry("1200x720")
        self.items, self.run_count, self.default_csv_path = [], 0, ""
        self.setup_ui()

    def setup_ui(self):
        top = ttkb.Frame(self.root)
        bottom = ttkb.Frame(self.root)
        top.pack(side="top", fill="both", expand=True, padx=10, pady=5)
        bottom.pack(side="bottom", fill="both", expand=True, padx=10, pady=5)
        self.setup_top_panel(top)
        self.setup_bottom_panel(bottom)

    def setup_top_panel(self, p):
        left = ttkb.Frame(p)
        center = ttkb.Frame(p)
        right = ttkb.Frame(p)
        for f in [left, center, right]: f.pack(side="left", fill="both", expand=True, padx=5)

        self.setup_item_table(left)
        self.setup_entry_form(center)
        self.setup_algo_params(right)

    def setup_item_table(self, p):
        ttkb.Label(p, text=" Dữ liệu vật phẩm", font=("Arial", 14, "bold"), bootstyle="primary").pack(pady=5)
        tf = ttkb.Frame(p)
        tf.pack(pady=5, fill="both", expand=True)
        ts = ttkb.Scrollbar(tf, bootstyle="primary-round")
        ts.pack(side="right", fill="y")
        self.tree = ttkb.Treeview(tf, columns=("Name", "Value", "Weight"), show="headings", bootstyle="dark", yscrollcommand=ts.set)
        for col, text, w in [("Name", " Tên", 160), ("Value", " Giá trị", 110), ("Weight", " Khối lượng", 110)]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)
        ts.config(command=self.tree.yview)
        bf = ttkb.Frame(p); bf.pack(fill="x", pady=5)
        ttkb.Button(bf, text=" Tải CSV", command=self.load_csv, bootstyle="info").pack(side="left", padx=5)
        ttkb.Button(bf, text=" Tạo mẫu", command=self.gen_data, bootstyle="secondary").pack(side="left", padx=5)

    def setup_entry_form(self, p):
        ef = ttkb.Labelframe(p, text=" Thêm vật phẩm", bootstyle="success", padding=10)
        ef.pack(fill="x", pady=8)
        self.entries = {}
        for i, (lbl, key) in enumerate([("Tên:", "name"), ("Giá trị:", "value"), ("Khối lượng:", "weight")]):
            ttkb.Label(ef, text=lbl, bootstyle="success", font=("Arial", 10)).grid(row=i, column=0, sticky="w", padx=5, pady=4)
            self.entries[key] = ttkb.Entry(ef, bootstyle="success")
            self.entries[key].grid(row=i, column=1, padx=8, pady=4, sticky="ew")
        ef.grid_columnconfigure(1, weight=1)
        ttkb.Button(ef, text=" Thêm", command=self.add_item, bootstyle="success").grid(row=3, column=0, columnspan=2, pady=8)

        df = ttkb.Labelframe(p, text=" Quản lý", bootstyle="warning", padding=8)
        df.pack(fill="x", pady=5)
        ttkb.Button(df, text=" Xóa tất cả", command=self.clear_data, bootstyle="danger", width=14).pack(side="left", padx=5)
        ttkb.Button(df, text=" Xóa đã chọn", command=self.del_selected, bootstyle="warning", width=14).pack(side="left", padx=5)

    def setup_algo_params(self, p):
        af = ttkb.Labelframe(p, text=" Tham số thuật toán", bootstyle="info", padding=10)
        af.pack(fill="x", pady=8)
        self.algo = {}
        for i, (lbl, key, default) in enumerate([("Khối lượng tối đa:", "max_w", ""), ("Nhiệt độ:", "temp", "10000"),
                                                 ("Tỷ lệ làm mát:", "cool", "0.95"), ("Số lần lặp:", "iter", "1000")]):
            ttkb.Label(af, text=lbl, bootstyle="info", font=("Arial", 10)).grid(row=i, column=0, sticky="w", padx=5, pady=3)
            self.algo[key] = ttkb.Entry(af, bootstyle="info")
            if default: self.algo[key].insert(0, default)
            self.algo[key].grid(row=i, column=1, padx=8, pady=3, sticky="ew")
        af.grid_columnconfigure(1, weight=1)
        ttkb.Button(p, text=" Chạy thuật toán", command=self.run_algo, bootstyle="success", width=20).pack(pady=20)

    def setup_bottom_panel(self, p):
        ttkb.Button(p, text="🗑 Xóa kết quả & lịch sử", command=self.clear_history,
                    bootstyle="danger-outline", width=25).pack(pady=(8, 6))

        for title, height, style in [(" Kết quả", 12, "success"), (" Lịch sử", 14, "secondary")]:
            ttkb.Label(p, text=title, font=("Arial", 14, "bold"), bootstyle=style).pack(pady=(5, 3))
            f = ttkb.Frame(p); f.pack(fill="both", expand=True, pady=4)
            s = ttkb.Scrollbar(f, bootstyle=f"{style}-round"); s.pack(side="right", fill="y")
            text_widget = Text(f, height=height, wrap="word", yscrollcommand=s.set,
                               font=("Consolas", 10), bg="#1e272e", fg="#d2dae2", insertbackground="#00a8ff")
            text_widget.pack(side="left", fill="both", expand=True)
            s.config(command=text_widget.yview)
            if "Kết quả" in title: self.result_text = text_widget
            else: self.history_text = text_widget

    def load_csv(self):
        file_path = filedialog.askopenfilename(title="Chọn CSV", filetypes=[("CSV", "*.csv")])
        if not file_path: return
        self.default_csv_path = file_path
        try:
            self.items.clear()
            [self.tree.delete(item) for item in self.tree.get_children()]
            with open(file_path, newline='', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    try:
                        name, value, weight = row.get('Name', ''), int(row.get('Value', 0)), int(row.get('Weight', 0))
                        if value >= 0 and weight >= 0:
                            self.items.append((name, value, weight))
                            self.tree.insert("", "end", values=(name, value, weight))
                    except: continue
            messagebox.showinfo("Thành công", f" Đã tải {len(self.items)} vật phẩm")
        except Exception as e:
            messagebox.showerror("Lỗi", f" Lỗi đọc CSV: {e}")

    def gen_data(self):
        try:
            import tkinter.simpledialog as sd
            params = []
            for prompt, default in [("Số lượng:", 10), ("Giá trị max:", 500), ("Khối lượng max:", 20)]:
                val = sd.askinteger("Tạo dữ liệu", prompt, initialvalue=default, minvalue=1)
                if val is None: return
                params.append(val)
            data = generate_knapsack_data(*params)
            self.items.clear()
            [self.tree.delete(item) for item in self.tree.get_children()]
            for i in range(params[0]):
                item = (data['names'][i], data['values'][i], data['weights'][i])
                self.items.append(item)
                self.tree.insert("", "end", values=item)
            messagebox.showinfo("Thành công", f" Đã tạo {params[0]} vật phẩm")
        except Exception as e:
            messagebox.showerror("Lỗi", f" Lỗi tạo dữ liệu: {e}")

    def add_item(self):
        name = self.entries["name"].get()
        if not name: return messagebox.showerror("Lỗi", " Tên không được trống")
        try:
            value, weight = int(self.entries["value"].get()), int(self.entries["weight"].get())
            if value < 0 or weight < 0: return messagebox.showerror("Lỗi", " Không được âm")
            self.items.append((name, value, weight))
            self.tree.insert("", "end", values=(name, value, weight))
            [e.delete(0, "end") for e in self.entries.values()]
            if self.default_csv_path: self.save_csv()
        except: messagebox.showerror("Lỗi", " Nhập số hợp lệ")

    def clear_data(self):
        if messagebox.askyesno("Xác nhận", " Xóa tất cả dữ liệu?"):
            self.items.clear()
            [self.tree.delete(item) for item in self.tree.get_children()]
            [e.delete(0, "end") for e in self.entries.values()]
            messagebox.showinfo("Thành công", " Đã xóa tất cả")

    def clear_history(self):
        self.result_text.delete(1.0, "end")
        self.history_text.delete(1.0, "end")

    def del_selected(self):
        selected = self.tree.selection()
        if not selected: return messagebox.showwarning("Cảnh báo", " Chọn vật phẩm để xóa")
        for item in selected:
            vals = self.tree.item(item, "values")
            if vals:
                name, value, weight = vals
                self.items = [i for i in self.items if not (i[0] == name and i[1] == int(value) and i[2] == int(weight))]
            self.tree.delete(item)
        if self.default_csv_path: self.save_csv()

    def run_algo(self):
        if not self.items: return messagebox.showerror("Lỗi", " Không có dữ liệu")
        names, values, weights = zip(*self.items)
        try:
            max_w = int(self.algo["max_w"].get())
            temp = float(self.algo["temp"].get())
            cool = float(self.algo["cool"].get())
            iter_max = int(self.algo["iter"].get())
            if max_w < 0 or temp <= 0 or cool <= 0 or cool >= 1 or iter_max <= 0:
                return messagebox.showerror("Lỗi", " Tham số không hợp lệ")
        except: return messagebox.showerror("Lỗi", " Nhập tham số hợp lệ")

        self.result_text.delete(1.0, "end")
        self.history_text.delete(1.0, "end")
        info = [f" === Chạy lần #{self.run_count + 1} ===", f" Số vật phẩm: {len(names)}", f" Khối lượng tối đa: {max_w}", 
                f" Nhiệt độ: {temp}", f" Tỷ lệ mát: {cool}", f" Số lần lặp: {iter_max}\n"]
        self.history_text.insert("end", "\n".join(info))

        try:
            selected, history, time_exec = knapsack_simulated_annealing(names, values, weights, max_w, temp, cool, iter_max)
            total_val = sum(values[i] for i, name in enumerate(names) if name in selected)
            total_w = sum(weights[i] for i, name in enumerate(names) if name in selected)
            result = [f" === KẾT QUẢ ===", f" Tổng giá trị: {total_val:,}", f" Tổng khối lượng: {total_w}/{max_w}",
                     f" Số vật phẩm chọn: {len(selected)}/{len(names)}", f" Thời gian: {time_exec:.4f}s\n", 
                     " Danh sách vật phẩm được chọn:"]
            self.result_text.insert("end", "\n".join(result))
            for i, item in enumerate(selected):
                idx = names.index(item)
                self.result_text.insert("end", f"{i+1:2d}. {item} ({values[idx]:,} - {weights[idx]})\n")
            self.history_text.insert("end", "\n".join(history))
            self.run_count += 1
        except Exception as e:
            messagebox.showerror("Lỗi", f" Lỗi thuật toán: {e}")

    def save_csv(self):
        if not self.default_csv_path:
            self.default_csv_path = filedialog.asksaveasfilename(title="Lưu CSV", defaultextension=".csv", filetypes=[("CSV", "*.csv")])
            if not self.default_csv_path: return
        try:
            with open(self.default_csv_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Name", "Value", "Weight"])
                writer.writerows(self.items)
            messagebox.showinfo("Thành công", f" Đã lưu vào {self.default_csv_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f" Không lưu được: {e}")

def run_app():
    root = ttkb.Window(themename="darkly")
    InventoryManagementApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_app()
