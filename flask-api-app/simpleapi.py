from flask import Flask
from flask_restful import Resource,Api
from secure_check import authenticate,identity
from flask_jwt import JWT,jwt_required
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
app = Flask(__name__)
#app and database configuration
app.config['SECRET_KEY'] = 'secretkey'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Migrate(app,db)
api = Api(app)
jwt =  JWT(app,authenticate,identity)
#################################################
# model creation
class Movie(db.Model):
    name = db.Column(db.String(80),primary_key= True)
    def __init__(self,name):
        self.name = name

    def json(self):
        return {'name' : self.name}

class MovieNames(Resource):
    def get(self,name):
        movie = Movie.query.filter_by(name=name).first()
        if movie:
            return movie.json()
        else:
            return {'name':None},404
#add a movie
    def post(self,name):
        movie = Movie(name=name)
        db.session.add(movie)
        db.session.commit()
        return movie.json()
#delete a movie by its name
    def delete(self,name):
        movie = Movie.query.filter_by(name=name).first()
        db.session.delete(movie)
        db.session.commit()
        return {'note': 'movie deleted'}

#return all movies
class AllMovies(Resource):
    # @jwt_required
    def get(self):
        movies = Movie.query.all()
        return [movie.json() for movie in movies]

#url creation
api.add_resource(MovieNames,'/movie/<string:name>')
api.add_resource(AllMovies,'/movies')
if __name__ == '__main__':
    app.run(debug=True)