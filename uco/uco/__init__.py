import os 
import subprocess

from flask import Flask, render_template, request, json, send_file, make_response

import comparison

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
	global name
	name = request.form['name'];
	link = request.form['link'];
	start = request.form['start'];
	end = request.form['end'];
	textFile = request.form['textFile'];
	global new_filename
	new_filename = name+".txt"
	
	scrapy_call = '''scrapy runspider scrape.py -a name=%s -a link=%s -a start='%s' -a end='%s' ''' % (name,link,start,end)
	print(scrapy_call)
	os.system(scrapy_call)
	comparison.compare(textFile,new_filename,"templates/changes_table.html")

	# if request.method == 'POST':
	# 	datafromjs = request.form['mydata']
	# 	result = 'return this'
	# 	resp = make_response('{"response": '+result+'}')
	# 	resp.headers['Content-Type'] = "application/json"
	# 	return resp
	return ""

@app.route('/return_files/')
def return_files_tut():
	try:
		# response = make_response(new_filename)
		# cd = 'attachment; filename=%s' % new_filename
		# response.headers['Content-Disposition'] = cd 
		# response.mimetype='text/txt'
		# return response
		return send_file('%s' % new_filename , attachment_filename='%s.txt' % name, as_attachment = True)
	except Exception as e:
		return str("It failed yo..."+e)

if __name__ == '__main__':
    app.run(debug=True)