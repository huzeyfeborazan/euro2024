import json
import os
from pymongo import MongoClient


db_uri = os.getenv('MONGO_URI', 'mongodb://mongo:27017/euro2024')
client = MongoClient(db_uri)
db = client.get_default_database()


# Path to the JSON file
teams_file_path = 'teams.json'
matches_file_path = 'matches.json'

def insert_teams_from_json():
    with open(teams_file_path, 'r') as file:
        teams = json.load(file)
    
    for team in teams:
        # Check if the team already exists in the database
        if not db.teams.find_one({"_id": team['_id']}):
            db.teams.insert_one(team)
            print(f"Inserted team: {team['name']}")
        else:
            print(f"Team already exists: {team['name']}")


def insert_matches_from_json():
    with open(matches_file_path, 'r') as file:
        matches = json.load(file)
    
    for match in matches:
        # Check if the match already exists in the database
        if not db.matches.find_one({"match_number": match['match_number']}):
            db.matches.insert_one(match)
            print(f"Inserted match: {match['match_number']}")
        else:
            print(f"Match already exists: {match['match_number']}")

if __name__ == '__main__':
    print(f"Inserting teams")
    insert_teams_from_json()

    print(f"Inserting matches")
    insert_matches_from_json()
