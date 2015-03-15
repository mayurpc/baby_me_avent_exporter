import time
import sys
import csv
import datetime
import numpy
import re

regex_alph = re.compile('[^0-9]')

import plotly.plotly as py
from plotly.graph_objs import *
from db_funcs import Dbfuncs


class StatsParser:

    def __init__ (self):
        self.data_header = []
        self.rownum = 0
        self.colnum = 0
        self.dbf = Dbfuncs()
        self.plotly_username = 'm2r0007'
        self.plotly_token = "2itofo4gss"

    def plotter(self, xdate, ytotal, ywet, username, graphname='diaper'):
        py.sign_in(self.plotly_username, self.plotly_token)
        data = None
        #fill avrgae graph
        yavg = list(xdate)
        bftimeavg = list(xdate)
        sleeptimeavg = list(xdate)
        diaperavg    = list(xdate)
        feedtotalavg = list(xdate)

        for (x, item) in enumerate(yavg):
          yavg[x] = numpy.average(ytotal)
          if graphname == 'feeding':
            bftimeavg[x] = numpy.average(ywet)
            feedtotalavg[x] = numpy.average(ytotal)
          if graphname == 'sleeping':
            sleeptimeavg[x] = numpy.average(ywet)
          if graphname == 'Diaper':
            diaperavg[x] = numpy.average(ywet)

        #nappies time
        if graphname == 'Diaper':
          layout = Layout(title='Fig. nappies')
          totalnappies = Scatter(
                    name = 'totalnappies',
                    x=xdate,
                    y=ytotal)
          wetnappies = Scatter(
                    name = 'wetnappies',
                    x=xdate,
                    y=ywet)
          avgnappies = Scatter(
                    name = 'avgnappies',
                    x=xdate,
                    y=yavg )
          data = Data([totalnappies, wetnappies, avgnappies])

        #feeding time
        if graphname == 'feeding':
          layout = Layout(title='Fig. Feeding')
          totalfeedtime = Scatter(
                    name = 'totalfeednum',
                    x=xdate,
                    y=ytotal)
          eachfeedtime = Scatter(
                    name = 'eachfeedtime',
                    x=xdate,
                    y=ywet)
          avgfeednum = Scatter(
                    name = 'avgfeednum',
                    x=xdate,
                    y=feedtotalavg )
          avgbftime = Scatter(
                    name = 'avgfeeding',
                    x=xdate,
                    y=bftimeavg )
          data = Data([totalfeedtime, eachfeedtime, avgfeednum, avgbftime])

        # sleeping data
        if graphname == 'sleeping':
          # (3) Make Layout object (Layout is dict-like)
          layout = Layout(title='Fig. Sleeping')

          sleeptime = Scatter(
                        name = 'totalsleeptime',
                        x=xdate,
                        y=ywet)
          avgsleeptime = Scatter(
                        name = 'avgsleeptime',
                        x=xdate,
                        y=sleeptimeavg )
          data = Data([sleeptime, avgsleeptime])

        # (4) Make Figure object (Figure is dict-like)
        fig = Figure(data=data, layout=layout)

        if data:
            plot_url = py.plot(fig, filename=(graphname+username), auto_open=False)
            data = {graphname:plot_url}
            gotdb = self.dbf.get_connection('baby_stats')
            self.dbf.insert_bs_db(gotdb, 'babystat_urls', username, data)
            print "url:", plot_url
        else:
            return

    def parse_diapers_data(self, diaper_data):
      tmp_dict = {} # {'date':{'total':2,'wet':2,'dirty':2}}
      for eentry in diaper_data:
	if not eentry:
	  continue
        if eentry['Date'] in tmp_dict:
          tmp_dict[eentry['Date']]['total'] = tmp_dict[eentry['Date']]['total']+ 1
	  if eentry['Value'].find('dirty') < 0:
	    tmp_dict[eentry['Date']]['wet'] = tmp_dict[eentry['Date']]['wet']+ 1 
          else:
	    tmp_dict[eentry['Date']]['dirty'] = tmp_dict[eentry['Date']]['dirty']+ 1
        else:
	  tmp_dict[eentry['Date']] = {'total':1,'wet':1,'dirty':1}	  
      return tmp_dict

    def parse_feeding_data(self,csvdata):
        for ff in csvdata:
          if not ff:
            continue
          '''
          if ff['BFTime'].find('right') > 0:
            tmp = ff['BFTime'].split(' ')
            time = int(tmp[2].split(':')[0])+ int(tmp[5].split(':')[0])
            ff['BFTime'] = str(time)
          '''

          if ff['BFTime'].find(' ') > 0:
            ff['BFTime'] = regex_alph.sub('', ff['BFTime'].split(' ')[0])
        tmp_dict = {}
        for eentry in csvdata:
          if not eentry:
            continue
          if eentry['Date'] in tmp_dict:
              tmp_dict[eentry['Date']]['total'] = tmp_dict[eentry['Date']]['total']+ 1
              #if eentry['BFTime'] in tmp_dict:
              if eentry['BFTime']:
                tmp_dict[eentry['Date']]['BFTime'] = int(tmp_dict[eentry['Date']]['BFTime']) + int(eentry['BFTime'])
          else:
            tmp_dict[eentry['Date']] = {'total':1, 'BFTime':eentry['BFTime']}
        return tmp_dict

    def parse_sleeping_data(self,csvdata):
        for ff in csvdata:
          if not ff:
            continue

          timing = ff['SleepTime'].split('m ')
          if len(timing) > 1:
            timing = timing[0]
          else:
            timing = timing.strip('m')

          timing = timing.split('h ')
          timing = (int(timing[0])*60) + int(timing[1])

          ff['SleepTime'] = timing

        tmp_dict = {}
        for eentry in csvdata:
          if not eentry:
            continue
          if eentry['Date'] in tmp_dict:
              tmp_dict[eentry['Date']]['total'] = tmp_dict[eentry['Date']]['total']+ 1
              #if eentry['BFTime'] in tmp_dict:
              if eentry['SleepTime']:
                tmp_dict[eentry['Date']]['SleepTime'] = int(tmp_dict[eentry['Date']]['SleepTime']) + int(eentry['SleepTime'])
          else:
            tmp_dict[eentry['Date']] = {'total':1, 'SleepTime':eentry['SleepTime']}
        return tmp_dict

    def read_csv_data (self, filename, token):
        tmpdict = {}
        tmplist = []
        #reader = csv.reader(csv_read)
        with open(filename, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                if self.rownum == 0:
                    self.data_header = row
                else:
                    self.colnum = 0
                    if token == 'diaper':
                      tmpdict = {'Date':row[0],'Value':row[2]}
                    if token == 'feeding':
                      if row[5]:
                        time = int(row[5].split('m ')[0]) + int(row[6].split('m ')[0])
                        row[7] = str(time)
                      if len(row) > 6:
                        tmpdict = {'Date':row[0],'BFTime':row[7]}
                    if token == 'sleeping':
                      tmpdict = {'Date':row[0],'SleepTime':row[3]}
                self.rownum +=1
                #print "d:%s", tmplist
                tmplist.append(tmpdict)

        return tmplist

    def read_csv(self, filename, token):
        tmpdict = {}
        tmplist = []
        with open(filename, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
              if self.rownum == 0:
                self.data_header = row
              else:
                self.colnum = 0
                if token == 'diaper':
                  tmpdict = {'Date':row[0],'Value':row[2]}
                if token == 'feeding':
                  if row[5]:
                    time = int(row[5].split('m ')[0]) + int(row[6].split('m ')[0])
                    row[7] = str(time)
                  if len(row) > 6:
                    tmpdict = {'Date':row[0],'BFTime':row[7]}
                if token == 'sleeping':
                  tmpdict = {'Date':row[0],'SleepTime':row[3]}
              self.rownum +=1
              #print "d:%s", tmplist
              tmplist.append(tmpdict)

	return tmplist


def plot_diapers():
    graphname = 'Diaper'
    parsr = StatsParser()
    csvdata = parsr.read_csv('DiapersTrackers.csv', 'diaper')
    diaper_data =  parsr.parse_diapers_data(csvdata)

    xdate = []
    ytotal = []
    ywet = []
    for x,y in diaper_data.iteritems():
      xdate.append(x)
      ytotal.append(y['total'])
      ywet.append(y['dirty'])

    xxdate = sorted(xdate, key=lambda x: datetime.datetime.strptime(x, '%a %d %b %Y'))
    plotter(xxdate, ytotal, ywet, graphname)

def plot_feeding():
    graphname = 'feeding'
    parsr = StatsParser()
    csvdata = parsr.read_csv('FeedingTrackers_orig.csv', 'feeding')
    feeding_data = parsr.parse_feeding_data(csvdata)
    xdate = []
    ytotal = []
    ybftime = []
    for x,y in feeding_data.iteritems():
      xdate.append(x)
      ytotal.append(y['total'])
      ybftime.append(y['BFTime'])

    xxdate = sorted(xdate, key=lambda x: datetime.datetime.strptime(x, '%a %d %b %Y'))
    plotter(xxdate, ytotal, ybftime, graphname)

def plot_sleeping():
    graphname = 'sleeping'
    parsr = StatsParser()
    csvdata = parsr.read_csv('SleepingTrackers.csv', 'sleeping')
    feeding_data = parsr.parse_sleeping_data(csvdata)
    print "sleeping data", feeding_data
    xdate = []
    ytotal = []
    ysleeptime = []
    for x,y in feeding_data.iteritems():
      xdate.append(x)
      ytotal.append(y['total'])
      ysleeptime.append(y['SleepTime'])

    xxdate = sorted(xdate, key=lambda x: datetime.datetime.strptime(x, '%a %d %b %Y'))
    plotter(xxdate, ytotal, ysleeptime, graphname)

'''
if len(sys.argv)<1:
    print "usage : python execute_file option(diaper,feeding)"

if sys.argv[1] == 'diaper':
    print "plotting diaper data"
    plot_diapers()
elif sys.argv[1] == 'feeding':
    print "plotting feeding data"
    plot_feeding()
elif sys.argv[1] == 'sleeping':
    print "plotting sleeping data"
    plot_sleeping()

'''