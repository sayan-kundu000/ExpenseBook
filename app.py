import os
import io
import csv
import calendar
from datetime import datetime, date, timedelta
from collections import defaultdict
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, jsonify, send_file, session
)
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)
from sqlalchemy import func, extract

from config import Config
from models import db, User, Category, Expense, Income, Budget, FinancialGoal
from seed_data import seed_database
from ai.advisor import LocalFinancialAdvisorAI

ROLES_META = [
    {
        'id': 'individual',
        'title': 'Individual User',
        'badge': 'Personal Finance',
        'icon': 'user',
        'color': '#6366f1',
        'email': 'individual@expensebook.com',
        'desc': 'Daily spending tracker, 50/30/20 budget analysis & personal wealth analytics.',
        'highlights': ['Daily Spending Breakdown', '50/30/20 Budget Rule', 'Emergency Fund Goals']
    },
    {
        'id': 'student',
        'title': 'Student',
        'badge': 'Campus & Allowance',
        'icon': 'book-open',
        'color': '#10b981',
        'email': 'student@expensebook.com',
        'desc': 'Pocket money manager, campus allowance tracking & student savings goals.',
        'highlights': ['Allowance & Pocket Money', 'Daily Safe Spend Limit', 'Textbook & Campus Budgets']
    },
    {
        'id': 'freelancer',
        'title': 'Freelancer / Small Business',
        'badge': 'Business & Tax',
        'icon': 'briefcase',
        'color': '#f59e0b',
        'email': 'freelancer@expensebook.com',
        'desc': 'Business expense tracking, client bookkeeping & tax deduction planning.',
        'highlights': ['Tax-Deductible Tracking', 'Client / Project Breakdown', 'Schedule C Tax Ledger']
    },
    {
        'id': 'doom',
        'title': 'Dr. Doom (Victor Von Doom)',
        'badge': 'Monarch of Latveria',
        'icon': 'shield',
        'color': '#10b981',
        'email': 'doom@latveria.gov',
        'desc': 'Sovereign ruler of Latveria. Managing national treasury, Doombot fleet & arcane R&D.',
        'highlights': ['Doombot Army Manufacturing', 'Castle Doom Energy Grid', 'Latverian Sovereign War Vault']
    }
]

