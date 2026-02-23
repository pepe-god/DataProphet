import tkinter as tk
from tkinter import ttk, messagebox
from concurrent.futures import ThreadPoolExecutor
from core.models import SEARCH_FIELDS_MAP
from core.utils import is_valid_tc
from core.services import SearchService, FamilyService

class DataProphetApp:
    """Uygulamanın ana grafik arayüzü ve kontrol birimi."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DataProphet v2.0 - Crystal")
        self.root.geometry("800x700")
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.search_service = SearchService()
        self.family_service = FamilyService()
        
        self._setup_styles()
        self._build_ui()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        BG_COLOR = "#2d3436"
        ACCENT_BLUE = "#0984e3"

        style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
        style.configure("TNotebook.Tab", background="#636e72", foreground="white", 
                        font=('Arial', 10, 'bold'), padding=[15, 5])
        style.map("TNotebook.Tab", background=[("selected", ACCENT_BLUE)])
        style.configure("TFrame", background=BG_COLOR)
        style.configure("TEntry", fieldbackground="#dfe6e9", font=('Arial', 11))

    def _build_ui(self):
        self.root.configure(bg="#2d3436")
        
        header = tk.Frame(self.root, bg="#2d3436", height=60)
        header.pack(fill="x")
        tk.Label(header, text="DATAPROPHET", font=("Arial", 18, "bold"), 
                 bg="#2d3436", fg="#00b894").pack(pady=10)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=15, pady=5)

        # Sekme 1: Gelişmiş Arama
        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="  🔍  Gelişmiş Arama  ")
        self._build_search_tab()

        # Sekme 2: Soy Ağacı (FTR)
        self.family_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.family_frame, text="  🌳  Soy Ağacı Sorgula  ")
        self._build_family_tab()

        self.status_var = tk.StringVar(value="Hazır")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, 
                             relief=tk.FLAT, anchor="w", bg="#353b48", fg="#dfe6e9", 
                             font=("Arial", 9, "italic"), padx=10)
        status_bar.pack(side="bottom", fill="x")

    def _build_search_tab(self):
        container = tk.Frame(self.search_frame, bg="#2d3436", padx=30, pady=20)
        container.pack(fill="both", expand=True)

        self.search_entries = {}
        for idx, (label, field) in enumerate(SEARCH_FIELDS_MAP.items()):
            row, col = divmod(idx, 2)
            frame = tk.Frame(container, bg="#2d3436")
            frame.grid(row=row, column=col, sticky="ew", padx=15, pady=8)
            
            tk.Label(frame, text=f"{label}:", width=14, anchor="w", 
                     bg="#2d3436", fg="#dfe6e9", font=("Arial", 10)).pack(side="left")
            entry = ttk.Entry(frame, width=22)
            entry.pack(side="right", fill="x", expand=True)
            self.search_entries[field] = entry

        btn = tk.Button(container, text="ARAMAYI BAŞLAT", bg="#00b894", fg="white", 
                       font=("Arial", 11, "bold"), height=2, bd=0, cursor="hand2",
                       command=self._on_search_click)
        btn.grid(row=11, column=0, columnspan=2, pady=40, sticky="ew")

    def _build_family_tab(self):
        container = tk.Frame(self.family_frame, bg="#2d3436", pady=60)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="TC KİMLİK NUMARASI", font=("Arial", 12, "bold"),
                 bg="#2d3436", fg="#dfe6e9").pack(pady=10)
        
        entry_frame = tk.Frame(container, bg="#353b48", padx=2, pady=2)
        entry_frame.pack(pady=10)
        
        self.family_entry = tk.Entry(entry_frame, font=("Arial", 18), justify="center",
                                     bg="#dfe6e9", fg="#2d3436", bd=0, width=18)
        self.family_entry.pack(padx=2, pady=2)
        self.family_entry.bind("<Return>", lambda e: self._on_family_click())

        btn = tk.Button(container, text="SOY AĞACINI ÇIKAR", bg="#0984e3", fg="white", 
                       font=("Arial", 11, "bold"), height=2, width=30, bd=0, 
                       cursor="hand2", command=self._on_family_click)
        btn.pack(pady=40)

    def _on_search_click(self):
        conds = {k: v.get().strip() for k, v in self.search_entries.items() if v.get().strip()}
        if not conds: return
        self.status_var.set("Arama yapılıyor...")
        self.executor.submit(self._run_search, conds)

    def _on_family_click(self):
        tc = self.family_entry.get().strip()
        if not is_valid_tc(tc):
            messagebox.showwarning("Hata", "Geçersiz TC Numarası!"); return
        self.status_var.set("Soy ağacı hazırlanıyor...")
        self.executor.submit(self._run_family, tc)

    def _run_search(self, conds):
        try:
            f, c, d = self.search_service.search(conds)
            self.root.after(0, lambda: messagebox.showinfo("Tamamlandı", f"{c} kayıt bulundu.\nSüre: {d:.2f}s"))
        finally: self.root.after(0, lambda: self.status_var.set("Hazır"))

    def _run_family(self, tc):
        try:
            res = self.family_service.generate_tree(tc)
            self.root.after(0, lambda: messagebox.showinfo("Sonuç", res))
        finally: self.root.after(0, lambda: self.status_var.set("Hazır"))

    def run(self):
        self.root.mainloop()
