import tkinter as tk
from decimal import Decimal, DivisionByZero, InvalidOperation, getcontext

getcontext().prec = 15

# ---- 色の設定（灰色系）----
BG = "#2b2b2b"          # ウィンドウ背景
DISPLAY_BG = "#1f1f1f"  # 表示部の背景
DISPLAY_FG = "#f2f2f2"
SUB_FG = "#9a9a9a"      # 式の文字色
NUM_BG = "#4a4a4a"      # 数字ボタン
NUM_HOVER = "#5c5c5c"
FUNC_BG = "#6b6b6b"     # C / ⌫ / ± ボタン
FUNC_HOVER = "#7d7d7d"
OP_BG = "#8a8a8a"       # 演算子ボタン
OP_HOVER = "#9c9c9c"
EQ_BG = "#b0b0b0"       # = ボタン
EQ_HOVER = "#c4c4c4"

FONT_BTN = ("Helvetica", 22, "bold")
FONT_MAIN = ("Helvetica", 38, "bold")
FONT_SUB = ("Helvetica", 14)

OPS = {
    "+": lambda a, b: a + b,
    "−": lambda a, b: a - b,
    "×": lambda a, b: a * b,
    "÷": lambda a, b: a / b,
}


def fmt(d: Decimal) -> str:
    """Decimal を見やすい文字列にする（指数表記にしない）"""
    s = format(d.normalize(), "f")
    return "0" if s in ("-0", "") else s


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("電卓")
        self.configure(bg=BG, padx=12, pady=12)
        self.resizable(False, False)

        self.current = "0"
        self.stored = None
        self.operator = None
        self.reset_next = False
        self.error = False

        self._build_display()
        self._build_buttons()
        self._bind_keys()
        self._refresh()

    # ---------- 画面の組み立て ----------
    def _build_display(self):
        frame = tk.Frame(self, bg=DISPLAY_BG)
        frame.pack(fill="x", pady=(0, 10))
        self.sub_var = tk.StringVar()
        self.main_var = tk.StringVar()
        tk.Label(frame, textvariable=self.sub_var, bg=DISPLAY_BG, fg=SUB_FG,
                 font=FONT_SUB, anchor="e", padx=12).pack(fill="x", pady=(8, 0))
        tk.Label(frame, textvariable=self.main_var, bg=DISPLAY_BG, fg=DISPLAY_FG,
                 font=FONT_MAIN, anchor="e", padx=12).pack(fill="x", pady=(0, 8))

    def _build_buttons(self):
        grid = tk.Frame(self, bg=BG)
        grid.pack()

        # (表示文字, 行, 列, 列スパン, 色, ホバー色, 動作)
        layout = [
            ("C", 0, 0, 1, FUNC_BG, FUNC_HOVER, self.clear),
            ("⌫", 0, 1, 1, FUNC_BG, FUNC_HOVER, self.backspace),
            ("±", 0, 2, 1, FUNC_BG, FUNC_HOVER, self.toggle_sign),
            ("÷", 0, 3, 1, OP_BG, OP_HOVER, lambda: self.choose_operator("÷")),
            ("7", 1, 0, 1, NUM_BG, NUM_HOVER, lambda: self.input_digit("7")),
            ("8", 1, 1, 1, NUM_BG, NUM_HOVER, lambda: self.input_digit("8")),
            ("9", 1, 2, 1, NUM_BG, NUM_HOVER, lambda: self.input_digit("9")),
            ("×", 1, 3, 1, OP_BG, OP_HOVER, lambda: self.choose_operator("×")),
            ("4", 2, 0, 1, NUM_BG, NUM_HOVER, lambda: self.input_digit("4")),
            ("5", 2, 1, 1, NUM_BG, NUM_HOVER, lambda: self.input_digit("5")),
            ("6", 2, 2, 1, NUM_BG, NUM_HOVER, lambda: self.input_digit("6")),
            ("−", 2, 3, 1, OP_BG, OP_HOVER, lambda: self.choose_operator("−")),
            ("1", 3, 0, 1, NUM_BG, NUM_HOVER, lambda: self.input_digit("1")),
            ("2", 3, 1, 1, NUM_BG, NUM_HOVER, lambda: self.input_digit("2")),
            ("3", 3, 2, 1, NUM_BG, NUM_HOVER, lambda: self.input_digit("3")),
            ("+", 3, 3, 1, OP_BG, OP_HOVER, lambda: self.choose_operator("+")),
            ("0", 4, 0, 2, NUM_BG, NUM_HOVER, lambda: self.input_digit("0")),
            (".", 4, 2, 1, NUM_BG, NUM_HOVER, self.input_dot),
            ("=", 4, 3, 1, EQ_BG, EQ_HOVER, self.equals),
        ]

        for text, r, c, span, color, hover, cmd in layout:
            fg = "#1f1f1f" if color == EQ_BG else "#ffffff"
            btn = tk.Label(grid, text=text, bg=color, fg=fg, font=FONT_BTN,
                           width=4 * span + (span - 1) * 1, height=2,
                           cursor="hand2")
            btn.grid(row=r, column=c, columnspan=span, padx=4, pady=4, sticky="nsew")
            btn.bind("<Button-1>", lambda e, f=cmd: f())
            btn.bind("<Enter>", lambda e, b=btn, h=hover: b.config(bg=h))
            btn.bind("<Leave>", lambda e, b=btn, col=color: b.config(bg=col))

    def _bind_keys(self):
        for d in "0123456789":
            self.bind(d, lambda e, x=d: self.input_digit(x))
        self.bind(".", lambda e: self.input_dot())
        self.bind("+", lambda e: self.choose_operator("+"))
        self.bind("-", lambda e: self.choose_operator("−"))
        self.bind("*", lambda e: self.choose_operator("×"))
        self.bind("/", lambda e: self.choose_operator("÷"))
        self.bind("<Return>", lambda e: self.equals())
        self.bind("<KP_Enter>", lambda e: self.equals())
        self.bind("=", lambda e: self.equals())
        self.bind("<BackSpace>", lambda e: self.backspace())
        self.bind("<Escape>", lambda e: self.clear())

    # ---------- 表示更新 ----------
    def _refresh(self):
        self.main_var.set(self.current)

    def _set_sub(self, text=""):
        self.sub_var.set(text)

    # ---------- 入力処理 ----------
    def _recover_from_error(self):
        if self.error:
            self.clear()

    def input_digit(self, d):
        self._recover_from_error()
        if self.reset_next or self.current == "0":
            self.current = d
            self.reset_next = False
        elif len(self.current.replace("-", "").replace(".", "")) < 15:
            self.current += d
        self._refresh()

    def input_dot(self):
        self._recover_from_error()
        if self.reset_next:
            self.current = "0."
            self.reset_next = False
        elif "." not in self.current:
            self.current += "."
        self._refresh()

    def toggle_sign(self):
        self._recover_from_error()
        if self.current != "0":
            self.current = self.current[1:] if self.current.startswith("-") else "-" + self.current
            self._refresh()

    def backspace(self):
        self._recover_from_error()
        if self.reset_next:
            return
        self.current = self.current[:-1]
        if self.current in ("", "-"):
            self.current = "0"
        self._refresh()

    def clear(self):
        self.current = "0"
        self.stored = None
        self.operator = None
        self.reset_next = False
        self.error = False
        self._set_sub("")
        self._refresh()

    # ---------- 計算 ----------
    def _calculate(self):
        """stored (operator) current を計算して Decimal を返す。失敗時は None"""
        try:
            return OPS[self.operator](self.stored, Decimal(self.current))
        except (DivisionByZero, InvalidOperation, ZeroDivisionError):
            return None

    def _show_error(self):
        self.current = "エラー"
        self.stored = None
        self.operator = None
        self.error = True
        self.reset_next = True
        self._set_sub("0 で割ることはできません")
        self._refresh()

    def choose_operator(self, op):
        self._recover_from_error()
        # 連続で演算子を押したときは演算子を置き換えるだけ
        if self.operator and self.reset_next:
            self.operator = op
            self._set_sub(f"{fmt(self.stored)} {op}")
            return
        # 続けて計算（例: 1 + 2 + → 3 +）
        if self.operator:
            result = self._calculate()
            if result is None:
                self._show_error()
                return
            self.stored = result
            self.current = fmt(result)
        else:
            self.stored = Decimal(self.current)
        self.operator = op
        self.reset_next = True
        self._set_sub(f"{fmt(self.stored)} {op}")
        self._refresh()

    def equals(self):
        self._recover_from_error()
        if not self.operator:
            return
        left = fmt(self.stored)
        right = self.current
        op = self.operator
        result = self._calculate()
        if result is None:
            self._show_error()
            return
        self.current = fmt(result)
        self.stored = None
        self.operator = None
        self.reset_next = True
        self._set_sub(f"{left} {op} {right} =")
        self._refresh()


if __name__ == "__main__":
    Calculator().mainloop()