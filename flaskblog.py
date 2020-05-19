from flask import Flask, render_template, url_for
app = Flask(__name__)

app.config['SECRET_KEY'] = '9093f7fc341e08d9a1e5be02a205def9'

posts = [
    {
        'author': 'J.K. Rowling',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'May 18, 2020'
    },
    {
        'author': 'Stephen King',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'May 19, 2020'
    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

if __name__ == "__main__":
    app.run(debug=True)