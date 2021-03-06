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
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="uco",
    password="ucodreamteam",
    hostname="uco.mysql.pythonanywhere-services.com",
    databasename="uco$versioning",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 499
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 20
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Connects to the MySQL database
db = SQLAlchemy(app)

##################################
########### MODELS ###############
##################################

class Software(db.Model):

    # id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), primary_key=True)
    isApproved = db.Column(db.Boolean)
    date_added = db.Column(db.DateTime)

    versions = db.relationship('Version', backref='software', lazy=True)

    def __init__(self, name, isApproved, date_added):
    	self.name = name
    	self.isApproved = isApproved
    	self.date_added = date_added


class Version(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    software_name = db.Column(db.String(100), db.ForeignKey('software.name'),
        nullable=False)

    date_last_checked = db.Column(db.DateTime)
    date_last_updated = db.Column(db.DateTime)
    parsed_text = db.Column(db.Text)

    comments = db.relationship('Comment', backref='version', lazy=True)

    def __init__(self, software_name, date_last_checked, date_last_updated, parsed_text):
    	self.software_name = software_name
    	self.date_last_checked = date_last_checked
    	self.date_last_updated = date_last_updated
    	self.parsed_text = parsed_text

    def get_date_last_checked(self):
    	return self.date_last_checked

    def get_parsed_text(self):
        return self.parsed_text

class Comment(db.Model):

	id = db.Column(db.Integer, primary_key=True)
	version_id = db.Column(db.Integer, db.ForeignKey('version.id'), nullable=False)

	comment_text = db.Column(db.Text)
	line_number = db.Column(db.Integer)

	def __init__(self, version_id, comment_text, line_number):
		self.version_id = version_id
		self.comment_text = comment_text
		self.line_number = line_number


class Link(db.Model):

	id = db.Column(db.Integer, primary_key=True)
	version_id = db.Column(db.Integer, db.ForeignKey('version.id'), nullable=False)

	link_type = db.Column(db.String(100))
	address = db.Column(db.Text)
	start_text = db.Column(db.Text)
	end_text = db.Column(db.Text)

	def __init__(self, version_id, link_type, address, start_text, end_text):
		self.version_id = version_id
		self.link_type = link_type
		self.address = address
		self.start_text = start_text
		self.end_text = end_text


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
	new_filename = "uco/uco/"+name+date.strftime("%m_%d_%y")+".txt"

	scrapy_call = '''scrapy runspider uco/uco/scrape.py -a name=%s -a link=%s -a start='%s' -a end='%s' ''' % (name,link,start,end)
	os.system(scrapy_call)
	return ""

@app.route('/results')
def results():
    return render_template('changes_table.html')

@app.route('/help')
def help():
	return render_template('help.html')

@app.route('/list')
def list():
	return render_template('list.html', softwares=Software.query.order_by(Software.name).all())

@app.route('/process', methods=['GET','POST'])
def process():

	name = request.form['name'];
	link = request.form['link'];
	start = request.form['start'];
	end = request.form['end'];

	scrapy_call = '''scrapy runspider uco/uco/scrape.py -a name=%s -a link=%s -a start='%s' -a end='%s' ''' % (name,link,start,end)
	os.system(scrapy_call)

	# New terms will be saved into a file, which we can read to obtain the updated terms of agreement
	date = datetime.today()
	new_filename = "uco/uco/"+name+date.strftime("%m_%d_%y")+".txt"
	f = open(new_filename,"r+")
	text = f.read()
	f.close()

	result = Software.query.filter_by(name=name).count()

    # There exists a record in the database for this particular software
	if result > 0:

		last_version = Version.query.filter_by(software_name=request.form["name"]).order_by(Version.id.desc()).first()
		last_check = Version.get_date_last_checked(last_version)

		version = Version(software_name=request.form["name"], parsed_text=text, date_last_checked=datetime.now(), date_last_updated=None)
		db.session.add(version)
		db.session.commit()

		return render_template('confirm.html', name=name, link=link, start=start, end=end, last_check=last_check)

    # This is a new software being entered into the system/databases
	else:
		software = Software(name=name, date_added=datetime.now(), isApproved=None)
		version = Version(software_name=name, parsed_text=text, date_last_checked=datetime.now(), date_last_updated=None)

		db.session.add(software)
		db.session.add(version)
		db.session.commit()

		return render_template('upload.html', name=name, link=link, start=start, end=end)

@app.route('/compare', methods=['GET', 'POST'])
def compare():
	name = request.form['name'];
	link = request.form['link'];
	start = request.form['start'];
	end = request.form['end'];
	# textFile is the loaded in old terms if applicable
	textFile = request.form['textFile'];
	date = datetime.today()

	new_filename = "uco/uco/"+name+date.strftime("%m_%d_%y")+".txt"

# 	scrapy_call = '''scrapy runspider uco/uco/scrape.py -a name=%s -a link=%s -a start='%s' -a end='%s' ''' % (name,link,start,end)
# 	os.system(scrapy_call)

    # at this point the software is already in the database whether new or not
    # if it is new it was added to the db in the process route
	num_versions = Version.query.filter_by(software_name=request.form["name"]).count()
	# if it's already in the system it will have at least two versions, including the one just scraped
	if num_versions > 1:
	    last_version = Version.query.filter_by(software_name=request.form["name"]).order_by(Version.id.desc()).first()
	    text = Version.get_parsed_text(last_version)
	# if it's new in the system it will have only one version, the one just scraped
	else:
	    text = textFile

	comparison.compare(text,new_filename,"uco/uco/templates/changes_table.html")
	return ""

@app.route('/returndownload', methods=['GET', 'POST'])
def returndownload():
    date = datetime.today()
    new_filename = name+date.strftime("%m_%d_%y")+".txt"
    return Response('',mimetype="text/plain", headers={"Content-Disposition":
                                    "attachment; filename=%s" % new_filename})
	#return send_file('%s' % new_filename , attachment_filename=new_filename, as_attachment = True)

@app.route('/return_files/')
def return_files():
    date = datetime.today()
    new_filename = name+date.strftime("%m_%d_%y")+".txt"
    return Response('',mimetype="text/plain", headers={"Content-Disposition":"attachment; filename=%s" % new_filename})

@app.route('/display_terms/')
def display_terms():
	return render_template('split_changes.html')

@app.route('/backup')
def backup():
	return render_template('backup.html')

@app.route('/backup_scrape_only', methods=['GET','POST'])
def backup_scrape_only():
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
	session['new_filename'] = new_filename
	scrapy_call = '''scrapy runspider uco/uco/scrape.py -a name=%s -a link=%s -a start='%s' -a end='%s' ''' % (name,link,start,end)
	os.system(scrapy_call)
	return ""

@app.route('/backup_compare', methods=['GET', 'POST'])
def backup_compare():
	message = None
	global name
	name = request.form['name'];
	link = request.form['link'];
	start = request.form['start'];
	end = request.form['end'];
	textFile = request.form['textFile'];
	date = datetime.today()

	print(textFile)

	global new_filename
	new_filename = name+date.strftime("%m_%d_%y")+".txt"
	session['new_filename'] = new_filename

	scrapy_call = '''scrapy runspider uco/uco/scrape.py -a name=%s -a link=%s -a start='%s' -a end='%s' ''' % (name,link,start,end)
	os.system(scrapy_call)
	comparison.compare(textFile,new_filename,"uco/uco/templates/backup_changes_table.html")
	return ""

@app.route('/backup_results')
def backup_results():
    return render_template('backup_changes_table.html')

@app.route('/backup_return_files/')
def backup_return_files():
    new_filename = session.get('new_filename', None)
    # filename = new_filename.replace('/uco/uco','')
    return send_file('%s' % new_filename , attachment_filename=new_filename, as_attachment = True)

if __name__ == '__main__':
	app.run(threaded=True)
