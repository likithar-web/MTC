from app import app
from database import db, Food


foods = [

    # BREAKFAST

    {
        "name": "Idli",
        "description": "Soft and fluffy steamed South Indian rice cakes served with sambar and chutney.",
        "price": 40,
        "offer_price": None,
        "category": "Breakfast",
        "meal": "Breakfast",
        "featured": True
    },

    {
        "name": "Vada",
        "description": "Crispy golden South Indian medu vada served with hot sambar and chutney.",
        "price": 50,
        "offer_price": None,
        "category": "Breakfast",
        "meal": "Breakfast",
        "featured": True
    },

    {
        "name": "Poori Masala",
        "description": "Fluffy deep-fried pooris served with delicious potato masala.",
        "price": 60,
        "offer_price": None,
        "category": "Breakfast",
        "meal": "Breakfast",
        "featured": True
    },

    {
        "name": "Omelette",
        "description": "Fresh egg omelette prepared with onion, green chilli and spices.",
        "price": 50,
        "offer_price": None,
        "category": "Egg",
        "meal": "Breakfast",
        "featured": False
    },

    {
        "name": "Veg Sandwich",
        "description": "Fresh vegetable sandwich prepared with vegetables, spices and toasted bread.",
        "price": 70,
        "offer_price": None,
        "category": "Sandwich",
        "meal": "Breakfast",
        "featured": False
    },


    # LUNCH

    {
        "name": "Veg Biryani",
        "description": "Fragrant basmati rice cooked with fresh vegetables and aromatic Indian spices.",
        "price": 120,
        "offer_price": None,
        "category": "Rice & Biryani",
        "meal": "Lunch",
        "featured": True
    },

    {
        "name": "Chicken Biryani",
        "description": "Aromatic basmati rice cooked with tender chicken, herbs and traditional biryani spices.",
        "price": 180,
        "offer_price": 160,
        "category": "Rice & Biryani",
        "meal": "Lunch / Dinner",
        "featured": True
    },

    {
        "name": "Chicken Meals",
        "description": "Complete Indian meal served with rice, curry, vegetables and chicken preparation.",
        "price": 180,
        "offer_price": None,
        "category": "Meals",
        "meal": "Lunch",
        "featured": True
    },

    {
        "name": "Curd Rice",
        "description": "Creamy South Indian curd rice tempered with traditional spices.",
        "price": 60,
        "offer_price": None,
        "category": "Rice",
        "meal": "Lunch",
        "featured": False
    },

    {
        "name": "Jeera Rice",
        "description": "Long-grain basmati rice flavoured with aromatic roasted cumin seeds.",
        "price": 90,
        "offer_price": None,
        "category": "Rice",
        "meal": "Lunch",
        "featured": False
    },

    {
        "name": "Rice Sambar",
        "description": "Steamed rice served with flavorful South Indian sambar prepared with vegetables and lentils.",
        "price": 70,
        "offer_price": None,
        "category": "Rice",
        "meal": "Lunch",
        "featured": False
    },


    # EVENING

    {
        "name": "Gobi Manchurian",
        "description": "Crispy cauliflower tossed in a spicy and flavorful Indo-Chinese Manchurian sauce.",
        "price": 100,
        "offer_price": None,
        "category": "Starters",
        "meal": "Evening",
        "featured": True
    },

    {
        "name": "Egg Sandwich",
        "description": "Toasted bread filled with seasoned egg and fresh vegetables.",
        "price": 80,
        "offer_price": None,
        "category": "Sandwich",
        "meal": "Evening",
        "featured": False
    },

    {
        "name": "French Fries",
        "description": "Golden crispy potato fries served hot and seasoned perfectly.",
        "price": 90,
        "offer_price": None,
        "category": "Snacks",
        "meal": "Evening",
        "featured": True
    },


    # DINNER

    {
        "name": "Egg Fried Rice",
        "description": "Wok-tossed rice with scrambled egg, vegetables and aromatic spices.",
        "price": 110,
        "offer_price": None,
        "category": "Fried Rice",
        "meal": "Dinner",
        "featured": False
    },

    {
        "name": "Chicken Fried Rice",
        "description": "Flavorful wok-fried rice tossed with tender chicken, vegetables and spices.",
        "price": 140,
        "offer_price": None,
        "category": "Fried Rice",
        "meal": "Dinner",
        "featured": True
    },

    {
        "name": "Veg Noodles",
        "description": "Stir-fried noodles tossed with fresh vegetables and flavorful sauces.",
        "price": 100,
        "offer_price": None,
        "category": "Noodles",
        "meal": "Dinner",
        "featured": False
    },

    {
        "name": "Chicken Noodles",
        "description": "Stir-fried noodles with tender chicken, fresh vegetables and savory sauces.",
        "price": 130,
        "offer_price": None,
        "category": "Noodles",
        "meal": "Dinner",
        "featured": True
    },

    {
        "name": "Parota",
        "description": "Flaky layered South Indian parota served hot and fresh.",
        "price": 40,
        "offer_price": None,
        "category": "Breads",
        "meal": "Dinner",
        "featured": True
    },

    {
        "name": "Chapati",
        "description": "Soft and fresh Indian wheat chapati served hot.",
        "price": 30,
        "offer_price": None,
        "category": "Breads",
        "meal": "Dinner",
        "featured": False
    }

]


# IMAGE FILE NAMES

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


with app.app_context():

    print()
    print("======================================")
    print("      MTC HOTEL FOOD DATABASE")
    print("======================================")
    print()

    # ADD FOODS THAT DO NOT EXIST

    added = 0

    for item in foods:

        existing = Food.query.filter_by(
            name=item["name"]
        ).first()

        if existing:

            print("Already exists:", item["name"])

        else:

            food = Food(
                name=item["name"],
                description=item["description"],
                price=item["price"],
                offer_price=item["offer_price"],
                category=item["category"],
                meal=item["meal"],
                available=True,
                featured=item["featured"],
                image=image_map.get(item["name"])
            )

            db.session.add(food)

            added += 1

            print("Added:", item["name"])


    # UPDATE IMAGES FOR EXISTING FOODS

    print()
    print("Updating food images...")
    print()

    updated = 0

    for food_name, image_name in image_map.items():

        food = Food.query.filter_by(
            name=food_name
        ).first()

        if food:

            food.image = image_name

            updated += 1

            print(
                "Image updated:",
                food_name,
                "->",
                image_name
            )

        else:

            print(
                "Food not found:",
                food_name
            )


    db.session.commit()


    print()
    print("======================================")
    print("             FINISHED")
    print("======================================")
    print()
    print("New foods added:", added)
    print("Images updated:", updated)
    print("Total foods:", Food.query.count())
    print()