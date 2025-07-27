from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import os

app = Flask(__name__)
app.secret_key = 'bulkbuy_secret'
app.permanent_session_lifetime = timedelta(days=1)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)


# User model with role
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='vendor')  # 'vendor' or 'supplier'


# Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('user.id'))


# Helper cart functions (vendor only)
def get_cart():
    return session.setdefault("group_cart", {})


def save_cart(cart):
    session["group_cart"] = cart


@app.before_request
def create_tables():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        role = request.form.get("role")

        if not username or not password or not role:
            flash("Please fill in all fields.", "error")
            return redirect(url_for("signup"))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists!", "error")
            return redirect(url_for("signup"))

        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash("Signup successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session.permanent = True
            session["user"] = user.username
            flash("Logged in successfully!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials", "error")
            return render_template("login.html")
    return render_template("login.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("login"))

    user = User.query.filter_by(username=session["user"]).first()
    if not user:
        flash("User not found, please log in again.", "error")
        session.pop("user")
        return redirect(url_for("login"))

    if user.role == 'supplier':
        # Supplier dashboard for managing products
        if request.method == "POST":
            name = request.form.get("product_name", "").strip()
            price = request.form.get("product_price", "").strip()

            if not name or not price.isdigit() or int(price) <= 0:
                flash("Please provide valid product name and positive price.", "error")
            else:
                new_product = Product(name=name, price=int(price), supplier_id=user.id)
                db.session.add(new_product)
                db.session.commit()
                flash(f"Product '{name}' added!", "success")

        products = Product.query.filter_by(supplier_id=user.id).all()
        return render_template("supplier_dashboard.html", products=products, username=user.username)

    else:
        # Vendor dashboard to buy products
        all_products = Product.query.all()
        cart = get_cart()

        if request.method == "POST":
            prod_id = request.form.get("product_id")
            qty_str = request.form.get("quantity")

            if not prod_id or not qty_str or not qty_str.isdigit():
                flash("Invalid product or quantity.", "error")
            else:
                product = Product.query.get(int(prod_id))
                quantity = int(qty_str)
                if product and quantity > 0:
                    key = str(prod_id)
                    cart[key] = cart.get(key, 0) + quantity
                    save_cart(cart)
                    flash(f"Added {quantity} × {product.name} to the cart.", "success")
                else:
                    flash("Invalid product or quantity.", "error")

        cart_items = []
        total = 0
        for pid, qty in cart.items():
            prod = Product.query.get(int(pid))
            if prod:
                subtotal = prod.price * qty
                cart_items.append({'name': prod.name, 'qty': qty, 'price': prod.price, 'subtotal': subtotal})
                total += subtotal

        return render_template(
            "vendor_dashboard.html",
            username=user.username,
            products=all_products,
            group_cart=cart_items,
            total=total
        )


@app.route("/view_cart")
def view_cart():
    if "user" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("login"))

    user = User.query.filter_by(username=session["user"]).first()
    if not user or user.role != 'vendor':
        flash("Access denied.", "error")
        return redirect(url_for("dashboard"))

    cart = session.get("group_cart", {})
    cart_items = []
    total = 0
    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        if product:
            subtotal = product.price * qty
            cart_items.append({'name': product.name, 'qty': qty, 'price': product.price, 'subtotal': subtotal})
            total += subtotal

    return render_template("view_cart.html", username=user.username, group_cart=cart_items, total=total)


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if "user" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("login"))

    user = User.query.filter_by(username=session["user"]).first()
    if not user or user.role != 'vendor':
        flash("Access denied.", "error")
        return redirect(url_for("dashboard"))

    cart = session.get("group_cart", {})
    if not cart:
        flash("Your cart is empty!", "error")
        return redirect(url_for("dashboard"))

    cart_items = []
    total = 0
    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        if product:
            subtotal = product.price * qty
            cart_items.append({'name': product.name, 'qty': qty, 'price': product.price, 'subtotal': subtotal})
            total += subtotal

    if request.method == "POST":
        # Here you could integrate actual purchase processing
        session.pop("group_cart", None)
        flash("Purchase successful! Thank you for your order.", "success")
        return redirect(url_for("dashboard"))

    return render_template("checkout.html", username=user.username, group_cart=cart_items, total=total)


@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("group_cart", None)
    flash("Logged out successfully.", "success")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
    port = int(os.environ.get("PORT", 10000))  # Render uses PORT env var
    app.run(host="0.0.0.0", port=port)
