import math
import torch
import torch.nn as nn
import torch.nn.functional as F

class PositionalEncoding(nn.Module):
    """
    Standard Sinusoidal Positional Encoding for sequence Transformers.
    """
    def __init__(self, d_model: int, max_len: int = 500):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        pe = pe.unsqueeze(0)  # Shape: (1, max_len, d_model)
        self.register_buffer('pe', pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (batch_size, seq_len, d_model)
        seq_len = x.size(1)
        return x + self.pe[:, :seq_len]


class MultiHeadAttentionWithWeights(nn.Module):
    """
    Custom Multi-Head Self-Attention that explicitly preserves and returns
    attention weights for explainable AI in the Financial Advisor interface.
    """
    def __init__(self, d_model: int, nhead: int, dropout: float = 0.1):
        super().__init__()
        assert d_model % nhead == 0, "d_model must be divisible by nhead"
        self.d_model = d_model
        self.nhead = nhead
        self.head_dim = d_model // nhead
        
        self.q_proj = nn.Linear(d_model, d_model)
        self.k_proj = nn.Linear(d_model, d_model)
        self.v_proj = nn.Linear(d_model, d_model)
        self.out_proj = nn.Linear(d_model, d_model)
        self.dropout = nn.Dropout(dropout)
        self.scale = 1.0 / math.sqrt(self.head_dim)

    def forward(self, x: torch.Tensor, mask: torch.Tensor = None):
        batch_size, seq_len, _ = x.shape
        
        # Project and reshape into heads: (batch, nhead, seq_len, head_dim)
        Q = self.q_proj(x).view(batch_size, seq_len, self.nhead, self.head_dim).transpose(1, 2)
        K = self.k_proj(x).view(batch_size, seq_len, self.nhead, self.head_dim).transpose(1, 2)
        V = self.v_proj(x).view(batch_size, seq_len, self.nhead, self.head_dim).transpose(1, 2)
        
        scores = torch.matmul(Q, K.transpose(-2, -1)) * self.scale
        if mask is not None:
            # mask shape: (batch, seq_len) -> expand for heads
            mask = mask.unsqueeze(1).unsqueeze(2)  # (batch, 1, 1, seq_len)
            scores = scores.masked_fill(mask == 0, -1e9)
            
        attn_weights = F.softmax(scores, dim=-1)
        attn_weights = self.dropout(attn_weights)
        
        context = torch.matmul(attn_weights, V)
        context = context.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        out = self.out_proj(context)
        
        # Mean attention weights across heads for visualization
        mean_attn = attn_weights.mean(dim=1)  # (batch, seq_len, seq_len)
        return out, mean_attn


class TransformerTextClassifier(nn.Module):
    """
    Self-Attention Sequence Classifier for Transaction Categorization
    and Financial Advisor Query Intent Detection.
    Runs entirely on local CPU with sub-millisecond latency.
    """
    def __init__(self, vocab_size: int, num_categories: int = 10, num_intents: int = 8,
                 d_model: int = 64, nhead: int = 4, num_layers: int = 2,
                 dim_feedforward: int = 128, dropout: float = 0.1):
        super().__init__()
        self.d_model = d_model
        self.embedding = nn.Embedding(vocab_size, d_model, padding_idx=0)
        self.pos_encoder = PositionalEncoding(d_model)
        
        # Multi-head attention layer with explainable attention maps
        self.mha = MultiHeadAttentionWithWeights(d_model, nhead, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        
        # Feed-forward network
        self.ffn = nn.Sequential(
            nn.Linear(d_model, dim_feedforward),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(dim_feedforward, d_model)
        )
        self.norm2 = nn.LayerNorm(d_model)
        
        # Classification Heads
        self.category_classifier = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, num_categories)
        )
        self.intent_classifier = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, num_intents)
        )

    def forward(self, input_ids: torch.Tensor, mask: torch.Tensor = None):
        # input_ids: (batch_size, seq_len)
        embeds = self.embedding(input_ids) * math.sqrt(self.d_model)
        x = self.pos_encoder(embeds)
        
        # Self-Attention + Residual
        attn_out, attn_weights = self.mha(x, mask=mask)
        x = self.norm1(x + attn_out)
        
        # Feed-forward + Residual
        ffn_out = self.ffn(x)
        x = self.norm2(x + ffn_out)
        
        # Mean pooling over tokens (ignoring pad tokens if mask given)
        if mask is not None:
            mask_expanded = mask.unsqueeze(-1).float()
            sum_embeddings = (x * mask_expanded).sum(dim=1)
            sum_mask = mask_expanded.sum(dim=1).clamp(min=1e-9)
            pooled = sum_embeddings / sum_mask
        else:
            pooled = x.mean(dim=1)
            
        category_logits = self.category_classifier(pooled)
        intent_logits = self.intent_classifier(pooled)
        
        return {
            'category_logits': category_logits,
            'intent_logits': intent_logits,
            'attention_weights': attn_weights,
            'pooled_features': pooled
        }


