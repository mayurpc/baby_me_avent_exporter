import web
from web import form
from db_funcs import Dbfuncs

urls = ('/', 'index')

render = web.template.render('/home/kvmtest/PycharmProjects/baby_stats/templates/') # your templates

vusername = form.regexp(r".{6,20}$", 'must be between 6 and 20 characters')
vlimit = form.Validator('Must be more than 5', lambda x:int(x)>5)
vpass = form.regexp(r".{3,20}$", 'must be between 3 and 20 characters')
vemail = form.regexp(r".*@.*", "must be a valid email address")

register_form = form.Form(
    form.Textbox("username", form.notnull,  \
                 vusername, description="Username")
)

class index:

    def __init__(self):
        self.dbf = Dbfuncs()
        self.gotdb = self.dbf.get_connection('baby_stats')

    def GET(self):
        # do $:f.render() in the template
        f = register_form()
        #return f.render()
        return render.formtest(f)

    def POST(self):
        f = register_form()
        if not f.validates():
            print "validation failed"
            return render.formtest(f)
        else:
            print "posting andu", f.d.username
            if self.gotdb.babystat_urls.find({'_id':f.d.username}).count():
                tmp_list = []
                for entries in self.gotdb.babystat_urls.find():
                    print "data stored:", entries
                    self.dbf.delete_doc(gotdb, 'babystat_urls', entries['_id'])
                    tmp_list
                return render.baby_urls('mayur',['https://plot.ly/~m2r0007/34','https://plot.ly/~m2r0007/35'])
            else:
                print "got data"
                return render.upload()

if __name__ == "__main__":
   app = web.application(urls, globals())
   app.run()