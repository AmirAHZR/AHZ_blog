from database import get_db
from sqlite3 import IntegrityError
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_db

app = Flask(__name__)
app.secret_key = 'ahz-blog-secret-key'

DATABASE = 'blog.db'

@app.route("/")
def home():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = get_db()

    posts = conn.execute(
        """
        SELECT
            posts.*,

            CASE

                -- پست‌های خود کاربر → همیشه آخر
                WHEN posts.author_id = ?
                THEN 4

                -- دنبال‌شونده + دیده‌نشده
                WHEN followers.id IS NOT NULL
                     AND post_views.id IS NULL
                THEN 0

                -- بقیه + دیده‌نشده
                WHEN followers.id IS NULL
                     AND post_views.id IS NULL
                THEN 1

                -- دنبال‌شونده + دیده‌شده
                WHEN followers.id IS NOT NULL
                     AND post_views.id IS NOT NULL
                THEN 2

                -- بقیه + دیده‌شده
                ELSE 3

            END AS priority

        FROM posts

        LEFT JOIN followers
            ON followers.following_id = posts.author_id
            AND followers.follower_id = ?

        LEFT JOIN post_views
            ON post_views.post_id = posts.id
            AND post_views.user_id = ?

        ORDER BY priority ASC, posts.id DESC
        """,

        (
            user_id,  # posts.author_id = ?
            user_id,  # followers.follower_id = ?
            user_id   # post_views.user_id = ?
        )

    ).fetchall()

    conn.close()

    return render_template(
        "home.html",
        posts=posts
    )


@app.route('/post/<int:post_id>')
def post_detail(post_id):
    conn = get_db()

    post = conn.execute('''
        SELECT posts.*, users.username AS author
        FROM posts
        LEFT JOIN users ON posts.author_id = users.id
        WHERE posts.id = ?
    ''', (post_id,)).fetchone()

    if post is None:
        conn.close()
        return render_template('404.html'), 404

    like_count = conn.execute(
        'SELECT COUNT(*) FROM likes WHERE post_id = ?',
        (post_id,)
    ).fetchone()[0]

    user_liked = False

    if 'user_id' in session:
        user_liked = conn.execute(
            'SELECT * FROM likes WHERE user_id = ? AND post_id = ?',
            (session['user_id'], post_id)
        ).fetchone() is not None

    comments = conn.execute('''
        SELECT comments.*, users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.post_id = ?
        ORDER BY comments.created_at DESC
    ''', (post_id,)).fetchall()

    conn.execute(
    """
    INSERT OR IGNORE INTO post_views (user_id, post_id)
    VALUES (?, ?)
    """,
    (session["user_id"], post_id)
    )

    conn.commit()
    conn.close()

    return render_template(
        'post_detail.html',
        post=post,
        like_count=like_count,
        user_liked=user_liked,
        comments=comments
    )


@app.route('/add', methods=['GET', 'POST'])
def add_post():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title'].strip()
        content = request.form['content'].strip()

        if not title or not content:
            flash("They have be both full", 'error')
            return redirect(url_for('add_post'))

        conn = get_db()
        conn.execute(
            'INSERT INTO posts (title, content, author_id) VALUES (?, ?, ?)',
            (title, content, session['user_id'])
        )
        conn.commit()
        conn.close()

        flash('✅ پست با موفقیت اضافه شد!', 'success')
        return redirect(url_for('home'))

    return render_template('add_post.html')


@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()

    post = conn.execute(
        'SELECT * FROM posts WHERE id = ?',
        (post_id,)
    ).fetchone()

    if post is None:
        conn.close()
        return render_template('404.html'), 404

    if post['author_id'] != session['user_id']:
        conn.close()
        return 'You do not have permission to edit this post.', 403

    if request.method == 'POST':
        title = request.form['title'].strip()
        content = request.form['content'].strip()

        conn.execute(
            'UPDATE posts SET title = ?, content = ? WHERE id = ?',
            (title, content, post_id)
        )

        conn.commit()
        conn.close()

        return redirect(url_for('post_detail', post_id=post_id))

    conn.close()

    return render_template(
        'edit_post.html',
        post=post
    )


