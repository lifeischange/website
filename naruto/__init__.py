#-*-coding:utf-8-*-

#这是程序的构造文件，文件名为__init__

from flask import Flask,render_template
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
from flask_pagedown import PageDown


bootstrap=Bootstrap()
mail=Mail()
moment=Moment()
db=SQLAlchemy()
login_manager=LoginManager()
pagedown=PageDown()
login_manager.session_protection='strong'
#设置登录端点，因为前面注册认证蓝本时加了前缀
login_manager.login_view='auth.login'

def create_app(config_name): 
    app=Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    #这些类的实例的创建都是一样？？？
    bootstrap.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    
    if not app.debug and app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify=SSLify(app)
        
    #注册路由主体蓝本，即访问蓝本后第一个页面 第一个是文件夹，第二个是蓝本实例
    from .main import main as main_blueprint
    #注册蓝本
    app.register_blueprint(main_blueprint)
    
    #认证蓝本
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint,url_prefix='/auth')
    
    #api蓝本
    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint,url_prefix='/api/v1.0')
    
    return app
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
