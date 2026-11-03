import random
from datetime import date, datetime, timedelta
from models import db, User, Category, Expense, Income, Budget, FinancialGoal

DEFAULT_CATEGORIES = [
    {'name': 'Food & Dining', 'icon': 'utensils', 'color': '#f59e0b', 'nature': 'want', 'category_type': 'expense'},
    {'name': 'Transportation', 'icon': 'car', 'color': '#3b82f6', 'nature': 'need', 'category_type': 'expense'},
    {'name': 'Housing & Rent', 'icon': 'home', 'color': '#8b5cf6', 'nature': 'need', 'category_type': 'expense'},
    {'name': 'Utilities & Bills', 'icon': 'zap', 'color': '#06b6d4', 'nature': 'need', 'category_type': 'expense'},
    {'name': 'Entertainment & Leisure', 'icon': 'film', 'color': '#ec4899', 'nature': 'want', 'category_type': 'expense'},
    {'name': 'Shopping & Personal', 'icon': 'shopping-bag', 'color': '#10b981', 'nature': 'want', 'category_type': 'expense'},
    {'name': 'Healthcare & Fitness', 'icon': 'activity', 'color': '#ef4444', 'nature': 'need', 'category_type': 'expense'},
    {'name': 'Education & Learning', 'icon': 'book-open', 'color': '#14b8a6', 'nature': 'need', 'category_type': 'expense'},
    {'name': 'Investments & Savings', 'icon': 'trending-up', 'color': '#22c55e', 'nature': 'savings', 'category_type': 'expense'},
    {'name': 'Books & Academic Supplies', 'icon': 'book', 'color': '#6366f1', 'nature': 'need', 'category_type': 'expense'},
    {'name': 'Software & SaaS', 'icon': 'code', 'color': '#8b5cf6', 'nature': 'need', 'category_type': 'expense'},
    {'name': 'Office & Equipment', 'icon': 'monitor', 'color': '#3b82f6', 'nature': 'need', 'category_type': 'expense'},
    {'name': 'Client Meals & Meetings', 'icon': 'coffee', 'color': '#f97316', 'nature': 'want', 'category_type': 'expense'},
    {'name': 'Miscellaneous', 'icon': 'tag', 'color': '#64748b', 'nature': 'want', 'category_type': 'expense'},
]

