#-*-coding:utf-8-*-

#这是认证蓝本的登录表单

from flask_wtf import Form
from wtforms import StringField,PasswordField,BooleanField, SubmitField
from wtforms.validators import Required,Length,Email,Regexp,EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(Form):
    email=StringField('Email',validators=[Required(),Length(1,64),Email()])
    password=PasswordField('password',validators=[Required()])
    remember_me=BooleanField('Keep me logged in')
    submit=SubmitField('Log In')
    
class RegistrationForm(Form):
    email=StringField('Email',validators=[Required(),Length(1,64),Email()])
    username=StringField('Username',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][a-zA-Z_.]*$',0,'Usernames must have only\                         letters,numbers,dots or underscores')])
    password=PasswordField('Password',validators=[Required(),EqualTo('password2',message='Passwords must math.')])
    password2=PasswordField('Confirm password',validators=[Required()])
    submit=SubmitField('Register')
    
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
            
    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')
            
class ChangePasswordForm(Form): 
    old_password=StringField('Old password',validators=[Required()])           
    password=StringField('New Password',validators=[Required(),Length(1,64),EqualTo('password2',message='Password must match.')])        
    password2=StringField('Confirm Password',validators=[Required(),Length(1,64)])  
    submit=SubmitField('update')  
    
#重设密码表单
class PasswordResetRequestForm(Form):
    email=StringField('Email',validators=[Required(),Length(1,64),Email()])
    submit=SubmitField('重设密码')



class PasswordResetForm(Form):
    email=StringField('Email',validators=[Required(),Length(1,64),Email()])  
    password=PasswordField('New Password',validators=[Required(),EqualTo('password2',message='Password must match')])
    password2=PasswordField('Confirm Password',validators=[Required()])
    submit=SubmitField('重设密码') 
    
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('邮箱地址不符')
            
#重设邮件地址
               
class EmailaddressResetForm(Form):      
    email=StringField('New_Email',validators=[Required(),Length(1,64),Email()])
    password=PasswordField('Password',validators=[Required()])  
    submit=SubmitField('重设邮箱') 
    
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱地址已存在')
            
            
            
            
            
            
            
    
