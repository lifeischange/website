#-*-coding:utf-8-*-

#这是蓝本的错误处理程序

from flask import render_template,request,jsonify
from . import main

#这里有一个命名空间的issue，所以要用app_errorhandler
@main.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response=jsonify({'error':'not found'})#json格式响应
        response.status_code=404
        return response
    return render_template('404.html'),404

@main.app_errorhandler(403)
def forbidden(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response=jsonify({'error':'forbidden'})#json格式响应
        response.status_code=403
        return response
    return render_template('403.html'),403
    
@main.app_errorhandler(500)
def intenal_server_error(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response=jsonify({'error':'internal server error'})#json格式响应
        response.status_code=500
        return response
    return render_template('500.html'),500
