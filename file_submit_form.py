__author__ = 'kvmtest'

import web
import os
from web import form
import csv
from babyi_stats import StatsParser
import datetime
import os,errno
from db_funcs import Dbfuncs


#urls = ('/upload', 'Upload', '/', 'Babystats', '/', 'index')
#urls = ('/upload', 'Upload', '/', 'index', 'upload', 'Upload')
urls = ('/upload', 'Upload', '/', 'Upload', 'upload', 'Upload')

render = web.template.render('templates/')

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
            print "user posting:", f.d.username
            if self.gotdb.babystat_urls.find({'_id':f.d.username}).count():
                tmp_list = []
                entries = self.gotdb.babystat_urls.find_one({'_id':f.d.username})
                print "data stored:", entries
                tmp_list = [entries['feeding'], entries['sleeping'], entries['Diaper']]
                return render.baby_urls(f.d.username,tmp_list)
            else:
                print "got data"
                raise web.seeother('upload')
                #return render.upload()


class Upload:
    def __init__(self):
        self.dbf = Dbfuncs()
        self.gotdb = self.dbf.get_connection('baby_stats')

    def GET(self):
        return render.upload()


    def POST(self):
        xf = web.input(feedingfile={})
        xs = web.input(sleepingfile={})
        xd = web.input(diaperfile={})

        user = web.input(text="None")
        self.username = user.username
        print "user is :", user.username

        #raise web.seeother('/upload')
        print "posting andu", self.username
        if self.gotdb.babystat_urls.find({'_id':self.username}).count() and (not xf['feedingfile'].value ):
                tmp_list = []
                entries = self.gotdb.babystat_urls.find_one({'_id':self.username})
                print "data stored:", entries
                tmp_list = [entries['feeding'], entries['sleeping'], entries['Diaper']]
                return render.baby_urls(self.username,tmp_list)

        else:
            if (xf['feedingfile'].value):
                self.store_feeding(xf)

            if (xs['sleepingfile'].value):
                self.store_sleeping(xs)

            if (xd['diaperfile'].value):
                self.store_diaper(xd)

            if self.gotdb.babystat_urls.find({'_id':self.username}).count():
                tmp_list = []
                entries = self.gotdb.babystat_urls.find_one({'_id':self.username})
                print "data stored:", entries
                tmp_list = [entries['feeding'], entries['sleeping'], entries['Diaper']]
                return render.baby_urls(self.username,tmp_list)

    def store_feeding (self, x):
        web.debug(x['feedingfile'].filename) # This is the filename
        web.debug(x['feedingfile'].value) # This is the file contents
        web.debug(x['feedingfile'].file.read()) # Or use a file(-like) object

        filedir = os.getcwd() + '/' + self.username + '/' # change this to the directory you want to store the file in.
        directory = os.path.dirname(filedir)
        try:
            os.makedirs(directory)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        if ('feedingfile' in x) or ('sleepingfile' in x) or ('diaperfile' in x): # to check if the file-object is created
            filepath=x.feedingfile.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
            filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
            fout = open(filedir + filename,'w') # creates the file where the uploaded file should be stored
            fout.write(x.feedingfile.value) # writes the uploaded file to the newly created file.
            fout.close() # closes the file, upload complete.


        if (x['feedingfile'].value):
            filename_dir = filedir + x['feedingfile'].filename
            #self.plot_feeding(x['feedingfile'].filename)
            self.plot_feeding(filename_dir)

    def store_sleeping (self, x):
        web.debug(x['sleepingfile'].filename) # This is the filename
        web.debug(x['sleepingfile'].value) # This is the file contents
        web.debug(x['sleepingfile'].file.read()) # Or use a file(-like) object

        filedir = os.getcwd() + '/' + self.username + '/' # change this to the directory you want to store the file in.
        directory = os.path.dirname(filedir)
        try:
            os.makedirs(directory)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

        if ('feedingfile' in x) or ('sleepingfile' in x) or ('diaperfile' in x): # to check if the file-object is created
            filepath=x.sleepingfile.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
            filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
            fout = open(filedir + filename,'w') # creates the file where the uploaded file should be stored
            fout.write(x.sleepingfile.value) # writes the uploaded file to the newly created file.
            fout.close() # closes the file, upload complete.


        if (x['sleepingfile'].value):
            filename_dir = filedir + x['sleepingfile'].filename
            self.plot_sleeping(filename_dir)

    def store_diaper (self, x):
        web.debug(x['diaperfile'].filename) # This is the filename
        web.debug(x['diaperfile'].value) # This is the file contents
        web.debug(x['diaperfile'].file.read()) # Or use a file(-like) object

        filedir = os.getcwd() + '/' + self.username + '/' # change this to the directory you want to store the file in.
        directory = os.path.dirname(filedir)
        try:
            os.makedirs(directory)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

        if ('feedingfile' in x) or ('sleepingfile' in x) or ('diaperfile' in x): # to check if the file-object is created
            filepath=x.diaperfile.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
            filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
            fout = open(filedir + filename,'w') # creates the file where the uploaded file should be stored
            fout.write(x.diaperfile.value) # writes the uploaded file to the newly created file.
            fout.close() # closes the file, upload complete.


        if (x['diaperfile'].value):
            filename_dir = filedir + x['diaperfile'].filename
            self.plot_diapers(filename_dir)


    def plot_feeding(self, filename):
        graphname = 'feeding'
        parsr = StatsParser()
        csvdata = parsr.read_csv_data(filename, 'feeding')
        feeding_data = parsr.parse_feeding_data(csvdata)
        xdate = []
        ytotal = []
        ybftime = []
        for x,y in feeding_data.iteritems():
          xdate.append(x)

        xxdate = sorted(xdate, key=lambda x: datetime.datetime.strptime(x, '%a %d %b %Y'))

        for edate in xxdate:
          ytotal.append(feeding_data[edate]['total'])
          ybftime.append(feeding_data[edate]['BFTime'])

        parsr.plotter(xxdate, ytotal, ybftime, self.username, graphname)

    def plot_sleeping(self, filename):
        graphname = 'sleeping'
        parsr = StatsParser()
        csvdata = parsr.read_csv(filename, 'sleeping')
        sleeping_data = parsr.parse_sleeping_data(csvdata)
        print "sleeping data", sleeping_data
        xdate = []
        ytotal = []
        ysleeptime = []
        for x,y in sleeping_data.iteritems():
          xdate.append(x)
        xxdate = sorted(xdate, key=lambda x: datetime.datetime.strptime(x, '%a %d %b %Y'))

        for edate in xxdate:
          ytotal.append(sleeping_data[edate]['total'])
          ysleeptime.append(sleeping_data[edate]['SleepTime'])

        parsr.plotter(xxdate, ytotal, ysleeptime, self.username, graphname)

    def plot_diapers(self, filename):
        graphname = 'Diaper'
        parsr = StatsParser()
        csvdata = parsr.read_csv(filename, 'diaper')
        diaper_data =  parsr.parse_diapers_data(csvdata)

        xdate = []
        ytotal = []
        ywet = []
        for x,y in diaper_data.iteritems():
          xdate.append(x)

        xxdate = sorted(xdate, key=lambda x: datetime.datetime.strptime(x, '%a %d %b %Y'))
        for edate in xxdate:
          ytotal.append(diaper_data[edate]['total'])
          ywet.append(diaper_data[edate]['dirty'])
        parsr.plotter(xxdate, ytotal, ywet, self.username, graphname)

class Babystats:
    def GET(self):
        return render.babystats()

if __name__ == "__main__":
   app = web.application(urls, globals())
   app.run()
