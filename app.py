from flask import Flask, render_template, request
import mysql.connector
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import feedparser

app = Flask(__name__)

# MySQL Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2r2p1utx4k",
    database="placement_db"
)

cursor = db.cursor()

# Rss
def get_rss_feed():
    url = "https://news.google.com/rss/search?q=job+vacancies+India&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(url)

    articles = []

    for entry in feed.entries[:5]:
        articles.append({
            "title": entry.title,
            "link": entry.link,
            "source": entry.source.get('title', 'Google News')
        })

    return articles

# Fetch jobs from DB
def get_jobs():
    cursor.execute("SELECT role, skills FROM jobs")
    return cursor.fetchall()

# Recommendation function
def recommend_job(student_skills):
    jobs = get_jobs()

    job_skills = [job[1] for job in jobs]
    job_roles = [job[0] for job in jobs]

    data = job_skills + [student_skills]

    cv = CountVectorizer()
    vectors = cv.fit_transform(data).toarray()

    similarity = cosine_similarity([vectors[-1]], vectors[:-1])
    best_index = similarity[0].argmax()

    return job_roles[best_index], similarity[0][best_index]


@app.route('/')
def home():
    articles = get_rss_feed()
    return render_template('index.html', articles=articles)


@app.route('/recommend', methods=['POST'])
def recommend():
    name = request.form['name']
    skills = request.form['skills']

    # Save student data
    query = "INSERT INTO students (name, skills) VALUES (%s, %s)"
    cursor.execute(query, (name, skills))
    db.commit()

    job, score = recommend_job(skills)

    return render_template('result.html', name=name, job=job, score=round(score*100, 2))


if __name__ == "__main__":
    app.run(debug=True)

