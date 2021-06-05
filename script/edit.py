#using:encoding=utf8
import web
import sys
import os
import markdown2
try:
    import conf
    title = conf.title
    password = conf.password
    resume_path = conf.resume_path
except:
    title = 'password is 12345678900 for test'
    password = '12345678900'
    resume_path = os.path.join(os.path.split(os.path.dirname(__file__))[0], 'data')
    print resume_path

class authentication:
    def GET(self):
        return web.config._render.login(title)
    def POST(self):
        if web.input().passwd == password:
            web.config._session.authentication = True
            return web.seeother('/resume')
        else:
            return web.config._render.login(title, True)
class view:
    def GET(self):
        if not web.config._session.authentication:
            return web.seeother('/resume/login')
        else:
            html = ''
            with open(os.path.join(resume_path, 'resume.md'), 'rb') as f:
                html = markdown2.markdown(f.read())
            return web.config._render.resume(html)

class download:
    def GET(self, file_type):
        if not web.config._session.authentication:
            return web.config._render.login(title)
        else:
            if file_type == '.txt':
                file_type = '.md'
            f = os.path.join(resume_path, 'resume'+file_type)
            if not os.path.isfile(f):
                return web.seeother('/resume')
            web.header('content-type', 'application/octet-stream')
            c = ''
            with open(f, 'rb') as f:
                c = f.read()
            return c

