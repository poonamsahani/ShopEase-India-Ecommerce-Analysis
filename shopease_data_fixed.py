import random
import calendar
from datetime import date, timedelta

random.seed(42)

sql = []

def w(*args):
    for line in args:
        sql.append(line)

# ============================================================
# DATABASE SETUP
# ============================================================
w(
"USE master;",
"GO",
"IF EXISTS (SELECT name FROM sys.databases WHERE name = N'ShopEase_India')",
"    DROP DATABASE ShopEase_India;",
"GO",
"CREATE DATABASE ShopEase_India;",
"GO",
"USE ShopEase_India;",
"GO",
""
)

# ============================================================
# CREATE TABLES
# ============================================================
w(
"-- =============================================",
"-- TABLE: Customers",
"-- =============================================",
"CREATE TABLE Customers (",
"    customer_id     INT PRIMARY KEY,",
"    customer_name   NVARCHAR(100) NOT NULL,",
"    email           NVARCHAR(150) NOT NULL UNIQUE,",
"    city            NVARCHAR(50),",
"    region          NVARCHAR(20),",
"    signup_date     DATE,",
"    gender          NVARCHAR(10)",
");",
"GO",
""
)

w(
"-- =============================================",
"-- TABLE: Products",
"-- =============================================",
"CREATE TABLE Products (",
"    product_id      INT PRIMARY KEY,",
"    product_name    NVARCHAR(100) NOT NULL,",
"    category        NVARCHAR(50),",
"    sub_category    NVARCHAR(50),",
"    price           DECIMAL(10,2),",
"    launch_date     DATE",
");",
"GO",
""
)

w(
"-- =============================================",
"-- TABLE: Orders",
"-- =============================================",
"CREATE TABLE Orders (",
"    order_id        INT PRIMARY KEY,",
"    customer_id     INT NOT NULL,",
"    order_date      DATE,",
"    order_status    NVARCHAR(20),",
"    payment_method  NVARCHAR(30),",
"    shipping_city   NVARCHAR(50),",
"    total_amount    DECIMAL(10,2),",
"    -- DATA QUALITY NOTE: total_amount is populated for ALL orders including",
"    -- Cancelled and Pending. This is intentional (an order has a value even",
"    -- if not fulfilled). All revenue analysis queries MUST filter on",
"    -- order_status = 'Delivered' to avoid inflating revenue figures.",
"    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)",
");",
"GO",
""
)

w(
"-- =============================================",
"-- TABLE: Order_Items",
"-- =============================================",
"CREATE TABLE Order_Items (",
"    item_id         INT PRIMARY KEY,",
"    order_id        INT NOT NULL,",
"    product_id      INT NOT NULL,",
"    quantity        INT,",
"    unit_price      DECIMAL(10,2),",
"    discount_pct    DECIMAL(5,2),",
"    CONSTRAINT fk_items_order   FOREIGN KEY (order_id)   REFERENCES Orders(order_id),",
"    CONSTRAINT fk_items_product FOREIGN KEY (product_id) REFERENCES Products(product_id)",
");",
"GO",
""
)

w(
"-- =============================================",
"-- TABLE: Returns",
"-- =============================================",
"CREATE TABLE Returns (",
"    return_id       INT PRIMARY KEY,",
"    order_id        INT NOT NULL,",
"    product_id      INT NOT NULL,",
"    return_date     DATE,",
"    return_reason   NVARCHAR(50),",
"    refund_amount   DECIMAL(10,2),",
"    CONSTRAINT fk_returns_order   FOREIGN KEY (order_id)   REFERENCES Orders(order_id),",
"    CONSTRAINT fk_returns_product FOREIGN KEY (product_id) REFERENCES Products(product_id)",
");",
"GO",
""
)

