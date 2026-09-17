# AHZ_blog

A simple social blogging platform built with **Flask** and **SQLite**.

AHZ_blog started as a basic blogging project, but gradually evolved into a small social platform where users can create posts, interact with each other, and build their own feed.

## Features

* 🔐 User registration & login
* ✍️ Create, edit and delete posts
* ❤️ Like posts
* 💬 Comment on posts
* 👤 User profiles
* ➕ Follow / Unfollow users
* 👥 Followers & Following lists
* 📰 Personalized feed
* 👁️ Per-user post view tracking
* 🔒 Password hashing
* 🗃️ SQLite database

## Feed System

The homepage doesn't simply show posts in chronological order.

Posts are organized based on the user's relationship with the author and whether the post has already been viewed:

```text
Following + Unseen
        ↓
Others + Unseen
        ↓
Following + Seen
        ↓
Others + Seen
        ↓
My Posts
```

Post views are stored separately for each user, so a post being viewed by one user doesn't mark it as viewed for everyone else.

## Tech Stack

* Python
* Flask
* SQLite
* Jinja2
* HTML / CSS
* Werkzeug

## Project Structure

```text
AHZ_blog/
│
├── app.py
├── database.py
├── blog.db
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── signup.html
│   ├── profile.html
│   ├── post_detail.html
│   └── ...
│
└── static/
    └── ...
```

## Run Locally

Clone the repository:

```bash
git clone https://github.com/AmirAHZR/AHZ_blog.git
cd AHZ_blog
```

Install dependencies:

```bash
pip install flask werkzeug
```

Run the application:

```bash
python app.py
```

Then open:

```text
http://localhost:5000
```

## Status

🚧 **Still in development**

The project is actively being expanded with new social and feed features.

---

Made by **AmirAHZR**
