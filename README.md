# Project Milestone 1: LOLCODE Lexer
**Members:** 
- Matira, Eron Jay H.
- Samonte, Krizshna Yvonne H.
- Valentino, Nicole Phoebe G.
<<<<<<< HEAD
=======

>>>>>>> cb93df6bd499c730dc5408e8bbe8fb66183c9e7c
**Section:** ST-6L

## 📋 Overview
This project is a Python-based lexical analyzer (tokenizer) for the LOLCODE programming language.
It reads a .lol source file, identifies and classifies each token (such as keywords, identifiers, literals, and operators), and outputs the results to a text file (output.txt).

## ⚙️ Features
- Detects all major LOLCODE tokens including:
    - Comments (BTW, OBTW ... TLDR)
    - Keywords and operators (I HAS A, SUM OF, VISIBLE, etc.)
    - Literals (integers, floats, strings, booleans)
    - Identifiers
    - Code delimiters (HAI, KTHXBYE)
- Ignores whitespace, newlines, and comments
- Outputs formatted token list to a readable .txt file

## 🧩 Requirements
- Python 3.8+
- No external dependencies (only uses Python’s built-in re module).

### 📂 Files
| File | Description |
|------|--------------|
| `tokenizer.py` | The main Python script that performs lexical analysis. |
| `test.lol` | The sample LOLCODE source code to be tokenized. |
| `output.txt` | The generated output showing token classifications. |
| `README.md` | Project documentation (this file). |


### ▶️ How to Run
1. Place your LOLCODE program in a file named **`test.lol`**  
   (or modify the filename inside `tokenizer.py`).

2. Run the script:
   ```bash
   python tokenizer.py

3. The tokens will be written to `output.txt` in the same folder.

## 📚 References
- https://lokalise.com/blog/lolcode-tutorial-on-programming-language-for-cat-lovers/
- https://www.w3schools.com/python/python_regex.asp
<<<<<<< HEAD


## 👨‍💻 Author
Developed by Nicole Phoebe Valentino
LOLCODE and Lexemes by Eron Jay Matira & Krizshna Yvonne Samonte
For CMSC 141 Project (Milestone 1)
=======
>>>>>>> cb93df6bd499c730dc5408e8bbe8fb66183c9e7c
