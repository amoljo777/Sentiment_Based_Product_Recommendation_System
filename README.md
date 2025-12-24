# Ebuss Sentiment-based Product Recommendation (Flask + Heroku)

## What this contains
- `sentiment_model.pkl` : trained sentiment classifier (TF-IDF over HashingVectorizer + Logistic Regression)
- `recommender.pkl` : item-based collaborative filtering artifacts (user-item matrix + item-item similarity)
- `product_reviews.pkl` : product -> list of review texts (used to score sentiment for filtering)
- `model.py` : inference logic (recommend_5)
- `app.py` : Flask app
- `templates/index.html` : UI

## Run locally (Windows)
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open: http://127.0.0.1:5000/

## Deploy to Heroku (summary)
1. Create app, then from the project folder:
```bash
heroku login
heroku create <your-app-name>
git init
git add .
git commit -m "ebuss recommender"
git push heroku main
```
2. Ensure `Procfile` and `requirements.txt` are present (they are).
3. After deploy, open:
```bash
heroku open
```
