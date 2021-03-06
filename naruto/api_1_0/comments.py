# -*-coding:utf-8 -*-

#评论文件

from flask import jsonify,request,g,abort,url_for,current_app
from .. import db
from ..models import Post,Permission,Comment
from . import api
from .decorators import permission_required


@api.route('/comments/<int:id>')
def get_comment(id):
    comment=Comment.query.get_or_404(id)
    return jsonify(comment.to_json)
    
@api.route('/posts/<int:id>/comments/',methods=['POST'])
@permission_required(Permission.COMMENT)
def new_post_comment(id):
    post=Post.query.get_or_404(id)
    comment=Comment.from_json(request.json)
    comment.author=g.current_user
    comment.post=post
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json()),201,{'Location':url_for('api.get_comment',id=comment.id,_external=True)}
    

#分页资源
@api.route('/comments/')
def get_comments():
    page=reuqest.args.get('page',1,type=int)
    pagination=Comment.query.paginate(page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)
    posts=pagination.items
    perv=None
    if pagination.has_prev:
        prev=url_for('api.get_comments',page==page-1,_external=True)
    next=None
    if pagination.has_next:
        next=url_for('api.get_comments',page=page+1,_external=True)
    return jsonify({
                  'comments':[comment.to_json() for post in comments],
                  'prev':prev,
                  'next':next,
                  'count':pagination.total
                  
                  })    


@api.route('/posts/<int:id>/comments/')
def get_post_comments(id):
    post=Post.query.get_or_404(id)
    page=reuqest.args.get('page',1,type=int)
    pagination=post.comments.order_by(Comment.timestamp.asc()).paginate(page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)
    comments=pagination.items
    perv=None
    if pagination.has_prev:
        prev=url_for('api.get_post_comments',page==page-1,_external=True)
    next=None
    if pagination.has_next:
        next=url_for('api.get_post_comments',page=page+1,_external=True)
    return jsonify({
                  'comments':[comment.to_json() for post in comments],
                  'prev':prev,
                  'next':next,
                  'count':pagination.total
                  
                  })    











    
