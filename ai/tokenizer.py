import re
import json

class SimpleFinancialTokenizer:
    """
    Lightweight, self-contained offline tokenizer optimized for financial
    transactions, queries, and advisory prompts.
    Zero external API dependencies.
    """
    def __init__(self, max_length=32):
        self.max_length = max_length
        self.special_tokens = {
            '<PAD>': 0,
            '<UNK>': 1,
            '<CLS>': 2,
            '<SEP>': 3,
            '<NUM>': 4
        }
        self.vocab = dict(self.special_tokens)
        self._build_financial_vocab()
        self.inv_vocab = {v: k for k, v in self.vocab.items()}

    def _build_financial_vocab(self):
        core_words = [
            # Food & Dining
            'grocery', 'groceries', 'supermarket', 'market', 'walmart', 'target', 'kroger', 'wholefoods',
            'traderjoes', 'costco', 'restaurant', 'dinner', 'lunch', 'breakfast', 'cafe', 'coffee',
            'starbucks', 'mcdonalds', 'subway', 'pizza', 'burger', 'food', 'snack', 'bar', 'drinks',
            'bakery', 'takeout', 'doordash', 'ubereats', 'grubhub',
            'zomato', 'swiggy', 'blinkit', 'zepto', 'dmart', 'bigbasket', 'chai', 'tea', 'dosa', 'biryani', 'haldiram',
            # Transportation
            'uber', 'lyft', 'taxi', 'gas', 'fuel', 'petrol', 'metro', 'subway', 'bus', 'train',
            'transit', 'flight', 'airline', 'delta', 'united', 'parking', 'toll', 'car', 'auto',
            'repair', 'oil', 'service', 'maintenance', 'ola', 'rickshaw', 'fastag',
            # Housing & Utilities
            'rent', 'mortgage', 'lease', 'apartment', 'house', 'electric', 'electricity', 'water',
            'utility', 'utilities', 'gas', 'internet', 'wifi', 'broadband', 'phone', 'mobile',
            'at&t', 'verizon', 'tmobile', 'trash', 'maintenance', 'bescom', 'jio', 'airtel', 'tataplay',
            # Entertainment & Leisure
            'netflix', 'spotify', 'hulu', 'disney', 'cinema', 'movie', 'concert', 'theater',
            'game', 'gaming', 'steam', 'playstation', 'xbox', 'nintendo', 'book', 'subscription',
            'vacation', 'hotel', 'airbnb', 'club', 'hobby', 'pvr', 'inox',
            # Shopping & Personal
            'amazon', 'shopping', 'clothes', 'clothing', 'shoes', 'electronics', 'apple', 'gadget',
            'cosmetics', 'salon', 'barber', 'haircut', 'spa', 'gift', 'furniture', 'decor', 'myntra', 'flipkart',
            # Healthcare & Fitness
            'doctor', 'hospital', 'clinic', 'pharmacy', 'medicine', 'prescription', 'cvs', 'walgreens',
            'dental', 'dentist', 'vision', 'optometry', 'therapy', 'gym', 'fitness', 'workout',
            'cult', 'cultfit', 'apollo', 'pharmeasy', '1mg',
            # Income & Investment
            'salary', 'paycheck', 'payroll', 'wages', 'income', 'freelance', 'client', 'consulting',
            'bonus', 'dividend', 'interest', 'stock', 'shares', 'etf', 'crypto', 'savings',
            'deposit', 'transfer', 'refund', 'reimbursement', 'zerodha', 'groww', 'sip', 'fd', 'nifty', 'upi', 'inr', 'rupees', 'lakh',
            # Financial Advisor Query Tokens
            'how', 'what', 'why', 'can', 'should', 'will', 'my', 'i', 'spend', 'spent', 'spending',
            'budget', 'save', 'saving', 'savings', 'cut', 'reduce', 'emergency', 'fund', 'health',
            'score', 'advice', 'advisor', 'plan', 'forecast', 'predict', 'projection', 'debt',
            'loan', 'credit', 'card', 'interest', 'afford', 'invest', 'investing', '50/30/20',
            'leak', 'anomaly', 'unusual', 'high', 'low', 'monthly', 'month', 'year', 'week', 'next',
            'category', 'food', 'rent', 'travel', 'trend', 'analysis', 'report'
        ]
        
        idx = len(self.vocab)
        for w in core_words:
            if w not in self.vocab:
                self.vocab[w] = idx
                idx += 1

    def tokenize(self, text):
        if not text:
            return []
        text = text.lower()
        # Replace numbers with <NUM>
        text = re.sub(r'\b\d+(\.\d+)?\b', ' <NUM> ', text)
        # Tokenize words
        tokens = re.findall(r'\b[a-z0-9/&_-]+\b|<[A-Z]+>', text)
        return tokens

    def encode(self, text, add_special_tokens=True):
        tokens = self.tokenize(text)
        token_ids = []
        if add_special_tokens:
            token_ids.append(self.special_tokens['<CLS>'])
            
        for t in tokens:
            token_ids.append(self.vocab.get(t, self.special_tokens['<UNK>']))
            
        if add_special_tokens:
            token_ids.append(self.special_tokens['<SEP>'])
            
        # Pad or truncate to max_length
        if len(token_ids) > self.max_length:
            token_ids = token_ids[:self.max_length]
        else:
            token_ids += [self.special_tokens['<PAD>']] * (self.max_length - len(token_ids))
            
        return token_ids

    def decode(self, token_ids):
        words = []
        for tid in token_ids:
            if tid in self.inv_vocab:
                tok = self.inv_vocab[tid]
                if tok not in ['<PAD>', '<CLS>', '<SEP>']:
                    words.append(tok)
        return ' '.join(words)

    @property
    def vocab_size(self):
        return len(self.vocab)
