import sys,json

try:
    import requests
except ImportError:
    sys.exit("\r\nYou are missing required Python3 packages to execute this script. Please ensure the sparkFunctions.py file is located in the same directory as the leaveInsactiveSpaces.py file and that you have the requests and dateutil libriaries installed by using the following commands:\r\n\r\npip3 install requests\r\npip3 install python-dateutil\r\n")

contentType = str("application/json")

#Function to return API user information
def getUserInfo(authToken):
    jsonResponse = {'statuscode':"0"}
    url = "https://api.ciscospark.com/v1/people/me"
    headers = {
        'authorization': authToken,
        'content-type': contentType}
    response = requests.request("GET", url, headers=headers)
    if response.text:
        jsonResponse = json.loads(response.text)
    jsonResponse['statuscode'] = str(response.status_code)
    return jsonResponse

#Function to return room list for Spark user
def getRoomList(authToken):
    jsonResponse = {'statuscode':"0"}
    url = "https://api.ciscospark.com/v1/rooms"
    querystring = {"max":"2999"}
    headers = {
        'authorization': authToken,
        'content-type': contentType}
    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.text:
        jsonResponse = json.loads(response.text)
    jsonResponse['statuscode'] = str(response.status_code)
    return jsonResponse

#Function to return details of a specific space
def getRoomDetails(authToken,roomID):
    jsonResponse = {'statuscode':"0"}
    url = "https://api.ciscospark.com/v1/rooms/" + roomID
    headers = {
        'authorization': authToken,
        'content-type': contentType}
    response = requests.request("GET", url, headers=headers)
    if response.text:
        jsonResponse = json.loads(response.text)
    jsonResponse['statuscode'] = str(response.status_code)
    return jsonResponse

#Function to return details of a specific space
def getTeamDetails(authToken,teamID):
    jsonResponse = {'statuscode':"0"}
    url = "https://api.ciscospark.com/v1/teams/" + teamID
    headers = {
        'authorization': authToken,
        'content-type': contentType}
    response = requests.request("GET", url, headers=headers)
    if response.text:
        jsonResponse = json.loads(response.text)
    jsonResponse['statuscode'] = str(response.status_code)
    return jsonResponse

def listMembership(authToken,roomID,personID):
    jsonResponse = {'statuscode':"0"}
    url = "https://api.ciscospark.com/v1/memberships"
    querystring = {"roomId":roomID,"personId":personID}
    headers = {
        'authorization': authToken,
        'content-type': contentType}
    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.text:
        jsonResponse = json.loads(response.text)
    jsonResponse['statuscode'] = str(response.status_code)
    return jsonResponse

def deleteMembership (authToken,membershipID):
    jsonResponse = {'statuscode':"0"}
    url = "https://api.ciscospark.com/v1/memberships/" + membershipID
    headers = {
        'authorization': authToken,
        'content-type': contentType}
    response = requests.request("DELETE", url, headers=headers)
    if response.text:
        jsonResponse = json.loads(response.text)
    jsonResponse['statuscode'] = str(response.status_code)
    return jsonResponse

#Function to leave a room and return a result code
def deleteRoom (authToken,roomID):
    jsonResponse = {'statuscode':"0"}
    url = "https://api.ciscospark.com/v1/rooms/" + roomID
    headers = {
        'authorization': authToken,
        'content-type': contentType}
    response = requests.request("DELETE", url, headers=headers)
    if response.text:
        jsonResponse = json.loads(response.text)
    jsonResponse['statuscode'] = str(response.status_code)
    return jsonResponse

#Function that requires user input to proceed
def areYouSure(question, default="no"):
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
