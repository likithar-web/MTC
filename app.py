from flask import Flask, render_template, request, redirect, url_for, session
from database import db, Food, Customer, Order, OrderItem
from werkzeug.utils import secure_filename
from functools import wraps
import os
import uuid


# =========================================================
# MTC HOTEL - FLASK APP
# =========================================================

app = Flask(__name__)


# =========================================================
# APP CONFIGURATION
# =========================================================

app.config["SECRET_KEY"] = "mtc-hotel-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///food.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# =========================================================
# ADMIN LOGIN SETTINGS
# =========================================================

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


# =========================================================
# UPLOAD SETTINGS
# =========================================================

UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "static",
    "uploads",
    "foods"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)



# =========================================================
# ADMIN UPDATE ORDER STATUS
# =========================================================

@app.route("/admin/orders/status/<int:order_id>", methods=["POST"])
def update_order_status(order_id):

    order = Order.query.get_or_404(order_id)

    new_status = request.form.get("status", "").strip()

    allowed_statuses = [
        "Pending",
        "Confirmed",
        "Preparing",
        "Ready",
        "Delivered",
        "Cancelled"
    ]

    if new_status not in allowed_statuses:
        return redirect(url_for("admin_orders"))

    order.status = new_status

    db.session.commit()

    return redirect(url_for("admin_orders"))




# =========================================================
# DATABASE
# =========================================================

db.init_app(app)


# =========================================================
# FILE CHECK
# =========================================================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


def customer_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("customer_logged_in"):
            return redirect(url_for("customer_login"))
        return view(*args, **kwargs)

    return wrapped_view


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template("home.html")


# =========================================================
# CUSTOMER MENU
# =========================================================

@app.route("/menu")
def customer_menu():

    foods = (
        Food.query
        .filter_by(available=True)
        .order_by(Food.id.asc())
        .all()
    )

    cart = session.get("cart", {})
    cart_count = sum(int(quantity) for quantity in cart.values())

    return render_template(
        "customer/menu.html",
        foods=foods,
        cart_count=cart_count
    )


# =========================================================
# CUSTOMER REGISTRATION
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def customer_register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        # -----------------------------------------
        # CHECK REQUIRED FIELDS
        # -----------------------------------------

        if not name or not email or not phone or not password:

            return render_template(
                "customer/register.html",
                error="Please fill in all fields."
            )

        # -----------------------------------------
        # CHECK PASSWORD
        # -----------------------------------------

        if password != confirm_password:

            return render_template(
                "customer/register.html",
                error="Passwords do not match."
            )

        # -----------------------------------------
        # CHECK EXISTING EMAIL
        # -----------------------------------------

        existing_email = Customer.query.filter_by(
            email=email
        ).first()

        if existing_email:

            return render_template(
                "customer/register.html",
                error="An account with this email already exists."
            )

        # -----------------------------------------
        # CHECK EXISTING PHONE
        # -----------------------------------------

        existing_phone = Customer.query.filter_by(
            phone=phone
        ).first()

        if existing_phone:

            return render_template(
                "customer/register.html",
                error="An account with this phone number already exists."
            )

        # -----------------------------------------
        # CREATE CUSTOMER
        # -----------------------------------------

        customer = Customer(
            name=name,
            email=email,
            phone=phone,
            password=password
        )

        db.session.add(customer)

        db.session.commit()

        return render_template(
            "customer/register.html",
            success="Account created successfully."
        )

    return render_template(
        "customer/register.html"
    )


# =========================================================
# CUSTOMER LOGIN
# =========================================================

@app.route("/customer/login", methods=["GET", "POST"])
def customer_login():

    if session.get("customer_logged_in"):
        return redirect(url_for("customer_menu"))

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        if not email or not password:
            return render_template(
                "customer/login.html",
                error="Please enter email and password."
            )

        customer = Customer.query.filter_by(
            email=email
        ).first()

        if not customer or customer.password != password:
            return render_template(
                "customer/login.html",
                error="Invalid email or password."
            )

        session["customer_logged_in"] = True
        session["customer_id"] = customer.id
        session["customer_name"] = customer.name
        session["customer_email"] = customer.email

        return redirect(url_for("customer_menu"))

    return render_template(
        "customer/login.html"
    )


# =========================================================
# CUSTOMER LOGOUT
# =========================================================

