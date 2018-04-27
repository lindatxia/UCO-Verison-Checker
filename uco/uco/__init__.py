import os
import subprocess
import datetime
import time

from flask import Flask, render_template, request, json, send_file, make_response, send_from_directory, Response, session
from flask_sqlalchemy import SQLAlchemy

from . import comparison

app = Flask(__name__)

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
	date = datetime.date.today()
	global new_filename
	new_filename = name+date.strftime("%m_%d_%y")+".txt"

	scrapy_call = '''scrapy runspider uco/uco/scrape.py -a name=%s -a link=%s -a start='%s' -a end='%s' ''' % (name,link,start,end)
	os.system(scrapy_call)
	return ""

@app.route('/results')
def results():
    my_var = request.args.get('my_var', None)
    return render_template('changes_table.html')

@app.route('/compare', methods=['GET', 'POST'])
def compare():
	message = None
	global name
	name = request.form['name'];
	link = request.form['link'];
	start = request.form['start'];
	end = request.form['end'];
	textFile = request.form['textFile'];
	date = datetime.date.today()
	# I dont think this global works in this context between routes
	global new_filename
	new_filename = name+date.strftime("%m_%d_%y")+".txt"

	session['name'] = name

	scrapy_call = '''scrapy runspider uco/uco/scrape.py -a name=%s -a link=%s -a start='%s' -a end='%s' ''' % (name,link,start,end)
	os.system(scrapy_call)
	comparison.compare(textFile,new_filename,"uco/uco/templates/changes_table.html")
	return ""

@app.route('/returndownload', methods=['GET', 'POST'])
def returndownload():
    # name = session.get('name')
    date = datetime.date.today()
    new_filename = name+date.strftime("%m_%d_%y")+".txt"
    return Response('',mimetype="text/plain", headers={"Content-Disposition":
                                    "attachment; filename=%s" % new_filename})

@app.route('/return_files/')
def return_files():
	#return send_file('%s' % new_filename , attachment_filename=new_filename, as_attachment = True)
	return ''


if __name__ == '__main__':
	db.create_all()
	app.run()