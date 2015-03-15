__author__ = 'kvmtest'

__author__ = 'git_admin'

#!/usr/bin/python

from pymongo import MongoClient


class Dbfuncs():

        def __init__(self, ip='127.0.0.1', port=27017 ):
		self.ip = '127.0.0.1'
		self.port = port

	def get_connection(self, db='test_db'):
		#connect to db
		conn = MongoClient(self.ip, self.port)
		db = conn[db]
		return db

	def create_col(self, colname):
                conn_db = self.get_connection()
		conn_colname = conn_db[colname]
		return conn_colname

	def insert_default_cols(db):
		pref_house = db['col_house']
		pref_travel = db['col_travel']
		pref_qol = db['col_qol']

	def insert_bs_db(self, conn_db, col_ref, username, data):
            conn_colname = conn_db[col_ref]
            update_data = data.copy()
            update_data.update({'_id':username})
            if not update_data:
                print "None as update/insert data"
            print "updating", update_data
            if conn_colname.find({'_id':username}).count():
                print "old user:",data
                conn_colname.update({'_id':username}, {"$set": data}, upsert=False)
                #conn_colname.update(update_data, data,True)
            else:
                print "new user:",update_data
                conn_colname.insert(update_data, data,True)

	def insert_2_db(self, col_ref, data):
                conn_db = self.get_connection()
		conn_colname = conn_db[col_ref]

		conn_colname.update({"_id":data["_id"]}, data,True)

	def delete_doc(self, db, col_name, data_id):
		db[col_name].remove({'_id':data_id})

	def delete_all_col_data(self, db, col_name):
            for entries in db.col_name.find():
                db[col_name].remove(entries['_id'])

	def find_results_db(self, dbname, colname,key,data):
		db = self.get_connection(dbname)
		user_result = db[colname]
		#get user results based on uuid
		user_results = (user_result.find({key:data})).count()
		print "user results db", user_results, "key", key,"data",data
	        if user_results>0:
		    return True
		else:
		    return False

	def find_user_results(self, colname,key,data):
		db = self.get_connection()
		user_result = db[colname]
		#get user results based on uuid
		user_results = (user_result.find({key:data})).count()
		print "user results", user_results, "key", key,"data",data
	        if user_results>0:
		    return True
		else:
		    return False

def testing():
    dbf = Dbfuncs()
    gotdb = dbf.get_connection('baby_stats')
    print "dbname:", gotdb
    data = {'urls':{'nappy_url':'https://plot.ly/~m2r0007/34', \
                    'feedng_url':'https://plot.ly/~m2r0007/35', \
                    'diaper_url':'https://plot.ly/~m2r0007/36'}}

    #print "inset", gotdb.urls.insert({"_id":'mays'},data)
    dbf.insert_bs_db(gotdb, 'babystat_urls', 'mays', data)
    for entries in gotdb.babystat_urls.find():
        print "data stored:", entries
        dbf.delete_doc(gotdb, 'babystat_urls', entries['_id'])


