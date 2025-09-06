import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog
import hashlib

DB_NAME = "ecofinds.db"

# ---------- DATABASE ----------
def create_connection():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT,
        eco_points INTEGER DEFAULT 0
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        price REAL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        payment_method TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS wishlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )""")

    conn.commit()
    conn.close()

# ---------- UTILS ----------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# ---------- LOGIN ----------
def login_window():
    def login():
        user_input = entry_username.get()
        password = hash_password(entry_password.get())

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE (username=? OR email=?) AND password=?", (user_input, user_input, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            root.destroy()
            main_menu(user)
        else:
            messagebox.showerror("Error", "Invalid login")

    def signup():
        username = entry_username.get()
        email = entry_email.get()
        password = hash_password(entry_password.get())

        if not username or not email or not entry_password.get():
            messagebox.showerror("Error", "All fields are required")
            return

        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
            conn.commit()
            messagebox.showinfo("Success", "Account created! Please login.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username or Email already exists")
        conn.close()

    root = tk.Tk()
    root.title("EcoFinds - Login/Signup")
    root.geometry("350x300")

    tk.Label(root, text="Username / Email").pack()
    entry_username = tk.Entry(root)
    entry_username.pack()

    tk.Label(root, text="Email (only for signup)").pack()
    entry_email = tk.Entry(root)
    entry_email.pack()

    tk.Label(root, text="Password").pack()
    entry_password = tk.Entry(root, show="*")
    entry_password.pack()

    tk.Button(root, text="Login", command=login).pack(pady=5)
    tk.Button(root, text="Sign Up", command=signup).pack()

    root.mainloop()

# ---------- DASHBOARD ----------
def show_dashboard(frame, user):
    for widget in frame.winfo_children():
        widget.destroy()
    tk.Label(frame, text=f"Welcome {user[1]} 👋", font=("Arial", 18, "bold")).pack(pady=10)
    tk.Label(frame, text=f"Eco Points: {user[4]} 🌱", font=("Arial", 14), fg="green").pack(pady=5)
    tk.Label(frame, text="EcoFinds - Buy & Sell Second-Hand Products to save the planet!", fg="blue").pack(pady=10)

# ---------- ALL PRODUCTS ----------
def show_all_products(frame, user):
    for widget in frame.winfo_children():
        widget.destroy()
    tk.Label(frame, text="All Products", font=("Arial", 16, "bold")).pack(pady=10)

    list_frame = tk.Frame(frame)
    list_frame.pack(fill="both", expand=True)

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, price, user_id FROM products")
    products = cursor.fetchall()
    conn.close()

    if not products:
        tk.Label(list_frame, text="No products available.").pack()

    for p in products:
        item_frame = tk.Frame(list_frame, bd=1, relief="solid", padx=5, pady=5)
        item_frame.pack(pady=5, fill="x")
        tk.Label(item_frame, text=f"{p[1]} - ₹{p[2]} (Seller ID: {p[3]})", anchor="w").pack(side="left")

        tk.Button(item_frame, text="Add to Cart", command=lambda pid=p[0]: add_to_cart(user, pid)).pack(side="right", padx=5)
        tk.Button(item_frame, text="Wishlist", command=lambda pid=p[0]: add_to_wishlist(user, pid)).pack(side="right", padx=5)
        tk.Button(item_frame, text="Buy Now", command=lambda pid=p[0]: buy_now(user, pid)).pack(side="right", padx=5)

def add_to_cart(user, pid):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cart WHERE user_id=? AND product_id=?", (user[0], pid))
    if cursor.fetchone():
        messagebox.showinfo("Info", "Product already in cart")
    else:
        cursor.execute("INSERT INTO cart (user_id, product_id) VALUES (?, ?)", (user[0], pid))
        conn.commit()
        messagebox.showinfo("Success", "Added to cart")
    conn.close()

def add_to_wishlist(user, pid):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM wishlist WHERE user_id=? AND product_id=?", (user[0], pid))
    if cursor.fetchone():
        messagebox.showinfo("Info", "Product already in wishlist")
    else:
        cursor.execute("INSERT INTO wishlist (user_id, product_id) VALUES (?, ?)", (user[0], pid))
        conn.commit()
        messagebox.showinfo("Success", "Added to wishlist")
    conn.close()

def buy_now(user, pid):
    payment_method = simpledialog.askstring("Payment", "Enter payment method (Cash / UPI):")
    if payment_method not in ["Cash", "UPI"]:
        messagebox.showerror("Error", "Invalid payment method")
        return
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO purchases (user_id, product_id, payment_method) VALUES (?, ?, ?)", (user[0], pid, payment_method))
    cursor.execute("UPDATE users SET eco_points = eco_points + 10 WHERE id=?", (user[0],))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", f"Purchase successful using {payment_method}! 🌱 10 Eco Points awarded")

# ---------- PRODUCTS ----------
def show_products(frame, user):
    for widget in frame.winfo_children():
        widget.destroy()
    tk.Label(frame, text="My Products", font=("Arial", 16, "bold")).pack(pady=10)

    add_frame = tk.Frame(frame)
    add_frame.pack(pady=10)

    tk.Label(add_frame, text="Title:").grid(row=0, column=0, padx=5)
    title_entry = tk.Entry(add_frame)
    title_entry.grid(row=0, column=1, padx=5)

    tk.Label(add_frame, text="Price (₹):").grid(row=1, column=0, padx=5)
    price_entry = tk.Entry(add_frame)
    price_entry.grid(row=1, column=1, padx=5)

    def add_product():
        title = title_entry.get()
        price = price_entry.get()
        if not title or not price:
            messagebox.showerror("Error", "Both Title and Price required")
            return
        try:
            price_val = float(price)
        except:
            messagebox.showerror("Error", "Price must be a number")
            return

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (user_id, title, price) VALUES (?, ?, ?)", (user[0], title, price_val))
        conn.commit()
        conn.close()
        title_entry.delete(0, tk.END)
        price_entry.delete(0, tk.END)
        load_products()

    tk.Button(add_frame, text="Add Product", command=add_product, bg="#00796b", fg="white").grid(row=2, column=0, columnspan=2, pady=5)

    list_frame = tk.Frame(frame)
    list_frame.pack(pady=10, fill="both", expand=True)

    def load_products():
        for widget in list_frame.winfo_children():
            widget.destroy()
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, price FROM products WHERE user_id=?", (user[0],))
        products = cursor.fetchall()
        conn.close()

        if not products:
            tk.Label(list_frame, text="No products added yet.").pack()
        for p in products:
            item_frame = tk.Frame(list_frame)
            item_frame.pack(pady=2, fill="x")
            tk.Label(item_frame, text=f"{p[1]} - ₹{p[2]}", anchor="w").pack(side="left", padx=5)
            tk.Button(item_frame, text="Delete", command=lambda pid=p[0]: delete_product(pid)).pack(side="right", padx=5)

    def delete_product(pid):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id=?", (pid,))
        conn.commit()
        conn.close()
        load_products()

    load_products()

# ---------- CART ----------
def show_cart(frame, user):
    for widget in frame.winfo_children():
        widget.destroy()
    tk.Label(frame, text="Cart", font=("Arial", 16, "bold")).pack(pady=10)

    list_frame = tk.Frame(frame)
    list_frame.pack(pady=10, fill="both", expand=True)

    def load_cart_items():
        for widget in list_frame.winfo_children():
            widget.destroy()
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT products.id, products.title, products.price 
            FROM cart 
            JOIN products ON cart.product_id = products.id 
            WHERE cart.user_id=?
        """, (user[0],))
        items = cursor.fetchall()
        conn.close()

        if not items:
            tk.Label(list_frame, text="Your cart is empty.").pack()
        for item in items:
            item_frame = tk.Frame(list_frame)
            item_frame.pack(pady=2, fill="x")
            tk.Label(item_frame, text=f"{item[1]} - ₹{item[2]}", anchor="w").pack(side="left", padx=5)
            tk.Button(item_frame, text="Remove", command=lambda pid=item[0]: remove_item(pid)).pack(side="right", padx=5)
            tk.Button(item_frame, text="Buy", command=lambda pid=item[0]: buy_now(user, pid)).pack(side="right", padx=5)

    def remove_item(pid):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cart WHERE user_id=? AND product_id=?", (user[0], pid))
        conn.commit()
        conn.close()
        load_cart_items()

    def purchase_all():
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT product_id FROM cart WHERE user_id=?", (user[0],))
        items = cursor.fetchall()
        if not items:
            messagebox.showinfo("Info", "Cart is empty")
            conn.close()
            return
        for item in items:
            cursor.execute("INSERT INTO purchases (user_id, product_id, payment_method) VALUES (?, ?, ?)", (user[0], item[0], "Cash"))
        cursor.execute("DELETE FROM cart WHERE user_id=?", (user[0],))
        cursor.execute("UPDATE users SET eco_points = eco_points + ? WHERE id=?", (10*len(items), user[0]))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "All items purchased! 🌱")
        load_cart_items()

    tk.Button(frame, text="Purchase All", command=purchase_all, bg="#ff5722", fg="white").pack(pady=5)
    load_cart_items()

