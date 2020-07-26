# -*- encoding=UTF-8 -*-


from picture_web1.picture_web import app, db
from flask_script import Manager
from picture_web1.picture_web.models import User, Image, Comment
import random

manager = Manager(app)


def get_image_url():
    return 'http://images.nowcoder.com/head/' + str(random.randint(0,100)) + 'm.png'


@manager.command
def init_database():
    db.drop_all()
    db.create_all()

    for i in range(0,100):
        db.session.add(User('User'+str(i), 'a'+str(i)))
        for j in range(0,10):
            db.session.add(Image(get_image_url(), i+1))
            for k in range(0,3):
                db.session.add(Comment('这是一条评论'+str(k), 1+3*i+j, i+1))

    db.session.commit()


    print(1,User.query.get(3))
    print(2,User.query.filter_by(id=5).first())
    print(3,User.query.order_by(User.id.desc()).limit(2).all())
    print(4,User.query.filter(User.username.endswith('0')).limit(3).all())
    print(5,User.query.paginate(page=1,per_page=10).items)
    user = User.query.get(1)
    print(5,user.images)

    image = Image.query.get(1)
    print(6,image,image.user)


if __name__ == '__main__':
    manager.run()