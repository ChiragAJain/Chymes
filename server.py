from flask import Flask,url_for,render_template,request,redirect
import csv
app=Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<string:page_name>')
def html_page(page_name):
    return render_template(page_name)

def write_file(data):
    with open('feedback.csv','a+',newline='') as database:
        email = data['email']
        subject=  data['subject']
        message = data['message']
        cursor=csv.writer(database, delimiter = ',',quotechar='|')
        file=  cursor.writerow([email,subject,message])
@app.route('/submit_form',methods=['POST','GET'])
def submit():
    if request.method == "POST":
        data = request.form.to_dict()
        write_file(data)
        return redirect('thankyou.html')
    else:
        return 'things went wrong, try again'
@app.route('/playlist', methods=['POST','GET'])
def playlist():
    return redirect('playlist.html')
    
if __name__=='__main__':
    app.run()

