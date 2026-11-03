import os
import unittest
import json
import torch

from app import create_app
from config import Config
from models import db, User, Category, Expense, Budget, FinancialGoal
from ai.advisor import LocalFinancialAdvisorAI
from ai.transformer_models import (
    TransformerTextClassifier,
    TemporalExpenseTransformer,
    FinAdvisorAttentionModel
)

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ExpenseBookTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_authentication_and_password_hashing(self):
        user = User(username='tester', email='test@test.com', role='individual')
        user.set_password('mysecretpass')
        self.assertTrue(user.check_password('mysecretpass'))
        self.assertFalse(user.check_password('wrongpass'))
        self.assertTrue(user.is_individual)
        self.assertFalse(user.is_student)
        self.assertFalse(user.is_freelancer)

    def test_three_role_instant_logins(self):
        """Tests 1-click instant login for all 3 distinct roles from PDF Page 4."""
        # 1. Individual User
        res_ind = self.client.get('/role-login/individual', follow_redirects=True)
        self.assertEqual(res_ind.status_code, 200)
        self.assertIn(b'Aarav Sharma', res_ind.data)
        self.assertIn(b'Individual User', res_ind.data)

        # 2. Student Role
        res_stu = self.client.get('/role-login/student', follow_redirects=True)
        self.assertEqual(res_stu.status_code, 200)
        self.assertIn(b'Rohan Verma', res_stu.data)
        self.assertIn(b'Student', res_stu.data)
        self.assertIn(b'Pocket Money', res_stu.data)

        # 3. Freelancer Role
        res_fre = self.client.get('/role-login/freelancer', follow_redirects=True)
        self.assertEqual(res_fre.status_code, 200)
        self.assertIn(b'Kavya Deshmukh', res_fre.data)
        self.assertIn(b'Freelancer', res_fre.data)
        self.assertIn(b'Tax Deductible', res_fre.data)

        # 4. Dr. Doom Monarch Role
        res_doom = self.client.get('/role-login/doom', follow_redirects=True)
        self.assertEqual(res_doom.status_code, 200)
        self.assertIn(b'Victor Von Doom', res_doom.data)

    def test_role_switching_in_active_session(self):
        """Tests instant switching between the 3 roles."""
        self.client.get('/role-login/individual')
        # Switch to student
        res_switch = self.client.get('/switch-role/student', follow_redirects=True)
        self.assertEqual(res_switch.status_code, 200)
        self.assertIn(b'Rohan Verma', res_switch.data)
        
        # Switch to freelancer
        res_switch2 = self.client.get('/switch-role/freelancer', follow_redirects=True)
        self.assertEqual(res_switch2.status_code, 200)
        self.assertIn(b'Kavya Deshmukh', res_switch2.data)

    def test_user_registration_with_role_selection(self):
        """Tests creating custom accounts with Student and Freelancer roles."""
        # Register Student
        res_stu = self.client.post('/register', data={
            'username': 'Ananya Sen',
            'email': 'ananya@dtu.ac.in',
            'password': 'password123',
            'role': 'student',
            'institution': 'Delhi Technological University (DTU)',
            'monthly_income': '12000',
            'currency': '₹'
        }, follow_redirects=True)
        self.assertEqual(res_stu.status_code, 200)
        u_stu = User.query.filter_by(email='ananya@dtu.ac.in').first()
        self.assertIsNotNone(u_stu)
        self.assertEqual(u_stu.role, 'student')
        self.assertEqual(u_stu.institution, 'Delhi Technological University (DTU)')

        # Register Freelancer
        self.client.get('/logout')
        res_fre = self.client.post('/register', data={
            'username': 'Pooja Patel',
            'email': 'pooja@designstudio.in',
            'password': 'password123',
            'role': 'freelancer',
            'business_name': 'Pooja Design Labs LLP',
            'monthly_income': '65000',
            'currency': '₹'
        }, follow_redirects=True)
        self.assertEqual(res_fre.status_code, 200)
        u_fre = User.query.filter_by(email='pooja@designstudio.in').first()
        self.assertIsNotNone(u_fre)
        self.assertEqual(u_fre.role, 'freelancer')
        self.assertEqual(u_fre.business_name, 'Pooja Design Labs LLP')

    def test_student_hub_and_pocket_money_actions(self):
        """Tests the dedicated Student Pocket Money & Allowance Hub."""
        self.client.get('/role-login/student')
        res = self.client.get('/student-hub')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Pocket Money Hub', res.data)
        self.assertIn(b'Safe Daily Allowance', res.data)

        # Contribute to goal
        student_user = User.query.filter_by(email='student@expensebook.com').first()
        goal = FinancialGoal.query.filter_by(user_id=student_user.id).first()
        initial_amount = goal.current_amount
        res_contribute = self.client.post(f'/student/goal-contribute/{goal.id}', data={'amount': '25'}, follow_redirects=True)
        self.assertEqual(res_contribute.status_code, 200)
        db.session.refresh(goal)
        self.assertEqual(goal.current_amount, initial_amount + 25.0)

    def test_freelancer_bookkeeping_and_tax_export(self):
        """Tests the dedicated Freelancer Bookkeeping & Tax Deductions Hub."""
        self.client.get('/role-login/freelancer')
        res = self.client.get('/bookkeeping')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'IRS Schedule C Ready', res.data)
        self.assertIn(b'Est. Tax Savings (25%)', res.data)
        self.assertIn(b'Expenses by Client or Project', res.data)

        # Tax schedule export
        res_export = self.client.get('/bookkeeping/export-tax')
        self.assertEqual(res_export.status_code, 200)
        self.assertIn('text/csv', res_export.headers['Content-Type'])
        self.assertIn(b'Tax Year', res_export.data)
        self.assertIn(b'Est Tax Write-off Savings', res_export.data)

    def test_expense_tax_deductible_and_client_tagging(self):
        """Tests creating and editing expenses with tax-deductible flags and client tags."""
        self.client.get('/role-login/freelancer')
        res_add = self.client.post('/expenses/add', data={
            'description': 'Client UX Workshop Retainer Lunch',
            'amount': '125.50',
            'category_id': 'auto',
            'expense_date': '2026-10-20',
            'is_tax_deductible': '1',
            'client_or_project': 'Acme Corp',
            'notes': 'Quarterly strategy lunch'
        }, follow_redirects=True)
        self.assertEqual(res_add.status_code, 200)
        
        freelancer = User.query.filter_by(email='freelancer@expensebook.com').first()
        exp = Expense.query.filter_by(user_id=freelancer.id, description='Client UX Workshop Retainer Lunch').first()
        self.assertIsNotNone(exp)
        self.assertTrue(exp.is_tax_deductible)
        self.assertEqual(exp.client_or_project, 'Acme Corp')

        # Test editing the expense's tax-deductible status and client project
        res_edit = self.client.post(f'/expenses/{exp.id}/edit', data={
            'description': 'Client UX Workshop Retainer Lunch - Updated',
            'amount': '150.00',
            'category_id': str(exp.category_id),
            'expense_date': '2026-10-21',
            'is_tax_deductible': '1',
            'client_or_project': 'Acme Global Corp',
            'notes': 'Quarterly strategy lunch - revised'
        }, follow_redirects=True)
        self.assertEqual(res_edit.status_code, 200)
        db.session.refresh(exp)
        self.assertEqual(exp.amount, 150.00)
        self.assertEqual(exp.client_or_project, 'Acme Global Corp')

    def test_transformer_text_classifier_forward(self):
        model = TransformerTextClassifier(vocab_size=150, num_categories=10, num_intents=8)
        dummy_input = torch.tensor([[2, 10, 25, 4, 3, 0, 0, 0]], dtype=torch.long)
        out = model(dummy_input)
        self.assertIn('category_logits', out)
        self.assertIn('intent_logits', out)
        self.assertIn('attention_weights', out)
        self.assertEqual(out['category_logits'].shape, (1, 10))
        self.assertEqual(out['intent_logits'].shape, (1, 8))
        self.assertEqual(out['attention_weights'].shape, (1, 8, 8))

    def test_temporal_expense_transformer_forward(self):
        model = TemporalExpenseTransformer(input_dim=5, d_model=64, forecast_steps=14)
        dummy_seq = torch.randn(1, 30, 5)
        out = model(dummy_seq)
        self.assertIn('forecast', out)
        self.assertIn('anomaly_score', out)
        self.assertEqual(out['forecast'].shape, (1, 14))

    def test_vitals_attention_model_forward(self):
        model = FinAdvisorAttentionModel(num_vitals=8, d_model=32)
        vitals = torch.tensor([[[0.25], [0.48], [0.27], [0.85], [0.60], [0.75], [0.90], [0.80]]], dtype=torch.float32)
        score, attn = model(vitals)
        self.assertGreaterEqual(float(score.item()), 0.0)
        self.assertLessEqual(float(score.item()), 100.0)

    def test_ai_predict_category_api(self):
        self.client.post('/login', data={'email': 'individual@expensebook.com', 'password': 'password123'})
        res = self.client.post('/api/ai/predict-category',
            data=json.dumps({'description': 'Starbucks iced coffee latte'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('category', data)
        self.assertEqual(data['category'], 'Food & Dining')
        self.assertIn('attention_tokens', data)

    def test_ai_chat_api(self):
        self.client.post('/login', data={'email': 'individual@expensebook.com', 'password': 'password123'})
        res = self.client.post('/api/ai/chat',
            data=json.dumps({'question': 'Analyze my 50/30/20 budget breakdown'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('reply', data)
        self.assertIn('suggested_actions', data)
        self.assertIn('health_score', data)

    def test_csv_export(self):
        self.client.post('/login', data={'email': 'individual@expensebook.com', 'password': 'password123'})
        res = self.client.get('/expenses/export')
        self.assertEqual(res.status_code, 200)
        self.assertIn('text/csv', res.headers['Content-Type'])
        self.assertTrue(len(res.data) > 0)
        self.assertIn(b'Tax Deductible', res.data)
        self.assertIn(b'Client / Project', res.data)

    def test_demo_email_alias_login(self):
        res = self.client.post('/login', data={'email': 'demo@expensebook.com', 'password': 'password123'}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Aarav Sharma', res.data)

    def test_add_income(self):
        self.client.post('/login', data={'email': 'individual@expensebook.com', 'password': 'password123'})
        res = self.client.post('/income/add', data={
            'source': 'Consulting Retainer Milestone',
            'amount': '1200.00',
            'income_date': '2026-10-25'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

if __name__ == '__main__':
    unittest.main()
