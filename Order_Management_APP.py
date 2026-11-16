"""
ShopSphere - Online Shopping Order Management System
Batch 11 | Tkinter

Team:
    RA2511003011430  RYAN BIJU
    RA2511003011441  SUBHAM SINGH
    RA2511003011443  ABHINAV KUMAR

Features
    * Form fields  : Order ID, Customer Name, Product Name, Quantity
    * Selection    : OptionMenu (product category), Radiobuttons (payment mode)
    * Operations   : Add, Search (by Order ID), Update, Delete, Display all (Listbox)
    * Validation   : Order ID & Customer Name mandatory, Quantity = positive integer
    * Extras       : gradient header, live stats, striped Listbox, hover buttons,
                     status bar, click-a-row-to-edit, auto-save to orders.json
"""

import json
import os
import tkinter as tk
from tkinter import messagebox

# --------------------------------------------------------------------------
#  THEME
# --------------------------------------------------------------------------
BG = "#0b1220"        # window background
CARD = "#16213a"      # card background
FIELD = "#0b1220"     # input background
BORDER = "#2b3a5c"
TEXT = "#e8eefc"
MUTED = "#8fa1c7"
ACCENT = "#38bdf8"
PURPLE = "#a78bfa"

C_ADD = "#16a34a"
C_SEARCH = "#2563eb"
C_UPDATE = "#d97706"
C_DELETE = "#dc2626"
C_SHOW = "#7c3aed"
C_CLEAR = "#475569"

ROW_A = "#0f1930"
ROW_B = "#14223f"

FONT = ("Segoe UI", 10)
FONT_B = ("Segoe UI", 10, "bold")
MONO = ("Consolas", 10)
MONO_B = ("Consolas", 10, "bold")


