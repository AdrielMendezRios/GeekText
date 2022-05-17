# GeekText
Restful API project for Group 9 in CEN4010 RVDC RVCC 1225 summer '22 semester 

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
## once virtualenv is installed run
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

## running Flask in dev mode
before running 'flask run' set the FLASK_ENV to development to get hot-reloading and debuging turned on.
```
C:\> set FLASK_ENV=development
```
## activating environment
```
# run this command everytime before working on the project
# for Windows 
C:\project_folder\GeekText> env\Scripts\activate.bat

# macOS
$ source env/bin/activate
```
Where 'env' is the name you gave your local python environment.

Once you have activated your python environment run:

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


