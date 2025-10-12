def addHttpPrefix(url):
    result = {'http': '', 'https': ''}
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url
        result = {'http': url, 'https': url.replace('http://', 'https://')} 

    return result

def removeHttpPrefix(url):
    return url.replace('http://', '').replace('https://', '')

def getCSRFHostsFromAllowedHosts (allowedHostsArray):
    result = []
    for host in allowedHostsArray:
        cleanHost = removeHttpPrefix(host)
        
        #only append to result if the result does not already include the value in cleanHost
        if not cleanHost in result:
            result.append(addHttpPrefix(cleanHost)['http'])
            result.append(addHttpPrefix(cleanHost)['https'])
    return result