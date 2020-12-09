from flask import Flask
from flask import request
from flask import g
from flask import render_template
from flask import session
from flask import redirect
from flask import url_for
import io
import matplotlib.pyplot as plt


from idea_datalayer import IdeaData, Data_Collectaion

app = Flask(__name__)
app.secret_key = 'very secret string'

data = None
data_from_data = None

@app.teardown_appcontext
def close_connection(exception):
    data.close_connection()
    data_from_data.close_connection()

"""
Denne funktion sørger for at pakke den template, der skal vises,
ind i nogle standard-ting, f.eks. loginstatus.

my_render bør kaldes i stedet for at kalde render_template direkte.
"""
def my_render(template, **kwargs):
    login_status = get_login_status()
    if login_status:
        return render_template(template, loggedin=login_status, user = session['currentuser'], **kwargs)
    else:
        return render_template(template, loggedin=login_status, user = '', **kwargs)

def get_login_status():
    return 'currentuser' in session

def get_user_id():
    if get_login_status():
        return session['currentuser']
    else:
        return -1

@app.route("/")
@app.route("/home")
def home():
    return my_render('home.html')

@app.route("/nyide", methods=['POST'])
def nyide():
    text = request.form['idea']
    userid = get_user_id()
    data.register_new_idea(text, userid)
    return redirect("/visideer")

@app.route("/visideer", methods=['GET'])
def vis():
    if 'currentuser' in session:
        if 'id' in request.args:
            ideer = data.get_idea_list(session['currentuser'], ideaid = request.args['id'])
        else:
            ideer = data.get_idea_list(session['currentuser'])

    else:
        ideer = []
    return my_render("vis.html", ideas = ideer)

@app.route("/register")
def register():
    return my_render('register.html', success= True, complete = True)

@app.route("/login")
def login():
    return my_render('login.html', success = True)

@app.route("/logout")
def logout():
    session.pop('currentuser', None)
    return my_render('home.html')


@app.route("/about")
def about():
    return my_render('about.html', title='Om idéhuset')

@app.route("/profil")
def profil():
    id = get_user_id()
    if get_login_status():
        name,email = data.get_user_info(id)
        return my_render('profil.html', username = name, email = email)
    else:
        return redirect("/login")

@app.route("/contact")
def contact():
    return my_render('contact.html', title='Kontakt')

def login_success(user, pw):
    return data.login_success(user,pw)

def register_success(user, pw, email):
    return data.register_user(user, pw, email)

@app.route('/register_user', methods=['POST'])
def register_user():
    pw = request.form['password']
    user = request.form['username']
    email = request.form['email']

    if register_success(user, pw, email):
        #Create user object, store in session
        session['currentuser'] = data.get_user_id(user)
        return my_render('home.html')
    else:
        session.pop('currentuser', None)
        if len(pw) == 0 or len(user) == 0:
            return my_render('register.html', success = False, complete = False)
        else:
            return my_render('register.html', success = False, complete = True)


@app.route('/login_user', methods=['POST'])
def login_user():
    pw = request.form['password']
    user = request.form['username']

    if login_success(user, pw):
        #Create user object, store in session.
        session['currentuser'] = data.get_user_id(user)
        return my_render('home.html')
    else:
        session.pop('currentuser', None)
        return my_render('login.html', success = False)

#Tilføjelse af måledata i DATABASE!
@app.route('/opret_data')
def opret_data():
    return my_render('opret_data.html', titel='opret data')

@app.route("/nydata", methods=['POST'])
def nydata():
    npd = request.form['navn_paa_data']
    dsso = request.form['vaerdi_paa_data']
    userid = get_user_id()
    data_from_data.register_new_data(npd, dsso, userid)
    print('Data som bliver gemt: {} og tallet er: {}'.format(npd, dsso))
    return redirect("/visdata")

@app.route("/visdata", methods=['GET'])
def visdata():
    if 'currentuser' in session:
        data_from_data = Data_Collectaion()
        id = get_user_id()
        print(id)
        if 'id' in request.args:
            data_from_data = data_from_data.get_data_list(session['currentuser'], id, dataid = request.args['id'])
        else:
            data_from_data = data_from_data.get_data_list(session['currentuser'], id)
    else:
        data_from_data = []
    tal = 4
    print(data_from_data, tal)
    return my_render("vis_data.html", data = data_from_data, tal=tal)

@app.route('/fig/<figure_key>')
def fig(figure_key):
    plt.title(figure_key)
    plt.plot([1,2,3,4], [1,3,2,4])
    img = io.BytesIO()
    plt.savefig(img)
    img.seek(0)
    return send_file(img, mimetype='image/png')

@app.route('/indseat_maaledata', methods=['GET', 'POST'])
def test():
    npd = 'dette er en test af vores crap'
    return my_render('indsaet_maaling.html', test=npd)

@app.route('/gem_maaledata', methods=['POST', 'GET'])
def save_indseat_maaledata():
    # npd = 'dette er en test af vores crap'
    dsso = request.form['dsso']
    print(dsso)
    redirect('/indseat_maaledata')
    # return my_render('indsaet_maaling.html', title = 'Indtast måling', test = npd)
    #Her skal der laves en rute der redrecter til en anden side, så at man kan dende al dataen til serveren.
    #redirect eventuelt til den samme side.
    #Denne side sender data til databasen, det er i hvert fald det den skal når den er færdig.

if __name__ == "__main__":
    print('Hello World')
    with app.app_context():
        data = IdeaData()
        print('data print: {}'.format(data))
        data_from_data = Data_Collectaion()
        print('data_from_data print: {}'.format(data_from_data))


    app.run(debug=True)
