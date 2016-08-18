#-*-coding:utf-8-*-

#selenium端测试
import re
from selenium import webdriver
import threading
import time
import unittest
from naruto import create_app,db
from naruto.models import Role,User,Post

class SeleniumTestCase(unittest.TestCase):
    client=None
    
    @classmethod
    def setUpClass(cls):
        #启动浏览器
        try:
            cls.client=webdriver.IE()
        except:
            pass
        if cls.client:
            #创建程序
            cls.app=create_app('tesing')
            cls.app_context=cls.app.app_context()
            cls.app_context.push()
            
            #禁止日志，保持清洁
            import logging
            logger=logging.getLogger('werkzeug')
            logger.setLevel('ERROR')
            
            #创建数据库及虚拟模型
            db.create_all()
            Role.insert_roles()
            User.generate_fake(10)
            Post.generate_fake(10)
            
            #添加管理员
            admin_role=Role.query.filter_by(permission=0xff).first()
            admin=User(email='jhon@example.com',username='jhon',password='cat',role=admin_role,confirmed=True)
            db.session.add(admin)
            db.session.commit()
            
            #在一个线程中启动flask服务器
            threading.Thread(target=cls.app.run).start()
            
            time.sleep(1)
            
    @classmethod
    def tearDownClass(cls):
        if cls.client:
            #关闭服务器及浏览器
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.close()
                
            #销毁数据库
            db.drop_all()
            db.session.remove()
                
            #删除上下文
            cls.app_context.pop()
                
    def setUp(self):
        if not self.client:
            self.skipTest('web brower not availible.')
                
    def tearDown(self):
        pass
            
    
    def test_admin_home_page(self):
        self.client.get('http://localhost:5000/')
        self.assertTrue(re.search('Hello,\s+Stranger!',self.client.page_source))
        
        self.client.find_element_by_link_text('Log In').click()
        self.assertTrue('<h1>Login</h1>'in self.client.page_source)    
        
        self.client.find_element_by_name('email').send_keys('john@excaple.com')    
        self.client.find_element_by_name('password').send_keys('cat')    
        self.client.find_element_by_name('submit').click()   
        self.assertTrue(re.search('Hello,\s+john!',self.client.page_source))   
        
        self.client.find_element_by_link_text('Profile').click()
        self.assertTrue('<h1>john</h1>'in self.client.page_source)    
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
