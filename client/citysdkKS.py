from citysdkParti import CitySDKParticipation


class CitysdkKlarschiff(CitySDKParticipation):
    '''
    CitySDK extensions specific for Klarschiff
    https://github.com/bfpi/klarschiff-citysdk
    
    - agency, photo-requests per request
    - vote, comments, abuse, notes per request 
    - update existing requests   
    '''
    
    #TODO: Enforce HTTPS
    
    def __init__(self, url):
        CitySDKParticipation.__init__(self, url)
        
    def getRequests(self, agency=None, statusExt=None, service_object_type=None, service_object_id=None, lat=None, long=None, radius=None, updated_after=None, updated_before=None, protocol="http", formatResp="xml", jurisdinction=None, params={}):
        if not (agency is None):
            params["agency_responsible"] = agency
        if not (statusExt is None):
            params["detailed_status"] = statusExt
        return CitySDKParticipation.getRequests(self, service_object_type=service_object_type, service_object_id=service_object_id, lat=lat, long=long, radius=radius, updated_after=updated_after, updated_before=updated_before, protocol=protocol, formatResp=formatResp, jurisdinction=jurisdinction, params=params)

    def getComments(self, request_id, apikey, protocol="http", formatResp="xml", jurisdinction=None):
        return self.request(protocol, "requests/comments/"+str(request_id)+".", formatResp, jurisdinction, {}, apikey)

    def getNotes(self, request_id, apikey, protocol="http", formatResp="xml", jurisdinction=None):
        return self.request(protocol, "requests/notes/"+str(request_id)+".", formatResp, jurisdinction, {}, apikey)