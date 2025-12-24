import pickle
import numpy as np
from nltk.corpus.reader import reviews
import pandas as pd
import re, nltk, spacy, string
import en_core_web_sm
import pickle as pk
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from sklearn.ensemble import RandomForestClassifier,GradientBoostingClassifier
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import LancasterStemmer
from nltk.stem import WordNetLemmatizer
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

# Load artifacts once at import time (fast for Flask)
with open("sentiment_model.pkl", "rb") as f:
    SENTIMENT_MODEL = pickle.load(f)

with open("recommender.pkl", "rb") as f:
    REC = pickle.load(f)

with open("product_reviews.pkl", "rb") as f:
    PRODUCT_REVIEWS = pickle.load(f)

USERS = REC["users"]
ITEMS = REC["items"]
R = REC["user_item_csr"]              # csr matrix: users x items (filled with 0)
S = REC["item_similarity"]            # dense matrix: items x items


def _user_index(username: str) -> int:
    try:
        return USERS.index(username)
    except ValueError:
        return -1


def recommend_20(username: str, n: int = 20):
    """Pure item-based CF recommendations (top-N) for an existing user."""
    uidx = _user_index(username)
    if uidx < 0:
        return []

    # User's rating vector (1 x items)
    user_r = R.getrow(uidx).toarray().ravel()

    # items already rated by the user
    rated_mask = user_r > 0

    # Predict scores: weighted sum of similar items the user rated
    # score_i = sum_j sim(i,j)*r_u_j / sum_j |sim(i,j)|  (only for rated j)
    sims = S[:, rated_mask]            # items x rated_items
    ratings = user_r[rated_mask]       # rated_items

    if ratings.size == 0:
        return []

    numer = sims.dot(ratings)
    denom = np.abs(sims).sum(axis=1) + 1e-9
    scores = numer / denom

    # exclude already rated items
    scores[rated_mask] = -np.inf

    top_idx = np.argsort(-scores)[:n]
    return [ITEMS[i] for i in top_idx if np.isfinite(scores[i])]


def _avg_positive_sentiment(product_name: str) -> float:
    """Average predicted positive probability across available reviews for the product."""
    texts = PRODUCT_REVIEWS.get(product_name, [])
    if not texts:
        return 0.0

    # Predict positive prob for each review; average
    probs = SENTIMENT_MODEL.predict_proba(texts)[:, 1]
    return float(np.mean(probs))


def recommend_5(username: str):
    """Recommend 5 products: top-20 CF filtered/reranked by sentiment."""
    top20 = recommend_20(username, n=20)
    if not top20:
        return []

    scored = [(p, _avg_positive_sentiment(p)) for p in top20]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [p for p, s in scored[:5]]