@app.route("/customer/logout")
def customer_logout():

    session.pop("customer_logged_in", None)
    session.pop("customer_id", None)
    session.pop("customer_name", None)
    session.pop("customer_email", None)

    return redirect(url_for("home"))



# =========================================================
# CUSTOMER CART
# =========================================================

@app.route("/cart")
@customer_required
def cart():

    cart = session.get("cart", {})
    cart_items = []
    total = 0

    for food_id, quantity in cart.items():

        food = Food.query.get(int(food_id))

        if not food or not food.available:
            continue

        quantity = int(quantity)

        unit_price = (
            food.offer_price
            if food.offer_price is not None
            else food.price
        )

        subtotal = unit_price * quantity
        total += subtotal

        cart_items.append({
            "food": food,
            "quantity": quantity,
            "unit_price": unit_price,
            "subtotal": subtotal
        })

    return render_template(
        "customer/cart.html",
        cart_items=cart_items,
        total=total
    )


@app.route("/cart/add/<int:food_id>", methods=["POST"])
@customer_required
def add_to_cart(food_id):

    food = Food.query.get_or_404(food_id)

    if not food.available:
        return redirect(url_for("customer_menu"))

    cart = session.get("cart", {})

    key = str(food_id)

    cart[key] = int(cart.get(key, 0)) + 1

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("customer_menu"))


@app.route("/cart/update/<int:food_id>", methods=["POST"])
@customer_required
def update_cart(food_id):

    food = Food.query.get_or_404(food_id)

    quantity = request.form.get(
        "quantity",
        "1"
    )

    try:
        quantity = int(quantity)
    except ValueError:
        quantity = 1

    cart = session.get("cart", {})
    key = str(food_id)

    if quantity <= 0:
        cart.pop(key, None)
    else:
        cart[key] = quantity

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("cart"))


@app.route("/cart/remove/<int:food_id>", methods=["POST"])
@customer_required
def remove_from_cart(food_id):

    cart = session.get("cart", {})

    cart.pop(str(food_id), None)

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("cart"))


@app.route("/cart/clear", methods=["POST"])
@customer_required
def clear_cart():

    session["cart"] = {}
    session.modified = True

    return redirect(url_for("cart"))





# =========================================================
# CUSTOMER CHECKOUT
# =========================================================

@app.route("/checkout")
@customer_required
def checkout():

    return render_template(
        "customer/checkout.html"
    )





# =========================================================
# CUSTOMER PLACE ORDER
# =========================================================

@app.route("/api/place-order", methods=["POST"])
@customer_required
def place_order():

    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    address = str(data.get("address", "")).strip()
    payment_method = str(
        data.get("payment_method", "Cash on Delivery")
    ).strip()

    items = data.get("items", [])

    if not name or not phone or not address:
        return {
            "success": False,
            "message": "Please fill in all customer details."
        }, 400

    if not isinstance(items, list) or not items:
        return {
            "success": False,
            "message": "Your cart is empty."
        }, 400

    customer_id = session.get("customer_id")

    if not customer_id:
        return {
            "success": False,
            "message": "Please login again."
        }, 401

    customer = Customer.query.get(customer_id)

    if not customer:
        return {
            "success": False,
            "message": "Customer account not found."
        }, 404

    order = Order(
        customer_id=customer.id,
        customer_name=name,
        phone=phone,
        address=address,
        payment_method=payment_method,
        total_amount=0,
        status="Pending"
    )

    db.session.add(order)

    total = 0

    for cart_item in items:

        try:
            food_id = int(cart_item.get("id"))
            quantity = int(cart_item.get("quantity"))
        except (TypeError, ValueError):
            db.session.rollback()
            return {
                "success": False,
                "message": "Invalid cart item."
            }, 400

        if quantity <= 0:
            db.session.rollback()
            return {
                "success": False,
                "message": "Invalid quantity."
            }, 400

        food = Food.query.get(food_id)

        if not food or not food.available:
            db.session.rollback()
            return {
                "success": False,
                "message": "One of the selected food items is unavailable."
            }, 400

        unit_price = (
            food.offer_price
            if food.offer_price is not None
            else food.price
        )

        subtotal = float(unit_price) * quantity
        total += subtotal

        order_item = OrderItem(
            order=order,
            food_id=food.id,
            food_name=food.name,
            quantity=quantity,
            unit_price=float(unit_price),
            subtotal=subtotal
        )

        db.session.add(order_item)

    order.total_amount = total

    db.session.commit()

    return {
        "success": True,
        "message": "Order placed successfully.",
        "order_id": order.id
    }



