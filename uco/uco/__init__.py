import os
import subprocess
import datetime
import time

from datetime import datetime
from flask import Flask, render_template, request, json, send_file, make_response, send_from_directory, Response, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

from . import comparison

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="uco",
    password="ucodreamteam",
    hostname="uco.mysql.pythonanywhere-services.com",
    databasename="uco$versioning",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Connects to the MySQL database
db = SQLAlchemy(app)

import mysql.connector
cnx = mysql.connector.connect(user='uco', 
                        password='ucodreamteam',
                        host='uco.mysql.pythonanywhere-services.com',
                        database='uco$versioning')
cursor = cnx.cursor() 

##################################
########### MODELS ###############
##################################

class Software(db.Model):

    # id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), primary_key=True)
    isApproved = db.Column(db.Boolean)
    date_added = db.Column(db.DateTime)

    versions = db.relationship('Version', backref='software', lazy=True)


class Version(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    software_name = db.Column(db.String(100), db.ForeignKey('software.name'),
        nullable=False)

    date_last_checked = db.Column(db.DateTime)
    date_last_updated = db.Column(db.DateTime)
    parsed_text = db.Column(db.Text)
    
    comments = db.relationship('Comment', backref='version', lazy=True)


class Comment(db.Model):

	id = db.Column(db.Integer, primary_key=True)
	version_id = db.Column(db.Integer, db.ForeignKey('version.id'), nullable=False)

	comment_text = db.Column(db.Text)
	line_number = db.Column(db.Integer)
    

class Link(db.Model):

	id = db.Column(db.Integer, primary_key=True)
	version_id = db.Column(db.Integer, db.ForeignKey('version.id'), nullable=False)

	link_type = db.Column(db.String(100))
	address = db.Column(db.Text)
	start_text = db.Column(db.Text)
	end_text = db.Column(db.Text)


###################################
############ ROUTES ###############
###################################

@app.route('/')
def main():
	return render_template('index.html')

@app.route('/scrape_only', methods=['GET','POST'])
def scrape_only():
	message = None
	global name
	name = request.form['name'];
	link = request.form['link'];
	start = request.form['start'];
	end = request.form['end'];
	textFile = request.form['textFile'];
	date = datetime.today()
	global new_filename
	new_filename = name+date.strftime("%m_%d_%y")+".txt"

	scrapy_call = '''scrapy runspider uco/uco/scrape.py -a name=%s -a link=%s -a start='%s' -a end='%s' ''' % (name,link,start,end)
	os.system(scrapy_call)
	return ""

@app.route('/results')
def results():
    return render_template('changes_table.html')

@app.route('/new')
def new(): 
	return render_template('new.html')

@app.route('/create', methods=['GET','POST'])
def create(): 

	name = request.form['name'];
	link = request.form['link'];
	start = request.form['start'];
	end = request.form['end'];

	scrapy_call = '''scrapy runspider uco/uco/scrape.py -a name=%s -a link=%s -a start='%s' -a end='%s' ''' % (name,link,start,end)
	os.system(scrapy_call)

	# New terms will be saved into a file, which we can read to obtain the updated terms of agreement
	date = datetime.today()
	new_filename = name+date.strftime("%m_%d_%y")+".txt"
	f = open(new_filename,"r+")
	text = f.read()
	f.close()
	
	software = Software(name=request.form["name"], date_added=datetime.now())
	version = Version(software_name=request.form["name"], parsed_text=text, date_last_checked=datetime.now())

	db.session.add(software)
	db.session.add(version)
	db.session.commit()

	return redirect(url_for('list'))

@app.route('/list')
def list(): 
	return render_template('list.html', softwares=Software.query.all())

@app.route('/process', methods=['GET','POST'])
def process(): 

	name = request.form['name'];
	link = request.form['link'];
	start = request.form['start'];
	end = request.form['end'];

	print("Does process have any of these?")
	print(name)
	print(link)
	print(start)
	print(end)

	scrapy_call = '''scrapy runspider uco/uco/scrape.py -a name=%s -a link=%s -a start='%s' -a end='%s' ''' % (name,link,start,end)
	os.system(scrapy_call)

	# New terms will be saved into a file, which we can read to obtain the updated terms of agreement
	date = datetime.today()
	new_filename = name+date.strftime("%m_%d_%y")+".txt"
	f = open(new_filename,"r+")
	text = f.read()
	f.close()
	
	# If there is a record in the database for this particular software, automatically go to compare 

	cursor.execute("SELECT * FROM software WHERE name='%s'" % (name,))
	result = [item[0] for item in cursor.fetchall()]

	if len(result) > 0: 
		# There is a record in the database! Let's compare it 
		print("There is an record in the database!")
		version = Version(software_name=request.form["name"], parsed_text=text, date_last_checked=datetime.now())

		# db.session.add(version)
		# db.session.commit()
		return render_template('confirm.html', name=request.form["name"], link = request.form['link'], start = request.form['start'],end = request.form['end'] )


	else:
		# The system has not seen this 
		software = Software(name=request.form["name"], date_added=datetime.now())
		version = Version(software_name=request.form["name"], parsed_text=text, date_last_checked=datetime.now())

		# db.session.add(software)
		# db.session.add(version)
		# db.session.commit()

		return render_template('upload.html', name=request.form["name"], link = request.form['link'], start = request.form['start'],end = request.form['end'])


	# We need to find the foreign key (which software) for this version 
	# cursor.execute("SELECT id FROM software WHERE name='%s'" % (name,))

	# Since cursor.fetchall() returns a tuple, use a list comprehension to get the first element of the tuple 
	# result = [item[0] for item in cursor.fetchall()][0]


@app.route('/compare', methods=['GET', 'POST'])
def compare():
	message = None
	global name
	name = request.form['name'];
	link = request.form['link'];
	start = request.form['start'];
	end = request.form['end'];
	textFile = request.form['textFile'];
	date = datetime.today()
	
	global new_filename
	new_filename = name+date.strftime("%m_%d_%y")+".txt"

	scrapy_call = '''scrapy runspider uco/uco/scrape.py -a name=%s -a link=%s -a start='%s' -a end='%s' ''' % (name,link,start,end)
	os.system(scrapy_call)
	comparison.compare(textFile,new_filename,"uco/uco/templates/changes_table.html")
	return ""

@app.route('/returndownload', methods=['GET', 'POST'])
def returndownload():
    date = datetime.today()
    new_filename = name+date.strftime("%m_%d_%y")+".txt"
    return Response('',mimetype="text/plain", headers={"Content-Disposition":
                                    "attachment; filename=%s" % new_filename})

@app.route('/return_files/')
def return_files():
	#return send_file('%s' % new_filename , attachment_filename=new_filename, as_attachment = True)
	return ''


if __name__ == '__main__':
	app.run(threaded=True)