# ============================================================
# DATA POOLS
# ============================================================
male_names = [
    'Rahul','Amit','Vikram','Suresh','Rajesh','Arjun','Deepak','Nikhil',
    'Sandeep','Ajay','Ravi','Manish','Sanjay','Rohit','Anil','Pradeep',
    'Naveen','Vivek','Sachin','Ashok','Manoj','Dinesh','Ramesh','Sunil',
    'Gaurav','Abhishek','Pankaj','Vishal','Hemant','Tarun','Varun','Kartik',
    'Harsh','Mohit','Akash','Shubham','Ankit','Kunal','Sumit','Ritesh'
]
female_names = [
    'Priya','Anjali','Sneha','Pooja','Neha','Kavya','Divya','Meera',
    'Anita','Sunita','Rekha','Nisha','Swati','Pallavi','Shweta','Aarti',
    'Ritu','Sonia','Preeti','Deepika','Kavita','Manju','Shruti','Namrata',
    'Archana','Vandana','Poonam','Komal','Simran','Bhavna','Nidhi','Sakshi',
    'Tanvi','Ishita','Riya','Aditi','Kritika','Monika','Chandni','Srishti'
]
last_names = [
    'Sharma','Verma','Singh','Kumar','Gupta','Patel','Shah','Joshi',
    'Mehta','Agarwal','Yadav','Mishra','Pandey','Tiwari','Srivastava',
    'Chauhan','Saxena','Malhotra','Kapoor','Bhatia','Nair','Menon',
    'Reddy','Rao','Das','Bose','Banerjee','Chatterjee','Pillai','Iyer'
]

cities_regions = {
    'Delhi':       'North', 'Jaipur':      'North', 'Lucknow':   'North',
    'Chandigarh':  'North', 'Agra':        'North',
    'Mumbai':      'West',  'Pune':        'West',  'Ahmedabad': 'West',
    'Surat':       'West',  'Nagpur':      'West',
    'Bangalore':   'South', 'Chennai':     'South', 'Hyderabad': 'South',
    'Kochi':       'South', 'Coimbatore':  'South',
    'Kolkata':     'East',  'Bhubaneswar': 'East',  'Patna':     'East',
    'Guwahati':    'East',  'Ranchi':      'East'
}
city_list       = list(cities_regions.keys())
payment_methods = ['UPI','UPI','UPI','Credit Card','Credit Card','COD','Net Banking','Debit Card']

