import os
import tkinter as tk
from PIL import Image, ImageTk
from ttkbootstrap import Style
from tkinter import messagebox
from parser import CFGParser

class CFGApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CFG Parser")
        self.parser = None
        self.tree_img_path = "parse_tree.png"
        self.tree_photo = None

        self.style = Style(theme="flatly")
        self.root.geometry("800x700")

        self.setup_widgets()

    def setup_widgets(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10, fill=tk.X)

        # Grammar Text Area
        self.text_grammar = tk.Text(frame, width=70, height=10, wrap="word")
        self.text_grammar.insert("1.0",
            "E -> T E1\n"
            "E1 -> + T E1 | ε\n"
            "T -> F T1\n"
            "T1 -> * F T1 | ε\n"
            "F -> ( E ) | a"
        )
        self.text_grammar.pack(pady=5)

        # Input String Entry
        self.entry_string = tk.Entry(frame, width=60)
        self.entry_string.insert(0, "a + a * a")
        self.entry_string.pack(pady=5)

        # Parse Button
        btn_parse = tk.Button(frame, text="Parse", command=self.run_parser)
        btn_parse.pack(pady=5)

        # Show Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack()

        self.btn_show_derivation = tk.Button(btn_frame, text="Show Derivation", command=self.show_derivation)
        self.btn_show_derivation.grid(row=0, column=0, padx=10)

        self.btn_show_tree = tk.Button(btn_frame, text="Show Parse Tree", command=self.show_tree)
        self.btn_show_tree.grid(row=0, column=1, padx=10)

        # Container to hold derivation and tree side by side
        self.output_frame = tk.Frame(self.root)
        self.output_frame.pack()

        # Left side: derivation
        self.derivation_text = tk.Text(self.output_frame, height=15, width=40, state=tk.DISABLED)
        self.derivation_text.pack(side=tk.LEFT, padx=5, pady=5)

        # Right side: tree image in scrollable canvas
        self.tree_label = tk.LabelFrame(self.output_frame, text="Parse Tree")
        self.tree_label.pack(side=tk.RIGHT, padx=5, pady=5)

    def run_parser(self):
        grammar = self.text_grammar.get("1.0", tk.END)
        input_str = self.entry_string.get().strip().split()

        try:
            self.parser = CFGParser(grammar)
            success, path = self.parser.derive(input_str)
        except ValueError as e:
            messagebox.showerror("Grammar Error", str(e))
            self.derivation_steps = []
            self.tree_label.config(image="")
            return

        if success:
            messagebox.showinfo("Result", "✅ String Accepted!")

            self.derivation_steps = self.parser.get_derivation_steps(path)

            tree = self.parser.generate_parse_tree(path)
            tree.render("parse_tree", format="png", cleanup=True)

        else:
            messagebox.showerror("Result", "❌ String Rejected.")
            self.derivation_steps = []
            self.tree_label.config(image="")  # Clear image

    def show_derivation(self):
        self.derivation_text.config(state=tk.NORMAL)
        self.derivation_text.delete("1.0", tk.END)

        for i, step in enumerate(self.derivation_steps):
            self.derivation_text.insert(tk.END, f"Step {i}: {step}\n")

        self.derivation_text.config(state=tk.DISABLED)

    def show_tree(self):
        if os.path.exists(self.tree_img_path):
            image = Image.open(self.tree_img_path)
            self.tree_photo = ImageTk.PhotoImage(image)

            # Clear previous content if any
            for widget in self.tree_label.winfo_children():
                widget.destroy()

            # Scrollable Canvas
            canvas_frame = tk.Frame(self.tree_label)
            canvas_frame.pack()

            canvas = tk.Canvas(canvas_frame, width=700, height=350)
            hbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=canvas.xview)
            vbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)

            canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
            hbar.pack(side=tk.BOTTOM, fill=tk.X)
            vbar.pack(side=tk.RIGHT, fill=tk.Y)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            canvas_img = canvas.create_image(0, 0, anchor='nw', image=self.tree_photo)
            canvas.config(scrollregion=canvas.bbox(canvas_img))
