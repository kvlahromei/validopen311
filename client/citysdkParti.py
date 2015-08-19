from georeportv2 import georeporter

class CitySDKParticipation(georeporter):
    '''
    Open311 protocol extension introduced in CitySDK participation
    http://www.citysdk.eu/citysdk-toolkit/using-the-apis/open311-api/
    
    - multilang / locale support
    - extended attributes
    '''
    def __init__(self, url, apikey):
        georeporter.__init__(self, url, apikey)
    
   
    def getServices(self, locale=None, protocol="http", formatResp="xml", jurisdinction=None):
        params=None
        if not (locale is None):
            params={"locale":locale}
        return self.request(protocol,"services.",formatResp,jurisdinction,params)
    
    def getRequests(self,service_object_type=None, service_object_id=None, lat=None, long=None, radius=None, updated_after=None, updated_before=None, protocol="http", formatResp="xml", jurisdinction=None, params={}):
        params["extensions"]="true"
        if not (service_object_type is None): params["service_object_type"]=service_object_type
        if not (service_object_id is None): params["service_object_id"]=service_object_id
        if all([lat,long,radius]):
            params["lat"]=lat
            params["long"]=long
            params["radius"]=radius
        if not (updated_after is None): params["updated_after"]=updated_after
        if not (updated_before is None): params["updated_before"]=updated_before
        return self.request(protocol,"requests.",formatResp,jurisdinction,params)