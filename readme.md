This is a validator to test custom servers for the current Open311 protocol support.

#WIP

This scripts started as personal testsuite and is not an official verification tool! There's still a lot of stuff todo:

* JSON checks
* discovery check
* more test logic (what is not allowed, ...) 
* more accurate open311 specs. interpretation
* add pendantic testsuite 
* ... (see #todo lines)

#Usage

Setup your python 2.7 environment (virtualenv recomment) by installing the dependencies:
> pip install -R requirements.txt

Now launch the tests against your desired service. For example:
> python basic311.py host=open311.mydomain.com/api/v2 apikey=123  
> python citysdk311.py host=open311.mydomain.com/api/v2 apikey=123

#Development

* open new issues
* keep new "flavours"/ protocol extensions seperated in file and branches
* code in Python 2.7 use venv and requirements.txt
 