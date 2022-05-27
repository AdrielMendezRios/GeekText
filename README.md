# GeekText
Restful API project for Group 9 in CEN4010 RVDC RVCC 1225 summer '22 semester 

# Getting started
I'm gonna assume python, flask and git are downloaded.

1. Copy the git repo
2. create a local folder, name it whatever you want
3. open a terminal and cd into the folder you just created
4. run the command "git clone <url copied from step 1>"
5. run command "python3 -m venv env" to create your python virtual environment
6. type "env\Scripts\activate.bat" on the command line then press enter. (activates env)
7. run command "pip install -r requirements.txt"
8. initialize the database:
    1. run command "flask db init"
    2. run command "flask db migrate -m "init" "
    3. run command "flask db upgrade"
9. set the flask environment variable: "set FLASK_ENV=development"
10. finally run command "flask run"

## to create your own git branch
cd into the GeekText folder, then run "git checkout -b {the name you want to give your branch}"
i.e. git checkout -b book_details 

then add, commit, and push changes as you need

# testing enpoints with Postman
follow the videos in discord
your enpoints should all start with 127.0.0.1:5000 (or localhost:5000 if that works for you)

to get all books choose GET as the HTTP method and the endpoint is: 127.0.0.1:5000/books

to test-out/use book and author endpoints assume the data is being passed through the body as JSON 
the all_books and all_authors endpoint don't take any params or body content

# the old readme...
# initial setup
Download python 3.10.x
make a local folder where you'll clone the repo into
open a terminal window in that folder and run
```
C:\project_folder> git clone https://github.com/AdrielMendez/GeekText.git
```
## setting up python environment

```
C:\project_folder\GeekText> pip install virtualenv
```
## once virtualenv is installed run:
```
C:\project_folder\GeekText> python3 -m venv env
```
Where 'env' is the name of your python virtual environment.  
make sure to call your environment folder any one of these:
.env
.venv
env
venv
ENV
env.bak
venv.bak
to prevent it from being added to version control. (i use env)


## activating the python environment
```
# run this command everytime before working on the project
# for Windows 
C:\project_folder\GeekText> env\Scripts\activate.bat

# macOS
$ source env/bin/activate
```
Where 'env' is the name you gave your local python environment.
# a note on pip and packages
we'll probably going to be needing packages as we the semester progresses and our individual needs change. 
right after adding a package you know the project will need please run:
```
C:...\> pip freeze > requirements.txt
```
this will update the requirements.txt file with all the necessary packages to successfully build the project

now whenever you pull all you gotta do is run:
```
C:...\> pip install -r requirements.txt
```
and if there where any changes pip will download them.

## running Flask in dev mode
before running 'flask run' set the FLASK_ENV to development to get hot-reloading and debuging turned on.
```
C:\> set FLASK_ENV=development
```
Once you have activated your python python environment and set FLASK_ENV run:

```
C:...\> flask db init
C:...\> flask db migrate -m "initial migration"
C:...\> flask db upgrade
```
Note: since our db is local we will all have different data. which is nice cause if anything breaks on your db all you have to do is delete the migrations folder and 'db.sqlite' file then run the above commands again (I'll add a csv and helper funciton to initialize some data when i get a chan)

## deactivating python environment
type the word 'deactivate' (w.o the quotes) in your terminal then press enter.



## running Flask
```
C:project_folder\GeekText\> flask run
```
then open your browser to 127.0.0.1:5000


