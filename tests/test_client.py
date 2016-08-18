#-*-coding:utf-8-*-

#flask客户端测试框架

from flask import url_for
import unittest
from naruto import create_app,db
from naruto.models import User,Role
import re

class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app=create_app('testing')
        self.app_context=self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client=self.app.test_client(use_cookies=True)
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_home_page(self):
        response=self.client.get(url_for('main.index'))
        self.assertTrue('Stranger'in response.get_data(as_text=True))
        
    #注册新账户
    def test_register_and_login(self):
        response=self.client.post(url_for('auth.register'),data={
                                                                'email':'john@example.com',
                                                                'username':'john',
                                                                'password':'cat',
                                                                'password2':'cat'
                                                                })
        self.assertTrue(response.status_code==302)
        
        #登录新账户
        response=self.client.post(url_for('auth.login'),data={
                                                            'email':'john@example.com',
                                                            'password':'cat'
                                                            },follow_redirects=True)
        data=response.get_data(as_text=True)
        self.assertTrue(re.search('Hello,\s+john!',data))
        self.assertTrue('You have not confirmed your account yet.' in data)
        
        #发送令牌
        user=User.query.filter_by(email='john@example.com').first()
        token=user.generate_confirmation_token()
        response=self.client.get(url_for('auth.confirm',token=token),follow_redirects=True)
        data=response.get_data(as_text=True)
        self.assertTrue('You have confirmed your account.Thanks!' in data)
        
        #退出
        response=self.client.get(url_for('auth.logout'),follow_redirects=True)
        data=response.get_data(as_text=True)
        self.assertTrue('You have been logged out.' in data)
       
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
                                                                
