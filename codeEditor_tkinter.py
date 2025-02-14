import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import mysql.connector
import subprocess
import traceback

# Database connection 
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Akash123",
        database="CodeEditor"
    )

# user registration window
def register():
    def submit():
        username = username_entry.get()
        password = password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "All fields are required!")
            return
        
        db = connect_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            db.commit()
            messagebox.showinfo("Success", "Registration Successful!")
            reg_window.destroy()
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Username already exists!")
        db.close()

    reg_window = tk.Toplevel(root)
    reg_window.title("Register")
    tk.Label(reg_window, text="Username:").pack()
    username_entry = tk.Entry(reg_window)
    username_entry.pack()
    tk.Label(reg_window, text="Password:").pack()
    password_entry = tk.Entry(reg_window, show="*")
    password_entry.pack()
    tk.Button(reg_window, text="Register", command=submit).pack()

# After register login with same credentials
def login():
    def submit():
        global logged_in_user
        username = username_entry.get()
        password = password_entry.get()
        
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        
        if user:
            logged_in_user = username
            cursor.execute("INSERT INTO logged_in_users (username) VALUES (%s)", (username,))
            db.commit()
            db.close()
            messagebox.showinfo("Success", "Login Successful!")
            login_window.destroy()
            open_code_editor()
        else:
            messagebox.showerror("Error", "Invalid Credentials!")
            db.close()

    login_window = tk.Toplevel(root)
    login_window.title("Login")
    tk.Label(login_window, text="Username:").pack()
    username_entry = tk.Entry(login_window)
    username_entry.pack()
    tk.Label(login_window, text="Password:").pack()
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack()
    tk.Button(login_window, text="Login", command=submit).pack()

# Code Editor IDE
def open_code_editor():
    def run_code():
        code = code_editor.get("1.0", tk.END).strip()
        output_console.delete("1.0", tk.END)

        if not code:
            output_console.insert(tk.END, "⚠️ Error: No code to execute.\n", "error")
            return

        try:
            process = subprocess.run(["python", "-c", code], capture_output=True, text=True)

            if process.stderr:
                output_console.insert(tk.END, f"❌ Error:\n{process.stderr}", "error")
            else:
                output_console.insert(tk.END, "✅ Successful Developer!\n", "success")
                output_console.insert(tk.END, process.stdout)

        except Exception as e:
            output_console.insert(tk.END, f"⚠️ Runtime Error: {e}\n", "error")

    def save_code():
        code = code_editor.get("1.0", tk.END)
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO user_code (username, code) VALUES (%s, %s)", (logged_in_user, code))
        db.commit()
        db.close()
        messagebox.showinfo("Saved", "Code saved successfully!")

    def load_last_code():
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT code FROM user_code WHERE username=%s ORDER BY saved_at DESC LIMIT 1", (logged_in_user,))
        last_code = cursor.fetchone()
        db.close()
        if last_code:
            code_editor.delete("1.0", tk.END)
            code_editor.insert(tk.END, last_code[0])
        else:
            messagebox.showinfo("No Code", "No previous code found!")

    editor_window = tk.Toplevel(root)
    editor_window.title("Python Code Executor & Debugger")

    code_editor = scrolledtext.ScrolledText(editor_window, wrap=tk.WORD, font=("Consolas", 12), bg="#1e1e1e", fg="white")
    code_editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    run_button = tk.Button(editor_window, text="Run Code", command=run_code, bg="green", fg="white")
    run_button.pack(pady=5)

    output_console = scrolledtext.ScrolledText(editor_window, height=10, wrap=tk.WORD, font=("Consolas", 12), bg="black", fg="white")
    output_console.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    save_button = tk.Button(editor_window, text="Save Code", command=save_code, bg="blue", fg="white")
    save_button.pack(side=tk.LEFT, padx=5)

    load_button = tk.Button(editor_window, text="Load Last Code", command=load_last_code, bg="orange", fg="white")
    load_button.pack(side=tk.RIGHT, padx=5)

# Main Window
root = tk.Tk()
root.title("Indian.py editor - Login/Register")

tk.Button(root, text="Register", command=register, width=20).pack(pady=5)
tk.Button(root, text="Login", command=login, width=20).pack(pady=5)

logged_in_user = None
root.mainloop()
