from pymongo import MongoClient

def get_database():
    CONNECTION_STRING = "mongodb://useradmin:VelvetThunder.1993@localhost:27017"
    client = MongoClient(CONNECTION_STRING)
    return client['meal_manager']


if __name__ == "__main__":   
   dbname = get_database()