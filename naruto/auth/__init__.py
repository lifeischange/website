#-*-coding:utf-8-*-

#这是认证蓝本的构造文件

from flask import Blueprint

auth=Blueprint('auth',__name__)

from . import views