# Role 1: Individual User Sample Expenses (Personal Finance - India)
INDIVIDUAL_EXPENSES = [
    ("Blinkit & Zepto weekly grocery run", 1850.00, "Food & Dining", 0, False, None),
    ("Dinner at Barbeque Nation with family", 3200.00, "Food & Dining", 1, False, None),
    ("Starbucks roasted cold brew & croissant", 480.00, "Food & Dining", 2, False, None),
    ("BigBasket monthly organic staples", 4200.00, "Food & Dining", 4, False, None),
    ("Swiggy gourmet sushi & ramen delivery", 1250.00, "Food & Dining", 6, False, None),
    ("McDonald's McSpicy meal & fries", 420.00, "Food & Dining", 7, False, None),
    ("D-Mart supermarket bulk household grocery trip", 5400.00, "Food & Dining", 10, False, None),
    ("Chai Point ginger tea & snacks with colleague", 240.00, "Food & Dining", 12, False, None),
    ("Zomato biryani feast takeout", 890.00, "Food & Dining", 15, False, None),
    ("Theobroma bakery brownie & pastry box", 520.00, "Food & Dining", 18, False, None),
    ("Weekend buffet lunch at Mainland China", 2200.00, "Food & Dining", 20, False, None),
    ("Local fresh fruit & vegetable mandi", 650.00, "Food & Dining", 24, False, None),
    
    ("Uber cab ride to Kempegowda airport", 1150.00, "Transportation", 3, False, None),
    ("Indian Oil petrol refill (tank top-up)", 2800.00, "Transportation", 5, False, None),
    ("Monthly Metro Smart Card Recharge", 1200.00, "Transportation", 1, False, None),
    ("HP Auto petrol refill", 1800.00, "Transportation", 14, False, None),
    ("Ola auto ride back from MG Road", 180.00, "Transportation", 16, False, None),
    ("Mall parking & FASTag toll charge", 220.00, "Transportation", 21, False, None),
    
    ("Monthly 2BHK Apartment Rent", 22000.00, "Housing & Rent", 1, False, None),
    
    ("BESCOM / Tata Power electricity bill", 2450.00, "Utilities & Bills", 8, False, None),
    ("Airtel Xstream Fiber 1 Gbps broadband", 1199.00, "Utilities & Bills", 12, False, None),
    ("Jio 5G True Unlimited monthly plan", 749.00, "Utilities & Bills", 15, False, None),
    ("Piped gas & society maintenance", 1650.00, "Utilities & Bills", 22, False, None),
    
    ("Netflix India 4K Premium Plan", 649.00, "Entertainment & Leisure", 5, False, None),
    ("Spotify Premium Family subscription", 179.00, "Entertainment & Leisure", 9, False, None),
    ("PVR INOX IMAX movie tickets & popcorn", 1450.00, "Entertainment & Leisure", 11, False, None),
    ("Steam gaming store weekend pass", 1299.00, "Entertainment & Leisure", 17, False, None),
    
    ("Amazon India electronics & home essentials", 2850.00, "Shopping & Personal", 4, False, None),
    ("Looks Salon haircut & beard grooming", 600.00, "Shopping & Personal", 13, False, None),
    ("Myntra casual cotton shirts & trousers", 3400.00, "Shopping & Personal", 19, False, None),
    
    ("Cult.fit gym & fitness monthly membership", 2200.00, "Healthcare & Fitness", 2, False, None),
    ("Apollo Pharmacy prescription meds & vitamins", 950.00, "Healthcare & Fitness", 18, False, None),
    
    ("Zerodha / Groww Nifty 50 Index Fund SIP", 10000.00, "Investments & Savings", 1, False, None),
    ("HDFC High-Yield Emergency Fixed Deposit", 5000.00, "Investments & Savings", 15, False, None)
]

# Role 2: Student Sample Expenses (Pocket Money, Campus Life, Textbooks, Transit - India)
STUDENT_EXPENSES = [
    ("College Bookstore Engineering & Chemistry Textbook", 1450.00, "Books & Academic Supplies", 2, False, None),
    ("Casio Scientific Calculator fx-991CW", 1150.00, "Books & Academic Supplies", 5, False, None),
    ("Campus Photocopy, Printouts & Spiral Binding", 240.00, "Books & Academic Supplies", 11, False, None),
    ("Semester Exam Previous Year Question Banks", 450.00, "Books & Academic Supplies", 19, False, None),
    
    ("Campus Canteen Thali & Lunch", 120.00, "Food & Dining", 1, False, None),
    ("Nescafe Kiosk Cold Coffee & Maggi", 85.00, "Food & Dining", 3, False, None),
    ("Rolls King Paneer Roll with study group", 220.00, "Food & Dining", 6, False, None),
    ("Hostel Maggi packets & Quick Groceries", 380.00, "Food & Dining", 8, False, None),
    ("Subway 6-inch Sub student combo", 240.00, "Food & Dining", 12, False, None),
    ("Midnight hostel chai & samosa study session", 110.00, "Food & Dining", 16, False, None),
    ("Weekend lunch with college roommates", 650.00, "Food & Dining", 21, False, None),
    
    ("Student Delhi Metro Smart Card recharge", 600.00, "Transportation", 1, False, None),
    ("Uber Auto split fare with classmates", 90.00, "Transportation", 9, False, None),
    ("Campus shuttle bus monthly pass", 250.00, "Transportation", 17, False, None),
    
    ("Spotify Student Premium India", 59.00, "Entertainment & Leisure", 4, False, None),
    ("PVR INOX student ticket movie night", 250.00, "Entertainment & Leisure", 13, False, None),
    ("Weekend hostel pizza slice & cold drink", 280.00, "Entertainment & Leisure", 20, False, None),
    ("Steam indie game during break", 399.00, "Entertainment & Leisure", 25, False, None),
    
    ("Campus Sports Complex & Gym semester locker", 450.00, "Healthcare & Fitness", 2, False, None),
    ("Hostel laundry detergent & toiletry essentials", 420.00, "Shopping & Personal", 14, False, None),
    ("Student Savings: New Laptop Fund Deposit", 1000.00, "Investments & Savings", 10, False, None)
]