@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()

    post = conn.execute(
        'SELECT * FROM posts WHERE id = ?',
        (post_id,)
    ).fetchone()

    if post is None:
        conn.close()
        return render_template('404.html'), 404

    if post['author_id'] != session['user_id']:
        conn.close()
        return 'You do not have permission to delete this post.', 403

    conn.execute(
        'DELETE FROM posts WHERE id = ?',
        (post_id,)
    )

    conn.commit()
    conn.close()

    flash('🗑️ پست با موفقیت حذف شد!', 'success')

    return redirect(url_for('home'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        password_hash = generate_password_hash(password)

        conn = get_db()

        try:
            conn.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, password_hash)
            )

            conn.commit()
            conn.close()

            return redirect(url_for('login'))

        except IntegrityError:
            conn.close()
            return render_template(
                'signup.html',
                error='Username already exists'
            )

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()

        user = conn.execute(
            'SELECT * FROM users WHERE username = ?',
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']

            return redirect(url_for('home'))

        return render_template(
            'login.html',
            error='Invalid username or password'
        )

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()

    existing_like = conn.execute(
        'SELECT * FROM likes WHERE user_id = ? AND post_id = ?',
        (session['user_id'], post_id)
    ).fetchone()

    if existing_like:
        conn.execute(
            'DELETE FROM likes WHERE user_id = ? AND post_id = ?',
            (session['user_id'], post_id)
        )
    else:
        conn.execute(
            'INSERT INTO likes (user_id, post_id) VALUES (?, ?)',
            (session['user_id'], post_id)
        )

    conn.commit()
    conn.close()

    return redirect(url_for('post_detail', post_id=post_id))


@app.route('/comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    content = request.form['content'].strip()

    if not content:
        flash('Comment cannot be empty!', 'error')
        return redirect(url_for('post_detail', post_id=post_id))

    conn = get_db()

    conn.execute(
        '''
        INSERT INTO comments (content, user_id, post_id)
        VALUES (?, ?, ?)
        ''',
        (content, session['user_id'], post_id)
    )

    conn.commit()
    conn.close()

    return redirect(url_for('post_detail', post_id=post_id))

@app.route("/profile/<username>")
def profile(username):
    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    
    print(user)
    if user == None:
        return render_template("404_profile.html", user=user)

    posts = conn.execute(
        "SELECT * FROM posts WHERE author_id = ? ORDER BY id DESC",
        (user["id"],)
    ).fetchall()
    
    is_following = conn.execute(
    """
    SELECT id FROM followers
    WHERE follower_id = ? AND following_id = ?
    """,
    (session.get("user_id"), user["id"])
    ).fetchone()
    followers_count = conn.execute(
    "SELECT COUNT(*) FROM followers WHERE following_id = ?",
    (user["id"],)
    ).fetchone()[0]
    following_count = conn.execute(
    "SELECT COUNT(*) FROM followers WHERE follower_id = ?",
    (user["id"],)
    ).fetchone()[0]
    following = conn.execute(
    """
    SELECT users.*
    FROM followers
    JOIN users ON followers.following_id = users.id
    WHERE followers.follower_id = ?
    """,
    (user["id"],)
    ).fetchall()
    followers = conn.execute(
    """
    SELECT users.*
    FROM followers
    JOIN users ON followers.follower_id = users.id
    WHERE followers.following_id = ?
    """,
    (user["id"],)
    ).fetchall()
    conn.close()
    return render_template("profile.html", user=user,
                            posts=posts,
                            is_following=is_following,
                            following_count=following_count,
                            followers_count=followers_count,
                            following=following,
                            followers=followers,
                            )


@app.route("/follow/<username>", methods=["POST"])
def follow(username):
    if 'user_id' not in session:
        return redirect(url_for("login"))

    conn = get_db()

   
    user = conn.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    if user is None:
        conn.close()
        return render_template("404_profile.html")


    existing = conn.execute(
        """
        SELECT id FROM followers
        WHERE follower_id = ? AND following_id = ?
        """,
        (session["user_id"], user["id"])
    ).fetchone()

    if existing is None:
        conn.execute(
            """
            INSERT INTO followers (follower_id, following_id)
            VALUES (?, ?)
            """,
            (session["user_id"], user["id"])
        )
        conn.commit()

    conn.close()

    return redirect(url_for("profile", username=username))

@app.route("/unfollow/<username>", methods=["POST"])
def unfollow(username):
    if 'user_id' not in session:
        return redirect(url_for("login"))

    conn = get_db()

    user = conn.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    if user is None:
        conn.close()
        return render_template("404_profile.html")


    existing = conn.execute(
        """
        SELECT id FROM followers
        WHERE follower_id = ? AND following_id = ?
        """,
        (session["user_id"], user["id"])
    ).fetchone()

    if existing is None:

        conn.close()
        return redirect(url_for("show_profile", username=username))


    conn.execute(
        """
        DELETE FROM followers
        WHERE follower_id = ? AND following_id = ?
        """,
        (session["user_id"], user["id"])
    )

    conn.commit()
    conn.close()

    return redirect(url_for("profile", username=username))
    
#Running app part
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)