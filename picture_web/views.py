# -*- encoding=UTF-8 -*-

from picture_web1.picture_web import app, db
from picture_web1.picture_web.models import Image, User, Comment

from flask import render_template,redirect,request,flash,get_flashed_messages,send_from_directory
#uuid生成唯一ID
import random,json,os,uuid
import hashlib
from flask_login import login_user,logout_user,login_required,current_user
from picture_web1.picture_web.qiniusdk import qiniu_upload_file


@app.route('/')
def index():
    images = Image.query.order_by(Image.id.desc()).limit(10).all()
    return render_template('index.html',images=images)


@app.route('/image/<int:image_id>')
def image(image_id):
    image = Image.query.get(image_id)
    if image is None:
        return redirect('/')
    return render_template('pageDetail2.html', image=image)

@app.route('/profile/<int:user_id>/')
@login_required
def profile(user_id):
    user = User.query.get(user_id)
    if user is None:
        return redirect('/')
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=1,per_page=3)
    return render_template('profile2.html',user = user, has_next = paginate.has_next, images = paginate.items)

@app.route('/profile/images/<int:user_id>/<int:page>/<int:per_page>/')
def user_images(user_id,page,per_page):
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=page,per_page=per_page)

    map = {'has_next':paginate.has_next}
    images = []
    for image in paginate.items:
        imgvo = {'id':image.id, 'url':image.url, 'comment_count':len(image.comments)}
        images.append(imgvo)
    map['images'] = images
    return json.dumps(map)


@app.route('/regloginpage/')
def regloginpage(msg=''):
    for m in get_flashed_messages(with_categories=False,category_filter=['reglogin']):
        msg = msg+m
    return render_template('login.html',msg = msg, next=request.values.get('next'))

#flash在某一个请求中记录消息，在下一个请求中获取消息，然后做相应的处理”
#假设在a页面操作出错，跳转到b页面，在b页面显示a页面的错误信息

def redirect_with_msg(target,msg,category):
    if msg is not None:
        flash(msg,category=category)
    return redirect(target)

@app.route('/login/', methods=['get','post'])
def login():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()

    if username == '' or password == '':
        return redirect_with_msg('/regloginpage/', u'用户名或密码不能为空', 'reglogin')

    user = User.query.filter_by(username=username).first()

    if user is None:
        return redirect_with_msg('/regloginpage/', u'用户名不存在', 'reglogin')

    m = hashlib.md5()
    m.update((password + user.salt).encode('utf8'))
    #十六进制
    if m.hexdigest()!= user.password:
        return redirect_with_msg('/regloginpage/', u'用户名或密码错误', 'reglogin')
    login_user(user)

    next = request.values.get('next')
    if next is not None and next.startswith('/') >0:
        return redirect(next)

    return redirect('/')


@app.route('/reg/', methods=["GET", "POST"])
def reg():

    username = request.values.get('username').strip()
    password = request.values.get('password').strip()

    if username == '' or password == '':
        return redirect_with_msg('/regloginpage/', u'用户名或密码不能为空', 'reglogin')

    user = User.query.filter_by(username=username).first()

    if user is not None:
        return redirect_with_msg('/regloginpage/',u'用户名已存在','reglogin')

    salt = ''.join(random.sample('0123456789idasdjka53535435gdgczxczewrjuoumnfjahujywsATDSST',10))
    m = hashlib.md5()
    m.update((password+salt).encode('utf8'))
    password = m.hexdigest()
    user = User(username,password,salt)
    db.session.add(user)
    db.session.commit()

    login_user(user)

    next = request.values.get('next')
    if next != None and next.startswith('/') > 0:
        return redirect(next)

    return redirect('/')

@app.route('/logout/')
def logout():
    logout_user()
    return redirect('/')

def save_to_local(file,file_name):
    save_dir = app.config['UPLOAD_DIR']
    file.save(os.path.join(save_dir,file_name))
    return '/image/'+file_name


@app.route('/image/<image_name>')
def view_image(image_name):
    return send_from_directory(app.config['UPLOAD_DIR'],image_name)


@app.route('/upload/',methods=['post'])
def upload():
    file = request.files['file']
    file_ext = ''
    if file.filename.find('.')>0:
        file_ext = file.filename.rsplit('.',1)[1].strip().lower()
    if file_ext in app.config['ALLOWED_EXT']:
        file_name = str(uuid.uuid1()).replace('-','')+'.'+file_ext
        url = save_to_local(file,file_name)
        # url = qiniu_upload_file(file,file_name)
        if url != None:
            db.session.add(Image(url,current_user.id))
            db.session.commit()
    return redirect('/profile/%d' % current_user.id)



# @app.route('/add_comment/',methods=['post'])
# def add_comment():
#     username = request.values.get('username').strip()

@app.route('/addcomment/', methods={'post'})
@login_required
def add_comment():
    image_id = int(request.values['image_id'])
    content = request.values['content']
    comment = Comment(content, image_id, current_user.id)
    db.session.add(comment)
    db.session.commit()
    return json.dumps({"code":0, "id":comment.id,
                       "content":comment.content,
                       "username":comment.user.username,
                       "user_id":comment.user_id})