# Role 3: Freelancer / Small Business Sample Expenses (Tax Deductible, Clients & Overhead - India)
FREELANCER_EXPENSES = [
    ("Adobe Creative Cloud All Apps Suite", 4230.00, "Software & SaaS", 2, True, "Studio Overhead"),
    ("AWS & Cloud Servers Hosting Infrastructure", 12500.00, "Software & SaaS", 4, True, "Nova FinTech"),
    ("Figma Enterprise Annual Team Seat", 4500.00, "Software & SaaS", 7, True, "Studio Overhead"),
    ("GitHub Pro & Copilot Developer License", 1850.00, "Software & SaaS", 11, True, "Acme Corp"),
    ("Domain Name & SSL Certificates (GoDaddy / Cloudflare)", 2200.00, "Software & SaaS", 18, True, "Nova FinTech"),
    
    ("Ergonomic Office Chair & Standing Desk", 18500.00, "Office & Equipment", 5, True, "Office Setup"),
    ("Studio 4K UltraHD Monitor & Ring Light", 14500.00, "Office & Equipment", 12, True, "Office Setup"),
    ("HP Laser Printer Ink Toner & A4 Paper Reams", 2800.00, "Office & Equipment", 22, True, "Studio Overhead"),
    
    ("Client Strategy Dinner & Project Review at The Taj", 4800.00, "Client Meals & Meetings", 3, True, "Acme Corp"),
    ("Coffee Meeting with Prospective Client at Blue Tokai", 850.00, "Client Meals & Meetings", 9, True, "Vayu Media"),
    ("Lunch Workshop with UI/UX Subcontractor", 1950.00, "Client Meals & Meetings", 16, True, "Nova FinTech"),
    
    ("Uber Premier to Client HQ in Cyber City / BKC", 880.00, "Transportation", 6, True, "Acme Corp"),
    ("Client Corporate Office Parking & FASTag", 350.00, "Transportation", 14, True, "Acme Corp"),
    
    ("Commercial Studio High-Speed Fiber Internet", 2999.00, "Utilities & Bills", 1, True, "Studio Overhead"),
    ("Business Airtel Postpaid Corporate Plan", 1499.00, "Utilities & Bills", 15, True, "Studio Overhead"),
    
    ("Quarterly Advance Tax / GST Reserve Deposit", 35000.00, "Investments & Savings", 1, False, "Tax Buffer"),
    
    # Non-deductible personal expenses (to demonstrate business vs personal ratio)
    ("Blinkit Personal Groceries", 2400.00, "Food & Dining", 8, False, None),
    ("Weekend Personal Movie & Snacks at PVR", 1100.00, "Entertainment & Leisure", 17, False, None)
]

# Role 4: Dr. Doom (Victor Von Doom) — Sovereign Imperial Finances of Latveria
DOOM_EXPENSES = [
    ("Doombot Legion Mk. VII Titanium Alloy & Servos", 145000.0, "Office & Equipment", 2, True, "Latverian Armed Forces"),
    ("Castle Doom Anti-Matter Forcefield & Reactor Core", 88000.0, "Utilities & Bills", 4, True, "Imperial Citadel"),
    ("Baxter Building Sub-Quantum Espionage Sensor Array", 42000.0, "Software & SaaS", 7, True, "Counter-Richards Project"),
    ("Vibranium Synthesizer Dark Matter Crucible Recharge", 65000.0, "Software & SaaS", 9, True, "Arcane Science Lab"),
    ("Latverian Citizen Free Healthcare & Bread Ration Subsidy", 75000.0, "Healthcare & Fitness", 12, False, None),
    ("Dark Arts & Nether-Realm Grimoire Inscriptions", 34000.0, "Books & Academic Supplies", 15, False, None),
    ("Chrono-Platform Tachyon Fuel & Temporal Stabilizer", 92000.0, "Investments & Savings", 18, True, "Time Travel Division"),
    ("Imperial State Banquet & Diplomatic Immunity Feast", 28000.0, "Client Meals & Meetings", 21, True, "UN Diplomatic Corps"),
    ("Hypersonic Jet Fuel for Latverian Royal Transport", 36000.0, "Transportation", 23, True, "Imperial Flight Command"),
    ("Castle Doom Solar Energy Grid & Micro-Reactor Overhaul", 54000.0, "Utilities & Bills", 26, True, "State Energy Grid")
]

