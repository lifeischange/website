#-*-coding:utf-8-*-

#这是数据库模型文件

from . import db
from werkzeug.security import generate_password_hash,check_password_hash
from . import login_manager
from flask_login import UserMixin,AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app,request,url_for
from datetime import datetime
import hashlib
from markdown import markdown
import bleach
from naruto.exceptions import ValidationError


#权限常数
class Permission:
    FOLLOW=0x01
    COMMENT=0x02
    WRITE_ARTICLES=0x04
    MODERATE_COMMENTS=0x08
    ADMINISTER=0x80


class Role(db.Model):
    __tablename__='roles'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),unique=True)
    default=db.Column(db.Boolean,default=False,index=True)
    permissions=db.Column(db.Integer)
    users=db.relationship('User',backref='role',lazy='dynamic')
    
    def __repr__(self):
        return '<Role %r>'%self.name
        
    @staticmethod
    def insert_roles():
        roles={
            'User':(Permission.FOLLOW|Permission.COMMENT|Permission.WRITE_ARTICLES,True),
            'Moderator':(Permission.FOLLOW|Permission.COMMENT|Permission.WRITE_ARTICLES|Permission.MODERATE_COMMENTS,False),
            'Administrator':(0xff,False)
             }
        for r in roles:
            role=Role.query.filter_by(name=r).first()#查看角色
            if role is None:
                role=Role(name=r)
            role.permissions=roles[r][0]
            role.default=roles[r][1]
            db.session.add(role)
        db.session.commit()

#这是关注关联表的模型

class Follow(db.Model):
    __tablename__='follows'
    follower_id=db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
    followed_id=db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
    timestamp=db.Column(db.DateTime,default=datetime.utcnow)        
        
        

        
#登录用户认证模型
class User(UserMixin,db.Model):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(64),unique=True,index=True)
    username=db.Column(db.String(64),unique=True,index=True)
    password_hash=db.Column(db.String(128))
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))
    confirmed=db.Column(db.Boolean,default=False)
    name=db.Column(db.String(64))
    location=db.Column(db.String(64))
    about_me=db.Column(db.Text())
    member_since=db.Column(db.DateTime(),default=datetime.utcnow)
    last_seen=db.Column(db.DateTime(),default=datetime.utcnow)
    avatar_hash=db.Column(db.String(32))   
    posts=db.relationship('Post',backref='author',lazy='dynamic')
    followed=db.relationship('Follow',foreign_keys=[Follow.follower_id],backref=db.backref('follower',lazy='joined'),lazy='dynamic',cascade='all,delete-orphan')
    follower=db.relationship('Follow',foreign_keys=[Follow.followed_id],backref=db.backref('followed',lazy='joined'),lazy='dynamic',cascade='all,delete-orphan')
    comments=db.relationship('Comment',backref='author',lazy='dynamic')
    
    
    #生成虚拟信息
    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed#导入种子？
        import forgery_py
        
        seed()
        for i in xrange(count):
            u= User(email=forgery_py.internet.email_address(),
                    username=forgery_py.internet.user_name(True),
                    password=forgery_py.lorem_ipsum.word(),
                    confirmed=True,
                    name=forgery_py.name.full_name(),
                    location=forgery_py.address.city(),
                    about_me=forgery_py.lorem_ipsum.sentence(),
                    member_since=forgery_py.date.date(True)
                    )
                    
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                
    #自己设置自己为关注者
    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()
                
                
    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.role is None:#self.role代表什么？roles中的role
            if self.email==current_app.config['FLASKY_ADMIN']:
                self.role=Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role=Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash=hashlib.md5(self.email.encode('utf-8')).hexdigest()
        self.follow(self)
            
    def __repr__(self):
        return '<User, %r>'%username
        
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
        
    #获取关注用户的文章
    @property
    def followed_posts(self):
        return Post.query.join(Follow,Follow.followed_id==Post.author_id).filter(Follow.follower_id==self.id)
        
    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)
        
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)
        
    def generate_confirmation_token(self,expiration=3600):
        s=Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id})
        
    def confirm(self,token):
        s=Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token)
        except:
            return False
        if data.get('confirm')!=self.id:
            return False
        self.confirmed=True
        db.session.add(self)
        return True
        
    def generate_reset_token(self,expiration=3600):#造令牌
        s=Serializer(current_app.config['SECRET_KEY'],expiration)#创建令牌实例
        return s.dumps({'reset':self.id})#序列化实例
        
    def reset_password(self,token,new_password):#重设密码
        s=Serializer(current_app.config['SECRET_KEY'])#早匹配令牌
        try:
            data=s.loads(token)#反序列化令牌
        except:
            return False#没有就失败
        if data.get('reset')!=self.id:#验证id
            return False
        self.password=new_password#写入新密码
        db.session.add(self)#提交数据库
        return True    
        
    def generate_email_change_token(self,new_email,expiration=3600):#生成邮件令牌
        s=Serializer(current_app.config['SECRET_KEY'],expiration)#创建序列化实例，expiration由外传入
        return s.dumps({'change_email':self.id,'new_email':new_email})#序列化id和新邮箱
       
    def change_email(self,token):
        s=Serializer(current_app.config['SECRET_KEY'])#以当前程序生成的序列化实例
        try:
            data=s.loads(token)#试着反序列化
        except:
            return False#没有token就失败
        if data.get('change_email')!=self.id:#如果反序列化生成的id不等于当前模型的id
            return False
        new_email=data.get('new_email')#反序列化邮箱
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:#邮箱已存在 失败
            return False
        self.email=new_email#更改新邮箱
        self.avatar_hash=hashlib.md5(self.email.encode('utf-8')).hexdigest()
        db.session.add(self)#添加事务
        return True
     
    def can(self,permissions):#查看权限
        return self.role is not None and (self.role.permissions&permissions)==permissions#当前用户存在且权限符合
        
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)
        
    def ping(self):#定义登录时间
        self.last_seen=datetime.utcnow()
        db.session.add(self)
    
    #用户图像    
    def gravatar(self,size=100,default='identicon',rating='g'):
        if request.is_secure:
            url='http://secure.gravatar.com/avatar' 
        else:
            url='http://www.gravatar.com/avatar'
        hash=hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url,hash=hash,size=size,default=default,rating=rating)
        
    #关注关系辅助方法
    def follow(self,user):
        if not self.is_following(user):
            f=Follow(follower=self,followed=user)
            db.session.add(f)
            
    def unfollow(self,user):
        f=self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            
    def is_following(self,user):
        return self.followed.filter_by(followed_id=user.id).first() is not None
        
    def is_followed_by(self,user):
        return self.follower.filter_by(follower_id=user.id).first() is not None
        
        
    #认证令牌
    def generate_auth_token(self,expiration):
        s=Serializer(current_app.config['SECRET_KEY'],expires_in=expiration)
        return s.dumps({'id':self.id})
        
    @staticmethod
    def verify_auth_token(token):
        s=Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token)
        except:
            return None
        return User.query.get(data['id'])
        
    #json序列化字典
    def to_json(self):
        json_user={
                    'url':url_for('api.get_user',id=self.id,_external=True),
                    'username':self.username,
                    'member_since':self.member_since,
                    'last_seen':self.last_seen,
                    'posts':url_for('api.get_user_posts',id=self.id,_external=True),
                    'followed_posts':url_for('api.get_user_followed_posts',id=self.id,_external=True),
                    'post_count':self.posts.count()
                    }
        return json_user
        
