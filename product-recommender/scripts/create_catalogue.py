import json
from pathlib import Path

print("\n====================================================================================================")
print("Create catalog script running...")
print("====================================================================================================")

PRODUCTS = [
    # ── Fashion & Clothing ────────────────────────────────────
    {
        'id': 'P001',
        'name': 'Ankara Print Bomber Jacket',
        'description': 'Vibrant kente-inspired Ankara fabric bomber jacket. Water resistant outer shell. Warm fleece lining. Perfect for cool evenings and outdoor events.',
        'category': 'Fashion',
        'price_ghs': 280.0
    },
    {
        'id': 'P002',
        'name': 'Lightweight Rain Poncho',
        'description': 'Packable waterproof poncho in bright yellow. Fits in a small pouch. Protects against rain and light wind. Unisex, one-size-fits-all.',
        'category': 'Outdoor',
        'price_ghs': 45.0
    },
    {
        'id': 'P003', 'name': 'Kente Cloth Scarf',
        'description': 'Traditional Ghanaian kente woven scarf. Warm and cozy for air conditioned offices or cool weather. Handmade by artisans in Bonwire.',
        'category': 'Fashion',
        'price_ghs': 95.0
    },
    {
        'id': 'P004',
        'name': 'Heavy-Duty Raincoat',
        'description': 'Professional-grade waterproof raincoat with sealed seams. Double zip front and adjustable hood. Ideal for heavy tropical downpours.',
        'category': 'Outdoor', 'price_ghs': 320.0
    },
    {
        'id': 'P005',
        'name': 'Cozy Fleece Hoodie',
        'description': 'Ultra-soft fleece hoodie in earth tones. Kangaroo pocket. Perfect for cold evenings, travel, or working from home.',
        'category': 'Fashion',
        'price_ghs': 150.0
    },

    # ── Electronics ──────────────────────────────────────────
    {
        'id': 'P006',
        'name': 'Solar-Powered Phone Charger',
        'description': 'Portable solar panel with dual USB output. Charges two phones simultaneously. Foldable design for travel. Works even on cloudy days.',
        'category': 'Electronics',
        'price_ghs': 210.0
    },
    {
        'id': 'P007', 'name': 'Wireless Bluetooth Earbuds',
        'description': 'True wireless stereo earbuds with active noise cancellation. 8 hour battery. IPX5 water resistance. Compatible with all smartphones.',
        'category': 'Electronics',
        'price_ghs': 180.0
    },
    {
        'id': 'P008', 'name': 'Power Bank 20000mAh',
        'description': 'High-capacity portable power bank. Fast charge support. Powers laptops, tablets, and phones. LED battery indicator. Great for power outages.',
        'category': 'Electronics',
        'price_ghs': 240.0
    },
    {
        'id': 'P009', 'name': 'LED Desk Lamp with USB Charging',
        'description': 'Flexible neck LED desk lamp. 3 brightness levels. Built-in USB port to charge your phone. Low heat, eye-friendly light. Perfect for studying.',
        'category': 'Electronics',
        'price_ghs': 85.0
    },
    {
        'id': 'P010', 'name': 'Smart WiFi Security Camera',
        'description': 'Indoor/outdoor security camera. 1080p HD. Night vision. Motion detection alerts to phone. Works with mobile app. Easy DIY installation.',
        'category': 'Electronics',
        'price_ghs': 195.0
    },

    # ── Food & Kitchen ────────────────────────────────────────
    {
        'id': 'P011', 'name': 'Premium Ghanaian Cocoa Powder',
        'description': 'Single-origin dark cocoa powder from Brong-Ahafo Region. Certified organic. Rich chocolate flavour. For baking, hot drinks, and smoothies.',
        'category': 'Food',
        'price_ghs': 35.0
    },
    {
        'id': 'P012', 'name': 'Portable Gas Camping Stove',
        'description': 'Compact single-burner camping stove. Uses standard butane canisters. Wind-resistant design. Folds flat. Great for camping, outdoor cooking, and power cuts.',
        'category': 'Outdoor',
        'price_ghs': 120.0
    },
    {
        'id': 'P013', 'name': 'Electric Rice Cooker 3L',
        'description': 'Automatic 3-litre rice cooker. Keep-warm function. Steamer tray included. Non-stick inner pot. Cooks jollof, plain rice, and porridge perfectly.',
        'category': 'Kitchen', 'price_ghs': 165.0
    },
    {
        'id': 'P014', 'name': 'Water Filtration Bottle',
        'description': 'Reusable bottle with built-in 3-stage water filter. Removes bacteria, chlorine, and heavy metals. Safe for tap water anywhere. 750ml capacity.',
        'category': 'Outdoor',
        'price_ghs': 75.0
    },

    # ── Health & Beauty ───────────────────────────────────────
    {
        'id': 'P015', 'name': 'Natural Shea Butter Moisturiser',
        'description': 'Pure unrefined shea butter from Tamale. Deeply moisturising for dry skin. No artificial fragrance. Safe for babies and sensitive skin.',
        'category': 'Health',
        'price_ghs': 25.0},
    {
        'id': 'P016', 'name': 'Mosquito Repellent Wristbands',
        'description': 'DEET-free plant-based mosquito repellent wristbands. 200 hours of protection. Waterproof. Pack of 5. Safe for children. Citronella scent.',
        'category': 'Health',
        'price_ghs': 40.0},
    {
        'id': 'P017', 'name': 'Herbal Immune Boost Tea',
        'description': 'Blend of Ghanaian herbs: moringa, ginger, turmeric, and lemon grass. Supports immune system. Caffeine-free. 30 pyramid tea bags per box.',
        'category': 'Health',
        'price_ghs': 30.0},

    # ── Books & Education ─────────────────────────────────────
    {
        'id': 'P018', 'name': 'Python Programming for Beginners',
        'description': 'Practical Python programming book with Ghanaian real-world examples. Covers data analysis, web development, and automation. Includes free online exercises.',
        'category': 'Books',
        'price_ghs': 60.0
    },
    {
        'id': 'P019', 'name': 'African Business Strategy Handbook',
        'description': 'Essential guide to launching and scaling businesses in African markets. Case studies from Ghana, Nigeria, and Kenya. Covers fintech, agri-tech, and retail.',
        'category': 'Books',
        'price_ghs': 80.0
    },
    {
        'id': 'P020', 'name': 'STEM Activity Kit for Kids',
        'description': 'Hands-on science and engineering activity kit for children aged 8-14. Build circuits, create rockets, and conduct experiments. 30 activities included.',
        'category': 'Education',
        'price_ghs': 110.0
    },
]

Path('data').mkdir(exist_ok=True)
with open('data/products.json', 'w') as f:
    json.dump(PRODUCTS, f, indent=2)
print(f'Saved {len(PRODUCTS)} products to data/products.json')