# ============================================================
# PRODUCTS (50 rows - hardcoded for control over story)
# ============================================================
products_data = [
    # Electronics (15)
    (1,  "Samsung Galaxy M34",        "Electronics","Mobiles",    18999.00,"2023-01-15"),
    (2,  "Redmi Note 13",             "Electronics","Mobiles",    15999.00,"2023-06-01"),
    (3,  "OnePlus Nord CE3",          "Electronics","Mobiles",    24999.00,"2023-03-10"),
    (4,  "HP Pavilion Laptop 15",     "Electronics","Laptops",    55999.00,"2023-01-20"),
    (5,  "Lenovo IdeaPad Slim 3",     "Electronics","Laptops",    42999.00,"2023-05-05"),
    (6,  "Dell Inspiron 15",          "Electronics","Laptops",    61999.00,"2023-02-14"),
    (7,  "boAt Airdopes 141",         "Electronics","Earphones",   1299.00,"2023-01-01"),
    (8,  "Sony WH-1000XM4",          "Electronics","Earphones",  19990.00,"2023-01-01"),
    (9,  "JBL Tune 230NC",           "Electronics","Earphones",   3999.00,"2023-04-20"),
    (10, "Samsung 43 inch Smart TV", "Electronics","Smart TV",   32999.00,"2023-01-01"),
    (11, "LG 32 inch HD TV",         "Electronics","Smart TV",   22999.00,"2023-03-12"),
    (12, "Apple iPad 10th Gen",       "Electronics","Tablets",    44900.00,"2023-01-01"),
    (13, "Samsung Galaxy Tab A8",     "Electronics","Tablets",    17999.00,"2023-06-15"),
    (14, "Realme Pad Mini",           "Electronics","Tablets",    10999.00,"2023-08-01"),
    (15, "Xiaomi Smart Band 8",       "Electronics","Wearables",   3499.00,"2023-05-10"),
    # Clothing existing (9)
    (16, "Men Cotton T-Shirt Classic","Clothing","Men Topwear",     599.00,"2023-01-01"),
    (17, "Women Kurti Floral Print",  "Clothing","Women Ethnic",    899.00,"2023-01-01"),
    (18, "Men Slim Fit Jeans",        "Clothing","Men Bottomwear", 1299.00,"2023-01-01"),
    (19, "Women Palazzo Set",         "Clothing","Women Western",  1199.00,"2023-03-01"),
    (20, "Men Formal Shirt White",    "Clothing","Men Topwear",     799.00,"2023-01-01"),
    (21, "Women Anarkali Suit",       "Clothing","Women Ethnic",   1899.00,"2023-06-01"),
    (22, "Kids T-Shirt Pack of 3",    "Clothing","Kids Wear",       699.00,"2023-01-01"),
    (23, "Men Winter Jacket",         "Clothing","Men Outerwear",  2499.00,"2023-10-01"),
    (24, "Women Saree Cotton",        "Clothing","Women Ethnic",   1499.00,"2023-01-01"),
    # Clothing NEW LINE (6) - launched March 2025
    (25, "ShopEase Trendy Hoodie",        "Clothing","Men Topwear",    1799.00,"2025-03-01"),
    (26, "ShopEase Women Coord Set",      "Clothing","Women Western",  2299.00,"2025-03-01"),
    (27, "ShopEase Athleisure Joggers",   "Clothing","Men Bottomwear", 1399.00,"2025-03-01"),
    (28, "ShopEase Crop Top Collection",  "Clothing","Women Western",   999.00,"2025-03-01"),
    (29, "ShopEase Oversized Tee",        "Clothing","Men Topwear",    1299.00,"2025-03-01"),
    (30, "ShopEase Ethnic Fusion Dress",  "Clothing","Women Ethnic",   2799.00,"2025-03-01"),
    # Home & Kitchen (10)
    (31, "Prestige Pressure Cooker 5L", "Home & Kitchen","Cookware",  1899.00,"2023-01-01"),
    (32, "Bajaj Mixer Grinder 750W",    "Home & Kitchen","Appliances", 2499.00,"2023-01-01"),
    (33, "Milton Water Bottle Set",     "Home & Kitchen","Storage",     599.00,"2023-01-01"),
    (34, "Spaces Bed Sheet King Size",  "Home & Kitchen","Bedding",    1299.00,"2023-01-01"),
    (35, "Solimo Curtains Pack of 2",   "Home & Kitchen","Decor",       899.00,"2023-03-01"),
    (36, "Pigeon Non Stick Tawa",       "Home & Kitchen","Cookware",    699.00,"2023-01-01"),
    (37, "Cello OpalWare Dinner Set",   "Home & Kitchen","Dining",     1599.00,"2023-05-01"),
    (38, "Godrej Aer Room Freshener",   "Home & Kitchen","Cleaning",    349.00,"2023-01-01"),
    (39, "Amazon Basics Pillow Pack 2", "Home & Kitchen","Bedding",     799.00,"2023-02-01"),
    (40, "Philips LED Bulb Pack 4",     "Home & Kitchen","Lighting",    449.00,"2023-01-01"),
    # Beauty & Personal Care (10)
    (41, "Himalaya Neem Face Wash",       "Beauty & Personal Care","Skincare",   185.00,"2023-01-01"),
    (42, "Lakme 9to5 Primer",            "Beauty & Personal Care","Makeup",      349.00,"2023-01-01"),
    (43, "Dove Body Lotion 250ml",        "Beauty & Personal Care","Skincare",   299.00,"2023-01-01"),
    (44, "Head Shoulders Shampoo 340ml", "Beauty & Personal Care","Haircare",   349.00,"2023-01-01"),
    (45, "Fogg Scent Xpressio Perfume",  "Beauty & Personal Care","Fragrance",  449.00,"2023-01-01"),
    (46, "Mamaearth Vitamin C Serum",    "Beauty & Personal Care","Skincare",   599.00,"2023-06-01"),
    (47, "Biotique Bio Papaya Scrub",    "Beauty & Personal Care","Skincare",   249.00,"2023-01-01"),
    (48, "WOW Skin Science Hair Oil",    "Beauty & Personal Care","Haircare",   399.00,"2023-03-01"),
    (49, "Maybelline Fit Me Foundation", "Beauty & Personal Care","Makeup",     499.00,"2023-01-01"),
    (50, "The Body Shop Tea Tree Oil",   "Beauty & Personal Care","Skincare",   795.00,"2023-08-01"),
]

