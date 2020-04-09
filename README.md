# SalesDB

SalesDB is a sales data analysis program made with Flask. 
It is our course project for COP 5725. ORM model is 
not used due to the course requirement.

# Evironment setup
Install requirements
```
pip install -r requirements.txt
```
Configure Oracle Instant Client following [ODPI-C Installation](https://oracle.github.io/odpi/doc/installation.html#macos)

Then (otherwise you cannot run the tests)
```
python setup.py develop
```
Run a few tests
```
pytest
```
Then start the server with
```
flask run
```