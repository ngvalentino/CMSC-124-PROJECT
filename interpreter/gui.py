import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
from lexer import tokenize
from parser import validate_code, validate_file  # using direct parser calls
from semantic_analyzer import analyze_semantics_from_code  # ONLY this is needed

class LOLCodeGUI:
    def __init__(self, root):
        self.root = root
        root.title("LOLCODE Interpreter")
        self.loaded_file_path = None  # Track last loaded file

        # === Buttons ===
        self.load_button = tk.Button(root, text="Load File", command=self.load_file)
        self.load_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.run_button = tk.Button(root, text="Run Code", command=self.run_code)
        self.run_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # === Labels for Treeviews (aligned with buttons) ===
        tk.Label(root, text="Tokens").grid(row=0, column=2, padx=5, pady=5)
        tk.Label(root, text="Symbol Table").grid(row=0, column=3, padx=5, pady=5)

        # === Editor ===
        self.editor = scrolledtext.ScrolledText(root, width=80, height=30)
        self.editor.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # === Token Treeview ===
        self.token_tree = ttk.Treeview(root, columns=("Value", "Type"), show="headings", height=25)
        self.token_tree.heading("Value", text="Lexeme")
        self.token_tree.heading("Type", text="Token Type")
        self.token_tree.column("Value", width=100)
        self.token_tree.column("Type", width=140)
        self.token_tree.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")

        # === Symbol Table Treeview ===
        self.symbol_tree = ttk.Treeview(root, columns=("Name", "Value"), show="headings", height=25)
        self.symbol_tree.heading("Name", text="Variable")
        self.symbol_tree.heading("Value", text="Value")
        self.symbol_tree.column("Name", width=100)
        self.symbol_tree.column("Value", width=140)
        self.symbol_tree.grid(row=1, column=3, padx=5, pady=5, sticky="nsew")
        # === Console ===
        tk.Label(root, text="EXECUTE").grid(row=2, column=0, columnspan=4, pady=(10, 0))
        self.console = scrolledtext.ScrolledText(root, width=120, height=10)
        self.console.grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")

    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("LOLCODE files", "*.lol")])
        if filepath:
            self.loaded_file_path = filepath
            with open(filepath, 'r') as file:
                content = file.read()
                self.editor.delete("1.0", tk.END)
                self.editor.insert(tk.END, content)

    def run_code(self):
        code = self.editor.get("1.0", tk.END).strip()
        self.console.delete("1.0", tk.END)

        if code:
            # === Analyze directly from editor ===
            self.console.insert(tk.END, "Analyzing code from editor...\n")
            syntax_errors = validate_code(code)
            semantic_errors, symbol_table = analyze_semantics_from_code(code)

        elif self.loaded_file_path:
            # === Analyze directly from file ===
            self.console.insert(tk.END, f"Analyzing code from file: {self.loaded_file_path}\n")
            syntax_errors = validate_file(self.loaded_file_path)

            # read file content
            with open(self.loaded_file_path, 'r') as f:
                code = f.read()

            # use same analyzer
            semantic_errors, symbol_table = analyze_semantics_from_code(code)

        else:
            self.console.insert(tk.END, "No code to analyze. Please type or load a file.\n")
            return

        # === Token display ===
        all_tokens = [tokenize(line) for line in code.splitlines()]
        self.update_tokens([tok for line in all_tokens for tok in line])

        # === Symbol table display ===
        self.update_symbols(symbol_table)

        # === Error output ===
        if syntax_errors:
            self.console.insert(tk.END, "Syntax Errors:\n")
            for err in syntax_errors:
                self.console.insert(tk.END, f"  - {err}\n")
        elif semantic_errors:
            self.console.insert(tk.END, "Semantic Errors:\n")
            for err in semantic_errors:
                self.console.insert(tk.END, f"  - {err}\n")
        else:
            self.console.insert(tk.END, "No syntax or semantic errors found.\n")

    def update_tokens(self, tokens):
        self.token_tree.delete(*self.token_tree.get_children())
        for t in tokens:
            ttype = t[0]
            val = t[1]
            self.token_tree.insert("", "end", values=(val, ttype))


    def update_symbols(self, symbols):
        self.symbol_tree.delete(*self.symbol_tree.get_children())
        for name, typ in symbols.items():
            self.symbol_tree.insert("", "end", values=(name, typ))

# === Launch GUI ===
if __name__ == "__main__":
    root = tk.Tk()
    app = LOLCodeGUI(root)
    root.mainloop()