# =========================================================
# CUSTOMER MY ORDERS / ORDER TRACKING
# =========================================================

@app.route("/my-orders")
@customer_required
def my_orders():

    orders = (
        Order.query
        .filter_by(
            customer_id=session.get("customer_id")
        )
        .order_by(Order.created_at.desc())
        .all()
    )

    return render_template(
        "customer/my_orders.html",
        orders=orders
    )


# =========================================================
# CUSTOMER ORDER SUCCESS
# =========================================================

@app.route("/order-success/<int:order_id>")
@customer_required
def order_success(order_id):

    order = Order.query.filter_by(
        id=order_id,
        customer_id=session.get("customer_id")
    ).first_or_404()

    return render_template(
        "customer/order_success.html",
        order=order
    )




# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    # If already logged in, go directly to dashboard
    if session.get("admin_logged_in"):

        return redirect(
            url_for("admin_dashboard")
        )

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if (
            username == ADMIN_USERNAME
            and password == ADMIN_PASSWORD
        ):

            session["admin_logged_in"] = True

            return redirect(
                url_for("admin_dashboard")
            )

        return render_template(
            "admin/login.html",
            error="Invalid username or password."
        )

    return render_template(
        "admin/login.html"
    )


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect(
        url_for("admin_login")
    )


# =========================================================
# PROTECT ADMIN PAGES
# =========================================================

@app.before_request
def protect_admin_pages():

    if request.path.startswith("/admin"):

        # Login page must remain accessible
        if request.path == "/admin/login":

            return None

        # Allow static files
        if request.path.startswith("/admin/static"):

            return None

        # Redirect unauthenticated users
        if not session.get("admin_logged_in"):

            return redirect(
                url_for("admin_login")
            )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin")
def admin_dashboard():

    total_foods = Food.query.count()

    available_foods = (
        Food.query
        .filter_by(available=True)
        .count()
    )

    unavailable_foods = (
        Food.query
        .filter_by(available=False)
        .count()
    )

    featured_foods = (
        Food.query
        .filter_by(featured=True)
        .count()
    )

    return render_template(
        "admin/dashboard.html",
        total_foods=total_foods,
        available_foods=available_foods,
        unavailable_foods=unavailable_foods,
        featured_foods=featured_foods
    )


# =========================================================
# ADMIN MENU
# =========================================================

@app.route("/admin/menu")
def admin_menu():

    foods = (
        Food.query
        .filter_by(available=True)
        .order_by(Food.id.asc())
        .all()
    )

    return render_template(
        "admin/menu.html",
        foods=foods
    )


# =========================================================
# ADMIN FOODS
# =========================================================

@app.route("/admin/foods")
def admin_foods():

    selected_category = request.args.get(
        "category"
    )

    if selected_category:

        foods = (
            Food.query
            .filter(
                Food.category == selected_category
            )
            .order_by(Food.id.desc())
            .all()
        )

    else:

        foods = (
            Food.query
            .order_by(Food.id.desc())
            .all()
        )

    return render_template(
        "admin/foods.html",
        foods=foods,
        selected_category=selected_category
    )


# =========================================================
# ADD FOOD
# =========================================================

@app.route(
    "/admin/foods/add",
    methods=["GET", "POST"]
)
def add_food():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        price = request.form.get(
            "price",
            "0"
        )

        offer_price = request.form.get(
            "offer_price",
            ""
        )

        category = request.form.get(
            "category",
            ""
        ).strip()

        meal = request.form.get(
            "meal",
            ""
        ).strip()

        available = (
            request.form.get("available")
            == "on"
        )

        featured = (
            request.form.get("featured")
            == "on"
        )

        image_filename = None

        # -----------------------------------------
        # IMAGE UPLOAD
        # -----------------------------------------

        if "image" in request.files:

            file = request.files["image"]

            if (
                file
                and file.filename
                and allowed_file(file.filename)
            ):

                original_name = secure_filename(
                    file.filename
                )

                extension = (
                    original_name
                    .rsplit(".", 1)[1]
                    .lower()
                )

                unique_name = (
                    str(uuid.uuid4())
                    + "."
                    + extension
                )

                file.save(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        unique_name
                    )
                )

                image_filename = unique_name

        # -----------------------------------------
        # CREATE FOOD
        # -----------------------------------------

        food = Food(
            name=name,
            description=description,
            price=float(price or 0),
            offer_price=(
                float(offer_price)
                if offer_price
                else None
            ),
            category=category,
            meal=meal,
            image=image_filename,
            available=available,
            featured=featured
        )

        db.session.add(food)

        db.session.commit()

        return redirect(
            url_for("admin_foods")
        )

    return render_template(
        "admin/add_food.html"
    )


