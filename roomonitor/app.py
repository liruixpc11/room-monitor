import web

urls = (
    '/', 'index'
)
app = web.application(urls, globals())


class index:
    def GET(self):
        pass


if __name__ == '__main__':
    app.run()
else:
    application = app.wsgifunc()

