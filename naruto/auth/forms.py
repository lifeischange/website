#-*-coding:utf-8-*-

#这是认证蓝本的登录表单

from flask_wtf import Form
from wtforms import StringField,PasswordField,BooleanField, SubmitField
from wtforms.validators import Required,Length,Email,Regexp,EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(Form):
    email=StringField('邮箱',validators=[Required(),Length(1,64),Email()])
    password=PasswordField('密码',validators=[Required()])
    remember_me=BooleanField('记住我')
    submit=SubmitField('登录')
    
class RegistrationForm(Form):
    email=StringField('邮箱',validators=[Required(),Length(1,64),Email()])
    username=StringField('昵称',validators=[Required(),Length(1,64),Regexp('^[^0-9].*$',0,'第一个字符不能是数字，那样太丑！')])
    password=PasswordField('密码',validators=[Required(),EqualTo('password2',message='Passwords must math.')])
    password2=PasswordField('确认密码',validators=[Required()])
    submit=SubmitField('注册')
    
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经注册.')
            
    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经注册.')
            
class ChangePasswordForm(Form): 
    old_password=StringField('旧密码',validators=[Required()])           
    password=StringField('新密码',validators=[Required(),Length(1,64),EqualTo('password2',message='Password must match.')])        
    password2=StringField('确认密码',validators=[Required(),Length(1,64)])  
    submit=SubmitField('更新')  
    
#重设密码表单
class PasswordResetRequestForm(Form):
    email=StringField('邮箱',validators=[Required(),Length(1,64),Email()])
    submit=SubmitField('重设密码')



class PasswordResetForm(Form):
    email=StringField('邮箱',validators=[Required(),Length(1,64),Email()])  
    password=PasswordField('密码',validators=[Required(),EqualTo('password2',message='Password must match')])
    password2=PasswordField('确认密码',validators=[Required()])
    submit=SubmitField('重设密码') 
    
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('邮箱地址不符')
            
#重设邮件地址
               
class EmailaddressResetForm(Form):      
    email=StringField('新邮箱',validators=[Required(),Length(1,64),Email()])
    password=PasswordField('密码',validators=[Required()])  
    submit=SubmitField('重设邮箱') 
    
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱地址已存在')
            
            

#注销账户            
class DeleteAccountForm(Form):
    old_password=StringField('旧密码',validators=[Required()])
    submit=SubmitField('确认注销')        
        
class DeleteAccountAdminForm(Form):
    old_password=StringField('旧密码',validators=[Required()])
    submit=SubmitField('确认注销')             
            
            
            
            
    