class TemporalExpenseTransformer(nn.Module):
    """
    Temporal Self-Attention Transformer for Time-Series Expense Forecasting
    and Anomaly/Overspending Detection.
    Captures temporal spending dynamics (day of week, month cycles, spikes).
    """
    def __init__(self, input_dim: int = 5, d_model: int = 64, nhead: int = 4,
                 num_layers: int = 2, forecast_steps: int = 14, dropout: float = 0.1):
        super().__init__()
        self.d_model = d_model
        self.forecast_steps = forecast_steps
        
        # Temporal projection from input features [amount, dow_sin, dow_cos, dom_norm, cat_idx]
        self.input_proj = nn.Linear(input_dim, d_model)
        self.pos_encoder = PositionalEncoding(d_model, max_len=120)
        
        # Temporal self-attention encoder layers
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=128,
            dropout=dropout,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Forecasting head: predicts daily spend for next N days
        self.forecast_head = nn.Sequential(
            nn.Linear(d_model, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, forecast_steps)
        )
        
        # Anomaly / Reconstruction head: detects if current spending sequence is anomalous
        self.anomaly_detector = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )

    def forward(self, x: torch.Tensor):
        # x shape: (batch_size, seq_len, input_dim)
        projected = self.input_proj(x) * math.sqrt(self.d_model)
        pos_encoded = self.pos_encoder(projected)
        encoded = self.transformer_encoder(pos_encoded)
        
        # Use latest temporal state representation for forecast
        latest_state = encoded[:, -1, :]  # (batch, d_model)
        forecast = self.forecast_head(latest_state)  # (batch, forecast_steps)
        
        # Anomaly score per step or sequence
        anomaly_score = self.anomaly_detector(latest_state)  # (batch, 1)
        
        return {
            'forecast': forecast,
            'anomaly_score': anomaly_score,
            'temporal_features': latest_state
        }


class FinAdvisorAttentionModel(nn.Module):
    """
    Neural Multi-Attribute Attention Network for Financial Health Scoring
    and Personal Advisor Reasoning.
    Attends across 8 financial vitals to generate personalized diagnostic scores.
    """
    def __init__(self, num_vitals: int = 8, d_model: int = 32, nhead: int = 2):
        super().__init__()
        # 8 Vitals: [Savings Rate, Needs Ratio, Wants Ratio, Budget Utilization,
        #            Emergency Buffer, Volatility, Income Stability, Debt/Goal Index]
        self.vital_proj = nn.Linear(1, d_model)
        self.mha = MultiHeadAttentionWithWeights(d_model, nhead, dropout=0.05)
        self.score_head = nn.Sequential(
            nn.Linear(d_model * num_vitals, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()  # Returns score 0.0 to 1.0 (scaled to 0-100)
        )

    def forward(self, vitals: torch.Tensor):
        # vitals: (batch, num_vitals, 1)
        batch_size = vitals.size(0)
        x = self.vital_proj(vitals)  # (batch, num_vitals, d_model)
        attn_out, attn_weights = self.mha(x)
        flattened = attn_out.reshape(batch_size, -1)
        health_score = self.score_head(flattened) * 100.0  # Scale 0-100
        return health_score, attn_weights
