import os 

from flask import Flask, render_template

app = Flask('uco')


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/compare', methods=['GET', 'POST'])
def compare(): 
	message = None
	os.system('scrapy runspider asana_test.py')

	# if request.method == 'POST':
	# 	datafromjs = request.form['mydata']
	# 	result = 'return this'
	# 	resp = make_response('{"response": '+result+'}')
	# 	resp.headers['Content-Type'] = "application/json"
	# 	return resp
	return render_template('changes.html', message='')

if __name__ == '__main__':
    app.run()