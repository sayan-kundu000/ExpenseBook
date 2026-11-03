from datetime import datetime, date, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

def utc_now():
    return datetime.now(timezone.utc)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(30), default='individual', nullable=False)  # 'individual', 'student', 'freelancer'
    business_name = db.Column(db.String(120), nullable=True)  # For Freelancers & Small Businesses
    institution = db.Column(db.String(120), nullable=True)    # For Students (College/University)
    currency = db.Column(db.String(10), default='₹')
    monthly_income = db.Column(db.Float, default=60000.0)
    created_at = db.Column(db.DateTime, default=utc_now)

    # Relationships
    expenses = db.relationship('Expense', backref='user', lazy=True, cascade='all, delete-orphan')
    incomes = db.relationship('Income', backref='user', lazy=True, cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='user', lazy=True, cascade='all, delete-orphan')
    goals = db.relationship('FinancialGoal', backref='user', lazy=True, cascade='all, delete-orphan')

    @property
    def is_student(self):
        return self.role == 'student'

    @property
    def is_freelancer(self):
        return self.role == 'freelancer'

    @property
    def is_individual(self):
        return self.role == 'individual'

    @property
    def is_doom(self):
        return self.role == 'doom' or 'doom' in self.username.lower()

    @property
    def role_title(self):
        titles = {
            'individual': 'Individual User',
            'student': 'Student',
            'freelancer': 'Freelancer / Small Business',
            'doom': 'Sovereign Monarch of Latveria'
        }
        if 'doom' in self.username.lower():
            return 'Sovereign Monarch of Latveria'
        return titles.get(self.role, 'Individual User')

    @property
    def role_badge_icon(self):
        icons = {
            'individual': 'user',
            'student': 'book-open',
            'freelancer': 'briefcase',
            'doom': 'shield'
        }
        if 'doom' in self.username.lower():
            return 'shield'
        return icons.get(self.role, 'user')

    @property
    def role_color(self):
        colors = {
            'individual': '#6366f1',
            'student': '#10b981',
            'freelancer': '#f59e0b',
            'doom': '#10b981'
        }
        if 'doom' in self.username.lower():
            return '#10b981'
        return colors.get(self.role, '#6366f1')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'role_title': self.role_title,
            'business_name': self.business_name,
            'institution': self.institution,
            'currency': self.currency,
            'monthly_income': self.monthly_income
        }


class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    category_type = db.Column(db.String(20), default='expense')  # expense or income
    icon = db.Column(db.String(50), default='tag')  # Lucide/feather icon name
    color = db.Column(db.String(20), default='#6366f1')
    nature = db.Column(db.String(20), default='want')  # 'need', 'want', 'savings' for 50/30/20 analysis

    expenses = db.relationship('Expense', backref='category', lazy=True)
    budgets = db.relationship('Budget', backref='category', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category_type': self.category_type,
            'icon': self.icon,
            'color': self.color,
            'nature': self.nature
        }


class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    expense_date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_period = db.Column(db.String(20), default='monthly')  # daily, weekly, monthly, yearly
    notes = db.Column(db.Text, nullable=True)
    ai_predicted_category = db.Column(db.String(50), nullable=True)
    is_tax_deductible = db.Column(db.Boolean, default=False)  # For Freelancer & Small Business Bookkeeping
    client_or_project = db.Column(db.String(100), nullable=True)  # Client or Project tag
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else 'Unknown',
            'category_color': self.category.color if self.category else '#6366f1',
            'category_icon': self.category.icon if self.category else 'tag',
            'amount': self.amount,
            'description': self.description,
            'expense_date': self.expense_date.strftime('%Y-%m-%d'),
            'is_recurring': self.is_recurring,
            'recurrence_period': self.recurrence_period,
            'notes': self.notes or '',
            'ai_predicted_category': self.ai_predicted_category or '',
            'is_tax_deductible': self.is_tax_deductible,
            'client_or_project': self.client_or_project or ''
        }


class Income(db.Model):
    __tablename__ = 'incomes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    source = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    income_date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_period = db.Column(db.String(20), default='monthly')
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'source': self.source,
            'amount': self.amount,
            'income_date': self.income_date.strftime('%Y-%m-%d'),
            'is_recurring': self.is_recurring,
            'recurrence_period': self.recurrence_period
        }


class Budget(db.Model):
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1 - 12
    year = db.Column(db.Integer, nullable=False)   # e.g. 2026
    allocated_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'category_id', 'month', 'year', name='uq_user_cat_month_year'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else 'Unknown',
            'month': self.month,
            'year': self.year,
            'allocated_amount': self.allocated_amount
        }


class FinancialGoal(db.Model):
    __tablename__ = 'financial_goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    target_date = db.Column(db.Date, nullable=True)
    category = db.Column(db.String(50), default='Emergency Fund')
    status = db.Column(db.String(20), default='active')  # active, completed, paused

    def to_dict(self):
        progress = (self.current_amount / self.target_amount * 100) if self.target_amount > 0 else 0
        return {
            'id': self.id,
            'title': self.title,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'target_date': self.target_date.strftime('%Y-%m-%d') if self.target_date else None,
            'category': self.category,
            'status': self.status,
            'progress_percentage': min(100.0, round(progress, 1))
        }