class AnonymousUser(AnonymousUserMixin):
    def can(self,permissions):
        return False
    def is_administrator(self):
        return False
       

login_manager.anonymous_user=AnonymousUser#默认是没有权限的游客
 
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))        
        
#博文数据库模型
class Post(db.Model):
    __tablename__='posts'
    id=db.Column(db.Integer,primary_key=True)
    body=db.Column(db.Text)
    timestamp=db.Column(db.DateTime,index=True,default=datetime.utcnow)
    author_id=db.Column(db.Integer,db.ForeignKey('users.id'))       
    body_html=db.Column(db.Text)#博文字段
    comments=db.relationship('Comment',backref='post',lazy='dynamic')
    #静态虚拟博文        
    @staticmethod
    def generate_fake(count=100):
        from random import seed,randint
        import forgery_py
        
        seed()
        user_count=User.query.count()
        for i in xrange(count):
            u=User.query.offset(randint(0,user_count-1)).first()
            p=Post(body=forgery_py.lorem_ipsum.sentences(randint(1,3)),timestamp=forgery_py.date.date(True),author=u)
            db.session.add(p)
            db.session.commit()
            
    @staticmethod
    def on_changed_body(target,value,oldvalue,initiator):
        allowed_tags=['a','abbr','acronym','b','blockquote','code','em','i','li','ol','pre','strong','ul','h1','h2','h3','p']
        target.body_html=bleach.linkify(bleach.clean(markdown(value,output_format='html'),tags=allowed_tags,strip=True))


    def to_json(self):
        json_post={
                    'url':url_for('api.get_post',id=self.id,_external=True),
                    'body':self.body,
                    'body_html':self.body_html,
                    'timestamp':self.timestamp,
                    'author':url_for('api.get_user',id=self.author_id,_external=True),
                    'comments':url_for('api.get_post_comments',id=self.id,_external=True),
                    'comment_count':self.comments.count() }
        return json_post
    
    #从json创建post模型    
    @staticmethod
    def from_json(json_post):
        body=json_post.get('body')
        if body is None or body=='':
            raise ValidationError('post does not have a body.')
        return Post(body=body)
        
db.event.listen(Post.body,'set',Post.on_changed_body)        
        
#评论数据库
class Comment(db.Model):
    __tablename__='comments'
    id=db.Column(db.Integer,primary_key=True)
    body=db.Column(db.Text)
    body_html=db.Column(db.Text)
    timestamp=db.Column(db.DateTime,index=True,default=datetime.utcnow)
    disabled=db.Column(db.Boolean)
    author_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    post_id=db.Column(db.Integer,db.ForeignKey('posts.id'))
    
    @staticmethod
    def on_changed_body(target,value,oldvalue,initiator):
        allowed_tags=['a','abbr','acronym','b','code','em','i','strong']
        target.body_html=bleach.linkify(bleach.clean(markdown(value,output_format='html'),tags=allowed_tags,strip=True))
db.event.listen(Comment.body,'set',Comment.on_changed_body)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

        
        
        
        
        
        
        
        
