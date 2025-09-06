import tkinter as tk
from tkinter import messagebox
from database import create_connection

def login_window(callback):
    """
    Login / Signup window.
    callback: function to call after successful login (e.g., main_menu)
    """
    root = tk.Tk()
    root.title("EcoFinds - Login / SignUp")
    root.geometry("400x500")
    root.configure(bg="#e0f7fa")

    # Title
    tk.Label(root, text="EcoFinds", font=("Arial", 24, "bold"), bg="#e0f7fa").pack(pady=10)

    # Username (for signup)
    tk.Label(root, text="Username (for signup)", bg="#e0f7fa").pack()
    username_entry = tk.Entry(root)
    username_entry.pack(pady=5)

    # Email
    tk.Label(root, text="Email", bg="#e0f7fa").pack()
    email_entry = tk.Entry(root)
    email_entry.pack(pady=5)

    # Password
    tk.Label(root, text="Password", bg="#e0f7fa").pack()
    password_entry = tk.Entry(root, show="*")
    password_entry.pack(pady=5)

    # Login function
    def login():
        email = email_entry.get()
        password = password_entry.get()
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            messagebox.showinfo("Success", f"Welcome {user[1]}!")
            root.destroy()
            callback(user)  # call main_menu(user)
        else:
            messagebox.showerror("Error", "Invalid email or password")

    # Signup function
    def signup():
        username = username_entry.get()
        email = email_entry.get()
        password = password_entry.get()
        if username and email and password:
            try:
                conn = create_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                    (username, email, password)
                )
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Account created! Please login.")
            except:
                messagebox.showerror("Error", "Email already exists")
        else:
            messagebox.showerror("Error", "All fields are required")

    # Buttons
    tk.Button(root, text="Login", width=15, bg="#00796b", fg="white", command=login).pack(pady=10)
    tk.Button(root, text="Sign Up", width=15, bg="#004d40", fg="white", command=signup).pack(pady=5)

    root.mainloop()


# Run standalone for testing
if __name__ == "__main__":
    # For standalone testing, just pass a dummy callback
    login_window(lambda user: print("Logged in user:", user))