product_price = {p[0]: p[4] for p in products_data}

# ============================================================
# INSERT PRODUCTS
# ============================================================
w("-- =============================================",
  "-- INSERT: Products",
  "-- =============================================")
for p in products_data:
    w(f"INSERT INTO Products VALUES ({p[0]}, N'{p[1]}', N'{p[2]}', N'{p[3]}', {p[4]}, '{p[5]}');")
w("GO","")

# ============================================================
# GENERATE CUSTOMERS (500)
# ============================================================
w("-- =============================================",
  "-- INSERT: Customers",
  "-- =============================================")

customers  = []

def make_signup_date(cid):
    # Customers 1-400   : signed up during 2023-2024 (core base)
    # Customers 401-450 : signed up Jan-Feb 2025 (pre-launch early adopters)
    # Customers 451-500 : signed up Mar-Jun 2025 (clothing launch surge)
    if cid <= 400:
        start = date(2023, 1, 1)
        end   = date(2024, 12, 31)
    elif cid <= 450:
        start = date(2025, 1, 1)
        end   = date(2025, 2, 28)
    else:
        start = date(2025, 3, 1)
        end   = date(2025, 6, 30)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

for cid in range(1, 501):
    gender = random.choice(['Male','Female'])
    fname  = random.choice(male_names if gender == 'Male' else female_names)
    lname  = random.choice(last_names)
    name   = f"{fname} {lname}"
    city   = random.choice(city_list)
    region = cities_regions[city]
    sdate  = make_signup_date(cid)
    email  = f"{fname.lower()}.{lname.lower()}{cid}@gmail.com"
    customers.append((cid, name, email, city, region, sdate, gender))
    w(f"INSERT INTO Customers VALUES ({cid}, N'{name}', N'{email}', N'{city}', N'{region}', '{sdate}', N'{gender}');")

w("GO","")

# ============================================================
# FIX 1 — Build signup lookup BEFORE orders are generated.
# This dictionary maps every customer_id to their signup_date.
# It is used in order generation to ensure no customer is
# assigned an order dated before their signup_date.
# ============================================================
customer_signup_lookup = {c[0]: c[5] for c in customers}

# ============================================================
# GENERATE ORDERS + ORDER_ITEMS
# ============================================================

monthly_volumes = {
    (2024,1):150,(2024,2):130,(2024,3):160,(2024,4):170,(2024,5):180,
    (2024,6):155,(2024,7):185,(2024,8):190,(2024,9):200,
    (2024,10):285,(2024,11):315,(2024,12):205,
    (2025,1):175,(2025,2):155,
    (2025,3):225,
    (2025,4):215,(2025,5):205,(2025,6):195,
    (2025,7):225,(2025,8):230,(2025,9):220,
    (2025,10):270,(2025,11):290,(2025,12):225
}

