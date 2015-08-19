"""
Usage: basic311.py <host> <apikey> 

Arguments:
 host   open311 API endpoint
 apikey access key for API
  
"""

'''
Open311 tests that cover all feature, but are tollerant for tiny variations

This covers core usecases and should represent default open311 usage.
If you pass, most applications should work with your implementation
'''

import json
from dateutil import parser
import datetime
import valideer
from valideer import ValidationError
import xmltodict
from georeportv2 import georeporter
from lxml import etree
from docopt import docopt


class TestSuite(object):
    '''Open311 basic test. Inherited classes just run it's own tests'''
    
    SCHEMA_SERVICE = {
        "+services":
        {
         "+service": [{
                   "+service_code": "string",
                    "+service_name": "string",
                    "description": "string",
                    "+metadata": valideer.Enum(["true", "false"]),
                    "+type":  valideer.Enum(["realtime", "batch", "blackbox"]),
                    "+keywords": "string",
                    "group": "string",
                    }]
         }
    }
    SCHEMA_DEF = {
                "+service_code": "string",
                "+attributes": 
                    [{"+variable": valideer.Enum(["true", "false"]),
                    "+code": "string",
                    "+datatype": valideer.Enum(["string", "number", "datetime", "text", "singlevaluelist", "multivaluelist"]),
                    "+required": valideer.Enum(["true", "false"]),
                    "+datatype_description": "string",
                    "+order": valideer.Range(valideer.Number, 0),
                    "description": "string"}]
    }
    SCHEMA_REQUESTS = {
                     "+service_requests":
                        {
                         "+request": 
                            [{"+service_request_id": "string",
                              "+status": valideer.Enum(["open", "closed"]),
                              "status_notes": "string",
                              "+service_name": "string",
                              "+service_code": "string",
                              "description": "string",
                              "agency_responsible": "string",
                              "service_notice": "string",
                              "requested_datetime": valideer.AdaptBy(parser.parse),
                              "updated_datetime": valideer.AdaptBy(parser.parse), 
                              "expected_datetime": valideer.AdaptBy(parser.parse),
                              "address": "string",  #TODO: Make Position XOR address
                              "address_id": "string",
                              "zipcode": "string",
                              "+lat": valideer.AdaptTo(float, "number"),
                              "+long": valideer.AdaptTo(float, "number"),
                              "media_url": "string", }]  #TODO: make URL regex
                         }
        }
    SCHEMA_REQUEST = {"+service_requests":
                            {  #TODO: Try to remove slightly redundant schema
                             "+request":  
                                {"+service_request_id": "string",
                                  "+status": valideer.Enum(["open", "closed"]),
                                  "status_notes": "string",
                                  "+service_name": "string",
                                  "+service_code": "string",
                                  "description": "string",
                                  "agency_responsible": "string",
                                  "service_notice": "string",
                                  "requested_datetime": valideer.AdaptBy(parser.parse),
                                  "updated_datetime": valideer.AdaptBy(parser.parse), 
                                  "expected_datetime": valideer.AdaptBy(parser.parse),
                                  "address": "string",  #TODO: Make Position XOR address
                                  "address_id": "string",
                                  "+zipcode": "string",
                                  "+lat": valideer.AdaptTo(float, "number"),
                                  "+long": valideer.AdaptTo(float, "number"),
                                  "media_url": "string", }  #TODO: make URL regex
                             }
     }
    
    @staticmethod
    def __noNone(path, key, value):
        '''we skip dict none values for like <key/> elements '''
        if value is None:
            return key, ""           
        '''we skip additional typisation fields'''
        if (isinstance(value, dict)):
            if "@nil" in value:
                return key, ""
            if "@type" in value:
                if "#text" in value:
                    return key, value["#text"] 
            #if value.hasKey("@type"): oder alle mit @
        return key, value
    
    def __init__(self, host, api=None, apikey=None):
        self.host = host
        if api is None:
            api = georeporter(host, apikey)
        self.api = api
        self.__cacheTransfers()
    
    def showDifferences(self, expect, result, msgTest):
        '''helper for visual compare of two lists'''
        #TODO: Add normalizing option - lowercase, trim, ...
        s = set(expect)
        diff = [x for x in result if x not in s]
        print("- "+msgTest),
        if len(diff) == 0:
            print("OK")
        else:
            print("differs at: %s (expected: %s)" % (str(diff), str(expect)))

    def __cacheTransfers(self):
        '''call api just one time for defaults'''
        print "caching..."
        print "-",
        self.cache_services = self.api.getServices()
        print "-",
        self.cache_requests = self.api.getRequests()
        #TODO: Write to disk?
    
    def __getFirstServiceCode(self):
        serviceCode = None
        root = etree.fromstring(self.cache_services.content)
        for service in root.getchildren():
            fields = self.xmlToDict(etree.tostring(service))
            try:
                if fields["metadata"] == "true":
                    serviceCode = fields["service_code"]
                    return serviceCode
            except:
                pass  #TODO: Log that metadata is mandatory?
        return serviceCode
    
    def __getFirstRequestId(self):
        srid = None
        root = etree.fromstring(self.cache_requests.content)
        for servicereq in root.getchildren():
            fields = self.xmlToDict(etree.tostring(servicereq))["request"]
            if "service_request_id" in fields:
                srid = fields["service_request_id"]
                return srid
        return srid

    def xmlToDict(self, repl):
        '''Transform XML tree to dict tree'''
        tmp = xmltodict.parse(repl, postprocessor=self.__noNone)
        replFields = json.loads(json.dumps(tmp))
        return replFields
    
    #TODO: Test discovery

    def testGetServices(self):
        print("Testing GET services")
        repl = self.cache_services
        expect = [200, "UTF-8", "text/xml; charset=utf-8"]
        resp = [repl.status_code, repl.encoding, repl.headers["content-type"]]
        self.showDifferences(expect, resp, "http skelleton")
        print("- XML structure"),
        with valideer.parsing(additional_properties=True):
            validator = valideer.parse(self.SCHEMA_SERVICE)
        replFields = self.xmlToDict(repl.content)
        try:
            validator.validate(replFields)
            print("OK")
        except ValidationError as e:
            print("differs %s " % (str(e)))
    
    def testGetServicsDef(self):
        #TODO: walk trough all definitions
        print("Testing GET service definition"),
        firstCode = self.__getFirstServiceCode()
        if firstCode is not None:
            repl = self.api.getServiceDef(firstCode)
            expect = [200, "UTF-8", "text/xml; charset=utf-8"]
            resp = [repl.status_code, repl.encoding, repl.headers["content-type"]]
            self.showDifferences(expect, resp, "http skelleton")
            print("- XML structure"),
            with valideer.parsing(additional_properties=True):
                validator = valideer.parse(self.SCHEMA_DEF)
            replFields = self.xmlToDict(repl)
            try:
                validator.validate(replFields)
                print("OK")
            except ValidationError as e:
                print("differs at %s " % (str(e)))
        else:
            print "(No service definitions available for testing)"

    def testCreateRequest(self, email="matthias.meisser@rostock.de", lat=54.0867, lon=12.1359, descr="test", title="test", code="18"):
        #TODO: Extract attributes
        print("Testing POST request"),
        repl = self.api.createRequest(lat, lon, code, email, descr, attr={"title": title}, jurisdinction="rostock.de", tolerantSSL=True)
        expect = [200, "UTF-8", "text/xml; charset=utf-8"]
        resp = [repl.status_code, repl.encoding, repl.headers["content-type"]]
        self.showDifferences(expect, resp, "http skelleton")
        #TODO: Attributes of metadata / service definitions
        #TODO: what more can we check here?
        #TODO: Some might return token instead
    
    def testGetRequests(self):
        print("Testing GET requests"),
        repl = self.cache_requests
        expect = [200, "UTF-8", "text/xml; charset=utf-8"]
        resp = [repl.status_code, repl.encoding, repl.headers["content-type"]]
        self.showDifferences(expect, resp, "http skelleton")
        print("- XML structure"),
        with valideer.parsing(additional_properties=True):
            validator = valideer.parse(self.SCHEMA_REQUESTS)
        replFields = self.xmlToDict(repl.content)
        try:
            validator.validate(replFields)
            print("OK")
        except ValidationError as e:
            print("differs at %s " % (str(e)))
    
    def testGetRequestsFiltered(self):
        print("Testing GET requests with filters")
        #TODO: How to generate indipendend queries?
        #TODO: How to check logic on expected results?
        print("-service_request_id"),
        repl = self.api.getRequests(service_request_id="3,5")
        self.testEmptyRequestSet(repl)
        print ("-service_code")
        repl = self.api.getRequests(service_code=18)
        self.testEmptyRequestSet(repl)
        print ("-start_date")
        past = datetime.datetime.utcnow() - datetime.timedelta(2)        
        repl = self.api.getRequests(start_date=past.isoformat())
        self.testEmptyRequestSet(repl)
        print ("-end_date")       
        repl = self.api.getRequests(end_date=past.isoformat())
        self.testEmptyRequestSet(repl)
        print ("-status")        
        repl = self.api.getRequests(status="closed")
        self.testEmptyRequestSet(repl)
        #TODO: None older than 90days?
            
    def testGetRequest(self):
        print("Testing GET request"),
        srid = self.__getFirstRequestId()
        repl = self.api.getRequest(srid)
        expect = [200, "UTF-8", "text/xml; charset=utf-8"]
        resp = [repl.status_code, repl.encoding, repl.headers["content-type"]]
        self.showDifferences(expect, resp, "http skelleton")
        print("- XML structure")
        with valideer.parsing(additional_properties=True):
            validator = valideer.parse(self.SCHEMA_REQUEST)
        replFields = self.xmlToDict(repl.content)
        try:
            validator.validate(replFields)
            print("OK")
        except ValidationError as e:
            print("differs at %s " % (str(e)))
    
    def testGetRequestFromToken(self):
        print("Testing GET ID by token"),
        mytoken = "123"  #TODO: Implement lookup for an valid token?
        repl = self.api.getIdByToken(mytoken)
        expect = [200, "UTF-8", "text/xml; charset=utf-8"]
        resp = [repl.status_code, repl.encoding, repl.headers["content-type"]]
        self.showDifferences(expect, resp, "http skelleton")
        
    def testEmptyRequestSet(self, repl):
        expect = [200, "UTF-8", "text/xml; charset=utf-8"]
        resp = [repl.status_code, repl.encoding, repl.headers["content-type"]]
        self.showDifferences(expect, resp, "http skelleton")
        print "- queryset",
        replFields = self.xmlToDict(repl.content)
        amount = 1  #if no subdicts, just a single request
        try:
            for item in replFields["service_requests"]["request"]:
                if isinstance(item, dict):
                    amount += 1
            if (amount > 0):
                print "ok (%d)" % amount
            else:
                print ("failed (empty)") 
        except KeyError:
            print ("failed (empty)")
  
        
def cutArgs(args):
    '''return only true values'''
    temp = {}
    for arg in args:
        temp[arg] = args[arg].split("=")[1]
    return temp
                

if __name__ == '__main__':
    arguments = docopt(__doc__)
    arguments = cutArgs(arguments)
    tests = TestSuite(arguments["<host>"], None, arguments["<apikey>"])
    tests.testGetServices()
    tests.testGetServicsDef()
    tests.testCreateRequest()
    tests.testGetRequests()
    tests.testGetRequest()
    tests.testGetRequestFromToken()
    tests.testGetRequestsFiltered()
    #TODO: encoding
    #TODO: test Errorcodes 

