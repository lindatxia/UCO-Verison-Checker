import os 
import subprocess

from flask import Flask, render_template, request, json

app = Flask('uco')

@app.route('/')
def main():
	return render_template('index.html')

@app.route('/results')
def results():
	return render_template('changes_table.html')

@app.route('/compare', methods=['GET', 'POST'])
def compare(): 
	message = None
	name = request.form['name']
	link = request.form['link'];
	start = request.form['start'];
	end = request.form['end'];
	textFile = request.form['textFile']
	
	os.system('''scrapy runspider scrape.py -a name=%s -a link=%s -a start='%s' -a end='%s' -a textFile='%s' ''' % (name,link,start,end,textFile))

	# if request.method == 'POST':
	# 	datafromjs = request.form['mydata']
	# 	result = 'return this'
	# 	resp = make_response('{"response": '+result+'}')
	# 	resp.headers['Content-Type'] = "application/json"
	# 	return resp
	return ""

if __name__ == '__main__':
    app.run()