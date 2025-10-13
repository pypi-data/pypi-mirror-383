import tkinter as tk
from tkinter import ttk, messagebox
import re

APP_TITLE = "MAC Address Formatter"


def clean_mac(text: str) -> str:
    """Return only hex characters from the input string."""
    if not text:
        return ""
    return re.sub(r"[^0-9a-fA-F]", "", text)


def is_valid_mac12(hex_only: str) -> bool:
    """Validate the string has exactly 12 hex digits (48-bit MAC)."""
    return bool(re.fullmatch(r"[0-9a-fA-F]{12}", hex_only))


def format_mac(hex_only: str, style: str = ":", case: str = "upper") -> str:
    """
    Format 12-hex-digit MAC into specified style.
    style options:
      - ":" -> XX:XX:XX:XX:XX:XX
      - "-" -> XX-XX-XX-XX-XX-XX
      - "." -> XXXX.XXXX.XXXX
    case options: "upper" or "lower"
    """
    if not is_valid_mac12(hex_only):
        return ""

    h = hex_only.upper() if case.lower() == "upper" else hex_only.lower()

    if style == ".":
        return f"{h[0:4]}.{h[4:8]}.{h[8:12]}"
    elif style in (":", "-"):
        pairs = [h[i:i+2] for i in range(0, 12, 2)]
        return style.join(pairs)
    else:
        # default to colon style
        pairs = [h[i:i+2] for i in range(0, 12, 2)]
        return ":".join(pairs)


class MacFormatterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("520x300")
        self.minsize(480, 280)

        self.case_var = tk.StringVar(value="upper")
        self.input_var = tk.StringVar()
        self.colon_var = tk.StringVar()
        self.dash_var = tk.StringVar()
        self.dot_var = tk.StringVar()

        self._build_ui()
        self._bind_events()

    def _build_ui(self):
        pad = {"padx": 8, "pady": 6}

        # Input frame
        in_frame = ttk.LabelFrame(self, text="Input")
        in_frame.pack(fill="x", expand=False, **pad)

        ttk.Label(in_frame, text="MAC address (any format):").grid(row=0, column=0, sticky="w", **pad)
        self.input_entry = ttk.Entry(in_frame, textvariable=self.input_var, width=40)
        self.input_entry.grid(row=0, column=1, sticky="we", **pad)
        in_frame.columnconfigure(1, weight=1)

        convert_btn = ttk.Button(in_frame, text="Convert", command=self.update_outputs)
        convert_btn.grid(row=0, column=2, **pad)

        clear_btn = ttk.Button(in_frame, text="Clear", command=self.clear_all)
        clear_btn.grid(row=0, column=3, **pad)

        # Case selection
        case_frame = ttk.LabelFrame(self, text="Case")
        case_frame.pack(fill="x", expand=False, **pad)
        ttk.Radiobutton(case_frame, text="UPPERCASE", value="upper", variable=self.case_var, command=self.update_outputs).grid(row=0, column=0, **pad)
        ttk.Radiobutton(case_frame, text="lowercase", value="lower", variable=self.case_var, command=self.update_outputs).grid(row=0, column=1, **pad)

        # Output frame
        out_frame = ttk.LabelFrame(self, text="Formats")
        out_frame.pack(fill="both", expand=True, **pad)

        # Colon format
        ttk.Label(out_frame, text="Colon (XX:XX:...):").grid(row=0, column=0, sticky="w", **pad)
        self.colon_entry = ttk.Entry(out_frame, textvariable=self.colon_var, state="readonly")
        self.colon_entry.grid(row=0, column=1, sticky="we", **pad)
        ttk.Button(out_frame, text="Copy", command=lambda: self.copy_to_clipboard(self.colon_var.get())).grid(row=0, column=2, **pad)

        # Dash format
        ttk.Label(out_frame, text="Dash (XX-XX-...):").grid(row=1, column=0, sticky="w", **pad)
        self.dash_entry = ttk.Entry(out_frame, textvariable=self.dash_var, state="readonly")
        self.dash_entry.grid(row=1, column=1, sticky="we", **pad)
        ttk.Button(out_frame, text="Copy", command=lambda: self.copy_to_clipboard(self.dash_var.get())).grid(row=1, column=2, **pad)

        # Dotted format
        ttk.Label(out_frame, text="Dotted (XXXX.XXXX.XXXX):").grid(row=2, column=0, sticky="w", **pad)
        self.dot_entry = ttk.Entry(out_frame, textvariable=self.dot_var, state="readonly")
        self.dot_entry.grid(row=2, column=1, sticky="we", **pad)
        ttk.Button(out_frame, text="Copy", command=lambda: self.copy_to_clipboard(self.dot_var.get())).grid(row=2, column=2, **pad)

        out_frame.columnconfigure(1, weight=1)

        # Status label
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(self, textvariable=self.status_var, foreground="#b00020")
        self.status_label.pack(fill="x", padx=10, pady=(0, 8))

        # Focus input on start
        self.after(100, lambda: self.input_entry.focus_set())

    def _bind_events(self):
        # Update outputs when typing
        self.input_entry.bind("<KeyRelease>", lambda e: self.update_outputs())

    def clear_all(self):
        self.input_var.set("")
        self.colon_var.set("")
        self.dash_var.set("")
        self.dot_var.set("")
        self.status_var.set("")
        self.input_entry.focus_set()

    def update_outputs(self):
        raw = self.input_var.get().strip()
        hex_only = clean_mac(raw)
        case = self.case_var.get()

        if not raw:
            # Nothing entered
            self.colon_var.set("")
            self.dash_var.set("")
            self.dot_var.set("")
            self.status_var.set("")
            return

        if not is_valid_mac12(hex_only):
            self.colon_var.set("")
            self.dash_var.set("")
            self.dot_var.set("")
            if len(hex_only) == 0:
                self.status_var.set("Enter 12 hex digits (48-bit MAC).")
            else:
                self.status_var.set(f"Invalid MAC: found {len(hex_only)} hex digits. Need 12.")
            return

        # Valid
        self.status_var.set("")
        self.colon_var.set(format_mac(hex_only, ":", case))
        self.dash_var.set(format_mac(hex_only, "-", case))
        self.dot_var.set(format_mac(hex_only, ".", case))

    def copy_to_clipboard(self, text: str):
        if not text:
            self.bell()
            return
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            # Ensure the clipboard is updated for other apps
            self.update()
            self.status_var.set("Copied to clipboard.")
        except Exception as e:
            messagebox.showerror("Clipboard Error", str(e))


def main():
    app = MacFormatterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
