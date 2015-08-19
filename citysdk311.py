"""
Usage: citysdk311.py <host> <apikey>

Arguments:
 host   open311 API endpoint
 apikey access key for API
  
"""

'''
Open311 tests for CitySDK extension / flavour
'''

import basic311
import valideer
from valideer import ValidationError
from dateutil import parser
import datetime
from citysdkParti import CitySDKParticipation
from docopt import docopt

class TestSuiteCitySDK(basic311.TestSuite):
    '''Cover CitySDK specific tests'''
    
    SCHEMA_REQUESTSEXT={
                     "+service_requests":
                        {
                         "+request": 
                            [{"extended_attributes":{"title":"string", #TOOD: are EXT attributes optional even if requested?
                                                     "service_object_id":"string",
                                                     "service_object_type":"string",
                                                     "detailed_status":valideer.Enum(["RECEIVED","IN_PROCESS","PROCESSED","ARCHIVED","REJECTED"]), #TODO: Add Public works status
                                                     "media_urls":{"media_url":["string"]}} #TODO: some implement 
                                                     ,
                              "+service_request_id":"string",
                              "+status": valideer.Enum(["open","closed"]),
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
    
    def __init__(self, host, apikey, api=None):
        if (api is None):
            api=CitySDKParticipation(host, apikey)
        basic311.TestSuite.__init__(self, host, api)
    
    def testLocale(self,locale):
        print("Testing GET services (%s)" % locale),
        repl = self.api.getServices(locale)
        #TODO: Exact specs. for locale codes?
        expect=[200,"UTF-8","text/xml; charset=utf-8"]
        resp = [repl.status_code, repl.encoding, repl.headers["content-type"]]
        self.showDifferences(expect, resp, "http skelleton")
        #Default and custom should differ
        replFields = self.xmlToDict(repl.content)
        if len(replFields["services"])>0:
            serviceLocale=replFields["services"]["service"][0]
            replFieldsEN = self.xmlToDict(self.cache_services.content)
            serviceEN=replFieldsEN["services"]["service"][0]
            if not (serviceLocale["service_name"] == serviceEN["service_name"]):
                print ("ok")
            else:
                print ("is ignored (same as defaults)")
        else:
            print "empty"
    
    def testRequestsExt(self):
        print("Testing GET extended requests"),
#        repl=self.cache_requests
        repl = self.api.getRequests()
        expect=[200,"UTF-8","text/xml; charset=utf-8"]
        resp = [repl.status_code, repl.encoding, repl.headers["content-type"]]
        self.showDifferences(expect, resp, "http skelleton")
        replFields = self.xmlToDict(repl.content)
        print("- limits"),
        l=len(replFields["service_requests"])
        if (l>200):
            print ("to much (%d)" % l)
            #90 days or first 200
        else:
            print ("ok")
        print("- XML structure"),
        with valideer.parsing(additional_properties=True):
            validator = valideer.parse(self.SCHEMA_REQUESTSEXT)
            try:
                validator.validate(replFields)
                print("OK")
            except ValidationError as e:
                print("differs at %s " % (str(e))) 
    def testGetRequestsExtFiltered(self):
        print("Testing GET requests with extended filters")
        print("-geospatial"),
        repl = self.api.getRequests(lat=12.13955,long=54.09138,radius=2000) #TODO calculate that point
        self.testEmptyRequestSet(repl)
        print("-update_after")
        past = datetime.datetime.utcnow() - datetime.timedelta(7)        
        repl=self.api.getRequests(updated_after=past.isoformat())
        self.testEmptyRequestSet(repl)
        print("-update_after")        
        repl=self.api.getRequests(updated_before=past.isoformat())
        self.testEmptyRequestSet(repl)
        #TODO: service objects
        
    #TODO: Test moderation
    

if __name__ == '__main__':
    arguments = docopt(__doc__)
    arguments=basic311.cutArgs(arguments)
    tests=TestSuiteCitySDK(arguments["<host>"],arguments["<apikey>"])
    #tests=TestSuiteCitySDK("asiointi.hel.fi/palautews/rest/v1/")
    #TODO: Add additional citySDK tests
    tests.testLocale("fi")
    tests.testRequestsExt()
    tests.testGetRequestsExtFiltered()