# =========================================================
# EDIT FOOD
# =========================================================

@app.route(
    "/admin/foods/edit/<int:food_id>",
    methods=["GET", "POST"]
)
def edit_food(food_id):

    food = Food.query.get_or_404(
        food_id
    )

    if request.method == "POST":

        food.name = request.form.get(
            "name",
            ""
        ).strip()

        food.description = request.form.get(
            "description",
            ""
        ).strip()

        price = request.form.get(
            "price",
            "0"
        )

        offer_price = request.form.get(
            "offer_price",
            ""
        )

        food.price = float(
            price or 0
        )

        food.offer_price = (
            float(offer_price)
            if offer_price
            else None
        )

        food.category = request.form.get(
            "category",
            ""
        ).strip()

        food.meal = request.form.get(
            "meal",
            ""
        ).strip()

        food.available = (
            request.form.get("available")
            == "on"
        )

        food.featured = (
            request.form.get("featured")
            == "on"
        )

        # -----------------------------------------
        # NEW IMAGE
        # -----------------------------------------

        if "image" in request.files:

            file = request.files["image"]

            if (
                file
                and file.filename
                and allowed_file(file.filename)
            ):

                original_name = secure_filename(
                    file.filename
                )

                extension = (
                    original_name
                    .rsplit(".", 1)[1]
                    .lower()
                )

                unique_name = (
                    str(uuid.uuid4())
                    + "."
                    + extension
                )

                file.save(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        unique_name
                    )
                )

                # Delete old uploaded image
                if food.image:

                    old_image = os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        food.image
                    )

                    if os.path.exists(
                        old_image
                    ):

                        try:

                            os.remove(
                                old_image
                            )

                        except OSError:

                            pass

                food.image = unique_name

        db.session.commit()

        return redirect(
            url_for("admin_foods")
        )

    return render_template(
        "admin/edit_food.html",
        food=food
    )


# =========================================================
# TOGGLE FOOD AVAILABILITY
# =========================================================

@app.route(
    "/admin/foods/toggle/<int:food_id>"
)
def toggle_food(food_id):

    food = Food.query.get_or_404(
        food_id
    )

    food.available = not food.available

    db.session.commit()

    return redirect(
        url_for("admin_foods")
    )


# =========================================================
# TOGGLE FEATURED
# =========================================================

@app.route(
    "/admin/foods/featured/<int:food_id>"
)
def toggle_featured(food_id):

    food = Food.query.get_or_404(
        food_id
    )

    food.featured = not food.featured

    db.session.commit()

    return redirect(
        url_for("admin_foods")
    )


# =========================================================
# DELETE FOOD
# =========================================================

@app.route(
    "/admin/foods/delete/<int:food_id>"
)
def delete_food(food_id):

    food = Food.query.get_or_404(
        food_id
    )

    # Delete uploaded image
    if food.image:

        image_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            food.image
        )

        if os.path.exists(
            image_path
        ):

            try:

                os.remove(
                    image_path
                )

            except OSError:

                pass

    db.session.delete(food)

    db.session.commit()

    return redirect(
        url_for("admin_foods")
    )


# =========================================================
# ORDERS
# =========================================================

@app.route("/admin/orders")
def admin_orders():

    orders = (
        Order.query
        .order_by(Order.created_at.desc())
        .all()
    )

    return render_template(
        "admin/orders.html",
        orders=orders
    )


# =========================================================
# CATEGORIES
# =========================================================

@app.route("/admin/categories")
def admin_categories():

    categories = (
        db.session
        .query(Food.category)
        .filter(
            Food.category.isnot(None),
            Food.category != ""
        )
        .distinct()
        .order_by(
            Food.category.asc()
        )
        .all()
    )

    category_list = [
        category[0]
        for category in categories
    ]

    return render_template(
        "admin/categories.html",
        categories=category_list
    )


