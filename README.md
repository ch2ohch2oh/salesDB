# SalesDB

SalesDB is a sales data analysis program made with Flask. 
It is our course project for COP 5725. ORM model is 
not used due to the course requirement.

# Evironment setup
1. Install requirements
```
pip install -r requirements.txt
```
2. Configure Oracle Instant Client following [ODPI-C Installation](https://oracle.github.io/odpi/doc/installation.html#macos)

3. Setup and run a few tests
```
python setup.py develop
pytest
```
4. Start the server with
```
flask run
```