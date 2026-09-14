from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_db, init_db



app = Flask(__name__)



app.secret_key = 'ye-kelid-khasi-va-tasodofi-baraye-security'



@app.route('/')
def home():
    conn = get_db()
    posts = conn.execute(
        'SELECT * FROM posts ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    print(posts)
    return render_template('home.html', posts=posts)



@app.route('/add', methods=['GET', 'POST'])
def add_post():
    
    if request.method == 'POST':
        title = request.form['title'].strip()
        content = request.form['content'].strip()

       
        if not title or not content:
            flash("جفتشون باید پر باشن مشتی!", 'error')
            return redirect(url_for('add_post'))

      
        conn = get_db()
        conn.execute(
            'INSERT INTO posts (title, content) VALUES (?, ?)',
            (title, content)
        )
        conn.commit()
        conn.close()

        flash('✅ پست با موفقیت اضافه شد!', 'success')
        return redirect(url_for('home'))

   
    return render_template('add_post.html')

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    conn = get_db()
    post = conn.execute(
        'SELECT * FROM posts WHERE id = ?',
        (post_id,)
    ).fetchone()
    conn.close()

    if post is None:
        return render_template('404.html'), 404

    return render_template('post_detail.html', post=post)

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    conn = get_db()
    conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    
    flash('🗑️ پست با موفقیت حذف شد!', 'success')
    return redirect(url_for('home'))

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    conn = get_db()

    post = conn.execute(
        'SELECT * FROM posts WHERE id = ?',
        (post_id,)
    ).fetchone()

    if post is None:
        conn.close()
        return render_template('404.html'), 404

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

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
        
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404




if __name__ == '__main__':
    init_db()
    app.run(debug=True)