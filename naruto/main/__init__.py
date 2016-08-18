#-*-coding:utf-8-*-

#这是一个蓝本的构造文件

from flask import Blueprint

#创建蓝本实例，main是对象。括号内的第一个是蓝本名称
main=Blueprint('main',__name__)

from . import views,errors
from ..models import Permission

@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