def ensure_schema_migrations():
    """Ensures newly added columns in User and Expense exist in SQLite database."""
    try:
        with db.engine.connect() as conn:
            # Users table
            res = conn.execute(db.text("PRAGMA table_info(users)"))
            user_cols = [row[1] for row in res.fetchall()]
            if user_cols:
                if 'role' not in user_cols:
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN role VARCHAR(30) DEFAULT 'individual'"))
                if 'business_name' not in user_cols:
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN business_name VARCHAR(120)"))
                if 'institution' not in user_cols:
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN institution VARCHAR(120)"))
                conn.execute(db.text("UPDATE users SET email = 'individual@expensebook.com' WHERE email = 'demo@expensebook.com' AND NOT EXISTS (SELECT 1 FROM users WHERE email = 'individual@expensebook.com')"))
                conn.execute(db.text("UPDATE users SET username = 'Aarav Sharma' WHERE email IN ('individual@expensebook.com', 'demo@expensebook.com') AND username IN ('Alex Rivers', 'DemoUser')"))
                conn.execute(db.text("UPDATE users SET username = 'Rohan Verma' WHERE email = 'student@expensebook.com' AND username = 'Jordan Lee'"))
                conn.execute(db.text("UPDATE users SET username = 'Kavya Deshmukh', business_name = 'Vayu Creative Labs LLP' WHERE email = 'freelancer@expensebook.com' AND username = 'Morgan Vance'"))
                conn.commit()

            # Expenses table
            res_exp = conn.execute(db.text("PRAGMA table_info(expenses)"))
            exp_cols = [row[1] for row in res_exp.fetchall()]
            if exp_cols:
                if 'is_tax_deductible' not in exp_cols:
                    conn.execute(db.text("ALTER TABLE expenses ADD COLUMN is_tax_deductible BOOLEAN DEFAULT 0"))
                if 'client_or_project' not in exp_cols:
                    conn.execute(db.text("ALTER TABLE expenses ADD COLUMN client_or_project VARCHAR(100)"))
                conn.commit()
    except Exception as e:
        print("Schema migration notice:", e)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Context processor to make global template variables available everywhere
    @app.context_processor
    def inject_global_template_vars():
        return {
            'today': date.today(),
            'all_categories': Category.query.all(),
            'roles_meta': ROLES_META
        }

    # Initialize Local AI Engine
    ai_advisor = LocalFinancialAdvisorAI.get_instance()

    with app.app_context():
        db.create_all()
        ensure_schema_migrations()
        seed_database()

    # -------------------------------------------------------------
    # Authentication Routes (3 Roles: Individual, Student, Freelancer)
    # -------------------------------------------------------------
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            remember = True if request.form.get('remember') else False

            if email in ['individual@expensebook.com', 'demo@expensebook.com']:
                user = User.query.filter((func.lower(User.email) == 'individual@expensebook.com') | (func.lower(User.email) == 'demo@expensebook.com')).first()
            else:
                user = User.query.filter(func.lower(User.email) == email).first()

            if not user or not user.check_password(password):
                flash('Invalid email or password. Please try again.', 'danger')
                return render_template('login.html', email=email, roles_meta=ROLES_META)

            login_user(user, remember=remember)
            flash(f'Welcome back, {user.username}! Logged in as {user.role_title}.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))

        return render_template('login.html', roles_meta=ROLES_META)

    @app.route('/role-login/<role_name>')
    def role_login(role_name):
        """1-Click Instant Login for all distinct roles including Dr. Doom."""
        role_key = role_name.strip().lower()
        if role_key in ['doom', 'drdoom', 'dr_doom', 'victor']:
            user = User.query.filter(
                (User.email == 'doom@latveria.gov') | 
                (User.email == 'doom@expensebook.com') | 
                (User.role == 'doom')
            ).first()
        else:
            target_email = f'{role_key}@expensebook.com'
            user = User.query.filter_by(email=target_email).first()
            if not user:
                user = User.query.filter_by(role=role_key).first()
            if not user and role_key == 'individual':
                user = User.query.filter_by(email='demo@expensebook.com').first()

        if user:
            login_user(user)
            flash(f'Instant Demo Access: Logged in as {user.role_title} ({user.username})!', 'success')
            return redirect(url_for('dashboard'))

        flash(f'Demo account for role "{role_name}" not found. Initializing seed data.', 'warning')
        seed_database()
        if role_key in ['doom', 'drdoom', 'dr_doom', 'victor']:
            user = User.query.filter((User.email == 'doom@latveria.gov') | (User.role == 'doom')).first()
        else:
            user = User.query.filter_by(email=f'{role_key}@expensebook.com').first()
            
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))

        return redirect(url_for('login'))

    @app.route('/switch-role/<role_name>')
    @login_required
    def switch_role(role_name):
        """Quickly toggle between roles from anywhere in the app."""
        role_key = role_name.strip().lower()
        if role_key in ['doom', 'drdoom', 'dr_doom', 'victor']:
            target_user = User.query.filter(
                (User.email == 'doom@latveria.gov') | 
                (User.email == 'doom@expensebook.com') | 
                (User.role == 'doom')
            ).first()
        else:
            target_email = f'{role_key}@expensebook.com'
            target_user = User.query.filter_by(email=target_email).first()
            if not target_user:
                target_user = User.query.filter_by(role=role_key).first()

        if target_user:
            login_user(target_user)
            flash(f'Switched active session to {target_user.role_title} ({target_user.username})!', 'info')
        else:
            flash(f'Unable to switch to role "{role_name}".', 'warning')

        return redirect(request.referrer or url_for('dashboard'))

    @app.route('/demo-login')
    def demo_login():
        return redirect(url_for('role_login', role_name='individual'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            role = request.form.get('role', 'individual').strip().lower()
            business_name = request.form.get('business_name', '').strip() if role == 'freelancer' else None
            institution = request.form.get('institution', '').strip() if role == 'student' else None
            monthly_income = float(request.form.get('monthly_income') or 60000.0)
            currency = request.form.get('currency', '₹')

            if role not in ['individual', 'student', 'freelancer']:
                role = 'individual'

            if len(username) < 3:
                flash('Username must be at least 3 characters long.', 'danger')
                return render_template('register.html', roles_meta=ROLES_META)

            if User.query.filter(func.lower(User.email) == email).first():
                flash('Email already registered. Please log in.', 'warning')
                return redirect(url_for('login'))

            if User.query.filter_by(username=username).first():
                flash('Username already taken. Please choose another.', 'warning')
                return render_template('register.html', roles_meta=ROLES_META)

            new_user = User(
                username=username,
                email=email,
                role=role,
                business_name=business_name,
                institution=institution,
                monthly_income=monthly_income,
                currency=currency
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            # Seed default starter budgets tailored to selected role
            today = date.today()
            cat_map = {c.name: c.id for c in Category.query.all()}
            
            if role == 'student':
                starter_budgets = {
                    'Food & Dining': monthly_income * 0.30,
                    'Books & Academic Supplies': monthly_income * 0.25,
                    'Transportation': monthly_income * 0.10,
                    'Entertainment & Leisure': monthly_income * 0.15,
                    'Investments & Savings': monthly_income * 0.20
                }
            elif role == 'freelancer':
                starter_budgets = {
                    'Software & SaaS': monthly_income * 0.10,
                    'Office & Equipment': monthly_income * 0.15,
                    'Client Meals & Meetings': monthly_income * 0.08,
                    'Transportation': monthly_income * 0.06,
                    'Utilities & Bills': monthly_income * 0.08,
                    'Investments & Savings': monthly_income * 0.30,
                    'Food & Dining': monthly_income * 0.15
                }
            else:
                starter_budgets = {
                    'Housing & Rent': monthly_income * 0.35,
                    'Food & Dining': monthly_income * 0.18,
                    'Transportation': monthly_income * 0.08,
                    'Utilities & Bills': monthly_income * 0.08,
                    'Entertainment & Leisure': monthly_income * 0.06,
                    'Shopping & Personal': monthly_income * 0.05,
                    'Investments & Savings': monthly_income * 0.20
                }

            for cat_name, alloc in starter_budgets.items():
                if cat_name in cat_map:
                    db.session.add(Budget(
                        user_id=new_user.id,
                        category_id=cat_map[cat_name],
                        month=today.month,
                        year=today.year,
                        allocated_amount=round(alloc, 2)
                    ))
            db.session.commit()

            login_user(new_user)
            flash(f'Account created successfully as {new_user.role_title}! Welcome to ExpenseBook.', 'success')
            return redirect(url_for('dashboard'))

        return render_template('register.html', roles_meta=ROLES_META)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out safely.', 'info')
        return redirect(url_for('login'))

    # -------------------------------------------------------------
    # Dashboard Route
    # -------------------------------------------------------------
    @app.route('/')
    @app.route('/dashboard')
    @login_required
    def dashboard():
        today = date.today()
        first_day_of_month = today.replace(day=1)
        
        # Monthly expenses
        monthly_expenses = Expense.query.filter(
            Expense.user_id == current_user.id,
            Expense.expense_date >= first_day_of_month,
            Expense.expense_date <= today
        ).all()
        
        all_user_expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.expense_date.desc()).all()
        recent_expenses = all_user_expenses[:7]
        
        # Budgets for current month
        budgets = Budget.query.filter_by(
            user_id=current_user.id,
            month=today.month,
            year=today.year
        ).all()
        
        total_spent = sum(e.amount for e in monthly_expenses)
        total_budget = sum(b.allocated_amount for b in budgets)
        
        # Incomes
        monthly_incomes = Income.query.filter(
            Income.user_id == current_user.id,
            Income.income_date >= first_day_of_month
        ).all()
        actual_income = sum(i.amount for i in monthly_incomes) or current_user.monthly_income
        net_savings = actual_income - total_spent
        savings_rate = round((net_savings / actual_income * 100), 1) if actual_income > 0 else 0
        
        # AI Financial Health Evaluation via PyTorch Transformers
        ai_health = ai_advisor.calculate_financial_health(actual_income, monthly_expenses, budgets)
        
        # Category breakdown for charts
        cat_spending = defaultdict(float)
        for e in monthly_expenses:
            cat_spending[e.category.name if e.category else 'Other'] += e.amount
            
        # Top 4 category budgets with progress
        budget_progress = []
        for b in budgets:
            cat_name = b.category.name if b.category else 'Other'
            spent = cat_spending.get(cat_name, 0.0)
            pct = min(150.0, round((spent / b.allocated_amount * 100), 1)) if b.allocated_amount > 0 else 0
            status = 'danger' if pct > 100 else ('warning' if pct > 80 else 'success')
            budget_progress.append({
                'category': cat_name,
                'color': b.category.color if b.category else '#6366f1',
                'icon': b.category.icon if b.category else 'tag',
                'allocated': b.allocated_amount,
                'spent': spent,
                'remaining': max(0.0, b.allocated_amount - spent),
                'percentage': pct,
                'status': status
            })
        budget_progress = sorted(budget_progress, key=lambda x: x['spent'], reverse=True)

        categories = Category.query.all()
        goals = FinancialGoal.query.filter_by(user_id=current_user.id, status='active').all()

        # Role-specific computations for the 3 roles from the PDF
        role_stats = {}
        if current_user.is_student:
            month_days = calendar.monthrange(today.year, today.month)[1]
            days_left = max(1, month_days - today.day + 1)
            pocket_money_remaining = max(0.0, actual_income - total_spent)
            safe_daily_spend = round(pocket_money_remaining / days_left, 2)
            burn_rate_pct = min(100.0, round((total_spent / actual_income * 100), 1)) if actual_income > 0 else 0
            month_elapsed_pct = round((today.day / month_days * 100), 1)
            role_stats['student'] = {
                'days_left': days_left,
                'total_days': month_days,
                'pocket_money_remaining': pocket_money_remaining,
                'safe_daily_spend': safe_daily_spend,
                'burn_rate_pct': burn_rate_pct,
                'month_elapsed_pct': month_elapsed_pct,
                'is_overburning': burn_rate_pct > (month_elapsed_pct + 10)
            }
        elif current_user.is_freelancer:
            deductible_monthly = sum(e.amount for e in monthly_expenses if e.is_tax_deductible)
            non_deductible_monthly = sum(e.amount for e in monthly_expenses if not e.is_tax_deductible)
            est_tax_savings_monthly = round(deductible_monthly * 0.25, 2)
            
            client_sums = defaultdict(float)
            for e in monthly_expenses:
                if e.is_tax_deductible and e.client_or_project:
                    client_sums[e.client_or_project] += e.amount
                elif e.is_tax_deductible:
                    client_sums['Studio Overhead'] += e.amount

            role_stats['freelancer'] = {
                'deductible_monthly': deductible_monthly,
                'non_deductible_monthly': non_deductible_monthly,
                'est_tax_savings_monthly': est_tax_savings_monthly,
                'client_breakdown': dict(client_sums),
                'client_count': len(client_sums),
                'business_ratio_pct': round((deductible_monthly / total_spent * 100), 1) if total_spent > 0 else 0
            }

        return render_template(
            'dashboard.html',
            total_spent=total_spent,
            total_budget=total_budget,
            actual_income=actual_income,
            net_savings=net_savings,
            savings_rate=savings_rate,
            ai_health=ai_health,
            recent_expenses=recent_expenses,
            budget_progress=budget_progress[:5],
            categories=categories,
            goals=goals,
            role_stats=role_stats,
            today=today
        )

    # -------------------------------------------------------------
    # Expense CRUD Routes
    # -------------------------------------------------------------
    @app.route('/expenses')
    @login_required
    def expenses_list():
        category_filter = request.args.get('category')
        search_query = request.args.get('q', '').strip()
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        sort_by = request.args.get('sort', 'date_desc')
        tax_filter = request.args.get('tax_deductible')
        client_filter = request.args.get('client', '').strip()

        query = Expense.query.filter_by(user_id=current_user.id)

        if category_filter and category_filter != 'all':
            query = query.join(Category).filter(Category.name == category_filter)

        if search_query:
            query = query.filter(Expense.description.ilike(f'%{search_query}%'))

        if tax_filter == 'yes':
            query = query.filter(Expense.is_tax_deductible == True)
        elif tax_filter == 'no':
            query = query.filter(Expense.is_tax_deductible == False)

        if client_filter:
            query = query.filter(Expense.client_or_project.ilike(f'%{client_filter}%'))

        if start_date:
            try:
                s_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(Expense.expense_date >= s_date)
            except ValueError:
                pass

        if end_date:
            try:
                e_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(Expense.expense_date <= e_date)
            except ValueError:
                pass

        # Sorting
        if sort_by == 'amount_asc':
            query = query.order_by(Expense.amount.asc())
        elif sort_by == 'amount_desc':
            query = query.order_by(Expense.amount.desc())
        elif sort_by == 'date_asc':
            query = query.order_by(Expense.expense_date.asc())
        else:
            query = query.order_by(Expense.expense_date.desc())

        expenses = query.all()
        categories = Category.query.all()
        total_filtered_amount = sum(e.amount for e in expenses)

        return render_template(
            'expenses.html',
            expenses=expenses,
            categories=categories,
            total_filtered_amount=total_filtered_amount,
            category_filter=category_filter,
            search_query=search_query,
            start_date=start_date,
            end_date=end_date,
            sort_by=sort_by,
            tax_filter=tax_filter,
            client_filter=client_filter,
            today=date.today()
        )

    @app.route('/expenses/add', methods=['POST'])
    @login_required
    def add_expense():
        description = request.form.get('description', '').strip()
        amount_raw = request.form.get('amount')
        category_id_raw = request.form.get('category_id')
        expense_date_raw = request.form.get('expense_date')
        is_recurring = True if request.form.get('is_recurring') else False
        recurrence_period = request.form.get('recurrence_period', 'monthly')
        notes = request.form.get('notes', '').strip()
        is_tax_deductible = True if request.form.get('is_tax_deductible') else False
        client_or_project = request.form.get('client_or_project', '').strip()

        if not description or not amount_raw:
            flash('Description and amount are required.', 'danger')
            return redirect(request.referrer or url_for('expenses_list'))

        try:
            amount = float(amount_raw)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            flash('Please enter a valid positive amount.', 'danger')
            return redirect(request.referrer or url_for('expenses_list'))

        try:
            expense_date = datetime.strptime(expense_date_raw, '%Y-%m-%d').date() if expense_date_raw else date.today()
        except ValueError:
            expense_date = date.today()

        # Run AI Transformer Categorization
        ai_pred = ai_advisor.predict_category(description)
        predicted_cat_name = ai_pred['category']
        
        # If user didn't choose category or selected 'auto', use AI prediction
        if not category_id_raw or category_id_raw == 'auto':
            cat_obj = Category.query.filter_by(name=predicted_cat_name).first()
            if not cat_obj:
                cat_obj = Category.query.first()
            category_id = cat_obj.id
        else:
            category_id = int(category_id_raw)

        new_expense = Expense(
            user_id=current_user.id,
            category_id=category_id,
            amount=amount,
            description=description,
            expense_date=expense_date,
            is_recurring=is_recurring,
            recurrence_period=recurrence_period,
            notes=notes,
            ai_predicted_category=predicted_cat_name,
            is_tax_deductible=is_tax_deductible,
            client_or_project=client_or_project
        )
        db.session.add(new_expense)
        db.session.commit()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'expense': new_expense.to_dict(),
                'ai_prediction': ai_pred
            })

        flash(f'Expense of {current_user.currency}{amount:,.2f} added successfully!', 'success')
        return redirect(request.referrer or url_for('expenses_list'))

    @app.route('/expenses/<int:expense_id>/edit', methods=['POST'])
    @login_required
    def edit_expense(expense_id):
        expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
        
        expense.description = request.form.get('description', expense.description).strip()
        try:
            expense.amount = float(request.form.get('amount', expense.amount))
        except ValueError:
            pass
            
        category_id_raw = request.form.get('category_id')
        if category_id_raw:
            expense.category_id = int(category_id_raw)
            
        date_raw = request.form.get('expense_date')
        if date_raw:
            try:
                expense.expense_date = datetime.strptime(date_raw, '%Y-%m-%d').date()
            except ValueError:
                pass
                
        expense.is_recurring = True if request.form.get('is_recurring') else False
        expense.notes = request.form.get('notes', expense.notes).strip()
        expense.is_tax_deductible = True if request.form.get('is_tax_deductible') else False
        expense.client_or_project = request.form.get('client_or_project', '').strip()
        
        db.session.commit()
        flash('Expense updated successfully.', 'success')
        return redirect(request.referrer or url_for('expenses_list'))

    @app.route('/expenses/<int:expense_id>/delete', methods=['POST'])
    @login_required
    def delete_expense(expense_id):
        expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
        db.session.delete(expense)
        db.session.commit()
        flash('Expense deleted.', 'info')
        return redirect(request.referrer or url_for('expenses_list'))

    @app.route('/expenses/export')
    @login_required
    def export_expenses_csv():
        expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.expense_date.desc()).all()
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(['ID', 'Date', 'Description', 'Category', 'Amount', 'Currency', 'Recurring', 'Tax Deductible', 'Client / Project', 'Notes', 'AI Predicted Category'])
        for e in expenses:
            writer.writerow([
                e.id,
                e.expense_date.strftime('%Y-%m-%d'),
                e.description,
                e.category.name if e.category else '',
                f'{e.amount:.2f}',
                current_user.currency,
                'Yes' if e.is_recurring else 'No',
                'Yes' if e.is_tax_deductible else 'No',
                e.client_or_project or '',
                e.notes or '',
                e.ai_predicted_category or ''
            ])
            
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'ExpenseBook_Export_{date.today().strftime("%Y%m%d")}.csv'
        )

    # -------------------------------------------------------------
    # Role-Specific Dedicated Views (PDF Use Cases: Student & Freelancer)
    # -------------------------------------------------------------
    @app.route('/student-hub')
    @login_required
    def student_hub():
        """Dedicated Pocket Money & Allowance Hub for Students (PDF Page 4)."""
        today = date.today()
        first_day_of_month = today.replace(day=1)
        month_days = calendar.monthrange(today.year, today.month)[1]
        days_left = max(1, month_days - today.day + 1)

        monthly_incomes = Income.query.filter(
            Income.user_id == current_user.id,
            Income.income_date >= first_day_of_month
        ).order_by(Income.income_date.desc()).all()
        total_allowance = sum(i.amount for i in monthly_incomes) or current_user.monthly_income

        monthly_expenses = Expense.query.filter(
            Expense.user_id == current_user.id,
            Expense.expense_date >= first_day_of_month,
            Expense.expense_date <= today
        ).order_by(Expense.expense_date.desc()).all()

        total_spent = sum(e.amount for e in monthly_expenses)
        pocket_money_remaining = max(0.0, total_allowance - total_spent)
        safe_daily_spend = round(pocket_money_remaining / days_left, 2)
        burn_rate_pct = min(100.0, round((total_spent / total_allowance * 100), 1)) if total_allowance > 0 else 0
        month_elapsed_pct = round((today.day / month_days * 100), 1)

        goals = FinancialGoal.query.filter_by(user_id=current_user.id).all()
        categories = Category.query.all()

        return render_template(
            'student_hub.html',
            total_allowance=total_allowance,
            total_spent=total_spent,
            pocket_money_remaining=pocket_money_remaining,
            safe_daily_spend=safe_daily_spend,
            days_left=days_left,
            total_days=month_days,
            burn_rate_pct=burn_rate_pct,
            month_elapsed_pct=month_elapsed_pct,
            monthly_expenses=monthly_expenses,
            monthly_incomes=monthly_incomes,
            goals=goals,
            categories=categories,
            today=today
        )

    @app.route('/student/goal-contribute/<int:goal_id>', methods=['POST'])
    @login_required
    def student_goal_contribute(goal_id):
        goal = FinancialGoal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
        try:
            amount = float(request.form.get('amount', 25.0))
            if amount <= 0:
                raise ValueError()
        except ValueError:
            amount = 25.0

        goal.current_amount = round(goal.current_amount + amount, 2)
        if goal.current_amount >= goal.target_amount:
            goal.status = 'completed'
            flash(f'🎉 Congratulations! You reached your student savings goal: "{goal.title}"!', 'success')
        else:
            flash(f'Allocated {current_user.currency}{amount:,.2f} of pocket money into "{goal.title}"! Keep saving!', 'success')
        db.session.commit()
        return redirect(request.referrer or url_for('student_hub'))

    @app.route('/student/add-allowance', methods=['POST'])
    @login_required
    def student_add_allowance():
        source = request.form.get('source', 'Monthly Parent Allowance').strip()
        try:
            amount = float(request.form.get('amount', 0.0))
            if amount <= 0:
                raise ValueError()
        except ValueError:
            flash('Please enter a valid positive allowance amount.', 'danger')
            return redirect(url_for('student_hub'))

        income_date_raw = request.form.get('income_date')
        try:
            income_date = datetime.strptime(income_date_raw, '%Y-%m-%d').date() if income_date_raw else date.today()
        except ValueError:
            income_date = date.today()

        db.session.add(Income(
            user_id=current_user.id,
            source=source,
            amount=amount,
            income_date=income_date,
            is_recurring=False
        ))
        db.session.commit()
        flash(f'Logged allowance inflow of {current_user.currency}{amount:,.2f} ({source})!', 'success')
        return redirect(url_for('student_hub'))

    @app.route('/income/add', methods=['POST'])
    @login_required
    def add_income():
        source = request.form.get('source', 'Income Inflow').strip()
        try:
            amount = float(request.form.get('amount', 0.0))
            if amount <= 0:
                raise ValueError()
        except ValueError:
            flash('Please enter a valid positive income amount.', 'danger')
            return redirect(request.referrer or url_for('dashboard'))

        income_date_raw = request.form.get('income_date')
        try:
            income_date = datetime.strptime(income_date_raw, '%Y-%m-%d').date() if income_date_raw else date.today()
        except ValueError:
            income_date = date.today()

        is_recurring = True if request.form.get('is_recurring') else False

        db.session.add(Income(
            user_id=current_user.id,
            source=source,
            amount=amount,
            income_date=income_date,
            is_recurring=is_recurring
        ))
        db.session.commit()
        flash(f'Logged income inflow of {current_user.currency}{amount:,.2f} ({source})!', 'success')
        return redirect(request.referrer or url_for('dashboard'))

    @app.route('/bookkeeping')
    @login_required
    def bookkeeping():
        """Dedicated Bookkeeping & Tax Deductions Hub for Freelancers / Small Businesses (PDF Page 4)."""
        today = date.today()
        first_day_of_month = today.replace(day=1)
        first_day_of_year = today.replace(month=1, day=1)

        monthly_expenses = Expense.query.filter(
            Expense.user_id == current_user.id,
            Expense.expense_date >= first_day_of_month,
            Expense.expense_date <= today
        ).order_by(Expense.expense_date.desc()).all()

        yearly_expenses = Expense.query.filter(
            Expense.user_id == current_user.id,
            Expense.expense_date >= first_day_of_year,
            Expense.expense_date <= today
        ).all()

        deductible_monthly = sum(e.amount for e in monthly_expenses if e.is_tax_deductible)
        non_deductible_monthly = sum(e.amount for e in monthly_expenses if not e.is_tax_deductible)
        total_monthly = sum(e.amount for e in monthly_expenses)

        deductible_yearly = sum(e.amount for e in yearly_expenses if e.is_tax_deductible)
        est_tax_savings_monthly = round(deductible_monthly * 0.25, 2)
        est_tax_savings_yearly = round(deductible_yearly * 0.25, 2)

        client_breakdown = defaultdict(float)
        cat_deductible = defaultdict(float)
        for e in monthly_expenses:
            if e.is_tax_deductible:
                client_key = e.client_or_project.strip() if e.client_or_project else 'Studio Overhead'
                client_breakdown[client_key] += e.amount
                cat_deductible[e.category.name if e.category else 'General'] += e.amount

        client_incomes = Income.query.filter(
            Income.user_id == current_user.id,
            Income.income_date >= first_day_of_month
        ).order_by(Income.income_date.desc()).all()
        total_revenue = sum(i.amount for i in client_incomes) or current_user.monthly_income
        net_profit = total_revenue - total_monthly

        categories = Category.query.all()

        return render_template(
            'bookkeeping.html',
            monthly_expenses=monthly_expenses,
            deductible_monthly=deductible_monthly,
            non_deductible_monthly=non_deductible_monthly,
            total_monthly=total_monthly,
            deductible_yearly=deductible_yearly,
            est_tax_savings_monthly=est_tax_savings_monthly,
            est_tax_savings_yearly=est_tax_savings_yearly,
            client_breakdown=dict(client_breakdown),
            cat_deductible=dict(cat_deductible),
            client_incomes=client_incomes,
            total_revenue=total_revenue,
            net_profit=net_profit,
            categories=categories,
            today=today
        )

    @app.route('/bookkeeping/export-tax')
    @login_required
    def export_tax_schedule():
        """Exports tax-deductible expenses formatted for Schedule C / Tax filing."""
        expenses = Expense.query.filter_by(
            user_id=current_user.id,
            is_tax_deductible=True
        ).order_by(Expense.expense_date.desc()).all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Tax Year', 'Date', 'Expense Description', 'Tax Category',
            'Amount', 'Currency', 'Client / Project', 'Business Purpose / Notes', 'Est Tax Write-off Savings (25%)'
        ])
        for e in expenses:
            writer.writerow([
                e.expense_date.year,
                e.expense_date.strftime('%Y-%m-%d'),
                e.description,
                e.category.name if e.category else 'Business Expense',
                f'{e.amount:.2f}',
                current_user.currency,
                e.client_or_project or 'Studio Overhead',
                e.notes or 'Ordinary and necessary business expense (Sec 37/44ADA)',
                f'{e.amount * 0.25:.2f}'
            ])

        output.seek(0)
        safe_name = current_user.business_name or current_user.username
        safe_name = "".join(c for c in safe_name if c.isalnum() or c in (' ', '_')).replace(' ', '_')
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'Tax_Deduction_Schedule_{safe_name}_{date.today().strftime("%Y%m%d")}.csv'
        )

    # -------------------------------------------------------------
    # Budgets Routes
    # -------------------------------------------------------------
    @app.route('/budgets', methods=['GET', 'POST'])
    @login_required
    def budgets_page():
        today = date.today()
        month = int(request.args.get('month', today.month))
        year = int(request.args.get('year', today.year))

        if request.method == 'POST':
            category_id = int(request.form.get('category_id'))
            allocated_amount = float(request.form.get('allocated_amount', 0.0))
            
            existing = Budget.query.filter_by(
                user_id=current_user.id,
                category_id=category_id,
                month=month,
                year=year
            ).first()
            
            if existing:
                existing.allocated_amount = allocated_amount
            else:
                db.session.add(Budget(
                    user_id=current_user.id,
                    category_id=category_id,
                    month=month,
                    year=year,
                    allocated_amount=allocated_amount
                ))
            db.session.commit()
            flash('Budget target saved successfully.', 'success')
            return redirect(url_for('budgets_page', month=month, year=year))

        budgets = Budget.query.filter_by(user_id=current_user.id, month=month, year=year).all()
        categories = Category.query.filter_by(category_type='expense').all()
        
        # Calculate spending per category for this month
        month_start = date(year, month, 1)
        next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
        
        monthly_expenses = Expense.query.filter(
            Expense.user_id == current_user.id,
            Expense.expense_date >= month_start,
            Expense.expense_date < next_month
        ).all()
        
        spending_map = defaultdict(float)
        for e in monthly_expenses:
            spending_map[e.category_id] += e.amount

        budget_cards = []
        total_allocated = 0.0
        total_spent = 0.0

        for cat in categories:
            b_obj = next((b for b in budgets if b.category_id == cat.id), None)
            alloc = b_obj.allocated_amount if b_obj else 0.0
            spent = spending_map.get(cat.id, 0.0)
            pct = min(150.0, round((spent / alloc * 100), 1)) if alloc > 0 else 0
            
            total_allocated += alloc
            total_spent += spent
            
            budget_cards.append({
                'category_id': cat.id,
                'category_name': cat.name,
                'icon': cat.icon,
                'color': cat.color,
                'nature': cat.nature,
                'allocated': alloc,
                'spent': spent,
                'remaining': max(0.0, alloc - spent),
                'percentage': pct,
                'has_budget': (b_obj is not None and alloc > 0)
            })

        return render_template(
            'budgets.html',
            budget_cards=budget_cards,
            total_allocated=total_allocated,
            total_spent=total_spent,
            month=month,
            year=year,
            categories=categories,
            today=today
        )

    # -------------------------------------------------------------
    # Analytics Routes
    # -------------------------------------------------------------
    @app.route('/analytics')
    @login_required
    def analytics_page():
        today = date.today()
        user_expenses = Expense.query.filter_by(user_id=current_user.id).all()
        user_budgets = Budget.query.filter_by(user_id=current_user.id, month=today.month, year=today.year).all()
        categories = Category.query.all()
        
        # Run Temporal Transformer Forecast
        forecast_data = ai_advisor.forecast_spending(user_expenses, forecast_days=14)
        anomalies = ai_advisor.detect_anomalies(user_expenses, currency=current_user.currency)
        health_data = ai_advisor.calculate_financial_health(current_user.monthly_income, user_expenses, user_budgets)

        return render_template(
            'analytics.html',
            forecast_data=forecast_data,
            anomalies=anomalies,
            health_data=health_data,
            categories=categories,
            today=today
        )

    # -------------------------------------------------------------
    # AI Financial Advisor Dedicated Hub
    # -------------------------------------------------------------
    @app.route('/advisor')
    @login_required
    def advisor_hub():
        today = date.today()
        user_expenses = Expense.query.filter_by(user_id=current_user.id).all()
        user_budgets = Budget.query.filter_by(user_id=current_user.id, month=today.month, year=today.year).all()
        categories = Category.query.all()
        
        health_data = ai_advisor.calculate_financial_health(current_user.monthly_income, user_expenses, user_budgets)
        forecast_data = ai_advisor.forecast_spending(user_expenses, forecast_days=14)
        anomalies = ai_advisor.detect_anomalies(user_expenses, currency=current_user.currency)

        return render_template(
            'advisor.html',
            health_data=health_data,
            forecast_data=forecast_data,
            anomalies=anomalies,
            categories=categories,
            today=today
        )

    # -------------------------------------------------------------
    # AI REST APIs (100% Local, Zero External APIs)
    # -------------------------------------------------------------
    @app.route('/api/ai/predict-category', methods=['POST'])
    @login_required
    def api_predict_category():
        data = request.get_json() or {}
        description = data.get('description', '')
        result = ai_advisor.predict_category(description)
        return jsonify(result)

    @app.route('/api/ai/chat', methods=['POST'])
    @login_required
    def api_ai_chat():
        data = request.get_json() or {}
        question = data.get('question', '').strip()
        if not question:
            return jsonify({'error': 'Question cannot be empty'}), 400

        today = date.today()
        user_expenses = Expense.query.filter_by(user_id=current_user.id).all()
        user_budgets = Budget.query.filter_by(user_id=current_user.id, month=today.month, year=today.year).all()

        advice = ai_advisor.generate_chat_advice(current_user, question, user_expenses, user_budgets)
        return jsonify(advice)

    @app.route('/api/ai/forecast', methods=['GET'])
    @login_required
    def api_ai_forecast():
        user_expenses = Expense.query.filter_by(user_id=current_user.id).all()
        forecast_data = ai_advisor.forecast_spending(user_expenses, forecast_days=14)
        return jsonify(forecast_data)

    @app.route('/api/analytics/charts', methods=['GET'])
    @login_required
    def api_chart_data():
        today = date.today()
        # Monthly spending trend (past 6 months)
        six_months_ago = today - timedelta(days=180)
        expenses = Expense.query.filter(
            Expense.user_id == current_user.id,
            Expense.expense_date >= six_months_ago
        ).order_by(Expense.expense_date.asc()).all()

        month_totals = defaultdict(float)
        cat_totals = defaultdict(float)
        
        for e in expenses:
            month_key = e.expense_date.strftime('%b %Y')
            month_totals[month_key] += e.amount
            if e.expense_date.month == today.month and e.expense_date.year == today.year:
                cat_name = e.category.name if e.category else 'Other'
                cat_totals[cat_name] += e.amount

        # Categories list for colors
        cat_objs = Category.query.all()
        color_map = {c.name: c.color for c in cat_objs}
        
        pie_labels = list(cat_totals.keys())
        pie_data = [round(cat_totals[k], 2) for k in pie_labels]
        pie_colors = [color_map.get(k, '#6366f1') for k in pie_labels]

        return jsonify({
            'trend': {
                'labels': list(month_totals.keys()),
                'data': [round(v, 2) for v in month_totals.values()]
            },
            'categories': {
                'labels': pie_labels,
                'data': pie_data,
                'colors': pie_colors
            }
        })

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 3000))
    print("=" * 65)
    print("ExpenseBook with AI Financial Advisor & Local PyTorch Transformers")
    print(f"Server starting on http://localhost:{port}")
    print("Demo Login: demo@expensebook.com | password123")
    print("=" * 65)
    app.run(debug=False, host='0.0.0.0', port=port)