# =========================================================
# MEAL TIMINGS
# =========================================================

@app.route("/admin/meal-timings")
def admin_meal_timings():

    meal_timings = [

        {
            "name": "Breakfast",
            "icon": "☕",
            "time": "7:00 AM - 11:00 AM",
            "description":
                "Start the day with fresh breakfast items."
        },

        {
            "name": "Lunch",
            "icon": "🍛",
            "time": "12:00 PM - 3:30 PM",
            "description":
                "Enjoy our lunch menu and daily meals."
        },

        {
            "name": "Evening",
            "icon": "☕",
            "time": "4:00 PM - 7:00 PM",
            "description":
                "Tea, snacks and evening favourites."
        },

        {
            "name": "Dinner",
            "icon": "🍽️",
            "time": "7:00 PM - 10:30 PM",
            "description":
                "Freshly prepared dinner options."
        }

    ]

    return render_template(
        "admin/meal_timings.html",
        meal_timings=meal_timings
    )


# =========================================================
# OFFERS
# =========================================================

@app.route("/admin/offers")
def admin_offers():

    offers = [

        {
            "name": "Breakfast Combo",
            "icon": "🍳",
            "description":
                "A delicious combination of breakfast favourites.",
            "price": "₹99",
            "status": "Active"
        },

        {
            "name": "Lunch Special",
            "icon": "🍛",
            "description":
                "Special lunch combination for a complete meal.",
            "price": "₹149",
            "status": "Active"
        },

        {
            "name": "Evening Snack Combo",
            "icon": "☕",
            "description":
                "Tea or coffee with selected evening snacks.",
            "price": "₹79",
            "status": "Active"
        },

        {
            "name": "Family Dinner Combo",
            "icon": "🍽️",
            "description":
                "A convenient combination for family dining.",
            "price": "₹399",
            "status": "Active"
        }

    ]

    return render_template(
        "admin/offers.html",
        offers=offers
    )


# =========================================================
# CUSTOMERS
# =========================================================

@app.route("/admin/customers")
def admin_customers():

    return render_template(
        "admin/customers.html"
    )


# =========================================================
# REPORTS
# =========================================================

@app.route("/admin/reports")
def admin_reports():

    return render_template(
        "admin/page.html",
        page_title="Reports",
        page_subtitle=
            "View sales, orders and business reports.",
        page_icon="▥"
    )


# =========================================================
# SETTINGS
# =========================================================

@app.route("/admin/settings")
def admin_settings():

    return render_template(
        "admin/page.html",
        page_title="Settings",
        page_subtitle=
            "Manage MTC HOTEL website and system settings.",
        page_icon="⚙"
    )


# =========================================================
# DATABASE + IMAGE FIX
# =========================================================

with app.app_context():

    db.create_all()

    image_map = {

        "Idli": "idly.jpg.jpg",

        "Vada": "vada.jpg.jpg",

        "Poori Masala": "poori_sagu.jpg.jpg",

        "Omelette": "omelette.jpg.jpg",

        "Veg Sandwich": "veg_sandwich.jpg.jpg",

        "Veg Biryani": "veg_biryani.jpg.jpg",

        "Chicken Biryani": "chicken_biryani.jpg.jpg",

        "Chicken Meals": "chicken_meals.jpg.jpg",

        "Curd Rice": "curd_rice.jpg.jpg",

        "Jeera Rice": "jeera_rice.jpg.jpg",

        "Rice Sambar": "rice_sambar.jpg.jpg",

        "Gobi Manchurian": "gobi_manchurian.jpg.jpg",

        "Egg Sandwich": "egg_sandwich.jpg.jpg",

        "French Fries": "french_fries.jpg.jpg",

        "Egg Fried Rice": "egg_fried_rice.jpg.jpg",

        "Chicken Fried Rice": "chicken_fried_rice.jpg.jpg",

        "Veg Noodles": "noodles.jpg.jpg",

        "Chicken Noodles": "chicken_noodles.jpg.jpg",

        "Parota": "parota.jpg.jpg",

        "Chapati": "chapathi.jpg.jpg"
    }

    changed = False

    for food_name, image_name in image_map.items():

        food = Food.query.filter_by(
            name=food_name
        ).first()

        if food:

            if food.image != image_name:

                food.image = image_name

                changed = True

    if changed:

        db.session.commit()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )