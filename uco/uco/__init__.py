import os 

from flask import Flask, render_template, request, json

app = Flask('uco')

@app.route('/')
def main():
	return render_template('index.html')

@app.route('/compare', methods=['GET', 'POST'])
def compare(): 
	message = None
	print("starting compare")
	name = request.form['name']
	print(name)
	link = request.form['link'];
	print(link)
	start = request.form['start'];
	print(start)
	end = request.form['end'];
	print(end)
	print("finished compare")
	# print('old_file' in request.files)
	# old_terms = request.files['old_file'];
	# print(old_terms)
	
	os.system('''scrapy runspider scrape.py -a name=%s -a link=%s -a start='%s' -a end='%s' ''' % (name,link,start,end))

	# if request.method == 'POST':
	# 	datafromjs = request.form['mydata']
	# 	result = 'return this'
	# 	resp = make_response('{"response": '+result+'}')
	# 	resp.headers['Content-Type'] = "application/json"
	# 	return resp
	return render_template('changes.html', message='')

if __name__ == '__main__':
    app.run()