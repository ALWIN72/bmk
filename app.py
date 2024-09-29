from flask import Flask, render_template, request, redirect, url_for, flash, Response
from flask_sqlalchemy import SQLAlchemy
import csv
import io

app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = 'your_secret_key_here'  # Change this to a secure random key!

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookmarks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define the Bookmark model
class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Bookmark {self.title}>'

# Create the database and the Bookmark table
with app.app_context():
    db.create_all()

# Route to display bookmarks on the index page
@app.route("/")
def index():
    bookmarks = Bookmark.query.all()  # Fetch all bookmarks from the database
    return render_template("index.html", bookmarks=bookmarks)

# Route to add a new bookmark
@app.route("/add_bookmark", methods=["POST"])
def add_bookmark():
    title = request.form.get("title")
    url = request.form.get("url")

    if title and url:
        new_bookmark = Bookmark(title=title, url=url)
        db.session.add(new_bookmark)
        db.session.commit()
        flash("Bookmark added successfully!", "success")  # Feedback message

    return redirect(url_for("index"))

# Route to delete a bookmark based on its ID
@app.route("/delete_bookmark/<int:bookmark_id>")
def delete_bookmark(bookmark_id):
    bookmark = Bookmark.query.get_or_404(bookmark_id)
    db.session.delete(bookmark)
    db.session.commit()
    flash("Bookmark deleted successfully!", "success")  # Feedback message
    return redirect(url_for("index"))

# Route for editing a bookmark
@app.route("/edit_bookmark/<int:bookmark_id>", methods=["GET", "POST"])
def edit_bookmark(bookmark_id):
    bookmark = Bookmark.query.get_or_404(bookmark_id)

    if request.method == "POST":
        bookmark.title = request.form.get("title")
        bookmark.url = request.form.get("url")
        db.session.commit()
        flash("Bookmark updated successfully!", "success")  # Feedback message
        return redirect(url_for("index"))
    else:
        return render_template("edit_bookmark.html", bookmark=bookmark)

# Route to export bookmarks to CSV
@app.route("/export_csv")
def export_csv():
    bookmarks = Bookmark.query.all()  # Fetch all bookmarks

    # Create a CSV response
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Title', 'URL'])  # Write the header

    for bookmark in bookmarks:
        writer.writerow([bookmark.id, bookmark.title, bookmark.url])  # Write each bookmark

    # Prepare response
    output.seek(0)  # Move to the beginning of the StringIO object
    return Response(output.getvalue(),
                    mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=bookmarks.csv"})

# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)
