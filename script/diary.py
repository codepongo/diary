#coding:utf-8
import datetime
import sys
import os
sys.path.append(os.path.dirname(__file__))
import shutil
import web
import markdown2
perpage = 5
try:
    import conf
    path = conf.path
    css_path = conf.css_path
    js_path = conf.js_path
    player_path = conf.player_path 
    web.config.debug=conf.debug
    domain = conf.domain
except:
    path = './md'
    css_path = './css'
    js_path = './js'
    player_path = './player'
    web.config.debug=True
    domain ='http://127.0.0.1:8080'

class base:
    def __init__(self):
        self.entities = []
        if not os.path.isdir(path):
            os.mkdir(path)
        for p in os.listdir(path):
            if os.path.isdir(p):
                continue
            ext = os.path.splitext(p)[1]
            if ext == '.md':
                self.entities.append(os.path.join(path,p))
        self.entities.sort(reverse=True)
    def entity(self, idx):
        return self.generate(idx-1, idx)
    def page(self, begin=0):
        end = min(begin+perpage,len(self.entities))
        return self.generate(begin, end)
    def generate(self, begin, end):
        es = [] #entities in page
        for i in range(begin, end):
            e = {}
            with open(self.entities[i], 'rb') as f:
                content = f.read()
                e['id'] = i
                e['date'] = os.path.splitext(os.path.basename(self.entities[i]))[0]
                c = markdown2.markdown(content).replace('<img src="', '<img src="/')
                e['content'] = c
                es.append(e)
        return es

class static:
    def GET(self, name, arguments=''):
        folder = path
        if name == 'robots.txt':
            web.header('content-type', 'text/plain')
        elif os.path.splitext(name)[1] == '.css':
            folder = css_path
            web.header('content-type', 'text/css')
        elif os.path.splitext(name)[1] == '.js':
            folder = js_path
            web.header('content-type', 'text/javascript')
        elif os.path.splitext(name)[1] == '.mp3':
            web.header('content-type', 'audio/mp3')
            web.header('content-length', os.path.getsize(os.path.join(path,name)))
        else:
            web.header('content-type', 'image/%s' % os.path.splitext(name)[1].lower())
        with open(os.path.join(folder,name), 'rb') as f:
            content = f.read()
        return content

class player:
    def GET(self, name):
        if name[:3] == '.js':
            web.header('content-type', 'text/plain')
        else:
            web.header('content-type', 'application/x-shockwave-flash')
        with open(os.path.join(player_path,name), 'rb') as f:
            content = f.read()
        return content


class feed(base):
    def GET(self):
        date = datetime.datetime.today().strftime("%a, %d %b %Y %H:%M:%S +0200")
        web.header('Content-Type', 'application/xml')
        templates = os.path.join(os.path.dirname(__file__), 'templates')
        render = web.template.render(templates)
        return render.feed(entities=base.page(self), date=date,domain=domain)

class article():
    def GET(self, name):
        file_path = os.path.join(path, name) + '.md'
        if not os.path.isfile(file_path):
            raise web.seeother('/')
        e = {}
        with open(file_path) as f:
            content = f.read()
            e['date'] = name[:10]
            e['title'] = name[11:]
            c = markdown2.markdown(content).replace('<img src="', '<img src="/')
            e['content'] = c
        templates = os.path.join(os.path.dirname(__file__), 'templates')
        render = web.template.render(templates)
        return render.article(e)


class diary(base):
    def GET(self, t='page', idx=1):
        count = len(self.entities)
        templates = os.path.join(os.path.dirname(__file__), 'templates')
        render = web.template.render(templates)
        prev = True
        next = True
        if t == 'page':
            try:
                idx = int(idx)
            except:
                idx = 1
            pagecount = count / perpage
            if count % perpage != 0:
                pagecount += 1
            if idx >= pagecount:
                idx = pagecount
                next = False
            if idx <= 1:
                idx = 1
                prev = False
            begin = (idx - 1) * perpage
            return render.diary(base.page(self, begin), idx, prev, next, '/page/')
        else:
            try:
                idx = int(t)
            except:
                idx = 1
            if idx <= 1:
                idx = 1
                prev = False
            if idx >= count:
                idx = count
                next = False
            return render.diary(base.entity(self, idx), idx, prev, next)



urls = (
    '/',diary,
    '/player/(.*)', player,
    '/(.*.mp3)(.*)', static,
    '/(.*.JPEG)', static,
    '/(.*.jpeg)', static,
    '/(.*.jpg)', static,
    '/(.*.png)', static,
    '/(.*.bmp)', static,
    '/(.*.css)', static,
    '/(.*.js)', static,
    '/feed', feed,
    '/rss', feed,
    '/(page)/(.*)',diary,
    '/(robots.txt)',static,
    '/article/(.*)',article,
    '/(.*)',diary,

)
app = web.application(urls, globals())
if __name__ == '__main__':
    app.run()
else:
    application = app.wsgifunc()
