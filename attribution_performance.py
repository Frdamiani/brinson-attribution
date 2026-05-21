import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import matplotlib
matplotlib.use("TkAgg")

# proxies ETF par classe d'actifs
# port = biais actif / bench = indice large
classes = ["Actions US", "Actions Europe", "Actions EM", "Oblig. LT", "Oblig. CT", "Monetaire"]
tck_p = ["QQQ", "EWQ", "MCHI", "VCLT", "VCSH", "BIL"]
tck_b = ["SPY", "EZU", "EEM",  "TLT",  "IEF",  "SHV"]

wp_def = [0.40, 0.20, 0.05, 0.15, 0.10, 0.10]
wb_def = [0.30, 0.15, 0.10, 0.20, 0.15, 0.10]


def get_ret(tickers, deb, fin):
    df = yf.download(tickers, start=deb, end=fin, auto_adjust=True, progress=False)["Close"]
    if isinstance(df, pd.Series):
        df = df.to_frame(tickers[0])
    df = df[tickers]
    return ((1 + df.pct_change().dropna()).prod() - 1).values.astype(float)


def brinson(wp, wb, rp, rb):
    eff_alloc = (wp - wb) * rb
    eff_sel   = wb * (rp - rb)
    eff_inter = (wp - wb) * (rp - rb)
    return {
        "alloc": eff_alloc,
        "sel":   eff_sel,
        "inter": eff_inter,
        "rp":    float(np.dot(wp, rp)),
        "rb":    float(np.dot(wb, rb)),
    }