# ---------- PURCHASES ----------
def show_purchases(frame, user):
    for widget in frame.winfo_children():
        widget.destroy()
    tk.Label(frame, text="My Purchases", font=("Arial", 16, "bold")).pack(pady=10)

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT products.title, products.price, purchases.payment_method 
        FROM purchases
        JOIN products ON purchases.product_id = products.id
        WHERE purchases.user_id=?
    """, (user[0],))
    purchases = cursor.fetchall()
    conn.close()

    if not purchases:
        tk.Label(frame, text="No purchases yet.").pack()
    for p in purchases:
        tk.Label(frame, text=f"{p[0]} - ₹{p[1]} (Paid via {p[2]})").pack()

# ---------- WISHLIST ----------
def show_wishlist(frame, user):
    for widget in frame.winfo_children():
        widget.destroy()
    tk.Label(frame, text="My Wishlist", font=("Arial", 16, "bold")).pack(pady=10)

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT products.title, products.price FROM wishlist
        JOIN products ON wishlist.product_id = products.id
        WHERE wishlist.user_id=?
    """, (user[0],))
    wishlist = cursor.fetchall()
    conn.close()

    if not wishlist:
        tk.Label(frame, text="Your wishlist is empty.").pack()
    for w in wishlist:
        tk.Label(frame, text=f"{w[0]} - ₹{w[1]}").pack()