def get_cat_weights(year, month):
    if year==2024 and month in [10,11]:
        return [('Electronics',0.40),('Clothing',0.30),('Home & Kitchen',0.20),('Beauty & Personal Care',0.10)]
    elif year==2024:
        return [('Electronics',0.35),('Clothing',0.25),('Home & Kitchen',0.25),('Beauty & Personal Care',0.15)]
    elif year==2025 and month<=2:
        return [('Electronics',0.28),('Clothing',0.30),('Home & Kitchen',0.27),('Beauty & Personal Care',0.15)]
    elif year==2025 and month==3:
        return [('Electronics',0.22),('Clothing',0.45),('Home & Kitchen',0.20),('Beauty & Personal Care',0.13)]
    elif year==2025 and month in [4,5,6]:
        return [('Electronics',0.17),('Clothing',0.48),('Home & Kitchen',0.22),('Beauty & Personal Care',0.13)]
    else:
        return [('Electronics',0.14),('Clothing',0.48),('Home & Kitchen',0.25),('Beauty & Personal Care',0.13)]

def pick_category(year, month):
    weights = get_cat_weights(year, month)
    cats    = [w[0] for w in weights]
    probs   = [w[1] for w in weights]
    return random.choices(cats, weights=probs, k=1)[0]

elec_ids      = [p[0] for p in products_data if p[2]=='Electronics']
cloth_old_ids = [p[0] for p in products_data if p[2]=='Clothing' and p[5] < '2025-01-01']
cloth_new_ids = [p[0] for p in products_data if p[2]=='Clothing' and p[5] >= '2025-01-01']
home_ids      = [p[0] for p in products_data if p[2]=='Home & Kitchen']
beauty_ids    = [p[0] for p in products_data if p[2]=='Beauty & Personal Care']

def pick_product(category, year, month):
    if category == 'Electronics':
        return random.choice(elec_ids)
    elif category == 'Clothing':
        if year == 2025 and month >= 3:
            # FIX 4 — Normalize weights by group size, not per item.
            # Old logic : [0.4]*9 + [0.6]*6 = total 3.6 old vs 3.6 new = 50/50 split (WRONG)
            # Fixed logic: each old product gets weight 0.4/9, each new product gets 0.6/6
            # This ensures old group = 40% total probability, new group = 60% total (CORRECT)
            weights = (
                [0.4 / len(cloth_old_ids)] * len(cloth_old_ids) +
                [0.6 / len(cloth_new_ids)] * len(cloth_new_ids)
            )
            return random.choices(cloth_old_ids + cloth_new_ids, weights=weights, k=1)[0]
        else:
            return random.choice(cloth_old_ids)
    elif category == 'Home & Kitchen':
        return random.choice(home_ids)
    else:
        return random.choice(beauty_ids)

def get_status(year, month):
    if year==2025 and month>=4 and random.random()<0.12:
        return 'Cancelled'
    elif random.random()<0.05:
        return 'Cancelled'
    elif random.random()<0.02:
        return 'Pending'
    else:
        return 'Delivered'

def get_discount(category, year, month):
    if year==2024 and month in [10,11]:
        return round(random.choice([0,0,5,10,15,20,25,30]),2)
    elif year==2025 and month==3 and category=='Clothing':
        return round(random.choice([10,15,20,25,30]),2)
    else:
        return round(random.choice([0,0,0,5,5,10,15,20]),2)

def random_day_in_month(year, month):
    _, days = calendar.monthrange(year, month)
    return date(year, month, random.randint(1, days))

customer_order_count = {cid: 0 for cid in range(1, 501)}

w("-- =============================================",
  "-- INSERT: Orders and Order_Items",
  "-- =============================================")

orders      = []
order_items = []
order_id    = 1
item_id     = 1

