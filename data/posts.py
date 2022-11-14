import sqlalchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class Post(SqlAlchemyBase, UserMixin):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    images = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=True)
    comments = sqlalchemy.Column(sqlalchemy.String, nullable=True, default=0)
    likes = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default="")
    avtor = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    def __repr__(self):
        return f'<Post> {self.title} {self.description} {self.images} {self.comments} {self.likes} {self.avtor}'

    def set_description(self, desc):
        self.description = desc