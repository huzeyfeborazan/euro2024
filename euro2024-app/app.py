import os
from flask import Flask, redirect, url_for, request, render_template, session, abort, flash, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from forms import SignupForm, LoginForm
from models import User, Team, Match, Prediction, JSONEncoder
from bson import ObjectId

app = Flask(__name__)
app.secret_key = '908fa219d72a1b02c8f3aab7c3979ab1'

db_uri = os.getenv('MONGO_URI', 'mongodb://mongo:27017/euro2024')
client = MongoClient(db_uri)
db = client.get_default_database()

app.json_encoder = JSONEncoder


@app.route('/')
def home():
    registrations = db.users.count_documents({})
    predictions = db.predictions.count_documents({})
    return render_template('index.html', registrations=registrations, predictions=predictions)

@app.route('/register', methods=['GET', 'POST'])
def register():
    
    form = SignupForm()
    
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('register.html', form=form)
        else:
            user = User.create(
                email=form.email.data.lower(),
                nickname=form.nickname.data,
                password=form.password.data
            )
            session['user_id'] = str(user.user_id)
            session['user_nickname'] = user.nickname

        return redirect(url_for('home'))
    elif request.method == 'GET':
        return render_template('register.html', form=form)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/schedule', methods=['GET'])
def show_shedule():
    teams = list(db.teams.find())
    return render_template('schedule.html', teams=teams)

@app.route('/predictions')
def list_predictions():

    user_id = session.get('user_id')
    matches = Match.get_all()
    teams = Team.get_team_dict()
    
    serialized_matches = []
    for match in matches:
        print(match)
        if match.home_team_id in teams and match.away_team_id in teams:
            match_data = match.serialize()
            match_data['home_team'] = teams[match_data['home_team_id']]
            match_data['away_team'] = teams[match_data['away_team_id']]
            match_time = datetime.strptime(match_data['date'], "%Y-%m-%dT%H:%M:%SZ")
            now = datetime.utcnow()
            time_diff = match_time - now
            prediction = match.get_predictions(user_id)
            
            if time_diff < timedelta(hours=1.5) or now > match_time:
                match_data['prediction_status'] = 'N/A'
            elif prediction:
                match_data['prediction_status'] = 'edit'
                match_data['prediction'] = {
                    'home_score': prediction.home_score,
                    'away_score': prediction.away_score
                }
            else:
                match_data['prediction_status'] = 'submit'
            
            serialized_matches.append(match_data)

    return render_template('predictions.html', matches=serialized_matches)


@app.route('/submit_prediction', methods=['POST'])
def submit_prediction():
    user_id = session.get('user_id')
    match_id = request.form['match_id']
    home_score = request.form['home_score']
    away_score = request.form['away_score']
    
    prediction = Prediction(user_id, ObjectId(match_id), home_score, away_score)
    prediction.save()
    flash('Prediction submitted successfully!', 'success')
    return jsonify({'status': 'success', 'home_score': home_score, 'away_score': away_score})


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('login.html', form=form)
        else:
            return redirect(url_for('home'))
                
    elif request.method == 'GET':
        return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.secret_key = 'your_secret_key'
    app.run(host='0.0.0.0', port=5000, debug=True)