def lighten(hex_color, factor=0.18):
    """Return a lighter shade of a #rrggbb colour (used for hover effects)."""
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    r, g, b = (int(c + (255 - c) * factor) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


# --------------------------------------------------------------------------
#  MAIN APPLICATION
# --------------------------------------------------------------------------
class OrderApp(tk.Tk):
    DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orders.json")
    CATEGORIES = ["Electronics", "Fashion", "Grocery", "Books", "Home & Kitchen", "Beauty"]
    PAYMENTS = ["UPI", "Card", "Cash on Delivery"]

    def __init__(self):
        super().__init__()
        self.title("ShopSphere  |  Order Management System")
        self.geometry("1150x690")
        self.minsize(1050, 640)
        self.configure(bg=BG)

        # ---- data (key = Order ID) ----
        self.orders = {}

        # ---- form variables ----
        self.var_id = tk.StringVar()
        self.var_cust = tk.StringVar()
        self.var_prod = tk.StringVar()
        self.var_cat = tk.StringVar(value=self.CATEGORIES[0])
        self.var_qty = tk.StringVar()
        self.var_pay = tk.StringVar(value=self.PAYMENTS[0])
        self.var_status = tk.StringVar()

        self.load_data()
        self.build_header()
        self.build_body()
        self.build_statusbar()
        self.refresh_list()
        self.set_status("Welcome to ShopSphere! Add your first order to get started.", ACCENT)

    # ======================================================================
    #  UI BUILDING
    # ======================================================================
    def build_header(self):
        """Canvas with a horizontal colour gradient and the app title."""
        self.header = tk.Canvas(self, height=84, highlightthickness=0, bd=0, bg=BG)
        self.header.pack(fill="x")
        self.header.bind("<Configure>", self.draw_header)

    def draw_header(self, event=None):
        c = self.header
        c.delete("all")
        w, h = max(c.winfo_width(), 1), 84
        start, end = (0x63, 0x66, 0xF1), (0x06, 0xB6, 0xD4)   # indigo -> cyan
        step = 4
        for x in range(0, w, step):
            t = x / w
            r, g, b = (int(s + (e - s) * t) for s, e in zip(start, end))
            colour = f"#{r:02x}{g:02x}{b:02x}"
            c.create_rectangle(x, 0, x + step, h, fill=colour, outline=colour)
        c.create_text(28, 32, anchor="w", text="🛒  ShopSphere",
                      font=("Segoe UI", 22, "bold"), fill="white")
        c.create_text(30, 62, anchor="w",
                      text="Online Shopping Order Management System",
                      font=("Segoe UI", 10), fill="#e0f2fe")

    def build_body(self):
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=16)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)
        self.build_form(body)
        self.build_list(body)

    def make_card(self, parent):
        return tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)

    # ---------------------------- LEFT : FORM ----------------------------
    def build_form(self, parent):
        card = self.make_card(parent)
        card.grid(row=0, column=0, sticky="ns", padx=(0, 14))

        tk.Label(card, text="📝  Order Details", font=("Segoe UI", 14, "bold"),
                 bg=CARD, fg=ACCENT).pack(anchor="w", padx=22, pady=(18, 2))
        tk.Label(card, text="Fields marked * are mandatory", font=("Segoe UI", 9),
                 bg=CARD, fg=MUTED).pack(anchor="w", padx=22, pady=(0, 12))

        form = tk.Frame(card, bg=CARD)
        form.pack(fill="x", padx=22)
        form.columnconfigure(1, weight=1)

        # Text entries
        self.ent_id = self.add_entry(form, 0, "Order ID *", self.var_id)
        self.ent_cust = self.add_entry(form, 1, "Customer Name *", self.var_cust)
        self.ent_prod = self.add_entry(form, 2, "Product Name", self.var_prod)

        # OptionMenu  -> product category
        self.add_label(form, 3, "Category")
        opt = tk.OptionMenu(form, self.var_cat, *self.CATEGORIES)
        opt.config(bg=FIELD, fg=TEXT, activebackground=ACCENT, activeforeground=BG,
                   font=FONT, bd=0, relief="flat", highlightthickness=2,
                   highlightbackground=BORDER, anchor="w", cursor="hand2")
        opt["menu"].config(bg=FIELD, fg=TEXT, activebackground=ACCENT,
                           activeforeground=BG, font=FONT, bd=0)
        opt.grid(row=3, column=1, sticky="ew", pady=7, ipady=3)

        self.ent_qty = self.add_entry(form, 4, "Quantity *", self.var_qty)

        # RadioButtons -> payment mode
        self.add_label(form, 5, "Payment Mode", pady=(10, 0))
        pay = tk.Frame(form, bg=CARD)
        pay.grid(row=5, column=1, sticky="w", pady=(7, 0))
        icons = {"UPI": "📱", "Card": "💳", "Cash on Delivery": "💵"}
        for mode in self.PAYMENTS:
            tk.Radiobutton(pay, text=f"{icons[mode]}  {mode}", value=mode,
                           variable=self.var_pay, bg=CARD, fg=TEXT, font=FONT,
                           selectcolor=FIELD, activebackground=CARD,
                           activeforeground=ACCENT, highlightthickness=0,
                           cursor="hand2").pack(anchor="w", pady=1)

        # Action buttons (2 rows x 3 columns)
        btns = tk.Frame(card, bg=CARD)
        btns.pack(fill="x", padx=22, pady=(22, 22))
        for col in range(3):
            btns.columnconfigure(col, weight=1)
        buttons = [
            ("➕  Add", C_ADD, self.add_order),
            ("🔍  Search", C_SEARCH, self.search_order),
            ("✏️  Update", C_UPDATE, self.update_order),
            ("🗑️  Delete", C_DELETE, self.delete_order),
            ("📋  Show All", C_SHOW, self.show_all),
            ("🧹  Clear", C_CLEAR, self.clear_form),
        ]
        for i, (text, colour, cmd) in enumerate(buttons):
            b = self.make_button(btns, text, colour, cmd)
            b.grid(row=i // 3, column=i % 3, sticky="ew", padx=4, pady=5, ipady=5)

    def add_label(self, parent, row, text, pady=(7, 7)):
        tk.Label(parent, text=text, font=FONT_B, bg=CARD, fg=MUTED,
                 anchor="w").grid(row=row, column=0, sticky="w", padx=(0, 14), pady=pady)

    def add_entry(self, parent, row, label, variable):
        self.add_label(parent, row, label)
        entry = tk.Entry(parent, textvariable=variable, font=FONT, width=24,
                         bg=FIELD, fg=TEXT, insertbackground=ACCENT, relief="flat",
                         highlightthickness=2, highlightbackground=BORDER,
                         highlightcolor=ACCENT)
        entry.grid(row=row, column=1, sticky="ew", pady=7, ipady=5)
        return entry

    def make_button(self, parent, text, colour, command):
        btn = tk.Button(parent, text=text, command=command, bg=colour, fg="white",
                        font=FONT_B, relief="flat", bd=0, cursor="hand2",
                        activebackground=lighten(colour), activeforeground="white")
        btn.bind("<Enter>", lambda e: btn.config(bg=lighten(colour)))
        btn.bind("<Leave>", lambda e: btn.config(bg=colour))
        return btn

    # --------------------------- RIGHT : LIST ----------------------------
    def build_list(self, parent):
        card = self.make_card(parent)
        card.grid(row=0, column=1, sticky="nsew")

        # Live statistics tiles
        stats = tk.Frame(card, bg=CARD)
        stats.pack(fill="x", padx=22, pady=(18, 8))
        self.lbl_orders = self.stat_tile(stats, "TOTAL ORDERS", ACCENT)
        self.lbl_items = self.stat_tile(stats, "ITEMS ORDERED", PURPLE)

        tk.Label(card, text="📦  All Orders  (click a row to edit it)",
                 font=("Segoe UI", 12, "bold"), bg=CARD, fg=TEXT
                 ).pack(anchor="w", padx=22, pady=(8, 8))

        # Column header
        tk.Label(card, text=self.row_text("ORDER ID", "CUSTOMER", "PRODUCT",
                                          "CATEGORY", "QTY", "PAYMENT"),
                 font=MONO_B, bg=BORDER, fg=TEXT, anchor="w", padx=4, pady=5
                 ).pack(fill="x", padx=22)

        # Listbox + scrollbar
        wrap = tk.Frame(card, bg=CARD)
        wrap.pack(fill="both", expand=True, padx=22, pady=(0, 20))
        sb = tk.Scrollbar(wrap, orient="vertical")
        self.listbox = tk.Listbox(wrap, font=MONO, bg=ROW_A, fg=TEXT, bd=0,
                                  highlightthickness=0, relief="flat",
                                  selectbackground=ACCENT, selectforeground=BG,
                                  activestyle="none", exportselection=False,
                                  yscrollcommand=sb.set)
        sb.config(command=self.listbox.yview)
        sb.pack(side="right", fill="y")
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

    def stat_tile(self, parent, caption, colour):
        tile = tk.Frame(parent, bg=FIELD, highlightbackground=BORDER, highlightthickness=1)
        tile.pack(side="left", padx=(0, 12), ipadx=14, ipady=4)
        number = tk.Label(tile, text="0", font=("Segoe UI", 22, "bold"), bg=FIELD, fg=colour)
        number.pack(anchor="w", padx=8)
        tk.Label(tile, text=caption, font=("Segoe UI", 8, "bold"), bg=FIELD,
                 fg=MUTED).pack(anchor="w", padx=8)
        return number

    def build_statusbar(self):
        self.status = tk.Label(self, textvariable=self.var_status, font=("Segoe UI", 10),
                               bg="#070c17", fg=MUTED, anchor="w", padx=16, pady=7)
        self.status.pack(fill="x", side="bottom")

    # ======================================================================
    #  HELPERS
    # ======================================================================
    @staticmethod
    def row_text(oid, cust, prod, cat, qty, pay):
        """One fixed-width line so the Listbox columns line up."""
        return (f"{str(oid)[:11]:<12}{str(cust)[:15]:<16}{str(prod)[:15]:<16}"
                f"{str(cat)[:12]:<13}{str(qty):>4}  {pay}")

    def set_status(self, message, colour=MUTED):
        self.var_status.set("  " + message)
        self.status.config(fg=colour)

    def find_key(self, order_id):
        """Case-insensitive lookup; returns the stored Order ID or None."""
        for key in self.orders:
            if key.lower() == order_id.lower():
                return key
        return None

    def get_form(self):
        return {
            "id": self.var_id.get().strip(),
            "customer": self.var_cust.get().strip(),
            "product": self.var_prod.get().strip() or "-",
            "category": self.var_cat.get(),
            "qty": self.var_qty.get().strip(),
            "payment": self.var_pay.get(),
        }

    def fill_form(self, order):
        self.var_id.set(order["id"])
        self.var_cust.set(order["customer"])
        self.var_prod.set("" if order["product"] == "-" else order["product"])
        self.var_cat.set(order["category"])
        self.var_qty.set(str(order["qty"]))
        self.var_pay.set(order["payment"])

    # ---------------------------- VALIDATION -----------------------------
    def validate(self, data):
        if not data["id"]:
            messagebox.showerror("Missing Order ID", "Order ID is mandatory.")
            self.ent_id.focus_set()
            return False
        if not data["customer"]:
            messagebox.showerror("Missing Customer Name", "Customer name is mandatory.")
            self.ent_cust.focus_set()
            return False
        try:
            qty = int(data["qty"])
            if qty <= 0 or not data["qty"].isdigit():
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Quantity",
                                 "Quantity must be a positive whole number (1, 2, 3 ...).")
            self.ent_qty.focus_set()
            return False
        return True

    # ======================================================================
    #  CRUD OPERATIONS
    # ======================================================================
    def add_order(self):
        data = self.get_form()
        if not self.validate(data):
            return
        if self.find_key(data["id"]):
            messagebox.showerror("Duplicate Order",
                                 f"Order ID '{data['id']}' already exists.\n"
                                 "Use Update to change it.")
            return
        data["qty"] = int(data["qty"])
        self.orders[data["id"]] = data
        self.save_data()
        self.refresh_list(select=data["id"])
        self.clear_form(keep_status=True)
        self.set_status(f"Order {data['id']} added for {data['customer']}.", "#4ade80")

    def search_order(self):
        oid = self.var_id.get().strip()
        if not oid:
            messagebox.showwarning("Search", "Enter an Order ID to search.")
            self.ent_id.focus_set()
            return
        key = self.find_key(oid)
        if key is None:
            messagebox.showinfo("Not Found", f"No order found with ID '{oid}'.")
            self.set_status(f"Order {oid} not found.", "#f87171")
            return
        self.fill_form(self.orders[key])
        self.refresh_list(select=key)
        self.set_status(f"Order {key} found - details loaded into the form.", ACCENT)

    def update_order(self):
        data = self.get_form()
        if not self.validate(data):
            return
        key = self.find_key(data["id"])
        if key is None:
            messagebox.showerror("Update Failed",
                                 f"Order ID '{data['id']}' does not exist.\n"
                                 "Use Add to create a new order.")
            return
        data["id"] = key          # Order ID is the key, so it never changes
        data["qty"] = int(data["qty"])
        self.orders[key] = data
        self.save_data()
        self.refresh_list(select=key)
        self.set_status(f"Order {key} updated successfully.", "#fbbf24")
        messagebox.showinfo("Updated", f"Order {key} has been updated.")

    def delete_order(self):
        oid = self.var_id.get().strip()
        if not oid:
            messagebox.showwarning("Delete", "Enter or select an Order ID to delete.")
            self.ent_id.focus_set()
            return
        key = self.find_key(oid)
        if key is None:
            messagebox.showerror("Delete Failed", f"Order ID '{oid}' does not exist.")
            return
        if not messagebox.askyesno("Confirm Delete",
                                   f"Delete order {key} permanently?"):
            return
        del self.orders[key]
        self.save_data()
        self.refresh_list()
        self.clear_form(keep_status=True)
        self.set_status(f"Order {key} deleted.", "#f87171")

    def show_all(self):
        self.clear_form(keep_status=True)
        self.refresh_list()
        self.set_status(f"Showing all {len(self.orders)} order(s).", ACCENT)

    def clear_form(self, keep_status=False):
        self.var_id.set("")
        self.var_cust.set("")
        self.var_prod.set("")
        self.var_qty.set("")
        self.var_cat.set(self.CATEGORIES[0])
        self.var_pay.set(self.PAYMENTS[0])
        self.listbox.selection_clear(0, "end")
        self.ent_id.focus_set()
        if not keep_status:
            self.set_status("Form cleared.", MUTED)

    # ======================================================================
    #  LISTBOX
    # ======================================================================
    def refresh_list(self, select=None):
        """Re-draw the Listbox (striped rows) and the statistics tiles."""
        self.listbox.delete(0, "end")
        if not self.orders:
            self.listbox.insert("end", "   No orders yet - add one using the form!")
            self.listbox.itemconfig(0, fg=MUTED)
        else:
            for i, order in enumerate(self.orders.values()):
                self.listbox.insert("end", self.row_text(
                    order["id"], order["customer"], order["product"],
                    order["category"], order["qty"], order["payment"]))
                self.listbox.itemconfig(i, bg=ROW_A if i % 2 == 0 else ROW_B)

        if select is not None and select in self.orders:
            index = list(self.orders).index(select)
            self.listbox.selection_clear(0, "end")
            self.listbox.selection_set(index)
            self.listbox.see(index)

        self.lbl_orders.config(text=str(len(self.orders)))
        self.lbl_items.config(text=str(sum(o["qty"] for o in self.orders.values())))

    def on_select(self, event=None):
        """Clicking a row loads that order into the form for quick editing."""
        if not self.orders:
            return
        selection = self.listbox.curselection()
        if not selection:
            return
        key = list(self.orders)[selection[0]]
        self.fill_form(self.orders[key])
        self.set_status(f"Order {key} selected - edit the fields and press Update, "
                        "or press Delete.", ACCENT)

    # ======================================================================
    #  PERSISTENCE (bonus: orders survive after closing the app)
    # ======================================================================
    def load_data(self):
        try:
            with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                self.orders = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.orders = {}

    def save_data(self):
        try:
            with open(self.DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.orders, f, indent=2)
        except OSError:
            self.set_status("Could not save orders to disk.", "#f87171")


if __name__ == "__main__":
    OrderApp().mainloop()