# ---------- DELETE ACCOUNT ----------
def delete_account(user_id, root):
    confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete your account? This cannot be undone.")
    if confirm:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
        cursor.execute("DELETE FROM products WHERE user_id=?", (user_id,))
        cursor.execute("DELETE FROM cart WHERE user_id=?", (user_id,))
        cursor.execute("DELETE FROM wishlist WHERE user_id=?", (user_id,))
        cursor.execute("DELETE FROM purchases WHERE user_id=?", (user_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Deleted", "Your account has been deleted.")
        root.destroy()
        login_window()

# ---------- MAIN MENU ----------
def main_menu(user):
    root = tk.Tk()
    root.title("EcoFinds - Marketplace")
    root.geometry("800x500")

    sidebar = tk.Frame(root, width=180, bg="#00796b")
    sidebar.pack(side="left", fill="y")

    main_frame = tk.Frame(root, bg="white")
    main_frame.pack(side="right", expand=True, fill="both")

    tk.Label(sidebar, text="EcoFinds", bg="#00796b", fg="white", font=("Arial", 16, "bold")).pack(pady=10)

    tk.Button(sidebar, text="Dashboard", width=20, command=lambda: show_dashboard(main_frame, get_user(user[0]))).pack(pady=5)
    tk.Button(sidebar, text="All Products", width=20, command=lambda: show_all_products(main_frame, get_user(user[0]))).pack(pady=5)
    tk.Button(sidebar, text="My Products", width=20, command=lambda: show_products(main_frame, get_user(user[0]))).pack(pady=5)
    tk.Button(sidebar, text="Cart", width=20, command=lambda: show_cart(main_frame, get_user(user[0]))).pack(pady=5)
    tk.Button(sidebar, text="Purchases", width=20, command=lambda: show_purchases(main_frame, get_user(user[0]))).pack(pady=5)
    tk.Button(sidebar, text="Wishlist", width=20, command=lambda: show_wishlist(main_frame, get_user(user[0]))).pack(pady=5)

    tk.Button(sidebar, text="Delete Account", width=20, fg="red", command=lambda: delete_account(user[0], root)).pack(pady=30)

    show_dashboard(main_frame, user)
    root.mainloop()

# ---------- START APP ----------
if __name__ == "__main__":
    create_tables()
    login_window()
