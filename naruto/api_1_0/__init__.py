#-*- coding:utf-8 -*-

#这是api 1.0版

from flask import Blueprint
api=Blueprint('api',__name__)
from . import authentication,posts,users,comments,errors
