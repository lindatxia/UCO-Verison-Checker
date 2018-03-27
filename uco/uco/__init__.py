import os 

from flask import Flask, render_template

app = Flask('uco')


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/compare', methods=['GET', 'POST'])
def compare(): 
	message = None
	# command = '''scrapy runspider scrape.py 
	# -a link=https://asana.com/terms 
	# start="Asana User Terms of Service"
	# end="an integral link."
	# '''
	os.system('''scrapy runspider scrape.py -a link=https://asana.com/terms -a start='Asana User Terms of Service' -a end='an integral link.' ''')

	# if request.method == 'POST':
	# 	datafromjs = request.form['mydata']
	# 	result = 'return this'
	# 	resp = make_response('{"response": '+result+'}')
	# 	resp.headers['Content-Type'] = "application/json"
	# 	return resp
	return render_template('changes.html', message='')

if __name__ == '__main__':
    app.run()