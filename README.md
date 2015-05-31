# udacity-p3
Item Catalog

# Configuration: 
## Setting up vagrant virtual machine:
> cd path_to_project  
> cd vagrant  
> vagrant up  
> vagrant ssh  

## Installing python libraries:
> apt-get -qqy update  
> apt-get -qqy install postgresql python-psycopg2  
> apt-get -qqy install python-flask python-sqlalchemy  
> apt-get -qqy install python-pip  
> pip install coverage Flask-Login flask-marshmallow Flask-SQLAlchemy Flask-WTF rauth marshmallow-sqlalchemy bleach oauth2client requests httplib2  

## Starting up web server: 
> cd /vagrant/catalog  
> python run.py # script will build DB before running a server  

# Usage
## Web app:
Open web app by typing localhost:5000 in browser

## JSON API Endpoint:
http://localhost:5000/api/catalog