for (year, month), count in sorted(monthly_volumes.items()):
    for _ in range(count):

        # FIX 1 — Generate order date FIRST.
        # Then build an eligible customer pool: only customers whose
        # signup_date <= odate. This ensures no order is ever dated
        # before the customer signed up — logical integrity is enforced.
        odate = random_day_in_month(year, month)

        eligible_customers = [
            cid for cid in range(1, 501)
            if customer_signup_lookup[cid] <= odate
        ]

        # Safety guard: if eligible pool is somehow empty, fall back to all customers.
        # In practice this should never happen since customers 1-400
        # sign up from Jan 2023 and orders start Jan 2024.
        if not eligible_customers:
            eligible_customers = list(range(1, 501))

        # Retention story — H2 2025: high volume of first-time / lapsing buyers
        if year == 2025 and month >= 7:
            if random.random() < 0.55:
                # FIX 1 (continued) — low_activity pool also respects signup_date.
                # Previously this list was built from all 500 customers regardless
                # of signup_date — now it is filtered by eligible_customers only.
                low_activity = [
                    c for c in eligible_customers
                    if customer_order_count[c] <= 1
                ]
                if low_activity:
                    cid = random.choice(low_activity)
                else:
                    cid = random.choice(eligible_customers)
            else:
                cid = random.choice(eligible_customers)
        else:
            cid = random.choice(eligible_customers)

        status = get_status(year, month)
        pmeth  = random.choice(payment_methods)
        scity  = random.choice(city_list)

        # FIX 3 — Track which product_ids have already been added to this order.
        # Before: pid was picked independently for each item with no memory,
        # allowing the same product to appear twice in one order.
        # After: used_pids set is maintained per order. If a duplicate pid is
        # picked, we retry up to 10 times. After 10 failed attempts (extremely
        # rare edge case where category has very few products), we allow it
        # so the script never gets stuck in an infinite loop.
        num_items  = random.choices([1,2,3], weights=[0.5,0.35,0.15], k=1)[0]
        total      = 0.0
        these_items = []
        used_pids  = set()  # reset for every new order

        for _ in range(num_items):
            attempts = 0
            while True:
                cat = pick_category(year, month)
                pid = pick_product(cat, year, month)
                if pid not in used_pids or attempts > 10:
                    break
                attempts += 1
            used_pids.add(pid)

            qty      = random.choices([1,2,3,4,5], weights=[0.55,0.25,0.10,0.06,0.04], k=1)[0]
            uprice   = product_price[pid]
            disc     = get_discount(cat, year, month)
            line_tot = round(uprice * qty * (1 - disc/100), 2)
            total   += line_tot
            these_items.append((item_id, order_id, pid, qty, uprice, disc))
            item_id += 1

        total = round(total, 2)
        orders.append((order_id, cid, odate, status, pmeth, scity, total))
        for it in these_items:
            order_items.append(it)

        customer_order_count[cid] += 1
        order_id += 1

# Write orders
for o in orders:
    w(f"INSERT INTO Orders VALUES ({o[0]},{o[1]},'{o[2]}',N'{o[3]}',N'{o[4]}',N'{o[5]}',{o[6]});")
w("GO","")

# Write order_items
for it in order_items:
    w(f"INSERT INTO Order_Items VALUES ({it[0]},{it[1]},{it[2]},{it[3]},{it[4]},{it[5]});")
w("GO","")

# ============================================================
# GENERATE RETURNS (~600)
# ============================================================
w("-- =============================================",
  "-- INSERT: Returns",
  "-- =============================================")

delivered_orders = [o for o in orders if o[3]=='Delivered']

order_to_items = {}
for it in order_items:
    oid = it[1]
    if oid not in order_to_items:
        order_to_items[oid] = []
    order_to_items[oid].append(it)

return_reasons = ['Damaged','Wrong Item','Not as Described','Changed Mind']

def get_return_prob(pid, order_date):
    cat = next(p[2] for p in products_data if p[0]==pid)
    yr  = order_date.year
    mo  = order_date.month
    if cat=='Electronics' and yr==2025 and mo>=4:
        return 0.22
    elif cat=='Electronics':
        return 0.08
    elif cat=='Clothing' and yr==2025 and mo>=3:
        return 0.12
    elif cat=='Clothing':
        return 0.07
    elif cat=='Home & Kitchen':
        return 0.06
    else:
        return 0.04

