import json
from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os


db_uri = os.getenv('MONGO_URI', 'mongodb://mongo:27017/euro2024')
client = MongoClient(db_uri)
db = client.get_default_database()


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(JSONEncoder, self).default(obj)


class User:
    def __init__(self, user_id, nickname, email, password_hash):
        self.user_id = user_id
        self.nickname = nickname
        self.email = email
        self.password_hash = password_hash

    @classmethod
    def find_by_email(cls, email):
        user_data = db.users.find_one({'email': email})
        if user_data:
            return cls(user_data['_id'], user_data['email'], user_data['nickname'], user_data['password'])
        return None

    @classmethod
    def create(cls, nickname, email, password):
        created_date = datetime.utcnow()
        password_hash = generate_password_hash(password)
        result = db.users.insert_one({'nickname': nickname, 'email': email, 'password': password_hash, 'created_date': created_date})
        return cls(result.inserted_id, nickname, email, password_hash)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def serialize(self):
        return {
            '_id': str(self.user_id),
            'nickname': self.nickname,
            'email': self.email
        }


class Team:
    def __init__(self, team_id, name, group):
        self.team_id = team_id
        self.name = name
        self.group = group

    @classmethod
    def get_all(cls):
        teams = db.teams.find()
        return [cls(team['_id'], team['name'], team['group']) for team in teams]

    @classmethod
    def get_team_dict(cls):
        teams = cls.get_all()
        return {str(team.team_id): team for team in teams}

class Match:
    def __init__(self, match_id, home_team_id, away_team_id, stadium, date):
        self.match_id = match_id
        self.home_team_id = home_team_id
        self.away_team_id = away_team_id
        self.stadium = stadium
        self.date = date

    @classmethod
    def get_all(cls):
        matches = db.matches.find()
        return [cls(match['_id'], match['home_team_id'], match['away_team_id'], match['stadium'], match['date']) for match in matches]

    def serialize(self):
        return {
            '_id': str(self.match_id),
            'home_team_id': str(self.home_team_id),
            'away_team_id': str(self.away_team_id),
            'stadium': self.stadium,
            'date': self.date,
            'formatted_date': datetime.strptime(self.date, "%Y-%m-%dT%H:%M:%SZ").strftime("%d %b, %H:%M %p")
        }

    def get_predictions(self, user_id):
        prediction = db.predictions.find_one({'user_id': user_id, 'match_id': self.match_id})
        return Prediction(prediction['user_id'], prediction['match_id'], prediction['home_score'], prediction['away_score']) if prediction else None

class Prediction:
    def __init__(self, user_id, match_id, home_score, away_score):
        self.user_id = user_id
        self.match_id = match_id
        self.home_score = home_score
        self.away_score = away_score

    def save(self):
        db.predictions.update_one(
            {'user_id': self.user_id, 'match_id': self.match_id},
            {'$set': {'home_score': self.home_score, 'away_score': self.away_score}},
            upsert=True
        )
