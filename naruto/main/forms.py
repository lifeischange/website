# -*-coding:utf-8-*-

#这是表单文件

from flask_wtf import Form
from wtforms import StringField,SubmitField,TextAreaField,BooleanField,SelectField
from wtforms.validators import Required,Length,Email,Regexp
from ..models import Role,User
from flask_pagedown.fields import PageDownField

class PostForm(Form):
    body=PageDownField('写下你想说的',validators=[Required()])
    submit=SubmitField('发表文章')
#普通用户资料表单   
class EditProfileForm(Form):
    username=StringField('新昵称'，validators=[Length(0,64)])
    name=StringField('真实姓名',validators=[Length(0,64)])
    location=StringField('坐标',validators=[Length(0,64)])
    about_me=TextAreaField('我的信息')
    submit=SubmitField('提交')
    
#管理员资料表单
class EditProfileAdminForm(Form):
    email=StringField('邮箱地址',validators=[Required(),Length(1,64),Email()])
    username=StringField('昵称',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][a-zA-Z0-9_.]*$',0,'用户名必须使用字母打头,后面接字母、数字、点、下划线等')])
    confirmed=BooleanField('确认')
    role=SelectField('角色',coerce=int)
    name=StringField('真是姓名',validators=[Length(0,64)])
    location=StringField('坐标',validators=[Length(0,64)])
    about_me=TextAreaField('我的信息')
    submit=SubmitField('提交')
    
    def __init__(self,user,*args,**kwargs):
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        self.role.choices=[(role.id,role.name) for role in Role.query.order_by(Role.name).all()]#为上边selectfield做选项，id对应标识符，name标志对象
        self.user=user
    #检查邮箱和用户名是否发生变化，若发生就查看其余已存在数据库中的有没有重合    
    def validate_email(self,field):
        if field.data!=self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经注册.')
        
    def validate_username(self,field):
        if field.data!=self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经注册.')
        
#评论提交表单
class CommentForm(Form):
    body=StringField('',validators=[Required()])
    submit=SubmitField('提交')


        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    

