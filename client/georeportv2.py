import requests


class georeporter(object):
    '''
    REST API access via Open311 GeoReport v2
    http://wiki.open311.org/GeoReport_v2
    '''
    def __init__(self, url, apikey):
        self.baseurl = url  #url of API endpoint!
        self.apikey = apikey  #TODO: send key also on read requests?
    
    def getServices(self, protocol="http", formatResp="xml", jurisdinction=None):
        return self.request(protocol, "services.", formatResp, jurisdinction)
    
    def getServiceDef(self, serviceCode, protocol="http", formatResp="xml", jurisdinction=None):
        return self.request("http", "services/" + serviceCode + ".", formatResp, jurisdinction)
    
    def getRequest(self, request_id, protocol="http", formatResp="xml", jurisdinction=None):
        return self.request(protocol, "requests/" + request_id + ".", formatResp, jurisdinction)
    
    def getRequests(self, service_request_id=None, service_code=None, start_date=None, end_date=None, status=None, protocol="http", formatResp="xml", jurisdinction=None):
        params = {}
        if not (service_request_id is None):
            params["service_request_id"] = service_request_id  #TODO:Can be CSV
        if not (service_code is None):
            params["service_code"] = service_code  #TODO:Can be CSV
        if not (start_date is None):
            params["start_date"] = start_date
        if not (end_date is None):
            params["end_date"] = end_date
        if not (status is None):
            params["status"] = status  #TODO:Can be CSV
        return self.request(protocol, "requests.", formatResp, jurisdinction, params)
    
    def createRequest(self, lat, lon, service_code, email, description, protocol="https", formatResp="xml", jurisdinction=None, attr={}, tolerantSSL=False):
        #TODO: address_string
        #TODO: device_id etc.
        return self.__send(lat, lon, service_code, email, description, self.apikey, protocol, "services.", formatResp, jurisdinction, attributes=attr, tolerantSSL=tolerantSSL)

    def getIdByToken(self, token, protocol="http", formatResp="xml", jurisdinction=None):
        return self.request(protocol, "tokens/"+token+".", formatResp, jurisdinction)

    def request(self, protocol, path, formatResp, jurisdinction, reqParams=None, apikey=None):
        params = {}
        if not (jurisdinction is None):
            params["jurisdiction_id"] = jurisdinction
        if not (apikey is None):
            params["api_key"] = apikey
        if not (reqParams is None):
            params.update(reqParams)
        url = protocol + "://" + self.baseurl + path + formatResp
        print url
        return requests.get(url, params=params)
        
    def __send(self, lat, lon, service_code, email, description, apikey, protocol, path, formatResp, jurisdinction=None, address_string=None, address_id=None, device_id=None, account_id=None, first_name=None, last_name=None, phone=None, media_url=None, attributes={}, tolerantSSL=False):
        params = {}
        if not (jurisdinction is None):
            params["jurisdiction_id"] = jurisdinction
        params["api_key"] = apikey
        if all((lat, lon)):
            params["lat"] = lat
            params["long"] = lon
        else:
            params["address_string"] = address_string
            params["address_id"] = address_id
        params["service_code"] = service_code
        params["email"] = email
        params["description"] = description
        if not (device_id is None):
            params["device_id"] = device_id
        if not (account_id is None):
            params["account_id"] = account_id
        if not (first_name is None):
            params["first_name"] = first_name
        if not (last_name is None):
            params["last_name"] = last_name
        if not (phone is None):
            params["phone"] = phone
        if not (media_url is None):
            params["media_url"] = media_url
        params.update(attributes)
        url = protocol + "://" + self.baseurl + path + formatResp + "?" + self.__printURLParams(params)
        print url
        return requests.post(url, data=params, verify=not tolerantSSL)
    
    def __printURLParams(self, params):
        line = ""
        for k in params:
            line += ",%s=%s" % (k, params[k])
        return line[1:]
        