def get_return_reason(pid, order_date):
    cat = next(p[2] for p in products_data if p[0]==pid)
    yr  = order_date.year
    mo  = order_date.month
    if cat=='Electronics' and yr==2025 and mo>=4:
        return random.choices(
            ['Damaged','Not as Described','Wrong Item','Changed Mind'],
            weights=[0.40,0.35,0.15,0.10], k=1
        )[0]
    elif cat=='Clothing':
        return random.choices(
            ['Changed Mind','Wrong Item','Not as Described','Damaged'],
            weights=[0.40,0.30,0.20,0.10], k=1
        )[0]
    else:
        return random.choices(return_reasons, weights=[0.30,0.25,0.25,0.20], k=1)[0]

return_id   = 1
return_rows = []

random.shuffle(delivered_orders)

for o in delivered_orders:
    oid, cid, odate, status, pmeth, scity, total = o
    items_in_order = order_to_items.get(oid, [])
    for it in items_in_order:
        _, _, pid, qty, uprice, disc = it
        prob = get_return_prob(pid, odate)
        if random.random() < prob:
            days_after = random.randint(1, 20)

            # FIX 2 — Cap return_date to 2025-12-31.
            # Before: odate + up to 20 days could push December orders
            # into January 2026, silently breaking the dataset boundary.
            # After: return_date is capped at the last day of the dataset.
            rdate  = min(odate + timedelta(days=days_after), date(2025, 12, 31))

            reason = get_return_reason(pid, odate)
            refund = round(uprice * qty * (1 - disc/100) * random.uniform(0.85, 1.0), 2)
            return_rows.append((return_id, oid, pid, rdate, reason, refund))
            return_id += 1
            if return_id > 601:
                break
    if return_id > 601:
        break

for r in return_rows:
    w(f"INSERT INTO Returns VALUES ({r[0]},{r[1]},{r[2]},'{r[3]}',N'{r[4]}',{r[5]});")
w("GO","")

# ============================================================
# SUMMARY COMMENT
# ============================================================
w(
"",
"-- =============================================",
"-- ShopEase India database is ready.",
"-- Tables created  : Customers, Products, Orders, Order_Items, Returns",
f"-- Total customers : 500",
f"-- Total products  : 50",
f"-- Total orders    : {len(orders)}",
f"-- Total order items: {len(order_items)}",
f"-- Total returns   : {len(return_rows)}",
"-- Data covers     : January 2024 to December 2025",
"-- =============================================",
"-- DATA QUALITY FIXES APPLIED IN THIS VERSION:",
"-- Fix 1: signup_date vs order_date integrity enforced.",
"--        order_date is generated first; customer is selected",
"--        only from those whose signup_date <= order_date.",
"-- Fix 2: return_date capped at 2025-12-31.",
"--        Prevents December orders bleeding into January 2026.",
"-- Fix 3: Duplicate product per order eliminated.",
"--        used_pids set tracks products already added to each order.",
"-- Fix 4: Clothing new/old weight logic corrected.",
"--        Weights normalized by group size: new line gets true 60% share.",
"-- Note : total_amount is populated for all order statuses by design.",
"--        Always filter WHERE order_status = 'Delivered' for revenue queries.",
"-- =============================================",
""
)

# ============================================================
# WRITE TO FILE
# ============================================================
output = "\n".join(sql)
with open("shopease_insert.sql", "w", encoding="utf-8") as f:
    f.write(output)

print("Done! File created: shopease_insert.sql")
print(f"  Customers  : 500")
print(f"  Products   : 50")
print(f"  Orders     : {len(orders)}")
print(f"  Order Items: {len(order_items)}")
print(f"  Returns    : {len(return_rows)}")