class App(tk.Tk):
    BG  = "#1e1e2e"
    BG2 = "#313244"
    BG3 = "#45475a"
    FG  = "#cdd6f4"
    DIM = "#6c7086"
    BLU = "#89b4fa"
    GRN = "#a6e3a1"
    PCH = "#fab387"
    RED = "#f38ba8"

    def __init__(self):
        super().__init__()
        self.title("Attribution de Performance — Brinson-Hood-Beebower")
        self.configure(bg=self.BG)
        self.minsize(880, 580)
        self._ui()

    def _ui(self):
        # header
        f = tk.Frame(self, bg=self.BG)
        f.pack(fill="x", padx=22, pady=(16, 4))
        tk.Label(f, text="Attribution de Performance", font=("Helvetica", 15, "bold"),
                 bg=self.BG, fg=self.FG).pack(side="left")
        tk.Label(f, text="  Brinson-Hood-Beebower",
                 font=("Helvetica", 9), bg=self.BG, fg=self.DIM).pack(side="left")

        # dates
        fd = tk.Frame(self, bg=self.BG)
        fd.pack(fill="x", padx=22, pady=4)
        tk.Label(fd, text="Début :", bg=self.BG, fg=self.FG).pack(side="left")
        self.e_deb = tk.Entry(fd, width=12, bg=self.BG2, fg=self.FG,
                              insertbackground=self.FG, relief="flat")
        self.e_deb.insert(0, (datetime.today()-timedelta(days=365)).strftime("%Y-%m-%d"))
        self.e_deb.pack(side="left", padx=(3,16))
        tk.Label(fd, text="Fin :", bg=self.BG, fg=self.FG).pack(side="left")
        self.e_fin = tk.Entry(fd, width=12, bg=self.BG2, fg=self.FG,
                              insertbackground=self.FG, relief="flat")
        self.e_fin.insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.e_fin.pack(side="left", padx=3)

        tk.Frame(self, bg=self.BG3, height=1).pack(fill="x", padx=22, pady=6)

        # tableau poids
        t = tk.Frame(self, bg=self.BG)
        t.pack(padx=22, pady=4)
        for col, txt in enumerate(["Classe", "Port. (proxy)", "Poids port. %", "Bench. (indice)", "Poids bench. %"]):
            tk.Label(t, text=txt, font=("Helvetica", 9, "bold"), bg=self.BG, fg=self.BLU,
                     width=17, anchor="center").grid(row=0, column=col, padx=4, pady=(0,6))

        self.ep, self.eb = [], []
        for i, nom in enumerate(classes):
            tk.Label(t, text=nom, bg=self.BG, fg=self.FG, width=15,
                     anchor="w").grid(row=i+1, column=0, padx=4, pady=2)
            tk.Label(t, text=tck_p[i], bg=self.BG, fg=self.DIM,
                     width=15).grid(row=i+1, column=1, padx=4, pady=2)
            ep = tk.Entry(t, width=15, bg=self.BG2, fg=self.FG,
                          insertbackground=self.FG, relief="flat", justify="center")
            ep.insert(0, str(round(wp_def[i]*100, 1)))
            ep.grid(row=i+1, column=2, padx=4, pady=2)
            self.ep.append(ep)
            tk.Label(t, text=tck_b[i], bg=self.BG, fg=self.DIM,
                     width=15).grid(row=i+1, column=3, padx=4, pady=2)
            eb = tk.Entry(t, width=15, bg=self.BG2, fg=self.FG,
                          insertbackground=self.FG, relief="flat", justify="center")
            eb.insert(0, str(round(wb_def[i]*100, 1)))
            eb.grid(row=i+1, column=4, padx=4, pady=2)
            self.eb.append(eb)

        tk.Button(self, text="▶  Calculer", font=("Helvetica", 11, "bold"),
                  bg=self.BLU, fg=self.BG, relief="flat", cursor="hand2",
                  padx=18, pady=7, command=self._run).pack(pady=10)

        self.zone = tk.Frame(self, bg=self.BG)
        self.zone.pack(fill="both", expand=True, padx=22, pady=(0,14))

    def _run(self):
        try:
            wp = np.array([float(e.get()) for e in self.ep]) / 100
            wb = np.array([float(e.get()) for e in self.eb]) / 100
        except ValueError:
            messagebox.showerror("Erreur", "Poids invalides.")
            return

        if abs(wp.sum()-1) > 0.015:
            messagebox.showerror("Erreur", f"Poids port. = {wp.sum()*100:.1f}% (doit être 100%)")
            return
        if abs(wb.sum()-1) > 0.015:
            messagebox.showerror("Erreur", f"Poids bench. = {wb.sum()*100:.1f}% (doit être 100%)")
            return

        for w in self.zone.winfo_children():
            w.destroy()
        tk.Label(self.zone, text="Chargement yfinance…", bg=self.BG,
                 fg=self.DIM, font=("Helvetica", 10)).pack(pady=18)
        self.update()

        try:
            rp = get_ret(tck_p, self.e_deb.get(), self.e_fin.get())
            rb = get_ret(tck_b, self.e_deb.get(), self.e_fin.get())
        except Exception as e:
            messagebox.showerror("Erreur données", str(e))
            return

        res = brinson(wp, wb, rp, rb)
        self._show(res, rp, rb, wp, wb)

    def _show(self, res, rp, rb, wp, wb):
        for w in self.zone.winfo_children():
            w.destroy()

        a = res["alloc"]
        s = res["sel"]
        it = res["inter"]
        exc = res["rp"] - res["rb"]

        # tableau
        sty = ttk.Style()
        sty.theme_use("clam")
        sty.configure("M.Treeview", background=self.BG2, foreground=self.FG,
                      fieldbackground=self.BG2, rowheight=25, font=("Helvetica", 9))
        sty.configure("M.Treeview.Heading", background=self.BG3, foreground=self.FG,
                      font=("Helvetica", 9, "bold"))
        sty.map("M.Treeview", background=[("selected", self.BG3)])

        cols = ("Classe", "Rdt port.", "Rdt bench.", "Allocation", "Sélection", "Interaction", "Total")
        tv = ttk.Treeview(self.zone, columns=cols, show="headings",
                          height=len(classes)+1, style="M.Treeview")
        for col in cols:
            tv.heading(col, text=col)
            tv.column(col, width=100, anchor="center")
        tv.column("Classe", width=130, anchor="w")

        for i, nom in enumerate(classes):
            tv.insert("", "end", values=(
                nom,
                f"{rp[i]*100:+.2f}%", f"{rb[i]*100:+.2f}%",
                f"{a[i]*100:+.2f}%", f"{s[i]*100:+.2f}%",
                f"{it[i]*100:+.2f}%", f"{(a[i]+s[i]+it[i])*100:+.2f}%"
            ))
        tv.insert("", "end", values=(
            "TOTAL",
            f"{res['rp']*100:+.2f}%", f"{res['rb']*100:+.2f}%",
            f"{a.sum()*100:+.2f}%", f"{s.sum()*100:+.2f}%",
            f"{it.sum()*100:+.2f}%", f"{exc*100:+.2f}%"
        ))
        tv.pack(fill="x", pady=(0,8))

        # graphiques
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.6), facecolor=self.BG)
        fig.tight_layout(pad=2.5)

        ax1.set_facecolor(self.BG)
        vals = [a.sum()*100, s.sum()*100, it.sum()*100, exc*100]
        lbls = ["Allocation", "Sélection", "Interaction", "Excès total"]
        clrs = [self.BLU, self.GRN, self.PCH, self.RED]
        bars = ax1.bar(lbls, vals, color=clrs, edgecolor=self.BG, width=0.5)
        ax1.axhline(0, color=self.DIM, lw=0.8, ls="--")
        ax1.set_title("Décomposition globale", color=self.FG, fontsize=10)
        ax1.tick_params(colors=self.DIM, labelsize=8)
        ax1.set_ylabel("(%)", color=self.DIM, fontsize=8)
        for bar, v in zip(bars, vals):
            ax1.text(bar.get_x()+bar.get_width()/2,
                     bar.get_height() + (0.01 if v >= 0 else -0.05),
                     f"{v:+.2f}%", ha="center", color=self.FG, fontsize=8)
        for sp in ax1.spines.values(): sp.set_edgecolor(self.BG3)

        ax2.set_facecolor(self.BG)
        x = np.arange(len(classes))
        w = 0.22
        ax2.bar(x-w, a*100,  w, label="Allocation",  color=self.BLU, edgecolor=self.BG)
        ax2.bar(x,   s*100,  w, label="Sélection",   color=self.GRN, edgecolor=self.BG)
        ax2.bar(x+w, it*100, w, label="Interaction", color=self.PCH, edgecolor=self.BG)
        ax2.axhline(0, color=self.DIM, lw=0.8, ls="--")
        ax2.set_xticks(x)
        ax2.set_xticklabels([c.replace(" ", "\n") for c in classes], fontsize=7, color=self.DIM)
        ax2.set_title("Effets par classe d'actifs", color=self.FG, fontsize=10)
        ax2.tick_params(colors=self.DIM, labelsize=8)
        ax2.legend(fontsize=8, facecolor=self.BG2, labelcolor=self.FG, edgecolor=self.BG3)
        for sp in ax2.spines.values(): sp.set_edgecolor(self.BG3)

        canvas = FigureCanvasTkAgg(fig, master=self.zone)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

        clr = self.GRN if exc >= 0 else self.RED
        tk.Label(self, bg=self.BG, fg=clr, font=("Helvetica", 10, "bold"),
                 text=(f"Port. : {res['rp']*100:.2f}%   "
                       f"Bench. : {res['rb']*100:.2f}%   "
                       f"Excès : {exc*100:+.2f}%")).pack(pady=(0,10))


if __name__ == "__main__":
    App().mainloop()
