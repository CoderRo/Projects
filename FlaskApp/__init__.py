from flask import Flask,render_template,request,session,url_for,redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField ,TextField,SubmitField
from wtforms.validators import DataRequired,Email,Length
from flask_pymongo import PyMongo
from pymongo import MongoClient
import random
class Register(FlaskForm):
    username = StringField('Email',validators=[DataRequired(),Length(min=5,max=9)])
    password = PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField('Register')
    urls=TextField('urls',validators=[DataRequired()])


app=Flask(__name__)
app.config['SECRET_KEY'] = 'myseckey'
client = MongoClient("mongodb://urlshortner1:a123456@ds245022.mlab.com:45022/urlshortner1")
db = client['urlshortner1']
users = db['users']




@app.route('/',methods=['GET','POST'])
def register():
    session['username']=None
    form=Register()
    users=db.users
    msg= ""
    if request.method == 'POST':
        search = users.find_one({'username':form.username.data})
        if search:
            msg = 'Username already exist'
        else:
            users.insert({'username':form.username.data,'password':form.password.data})
            return redirect(url_for('login'))
    return render_template('register.html',form=form,msg=msg)


@app.route('/login/',methods=['GET','POST'])
def login():
    form=Register()
    users=db.users
    session['username'] = None
    msg = 'Invalid Username or Password'
    if request.method == 'POST':
        search=users.find_one({'username':form.username.data})
        if search is None:
            return render_template('Login.html',form=form,msg=msg)
        au=search['username']
        ap=search['password']
        if au == form.username.data and ap == form.password.data:
            session['username']=form.username.data
            return redirect(url_for('url',name=au))

        return render_template('Login.html',form=form,msg=msg)

    return render_template('Login.html',form=form)

@app.route('/<name>',methods=['POST','GET'])
def url(name):
    form=Register()
    urls=db[name]
    msg=''
    if session['username']:
        if request.method == 'POST':
            search=urls.find_one({'real':form.urls.data})
            if search:
                msg='URL already shortned'
                return redirect(url_for('url',name=name))
            else:
                rand=random.randint(0,pow(10,5))
                temp="http://127.0.0.1:5000/"+name+"/"+str(rand)
                urls.insert({'real':form.urls.data,'short':temp})
                return redirect(url_for('url', name=name,msg=msg))
        else:
            hi = urls.find()
            return render_template('short.html',form=form,name=name,hi=hi,msg=msg)

    return redirect(url_for('login'))

@app.route('/<name>/<trunc>', methods=['POST','GET'])
def link(name,trunc):
	urls = db[name]
	search = urls.find_one({'short':'http://127.0.0.1:5000/'+name+'/'+trunc})
	if search:
		return redirect(search['real'])
	return redirect(url_for('url', name=name))

@app.route('/logout')
def logout():
	session['username'] = None
	return redirect(url_for('login'))


if __name__=='__main__':
    app.run(debug=True)
