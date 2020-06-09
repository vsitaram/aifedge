AIFEdge
========

AIFEdge is the analyst portal for the Alternative Investment Fund at UVA. It can be used as a reflective tool for investment decisions, a resource to help generate new investment ideas, and a way to stay up to date with the fund. Analysts can use it to view current investments and all of the pitches that have come into the fund. Additionally, they can easily run various analytics tools that have been built by other AIF analysts.


For Exec
--------

How To Add a Pitch
- Go to https://aifedge.herokuapp.com/admin/ and log in
- Under 'Edge', click on 'Pitches'
- To the right of the page, click 'Add Pitch'

For Developers and Contributors
------------

Get Started

Install Python3 and Pip3 and alias python to python3 and pip to pip3.
     
    nano ./~bashrc

At the top of the file, type the following.

    alias python=python3
    alias pip=pip3

Exit and save the changes. To run your changes, run this in the terminal.

    source ~/.bashrc

Test to see if it worked.

    python -V
    pip -V

If it did not work, type the following into the terminal.

    alias python=python3
    alias pip=pip3

Install Git following the instructions here: https://git-scm.com/downloads.

Find a good place to keep your projects and clone the repository.

    git clone https://github.com/vsitaram/aifedge.git

Get the .env final and local_setting.py files from someone in Risk. Place the .env in the root directory and place the local_settings.py file in the aifedge subfolder.

Install PostgreSQL.

    sudo apt-get update
    sudo apt-get install  python3-dev libpq-dev postgresql postgresql-contrib

We now need to set up PostgreSQL with a database that the application can work with. 

Start the PostgreSQL server.

    sudo service postgresql start

Switch to the PostgreSQL administrative user.

    sudo su - postgres

Start PostgreSQL.

    psql

Check out the databases you currently have.

    \l

Create the database.

    CREATE DATABASE aifedge;

Create a user that will have access to that database. You have two options: 1) Use the same username and password given for the database in the .env file, or 2) Create your own username and password and store it in the .env file.Note the single quotes for the password only.

    CREATE USER aifedge_user WITH PASSWORD 'aifedge_password';

Change some of the settings for the user and grant permissions on the database for the user.

    ALTER ROLE aifedge_user SET client_encoding TO 'utf8';
    RANT ALL PRIVILEGES ON DATABASE aifedge TO aifedge_user;

Check that the database is created.

    \l

You should see that aifedge is there. Now double check that the user exists.

    \du

You should see that aifedge_user exists.

Exit out of PostgreSQL

    \q

Exit out of the postgres user

    CRTL + D

Go to the root of the project folder where the .env file and Pipfile are. 

Install pipenv (make sure you have pip set up for python3 beforehand)

    pip install --user pipenv

Create an environment

    pipenv shell

Install the packages and dependencies necessary for the application

    pipenv install

If you have issues in this stage with any of the packages, remove the problematic packages from the Pipfile but note them down first.

Run pipenv install again until you have a successful Pipfile.lock created. 

Then install the problematic packages.

    pipenv install package_1 package_2

Create the database tables necessary.

    python manage.py migrate

Start the server.

    python manage.py runserver.

Go to http://localhost:8000/. You'll see the application without any pitches or tools. You should just see the graph and KPIs on the dashboard.

To get the database information, you have to get a backup from the Heroku app called latest.dump. You can either 1) get the latest.dump file from someone in Risk, or 2) get it yourself with your access to the Heroku account. If you are following the latter option, follow these steps.

Install the Heroku CLI from https://devcenter.heroku.com/articles/heroku-cli. If you are using Windows Subsystem for Linux (WSL), run the following to install the Heroku CLI.

    curl https://cli-assets.heroku.com/install.sh | sh

Log in to Heroku

    heroku login

Download the database

    heroku pg:backups:capture
    heroku pg:backups:download

Load the backup file locally. Make sure to replace the aifedge_user username with the PostgreSQL username that you made before.

    pg_restore --verbose --clean --no-acl --no-owner -h localhost -U aifedge_user -d aifedge latest.dump

Check that the database was loaded correctly.

Again, if you haven't already, start PostgreSQL. Then, change to the postgres administrative user.

    sudo service postgreSQL start
    sudo su - postgres

Check that the aifedge database is there when you run the following.

    \l

Connect to the aifedge database.

    \c aifedge

See all of the tables that have been imported.

    \d

Quit PostgreSQL

    \q

Exit out of the postgres user

    CRTL + D

Start the application

    python manage.py runserver

TADA! You have the application running with all of its data locally on your computer.

How to Add a Tool

- Add your python script as a function(s) to the Data object in analysis.py
- Make a copy of template.html found in edge/templates/edge/ and alter it as you like.
- Create an API endpoint in urls.py that will serve your template. You should be requesting this endpoint somehow within your template.
- Copy your html template file to the edge/templates/edge/ folder. 
- Enlist your tool or have someone on exec Enlist your tool at https://aifedge.herokuapp.com/admin/edge/tool/. Provide a title, a description, a list of (co-)creators, and the html file's name. The 'Template name' entry and your file name must must be the same.






See Any Issues?
----------

- Submit them at the Issue Tracker: https://github.com/vsitaram/aifedge/issues


License
-------

The project is licensed under the BSD license.
