#-*-coding:utf-8-*-

#这是登录用户的视图文件

import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

from flask import render_template,redirect,request,url_for,flash
from flask_login import login_user,logout_user,login_required,current_user
from . import auth
from ..models import User
from .forms import LoginForm,RegistrationForm,ChangePasswordForm,PasswordResetRequestForm,PasswordResetForm,EmailaddressResetForm
from ..email import send_email
from .. import db
from datetime import datetime
from ..decorators import admin_required

@auth.before_app_request
def before_request():
    if current_user.is_authenticated():
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5]!='auth.':#请求的末尾的视图函数不是auth打头的
            return redirect(url_for('auth.unconfirmed'))

@auth.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html',form=form)
    
#这是登出视图文件

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))
    
#注册路由
@auth.route('/register',methods=['GET','POST'])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        user=User(email=form.email.data,username=form.username.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token=user.generate_confirmation_token()
        send_email(user.email,'Confirm Your Account','auth/email/confirm',user=user,token=token)
        flash('A confirmation email has been sent to your email.')
        return redirect(url_for('main.index'))
        
    return render_template('auth/register.html',form=form)
        
#确认账户
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account.Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))        
        
#过滤未确认的用户
@auth.before_app_request
def before_request():
    if current_user.is_authenticated() and not current_user.confirmed and request.endpoint[:5]!='auth.'\
    and request.endpoint!='static':
        return redirect(url_for('auth.unconfirmed'))
        
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous() or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html',current_time=datetime.now())

#发送确认邮件
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token=current_user.generate_confirmation_token()
    send_email(current_user.email,'Confirm Your Account','auth/email/confirm',user=current_user,token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))
    
#修改密码
@auth.route('/change-password',methods=['GET','POST'])
@login_required
def change_password():
    form=ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password=form.password.data
            db.session.add(current_user)
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template('auth/change-password.html',form=form)
            
#重设密码
@auth.route('/reset',methods=['GET','POST'])#定义路由
def password_reset_request():#视图函数
    if not current_user.is_anonymous:#如果当前用户不是匿名用户
        return redirect(url_for('main.index'))#返回首页，是的话直接修改密码了
    form=PasswordResetRequestForm()#加载请求重设密码请求表单
    if form.validate_on_submit():#表单符合要求
        user=User.query.filter_by(email=form.email.data).first()#查询数据库email列中符合表单email数据的第一个用户
        if user:
            token=user.generate_reset_token()#在数据库模型中
            send_email(user.email,'Reset Your Password','auth/email/reset_password',user=user,token=token,next=request.args.get('next'))
        flash('An email with instructions to reset your password has been '
              'sent to you.')   
        return redirect(url_for('auth.login'))#如果成功，就去登录界面
    return render_template('auth/reset-password.html',form=form) 
    
@auth.route('/reset/<token>',methods=['GET','POST'])#定义重设路由
def password_reset(token):
    if not current_user.is_anonymous:#不是匿名用户
        return redirect(url_for('main.index'))#带他走
    form=PasswordResetForm()#重设表单
    if form.validate_on_submit():#表单合格
        user=User.query.filter_by(email=form.email.data).first()#查询数据库
        if user is None:#没有注册
            return redirect(url_for('main.index'))#你走开
        if user.reset_password(token,form.password.data):#数据模型更行成功
            flash('Your password has been updated.')#提示语
            return redirect(url_for('auth.login'))#定向登录界面
        else:
            return redirect(url_for('main.index'))#要不你走
    return render_template('auth/reset-password.html',form=form)#表单不合格重新渲染
    
#重设邮箱
@auth.route('/reset-email',methods=['GET','POST'])
@login_required#登录后才能重设
def reset_email_address():
    form=EmailaddressResetForm()#加载请求重设邮箱请求表单
    if form.validate_on_submit():#表单符合要求
        if current_user.verify_password(form.password.data):#如果数据库中的密码哈希值等于表单中的
            new_email=form.email.data#记录新邮箱
            token=current_user.generate_email_change_token(new_email)#生成新令牌
            send_email(new_email,'Confirm your email address','auth/email/change_email',user=current_user,token=token)
        flash('An email with instructions to confirm your emailaddress has been '
              'sent to you.')   
        return redirect(url_for('main.index'))#如果成功，就去登录主留言、博客界面
    else:
        flash('Invalid email or password') 
    return render_template('auth/change-email.html',form=form)
    
@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index')) 
            
            
            
            
            
            
            
            
                  
            
            
            
            
            
            
            
            
            
            
            
                
        
        
        
        
        
        
        
        
        
        
        
