import unittest

from blog import app, db
from blog.models import Comments, Posts, Users


class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        app.config["TESTING"] = True
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = Users(username="timmy")
        u.set_password("cat")
        self.assertFalse(u.check_password("dog"))
        self.assertTrue(u.check_password("cat"))


class AuthorizationTestCase(unittest.TestCase):
    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        db.create_all()
        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_index(self):
        req = self.client.get("/")
        self.assertEqual(req.status_code, 200)
        self.assertIn(b"There is no posts yet", req.data)

    def test_register(self):
        self.assertEqual(self.client.get("/register").status_code, 200)
        self.assertEqual(Users.query.all(), [])

        response = self.client.post(
            "/register",
            data={
                "username": "user",
                "email": "u@u.ru",
                "password": 123,
                "password2": 123,
            },
            follow_redirects=True,
        )

        self.assertIn(
            b"Congratulations, you`ve successfully registered!", response.data
        )
        self.assertEqual(Users.query.first().username, "user")

    def test_login(self):
        self.assertEqual(Users.query.all(), [])
        self.client.post(
            "/register",
            data={
                "username": "user",
                "email": "u@u.ru",
                "password": 123,
                "password2": 123,
            },
            follow_redirects=True,
        )

        self.assertEqual(Users.query.first().username, "user")

        response = self.client.post(
            "/login", data={"username": "user", "password": 123}, follow_redirects=True
        )

        self.assertIn(b"User: user", response.data)
        self.assertIn(b"You haven't got any posts, create it!", response.data)

    def test_login_invalid_user(self):
        self.assertEqual(Users.query.all(), [])
        self.client.post(
            "/register",
            data={
                "username": "user",
                "email": "u@u.ru",
                "password": 123,
                "password2": 123,
            },
            follow_redirects=True,
        )

        self.assertEqual(Users.query.first().username, "user")

        invalid_password = self.client.post(
            "/login", data={"username": "user", "password": 000}, follow_redirects=True
        )
        invalid_username = self.client.post(
            "/login",
            data={"username": "another_name", "password": 123},
            follow_redirects=True,
        )

        self.assertIn(b"Invalid username or password", invalid_password.data)
        self.assertNotIn(
            b"You haven't got any posts, create it!", invalid_password.data
        )
        self.assertIn(b"Invalid username or password", invalid_username.data)
        self.assertNotIn(
            b"You haven't got any posts, create it!", invalid_username.data
        )

    def test_changing_username(self):
        self.client.post(
            "/register",
            data={
                "username": "user",
                "email": "u@u.ru",
                "password": 123,
                "password2": 123,
            },
            follow_redirects=True,
        )
        self.client.post(
            "/login", data={"username": "user", "password": 123}, follow_redirects=True
        )

        self.assertEqual(Users.query.first().username, "user")

        response = self.client.post(
            "/edit_profile", data={"username": "New name"}, follow_redirects=True
        )

        self.assertIn(b"Your changes have been saved.", response.data)
        self.assertEqual(Users.query.first().username, "New name")

    def test_logout(self):
        self.client.post(
            "/register",
            data={
                "username": "user",
                "email": "u@u.ru",
                "password": 123,
                "password2": 123,
            },
            follow_redirects=True,
        )
        self.client.post(
            "/login", data={"username": "user", "password": 123}, follow_redirects=True
        )
        self.assertEqual(self.client.get("user/user").status_code, 200)

        self.client.get("/logout")
        self.assertNotEqual(self.client.get("user/user").status_code, 200)


