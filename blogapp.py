from blog import app, db
from blog.models import Users, Posts, Comments


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Users': Users, 'Posts': Posts, "Comments": Comments}
