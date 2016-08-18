#-*-coding:utf-8-*-

#这是密码散列化测试模型

import unittest
from naruto.models import User,Role,AnonymousUser,Permission,Follow
import time
from datetime import datetime
from naruto import create_app,db

class UserModelTestCase(unittest.TestCase):
    #创建测试上下文
    def setUp(self):
        self.app=create_app('testing')
        self.app_context=self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
    
    #关闭测试    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    

    #测试密码是否已经hash
    def test_password_setter(self):
        u=User(password='cat')
        self.assertTrue(u.password_hash is not None)
     
    #测试是否还具有password属性，即不可逆性   
    def test_no_password_getter(self):
        u=User(password='cat')
        with self.assertRaises(AttributeError):
            u.password
    
    #测试密码验证功能是否实现        
    def test_password_verification(self):
        u=User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))
    
    #测试不同的数据模型使用相同的密码，能否生成相同的hash值    
    def test_password_salts_are_random(self):
        u=User(password='cat')
        u2=User(password='cat')
        self.assertTrue(u.password_hash!=u2.password_hash)
        
    #测试角色权限
    def test_roles_and_permissions(self):
        u=User(email='josthbn@example.com')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))
        
    def test_anonymous_user(self):
        u=AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
        
    #测试令牌生成及验证
    def test_valid_confirmation_token(self):
        u=User(password='cat')
        db.session.add(u)
        db.session.commit()
        token=u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))
        
    #不同用户令牌不同
    def test_invalid_confirmation_token(self):
        u1=User(password='cat')
        u2=User(password='cat')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token=u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))
        
    #不同令牌保质期
    def test_expired_confirmation_token(self):
        u=User(password='cat')
        db.session.add(u)
        db.session.commit()
        token=u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))
        
    #重置密码令牌
    def test_valid_reset_token(self):
        u=User(password='cat')
        db.session.add(u)
        db.session.commit()
        token=u.generate_reset_token()
        self.assertTrue(u.reset_password(token,'dog')) 
        self.assertTrue(u.verify_password('dog'))
        
    #不同用户重置密码令牌
    def test_invalid_reset_token(self):
        u1=User(password='cat')
        u2=User(password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token=u1.generate_reset_token()
        self.assertFalse(u2.reset_password(token,'horse')) 
        self.assertTrue(u2.verify_password('dog'))
        
    #更改新邮箱
    def test_valid_email_change_token(self):
        u=User(email='oahfoaohgblsg@example.com',password='cat')
        db.session.add(u)
        db.session.commit()
        token=u.generate_email_change_token('susan@example.cn')
        self.assertTrue(u.change_email(token))
        self.assertTrue(u.email=='susan@example.cn')
        
    #不同用户更改新邮箱
    def test_invalid_email_change_token(self):
        u1=User(email='oahfoaohgblsg@example.com',password='cat')
        u2=User(email='oahfohgblsg@example.com',password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token=u1.generate_email_change_token('susan@example.cn')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email=='oahfohgblsg@example.com')
    
    #    
    def test_duplicate_email_change_token(self):
        u1 = User(email='john@example.com', password='cat')
        u2 = User(email='susan@example.org', password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u2.generate_email_change_token('john@example.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'susan@example.org') 
        
    #测试邮戳
    def test_timestamps(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        self.assertTrue(
            (datetime.utcnow() - u.member_since).total_seconds() < 3)
        self.assertTrue(
            (datetime.utcnow() - u.last_seen).total_seconds() < 3)
            
    #测试时间
    def test_ping(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        time.sleep(2)
        last_seen_before = u.last_seen
        u.ping()
        self.assertTrue(u.last_seen > last_seen_before)
        
    #测试头像
    def test_gravatar(self):
        u = User(email='john@example.com', password='cat')
        with self.app.test_request_context('/'):
            gravatar = u.gravatar()
            gravatar_256 = u.gravatar(size=256)
            gravatar_pg = u.gravatar(rating='pg')
            gravatar_retro = u.gravatar(default='retro')
        with self.app.test_request_context('/', base_url='https://example.com'):
            gravatar_ssl = u.gravatar()
        self.assertTrue('http://www.gravatar.com/avatar/' +
                        'd4c74594d841139328695756648b6bd6'in gravatar)
        self.assertTrue('s=256' in gravatar_256)
        self.assertTrue('r=pg' in gravatar_pg)
        self.assertTrue('d=retro' in gravatar_retro)
        self.assertFalse('https://secure.gravatar.com/avatar/' +
                        'd4c74594d841139328695756648b6bd6' in gravatar_ssl)
    #测试评论
    def test_follows(self):
        u1 = User(email='john@example.com', password='cat')
        u2 = User(email='susan@example.org', password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        timestamp_before = datetime.utcnow()
        u1.follow(u2)
        db.session.add(u1)
        db.session.commit()
        timestamp_after = datetime.utcnow()
        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        self.assertTrue(u2.is_followed_by(u1))
        self.assertTrue(u1.followed.count() == 2)
        self.assertTrue(u2.follower.count() == 2)
        f = u1.followed.all()[-1]
        self.assertTrue(f.followed == u2)
        self.assertTrue(timestamp_before <= f.timestamp <= timestamp_after)
        f = u2.follower.all()[-1]
        self.assertTrue(f.follower == u1)
        u1.unfollow(u2)
        db.session.add(u1)
        db.session.commit()
        self.assertTrue(u1.followed.count() == 1)
        self.assertTrue(u2.follower.count() == 1)
        self.assertTrue(Follow.query.count() == 2)
        u2.follow(u1)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        db.session.delete(u2)
        db.session.commit()
        self.assertTrue(Follow.query.count() == 1)
    
    #测试json转换    
    def test_to_json(self):
        u = User(email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()
        json_user = u.to_json()
        expected_keys = ['url', 'username', 'member_since', 'last_seen',
                         'posts', 'followed_posts', 'post_count']
        self.assertEqual(sorted(json_user.keys()), sorted(expected_keys))
        self.assertTrue('api/v1.0/users/' in json_user['url'])
        
        
        
        
        
        
        
        
        
        
        
        
        
