import tkinter as tk
from tkinter import  ttk
from vampgui.file_io import InputFileViewer
from vampgui.helpkey import show_help
from vampgui.version import __version__
from home_page import MainInputTab

def apply_night_theme(root):
    style = ttk.Style()
    style.theme_use('default')

    # General widget colors
    bg_color = '#2e2e2e'
    fg_color = '#ffffff'
    entry_bg = '#3c3f41'
    button_bg = '#444444'
    highlight_color = '#5e81ac'

    root.configure(bg=bg_color)

    style.configure('.', background=bg_color, foreground=fg_color)
    style.configure('TNotebook', background=bg_color)
    style.configure('TNotebook.Tab', background=button_bg, foreground=fg_color)
    style.configure('TFrame', background=bg_color)
    style.configure('TLabel', background=bg_color, foreground=fg_color)
    style.configure('TCheckbutton', background=bg_color, foreground=fg_color)
    style.configure('TButton', background=button_bg, foreground=fg_color)
    style.configure('TCombobox', fieldbackground=entry_bg, background=entry_bg, foreground=fg_color)

    # For non-ttk widgets
    def apply_to_all_widgets(widget):
        if isinstance(widget, (tk.Frame, tk.LabelFrame)):
            widget.configure(bg=bg_color)
        elif isinstance(widget, tk.Label):
            widget.configure(bg=bg_color, fg=fg_color)
        elif isinstance(widget, tk.Entry):
            widget.configure(bg=entry_bg, fg=fg_color, insertbackground=fg_color)
        elif isinstance(widget, tk.Text):
            widget.configure(bg=entry_bg, fg=fg_color, insertbackground=fg_color)
        elif isinstance(widget, tk.Checkbutton):
            widget.configure(bg=bg_color, fg=fg_color, activebackground=bg_color, activeforeground=fg_color, selectcolor=bg_color)
        elif isinstance(widget, tk.Button):
            widget.configure(bg=button_bg, fg=fg_color, activebackground=highlight_color, activeforeground=fg_color)
        for child in widget.winfo_children():
            apply_to_all_widgets(child)

    apply_to_all_widgets(root)


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VampGUI with Theme Option")
        self.create_widgets()

    def create_widgets(self):
        # Top Frame for theme toggle
        top_frame = tk.Frame(self.root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        theme_btn = tk.Button(top_frame, text="Toggle Night Theme", command=lambda: apply_night_theme(self.root))
        theme_btn.pack(side=tk.RIGHT)

        # Main Notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True)

        tab_main = ttk.Frame(notebook)
        notebook.add(tab_main, text="Material Input")

        self.tab1 = MainInputTab(tab_main)


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
