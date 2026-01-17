#!/usr/bin/env python3

from flask import Flask, jsonify, session
from flask_migrate import Migrate
from models import db, Article, User

# ---------------------
# App setup
# ---------------------
app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'  # Required for sessions
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize DB and migrations
db.init_app(app)
migrate = Migrate(app, db)

# ---------------------
# Routes
# ---------------------

# Clear session route
@app.route('/clear')
def clear_session():
    session.clear()  # Clear all session data
    return {'message': '200: Successfully cleared session data.'}, 200


# List all articles (optional)
@app.route('/articles')
def index_articles():
    articles = Article.query.all()
    articles_list = []
    for article in articles:
        articles_list.append({
            'id': article.id,
            'title': article.title,
            'content': article.content,
            'author': article.author,
            'preview': article.preview,
            'minutes_to_read': article.minutes_to_read,
            'date': article.date.isoformat()
        })
    return jsonify(articles_list), 200


# Show single article with session-based paywall
@app.route('/articles/<int:id>')
def show_article(id):
    # Increment session page_views
    session['page_views'] = session.get('page_views', 0) + 1

    # Limit access after 3 page views
    if session['page_views'] > 3:
        return jsonify({'message': 'Maximum pageview limit reached'}), 401

    # Fetch the article from the DB
    article = db.session.get(Article, id)
    if not article:
        return jsonify({'message': 'Article not found'}), 404

    # Return the JSON including all required fields
    return jsonify({
        'id': article.id,
        'title': article.title,
        'content': article.content,
        'author': article.author,
        'preview': article.preview,
        'minutes_to_read': article.minutes_to_read,
        'date': article.date.isoformat()
    }), 200


# ---------------------
# Run server
# ---------------------
if __name__ == '__main__':
    app.run(port=5555)

