"""
Usage: citysdk311.py <host> <apikey>

Arguments:
 host   open311 API endpoint
 apikey access key for API
  
"""

'''
Open311/CitySDK tests for Klarschiff extensions
'''
import citysdk311
import basic311
from citysdkKS import CitysdkKlarschiff
import valideer
from valideer import ValidationError
from dateutil import parser
from docopt import docopt

class TestSuiteCitySDKKlarschiff(citysdk311.TestSuiteCitySDK):
    
    SCHEMA_REQUESTSEXT={
                     "+service_requests":
                        {
                         "+request": 
                            [{"extended_attributes":{"title":"string", #TOOD: are EXT attributes optional even if requested?
                                                     "service_object_id":"string",
                                                     "service_object_type":"string",
                                                     "detailed_status":valideer.Enum(["RECEIVED","IN_PROCESS","PROCESSED","ARCHIVED","REJECTED"]),
                                                     "detailed_status_datetime":valideer.AdaptBy(parser.parse),
                                                     "media_urls":{"media_url":["string"]}},
                                                     "photo_required": "boolean",
                                                     "trust": "integer",
                                                     "votes": "integer",
                              "+service_request_id":"string",
                              "+status": valideer.Enum(["OPEN","CLOSED"]),
                              "status_notes":"string",
                              "+service_name":"string",
                              "+service_code":"string",
                              "description":"string",
                              "agency_responsible":"string",
                              "service_notice":"string",
                              "requested_datetime":valideer.AdaptBy(parser.parse),
                              "updated_datetime":valideer.AdaptBy(parser.parse), 
                              "expected_datetime":valideer.AdaptBy(parser.parse),
                              "address":"string", #TODO: Make Position XOR address
                              "address_id":"string",
                              "zipcode":"string",
                              "+lat":valideer.AdaptTo(float,"number"),
                              "+long": valideer.AdaptTo(float,"number"),
                              "media_url":"string",}] #TODO: make URL regex
                         }
        }
    
    SCHEMA_COMMENTS={
                     "+comments": {  #TODO: Conditional Array?
                         "+comment":
                           { 
                              "+id": "integer",
                              "+jurisdiction_id": "string",
                              "+comment": "string",
                              "+datetime":valideer.AdaptBy(parser.parse),
                              "+service_request_id":"string",
                              "+author":"string", #TODO: Validate as email
                              }
                    }
        }
    
    SCHEMA_NOTES={
                     "+notes": {  #TODO: Conditional Array?
                         "+note":
                           { 
                              "+jurisdiction_id": "string",
                              "+comment": "string",
                              "+datetime":valideer.AdaptBy(parser.parse),
                              "+service_request_id":"string",
                              "+author":"string"
                              }
                    }
        }
    
    def __init__(self, host):
        self.api=CitysdkKlarschiff(host)
        citysdk311.TestSuiteCitySDK.__init__(self, host, self.api)
    
    def testRequestsExtKS(self):
        print("Testing GET extended requests"),
        repl = self.api.getRequests()
        expect=[200,"UTF-8","text/xml; charset=utf-8"]
        resp = [repl.status_code, repl.encoding, repl.headers["content-type"]]
        self.showDifferences(expect, resp, "http skelleton")
        replFields = self.xmlToDict(repl.content)
        print("- XML structure"),
        with valideer.parsing(additional_properties=True):
            validator = valideer.parse(self.SCHEMA_REQUESTSEXT)
            try:
                validator.validate(replFields)
                print("OK")
            except ValidationError as e:
                print("differs at %s " % (str(e))) 
    
    def testGetRequestsExFilteredKS(self,agency):
        print("Testing GET requests with extended filters")
        print("-agency"),
        repl = self.api.getRequests(lat=12.13955,long=54.09138,radius=2000) #TODO calculate that point
        self.testEmptyRequestSet(repl)
        print("-detailed_status"),
        repl = self.api.getRequests(statusEx="RECEIVED")
        self.testEmptyRequestSet(repl)
    
    def testGetComments(self,apikey):
        repl=self.api.getComments(66,apikey)
        expect=[200,"UTF-8","text/xml; charset=utf-8"]
        resp = [repl.status_code, repl.encoding, repl.headers["content-type"]]
        self.showDifferences(expect, resp, "http skelleton")
        replFields = self.xmlToDict(repl.content)
        print("- XML structure"),
        with valideer.parsing(additional_properties=True):
            validator = valideer.parse(self.SCHEMA_COMMENTS)
            try:
                validator.validate(replFields)
                print("OK")
            except ValidationError as e:
                print("differs at %s " % (str(e))) 
    
    def testGetNotes(self,apikey):
        repl=self.api.getNotes(66,apikey)
        expect=[200,"UTF-8","text/xml; charset=utf-8"]
        resp = [repl.status_code, repl.encoding, repl.headers["content-type"]]
        self.showDifferences(expect, resp, "http skelleton")
        replFields = self.xmlToDict(repl.content)
        print("- XML structure"),
        with valideer.parsing(additional_properties=True):
            validator = valideer.parse(self.SCHEMA_NOTES)
            try:
                validator.validate(replFields)
                print("OK")
            except ValidationError as e:
                print("differs at %s " % (str(e))) 


if __name__ == '__main__':
    arguments = docopt(__doc__)
    arguments=basic311.cutArgs(arguments)
    tests=TestSuiteCitySDKKlarschiff(arguments["<host>"])
    #tests.testGetRequestsExFilteredKS(agency="Stadtforstamt")
    #tests.testRequestsExtKS()
    tests.testGetComments(arguments["<apikey>"])
    tests.testGetNotes(arguments["<apikey>"])

#TODO: (enforce HTTPS)
#Auftragslisten lesen/umordnen/schreiben
#TODO: authorization (ext. read, write)
#TODO: write comments
#TODO: make vote
#TODO: Update request
#TODO: Fotowunsch