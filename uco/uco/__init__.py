import os 
import subprocess
import datetime
import time

from flask import Flask, render_template, request, json, send_file, make_response

# On PythonAnywhere, this needs to be 
# from uco.uco import comparison
import comparison

app = Flask(__name__)


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
	
	scrapy_call = '''scrapy runspider scrape.py -a name=%s -a link=%s -a start='%s' -a end='%s' ''' % (name,link,start,end)
	os.system(scrapy_call)
	return ""

@app.route('/results')
def results():
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
	global new_filename
	new_filename = name+date.strftime("%m_%d_%y")+".txt"
	
	# In PythonAnywhere, this needs to be: 
	# scrapy runspider uco/scrape.py... etc. 
	scrapy_call = '''scrapy runspider scrape.py -a name=%s -a link=%s -a start='%s' -a end='%s' ''' % (name,link,start,end)
	os.system(scrapy_call)
	comparison.compare(textFile,new_filename,"templates/changes_table.html")
	return ""

@app.route('/return_files/')
def return_files():
	return send_file('%s' % new_filename , attachment_filename=new_filename, as_attachment = True)

if __name__ == '__main__':
    app.run()