# -*-coding:utf-8 -*-

#这是启动文件

import os

from naruto import create_app,db
from naruto.models import User,Role,Permission,Post,Follow,Comment
from flask_script import Manager,Shell
from flask_migrate import Migrate,MigrateCommand

#将程序实例作为参数传入并构造实例
app=create_app(os.getenv('FLASK_CONFIG') or 'default')

migrate=Migrate(app,db)

#覆盖检测
COV=None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV=coverage.coverage(branch=True,include='naruto/*')
    COV.start() 

def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role,Permission=Permission,Post=Post,Follow=Follow,Comment=Comment)

manager=Manager(app)

manager.add_command('shell',Shell(make_context=make_shell_context))
manager.add_command('db',MigrateCommand)



@manager.command
def test(coverage=False):
    '''Run the unit tests.'''
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE']='1'
        os.execvp(sys.executable,[sys.executable]+sys.argv)
    import unittest
    tests=unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print 'Coverage Summary:'
        COV.report()
        basedir=os.path.abspath(os.path.dirname(__file__))
        covdir=os.path.join(basedir,'tmp/coverage')
        COV.html_report(directory=covdir)
        print 'HTML version:file://%s/index.html'%covdir
        COV.erase()

@manager.command
def profile(length=25,profile_dir=None):
    '''Start the application under the code profiler.'''
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app=ProfilerMiddleware(app.wsgi_app,restrictions=[length],profile_dir=profile_dir)
    
    app.run()        
#部署命令
@manager.command
def deploy():
    '''Run deployment tasks.'''
    from flask_migrate import upgrade
    from naruto.models import Role,User
    #迁移数据库
    upgrade()
    
    #创建用户角色
    Role.insert_roles()
    
    #关注自己
    User.add_self_follows()    


if __name__=='__main__':
    manager.run()
