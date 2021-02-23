from blog import app, db
from blog.models import Comments, Posts, Users


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "Users": Users, "Posts": Posts, "Comments": Comments}
