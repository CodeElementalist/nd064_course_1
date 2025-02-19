import sqlite3
import logging

from flask import Flask, jsonify, json, render_template, request, url_for
from flask import redirect, flash
from werkzeug.exceptions import abort

db_connection_count = [0]


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    db_connection_count[0] += 1
    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    connection.close()
    return post


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


# Define the main route of the web application
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.info('Request for post unsuccessful!')
        return render_template('404.html'), 404
    else:
        app.logger.info('Request for post successful!')
        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('Request for "About Us" page successful!')
    return render_template('about.html')


# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            app.logger.info(f"Article's title missing. Post creation unsuccessful!")
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute(
                        'INSERT INTO posts (title, content) VALUES (?, ?)',
                        (title, content))
            connection.commit()
            connection.close()

            app.logger.info(f'Article "{title}" posted successful!')
            return redirect(url_for('index'))

    return render_template('create.html')


#  Healthcheck endpoint
@app.route('/healthz')
def healtz_status():
    response = app.response_class(
            response=json.dumps({"result": "OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info('Request for healthcheck successful!')
    return response


#  Metrics endpoint
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    post_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    response = app.response_class(
            response=json.dumps({"db_connection_count": db_connection_count[0],
                                "post_count": post_count}),
            status=200,
            mimetype='application/json'
    )
    connection.close()
    app.logger.info('Request for matrics successful!')
    return response


# start the application on port 3111
if __name__ == "__main__":
    logging.basicConfig(filename='app.log', level=logging.DEBUG)
    app.run(host='0.0.0.0', port='3111')