class PostsTestCase(unittest.TestCase):
    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        db.create_all()
        self.client = app.test_client()
        self.client.post(
            "/register",
            data={
                "username": "Tim",
                "email": "tim@tim.ru",
                "password": 123,
                "password2": 123,
            },
            follow_redirects=True,
        )
        self.client.post(
            "/login", data={"username": "Tim", "password": 123}, follow_redirects=True
        )
        self.user = Users.query.filter_by(username="Tim").first()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_creation_post(self):
        self.assertEqual(self.client.get("user/Tim").status_code, 200)
        self.assertEqual(self.user.posts.all(), [])

        response = self.client.post(
            "user/Tim",
            data={"title": "First post!", "content": "Hello world!"},
            follow_redirects=True,
        )

        self.assertIn(
            b"Congratulations, you`ve successfully created new post!", response.data
        )
        self.assertEqual(Posts.query.first().title, "First post!")
        self.assertEqual(Posts.query.first().author, self.user)

    def test_changing_post(self):
        self.client.post(
            "user/Tim",
            data={"title": "First post!", "content": "Hello world!"},
            follow_redirects=True,
        )

        self.assertEqual(self.client.get("edit_post/1").status_code, 200)
        self.assertEqual(Posts.query.first().title, "First post!")
        self.assertEqual(Posts.query.first().content, "Hello world!")

        response = self.client.post(
            "edit_post/1",
            data={"title": "Another post!", "content": "Good night!"},
            follow_redirects=True,
        )
        self.assertIn(b"Your changes have been saved.", response.data)
        self.assertEqual(Posts.query.first().title, "Another post!")
        self.assertEqual(Posts.query.first().content, "Good night!")

    def test_deleting_post(self):
        self.client.post(
            "user/Tim",
            data={"title": "First post!", "content": "Hello world!"},
            follow_redirects=True,
        )

        self.assertEqual(self.client.get("edit_post/1").status_code, 200)
        self.assertNotEqual(Posts.query.all(), [])
        self.assertEqual(Posts.query.first().title, "First post!")

        response = self.client.post(
            "edit_post/1", data={"delete": "Delete"}, follow_redirects=True
        )

        self.assertIn(b"Your post is successfully deleted", response.data)
        self.assertEqual(Posts.query.all(), [])


class CommentsTestCase(unittest.TestCase):
    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        db.create_all()
        self.client = app.test_client()
        self.client.post(
            "/register",
            data={
                "username": "Tim",
                "email": "tim@tim.ru",
                "password": 123,
                "password2": 123,
            },
            follow_redirects=True,
        )
        self.client.post(
            "/login", data={"username": "Tim", "password": 123}, follow_redirects=True
        )
        self.client.post(
            "user/Tim",
            data={"title": "First post!", "content": "Hello world!"},
            follow_redirects=True,
        )
        self.user = Users.query.filter_by(username="Tim").first()
        self.post = self.user.posts.first()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_comment(self):
        self.assertEqual(self.client.get("post/1").status_code, 200)
        self.assertEqual(Comments.query.all(), [])

        self.client.post(
            "post/1",
            data={"title": "First comment", "content": "Thanks everyone!"},
            follow_redirects=True,
        )

        self.assertEqual(Comments.query.first().title, "First comment")
        self.assertEqual(Comments.query.first().author, self.user)

    def test_create_comment_without_login(self):
        self.assertEqual(self.client.get("user/Tim").status_code, 200)
        self.assertEqual(Comments.query.all(), [])
        self.client.get("/logout")
        self.assertNotEqual(self.client.get("user/Tim").status_code, 200)

        response = self.client.post(
            "post/1",
            data={"title": "First comment", "content": "Thanks everyone!"},
            follow_redirects=True,
        )

        self.assertIn(b"Please log in or register for leaving comments", response.data)
        self.assertEqual(Comments.query.all(), [])

    def test_changing_comment(self):
        self.client.post(
            "post/1",
            data={"title": "First comment", "content": "Thanks everyone!"},
            follow_redirects=True,
        )

        self.assertEqual(self.client.get("edit_comment/1").status_code, 200)
        self.assertEqual(Comments.query.first().title, "First comment")
        self.assertEqual(Comments.query.first().content, "Thanks everyone!")

        response = self.client.post(
            "edit_comment/1",
            data={"title": "Another comment!", "content": "See you!"},
            follow_redirects=True,
        )
        self.assertIn(b"Your changes have been saved.", response.data)
        self.assertEqual(Comments.query.first().title, "Another comment!")
        self.assertEqual(Comments.query.first().content, "See you!")

    def test_deleting_comment(self):
        self.client.post(
            "post/1",
            data={"title": "First comment", "content": "Thanks everyone!"},
            follow_redirects=True,
        )

        self.assertEqual(self.client.get("edit_comment/1").status_code, 200)
        self.assertNotEqual(Comments.query.all(), [])
        self.assertEqual(Comments.query.first().title, "First comment")

        response = self.client.post(
            "edit_comment/1", data={"delete": "Delete"}, follow_redirects=True
        )

        self.assertIn(b"Your comment is successfully deleted", response.data)
        self.assertEqual(Comments.query.all(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