def seed_database(force_reseed=False):
    """Initializes categories and 3 distinct persona users based on the PDF requirements with Indian Rupee (INR / ₹) data."""
    # 1. Categories
    existing_cats = {c.name: c for c in Category.query.all()}
    cat_objs = {}
    for cat_data in DEFAULT_CATEGORIES:
        if cat_data['name'] not in existing_cats:
            cat = Category(**cat_data)
            db.session.add(cat)
            cat_objs[cat_data['name']] = cat
        else:
            cat_objs[cat_data['name']] = existing_cats[cat_data['name']]
    db.session.commit()

    today = date.today()
    current_month = today.month
    current_year = today.year

    # -------------------------------------------------------------------------
    # 1. Role: Individual User (Aarav Sharma)
    # -------------------------------------------------------------------------
    individual_user = User.query.filter((User.email == 'individual@expensebook.com') | (User.email == 'demo@expensebook.com')).first()
    if force_reseed and individual_user:
        Expense.query.filter_by(user_id=individual_user.id).delete()
        Income.query.filter_by(user_id=individual_user.id).delete()
        Budget.query.filter_by(user_id=individual_user.id).delete()
        FinancialGoal.query.filter_by(user_id=individual_user.id).delete()
        db.session.delete(individual_user)
        db.session.commit()
        individual_user = None

    if not individual_user:
        individual_user = User(
            username='Aarav Sharma',
            email='individual@expensebook.com',
            role='individual',
            currency='₹',
            monthly_income=75000.0
        )
        individual_user.set_password('password123')
        db.session.add(individual_user)
        db.session.commit()

        # Incomes
        db.session.add(Income(
            user_id=individual_user.id,
            source='Tech Corp Software Engineering Salary',
            amount=65000.0,
            income_date=today.replace(day=1),
            is_recurring=True,
            recurrence_period='monthly'
        ))
        db.session.add(Income(
            user_id=individual_user.id,
            source='Freelance Web Consulting',
            amount=10000.0,
            income_date=today.replace(day=12),
            is_recurring=False
        ))

        # Monthly Budgets
        ind_budgets = {
            'Housing & Rent': 22000.0,
            'Food & Dining': 12000.0,
            'Transportation': 5000.0,
            'Utilities & Bills': 4500.0,
            'Entertainment & Leisure': 4000.0,
            'Shopping & Personal': 5000.0,
            'Healthcare & Fitness': 3000.0,
            'Investments & Savings': 15000.0
        }
        for cat_name, alloc in ind_budgets.items():
            if cat_name in cat_objs:
                db.session.add(Budget(
                    user_id=individual_user.id,
                    category_id=cat_objs[cat_name].id,
                    month=current_month,
                    year=current_year,
                    allocated_amount=alloc
                ))

        # Expenses
        for desc, amount, cat_name, day_offset, is_deduct, client in INDIVIDUAL_EXPENSES:
            exp_date = today - timedelta(days=day_offset)
            cat = cat_objs.get(cat_name)
            if cat:
                db.session.add(Expense(
                    user_id=individual_user.id,
                    category_id=cat.id,
                    amount=amount,
                    description=desc,
                    expense_date=exp_date,
                    ai_predicted_category=cat_name,
                    is_tax_deductible=is_deduct,
                    client_or_project=client
                ))

        # Financial Goals
        db.session.add(FinancialGoal(
            user_id=individual_user.id,
            title='3-Month Emergency Safety Buffer',
            target_amount=200000.0,
            current_amount=135000.0,
            target_date=today + timedelta(days=120),
            category='Emergency Fund'
        ))
        db.session.add(FinancialGoal(
            user_id=individual_user.id,
            title='Goa & Western Ghats Holiday',
            target_amount=45000.0,
            current_amount=28000.0,
            target_date=today + timedelta(days=90),
            category='Travel'
        ))
        db.session.commit()
    else:
        if individual_user.username in ['Alex Rivers', 'DemoUser']:
            individual_user.username = 'Aarav Sharma'
        individual_user.currency = '₹'
        db.session.commit()

    # -------------------------------------------------------------------------
    # 2. Role: Student (Rohan Verma)
    # -------------------------------------------------------------------------
    student_user = User.query.filter_by(email='student@expensebook.com').first()
    if force_reseed and student_user:
        Expense.query.filter_by(user_id=student_user.id).delete()
        Income.query.filter_by(user_id=student_user.id).delete()
        Budget.query.filter_by(user_id=student_user.id).delete()
        FinancialGoal.query.filter_by(user_id=student_user.id).delete()
        db.session.delete(student_user)
        db.session.commit()
        student_user = None

    if not student_user:
        student_user = User(
            username='Rohan Verma',
            email='student@expensebook.com',
            role='student',
            institution='Delhi Technological University (DTU)',
            currency='₹',
            monthly_income=15000.0  # Pocket money & allowance
        )
        student_user.set_password('password123')
        db.session.add(student_user)
        db.session.commit()

        # Incomes (Allowance + Tutoring)
        db.session.add(Income(
            user_id=student_user.id,
            source='Parent Monthly Allowance / Pocket Money',
            amount=12000.0,
            income_date=today.replace(day=1),
            is_recurring=True,
            recurrence_period='monthly'
        ))
        db.session.add(Income(
            user_id=student_user.id,
            source='Campus Math Peer Tutoring Stipend',
            amount=3000.0,
            income_date=today.replace(day=15),
            is_recurring=False
        ))

        # Student Budgets
        student_budgets = {
            'Food & Dining': 5500.0,
            'Books & Academic Supplies': 3000.0,
            'Transportation': 1500.0,
            'Entertainment & Leisure': 2000.0,
            'Shopping & Personal': 1500.0,
            'Investments & Savings': 1500.0
        }
        for cat_name, alloc in student_budgets.items():
            if cat_name in cat_objs:
                db.session.add(Budget(
                    user_id=student_user.id,
                    category_id=cat_objs[cat_name].id,
                    month=current_month,
                    year=current_year,
                    allocated_amount=alloc
                ))

        # Student Expenses
        for desc, amount, cat_name, day_offset, is_deduct, client in STUDENT_EXPENSES:
            exp_date = today - timedelta(days=day_offset)
            cat = cat_objs.get(cat_name)
            if cat:
                db.session.add(Expense(
                    user_id=student_user.id,
                    category_id=cat.id,
                    amount=amount,
                    description=desc,
                    expense_date=exp_date,
                    ai_predicted_category=cat_name,
                    is_tax_deductible=is_deduct,
                    client_or_project=client
                ))

        # Student Specific Goals
        db.session.add(FinancialGoal(
            user_id=student_user.id,
            title='New Apple MacBook Air M3 for College',
            target_amount=85000.0,
            current_amount=42000.0,
            target_date=today + timedelta(days=60),
            category='Tech & Study'
        ))
        db.session.add(FinancialGoal(
            user_id=student_user.id,
            title='Next Semester Textbooks & Lab Kits',
            target_amount=6000.0,
            current_amount=3800.0,
            target_date=today + timedelta(days=90),
            category='Books'
        ))
        db.session.add(FinancialGoal(
            user_id=student_user.id,
            title='Goa College Road Trip with Friends',
            target_amount=10000.0,
            current_amount=5500.0,
            target_date=today + timedelta(days=110),
            category='Leisure'
        ))
        db.session.commit()
    else:
        if student_user.username == 'Jordan Lee':
            student_user.username = 'Rohan Verma'
        student_user.currency = '₹'
        db.session.commit()

    # -------------------------------------------------------------------------
    # 3. Role: Freelancer / Small Business (Kavya Deshmukh)
    # -------------------------------------------------------------------------
    freelancer_user = User.query.filter_by(email='freelancer@expensebook.com').first()
    if force_reseed and freelancer_user:
        Expense.query.filter_by(user_id=freelancer_user.id).delete()
        Income.query.filter_by(user_id=freelancer_user.id).delete()
        Budget.query.filter_by(user_id=freelancer_user.id).delete()
        FinancialGoal.query.filter_by(user_id=freelancer_user.id).delete()
        db.session.delete(freelancer_user)
        db.session.commit()
        freelancer_user = None

    if not freelancer_user:
        freelancer_user = User(
            username='Kavya Deshmukh',
            email='freelancer@expensebook.com',
            role='freelancer',
            business_name='Vayu Creative Labs LLP',
            currency='₹',
            monthly_income=175000.0  # Business monthly revenue
        )
        freelancer_user.set_password('password123')
        db.session.add(freelancer_user)
        db.session.commit()

        # Incomes (Client project retainers)
        db.session.add(Income(
            user_id=freelancer_user.id,
            source='Acme Corp — Full-Stack Web Retainer',
            amount=110000.0,
            income_date=today.replace(day=1),
            is_recurring=True,
            recurrence_period='monthly'
        ))
        db.session.add(Income(
            user_id=freelancer_user.id,
            source='Nova FinTech — UI/UX Consulting Contract',
            amount=65000.0,
            income_date=today.replace(day=10),
            is_recurring=True,
            recurrence_period='monthly'
        ))

        # Freelancer Budgets
        freelance_budgets = {
            'Software & SaaS': 15000.0,
            'Office & Equipment': 25000.0,
            'Client Meals & Meetings': 8000.0,
            'Transportation': 6000.0,
            'Utilities & Bills': 6000.0,
            'Investments & Savings': 45000.0,
            'Food & Dining': 12000.0
        }
        for cat_name, alloc in freelance_budgets.items():
            if cat_name in cat_objs:
                db.session.add(Budget(
                    user_id=freelancer_user.id,
                    category_id=cat_objs[cat_name].id,
                    month=current_month,
                    year=current_year,
                    allocated_amount=alloc
                ))

        # Freelancer Expenses
        for desc, amount, cat_name, day_offset, is_deduct, client in FREELANCER_EXPENSES:
            exp_date = today - timedelta(days=day_offset)
            cat = cat_objs.get(cat_name)
            if cat:
                db.session.add(Expense(
                    user_id=freelancer_user.id,
                    category_id=cat.id,
                    amount=amount,
                    description=desc,
                    expense_date=exp_date,
                    ai_predicted_category=cat_name,
                    is_tax_deductible=is_deduct,
                    client_or_project=client
                ))

        # Freelancer Specific Goals
        db.session.add(FinancialGoal(
            user_id=freelancer_user.id,
            title='Advance Tax / Section 44ADA Reserve (25%)',
            target_amount=85000.0,
            current_amount=62000.0,
            target_date=today + timedelta(days=45),
            category='Tax Reserve'
        ))
        db.session.add(FinancialGoal(
            user_id=freelancer_user.id,
            title='Studio M4 Max Workstation Upgrade',
            target_amount=220000.0,
            current_amount=145000.0,
            target_date=today + timedelta(days=90),
            category='Equipment'
        ))
        db.session.commit()
    else:
        if freelancer_user.username == 'Morgan Vance':
            freelancer_user.username = 'Kavya Deshmukh'
            freelancer_user.business_name = 'Vayu Creative Labs LLP'
        freelancer_user.currency = '₹'
        db.session.commit()

    # -------------------------------------------------------------------------
    # 4. Role: Dr. Doom (Victor Von Doom) — Sovereign Imperial Finances of Latveria
    # -------------------------------------------------------------------------
    doom_user = User.query.filter((User.email == 'doom@latveria.gov') | (User.email == 'doom@expensebook.com')).first()
    if force_reseed and doom_user:
        Expense.query.filter_by(user_id=doom_user.id).delete()
        Income.query.filter_by(user_id=doom_user.id).delete()
        Budget.query.filter_by(user_id=doom_user.id).delete()
        FinancialGoal.query.filter_by(user_id=doom_user.id).delete()
        db.session.delete(doom_user)
        db.session.commit()
        doom_user = None

    if not doom_user:
        doom_user = User(
            username='Victor Von Doom (Dr. Doom)',
            email='doom@latveria.gov',
            role='doom',
            business_name='Latverian Imperial State Treasury',
            currency='₹',
            monthly_income=1200000.0  # Imperial Treasury Monthly Inflow
        )
        doom_user.set_password('password123')
        db.session.add(doom_user)
        db.session.commit()

        # Incomes
        db.session.add(Income(
            user_id=doom_user.id,
            source='Latverian Sovereign Mineral Extraction & State Patents',
            amount=950000.0,
            income_date=today.replace(day=1),
            is_recurring=True,
            recurrence_period='monthly'
        ))
        db.session.add(Income(
            user_id=doom_user.id,
            source='Stark & Baxter International Patent Infringement Settlement',
            amount=250000.0,
            income_date=today.replace(day=10),
            is_recurring=False
        ))

        # Monthly Budgets
        doom_budgets = {
            'Office & Equipment': 250000.0,      # Doombot Manufacturing & Hardware
            'Software & SaaS': 150000.0,         # AI & Espionage Sub-systems
            'Utilities & Bills': 160000.0,       # Castle Doom Reactor & Shield Grid
            'Investments & Savings': 300000.0,   # Sovereign War Vault Accumulation
            'Healthcare & Fitness': 100000.0,    # Citizen Welfare & Armor Biometrics
            'Transportation': 80000.0,           # Latverian Royal Hypersonic Fleet
            'Books & Academic Supplies': 60000.0,# Arcane Grimoires & Dark Arts
            'Client Meals & Meetings': 50000.0   # Diplomatic Immunity Banquets
        }
        for cat_name, alloc in doom_budgets.items():
            if cat_name in cat_objs:
                db.session.add(Budget(
                    user_id=doom_user.id,
                    category_id=cat_objs[cat_name].id,
                    month=current_month,
                    year=current_year,
                    allocated_amount=alloc
                ))

        # Expenses
        for desc, amount, cat_name, day_offset, is_deduct, client in DOOM_EXPENSES:
            exp_date = today - timedelta(days=day_offset)
            cat = cat_objs.get(cat_name)
            if cat:
                db.session.add(Expense(
                    user_id=doom_user.id,
                    category_id=cat.id,
                    amount=amount,
                    description=desc,
                    expense_date=exp_date,
                    ai_predicted_category=cat_name,
                    is_tax_deductible=is_deduct,
                    client_or_project=client
                ))

        # Goals
        db.session.add(FinancialGoal(
            user_id=doom_user.id,
            title='Orbital Planetary Defense Shield Network',
            target_amount=5000000.0,
            current_amount=3200000.0,
            target_date=today + timedelta(days=180),
            category='Imperial Defense'
        ))
        db.session.add(FinancialGoal(
            user_id=doom_user.id,
            title='Sovereign War Chest against Richards / Avengers Incursions',
            target_amount=10000000.0,
            current_amount=7800000.0,
            target_date=today + timedelta(days=365),
            category='War Vault'
        ))
        db.session.commit()
    else:
        doom_user.currency = '₹'
        db.session.commit()

    print("Successfully seeded Roles (Indian Rupee INR):")
    print(" 1) Individual: individual@expensebook.com / password123")
    print(" 2) Student: student@expensebook.com / password123")
    print(" 3) Freelancer: freelancer@expensebook.com / password123")
    print(" 4) Dr. Doom: doom@latveria.gov / password123 (or doom@expensebook.com)")
