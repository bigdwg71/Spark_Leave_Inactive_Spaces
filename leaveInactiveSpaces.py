import datetime, sys, getopt, re, unicodedata, time, os

try:
    import dateutil.parser
    import sparkFunctions
except ImportError:
    sys.exit("\r\nYou are missing required Python3 packages to execute this script. Please ensure the sparkFunctions.py file is located in the same directory as the leaveInsactiveSpaces.py file and that you have the requests and dateutil libriaries installed by using the following commands:\r\n\r\npip3 install requests\r\npip3 install python-dateutil\r\n")

#Declare variables needed in the script
authToken = ""
contentType = str("application/json")
lastActive = 365
count = 0
oldCount = 0
deletedCount = 0
failedDeleted = 0
executeDeleteMembership = False
warningMessage = "\r\nThe -r (--remove) flag has NOT been set. This script will only find and list inactive spaces. To actually remove yourself from inactive spaces, please use the -r (--remove) CLI argument"

#Suck in the options and arguments from the CLI
try:
    opts, args = getopt.getopt(sys.argv[1:],"ha:l:r",["help","authToken=","lastActive=","remove"])
except getopt.GetoptError:
    print('LeaveInactiveSpaces.py [-h Help contents -a <Spark API authorization bearer token> -l <number of days inactive> -r <remove user from inactive spaces>]')
    sys.exit(2)
for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("\r\nDetailed Help:\r\n\r\n LeaveInactiveSpaces.py [-a <Spark API authorization bearer token> -l <number of days inactive> -r <remove matching spaces>]\r\n\r\n\
The LeaveInactiveSpaces script finds spaces that have been inactive for a user-defined amount of time and then removes the user from those spaces. By default, it simply finds the spaces matching the amount of time its been inactive. With the proper flag, it will actually remove the user from the space.\r\n\r\n\
-a    --authToken    Spark Authorization Bearer token needed to execute Spark API commands. DO NOT include Bearer prefix\r\n\r\n\
-l    --lastActive    Specify the time in days since the last activity in the space. Default is 365 days.\r\n\r\n\
-r    --remove    This flag sets the script to actually remove the user from the spaces found that have been inactive for the defined amount of time. Default is to just find and list the inactive spaces while NOT affecting membership.\r\n\r\n")
        sys.exit()
    elif opt in ("-a", "--authToken"):
        prefix = 'Bearer '
        if not re.match(prefix, arg):
            authToken = str("Bearer " + arg)
        else:
            authToken = str(arg)
    elif opt in ("-l", "--lastActive"):
        try:
            lastActive = int(arg)
        except ValueError:
            print("\r\n\r\n",arg,"is invalid! Please specify a number for the lastActive arguement.\r\n\r\n")
            sys.exit(2)
    elif opt in ("-r", "--remove"):
        executeDeleteMembership = True
        warningMessage = "\r\nTHIS IS NOT A TEST. You WILL BE REMOVED FROM Spaces! Prepare for ludicrous speed!"

#Checks if we received an authorization token, if we don't we exit, cause we know we gonna fail
if authToken == "":
    print("\r\nA Spark authorization bearer token is required. Please use the -h for help with using this script.\r\n")
    sys.exit(2)

#if the delete flag is set, we ask the user to confirm since this action is permanent
if executeDeleteMembership == True:
    proceed = sparkFunctions.areYouSure("\r\nYou have selected the remove flag. This will permanently remove you from the spaces that have been inactive for the specified amount of days.\r\n\r\nARE YOU SURE YOU WANT TO DO THIS?")
    if proceed == False:
        print("\r\nExiting...\r\n")
        sys.exit(2)

#Get the current user's email address
userInfo = sparkFunctions.getUserInfo(authToken)
personID = str(userInfo['id'])

print(warningMessage)

if executeDeleteMembership == True:
    print("\r\n5")
    time.sleep(1)
    print("4")
    time.sleep(1)
    print("3")
    time.sleep(1)
    print("2")
    time.sleep(1)
    print("1")
    time.sleep(1)
    print("Executing!")

print("\r\nLooking for spaces that haven't been active in", lastActive, "days...\r\n")

startTime = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
fileName = "LeaveInactiveSpaces-" + startTime + ".log"
#filePath = os.path.abspath(os.path.join(os.getcwd(), fileName))
filePath = os.path.join(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))),fileName)
print("A log file of this operation will be written to:\r\n" + filePath + "\r\n")
logFile = open(filePath,'x')
logFile.write("LeaveInactiveSpaces started at: " + startTime + "\r\n\r\n")
logFile = open(filePath,'a')

#Get the list of spaces
roomList = sparkFunctions.getRoomList(authToken)

#If we did NOT get a list of spaces, then we print an error and exit.
if roomList['statuscode'] != "200":
    print("Failed to retrieve space list. " + str(roomList) + "\r\n")
    logFile.write("Failed to retrieve Spark spaces list. ERROR: " + str(roomList) + "\r\n Exiting... \r\n")
    logFile.close()
    sys.exit(2)


#Process the list of spaces we received from the previous API call
for resp in roomList['items']:

    count += 1
    responseCode = "0"

    #convert the Spark-return lastActivity time into a useable value
    lastActivity = dateutil.parser.parse(resp['lastActivity'],ignoretz=True)

    #calculate the time in days since the space has been active
    currentLastActivity = abs(datetime.datetime.utcnow() - lastActivity).days

    #if the calculated inactivity is longer than the specified, then we will take action
    if currentLastActivity >= lastActive:

        oldCount += 1
        roomName = str(unicodedata.normalize('NFKD', resp['title']).encode('ascii','ignore'),'utf-8')
        roomID = str(resp['id'])

        #if the -d flag is set, we will do deletes. If not, we will just list
        if executeDeleteMembership == True:
            #Get team info
            if "teamId" in resp:
                teamID = str(resp['teamId'])
                #print(s.decode('unicode_escape').encode('ascii','ignore'))
                                
                teamInfo = sparkFunctions.getTeamDetails(authToken,teamID)
                logFile.write("Attempting action on: " + str(resp) + str(teamInfo) + "\r\n")
                
                if teamInfo['statuscode'] == "404":
                    teamName = ""
                else:
                    teamName = str(unicodedata.normalize('NFKD', teamInfo['name']).encode('ascii','ignore'),'utf-8')
                
                #If the room name is the same as the team name it belongs to, then assume its the General room, we don't want to touch it.
                if roomName == teamName:
                    print("General space in a Team detected. Skipping space: " + roomName + " - ID: " + roomID + " which has been inactive for " + str(currentLastActivity) + " days.")
                    logFile.write("General space in a Team detected. Skipping space: " + str(resp) + "\r\n")
                    continue
            elif resp['type'] == "direct":
                print("1:1 / People Space detected. Delete membership is not allowed. Skipping delete membership on : " + roomName + " - ID: " + roomID + " which has been inactive for " + str(currentLastActivity) + " days.")
                logFile.write("1:1 / People Space detected. Delete membership is not allowed. Skipping space: " + str(resp))
                continue

            membershipInfo = sparkFunctions.listMembership(authToken,roomID,personID)
            membershipID = membershipInfo['items'][0]['id']

            logFile.write("\r\nFound space has been inactive for " + str(currentLastActivity) + " days; attempting to delete membership: " + str(resp) + "\r\n")
            responseCode = sparkFunctions.deleteMembership(authToken,membershipID)

            if responseCode['statuscode'] == "204":
                deletedCount += 1
                print("Successfuly removed user from space: " + roomName + " - ID: " + resp['id'] + " which was inactive for " + str(currentLastActivity) + " days.")
                logFile.write("Successfully deleted memberbership: " + str(responseCode) + "\r\n")
            elif responseCode['statuscode'] == "0":
                failedDeleted +=1
                print("ERROR: " + responseCode['message'] + " - Space: " + roomName + " - " + resp['id'] + " which has been inactive for " + str(currentLastActivity) + " days.")
                logFile.write("Delete membership result: " + str(responseCode) + "\r\n")
            else:
                failedDeleted +=1
                print("ERROR: " + responseCode['statuscode'] + " : " + responseCode['message'] + " - Space: " + roomName + " - " + resp['id'] + " which has been inactive for " + str(currentLastActivity) + " days.")
                logFile.write("Delete membership result: " + str(responseCode) + "\r\n")
        else:
            print("Found: " + roomName + " - ID: " + resp['id'] + " which has been inactive for " + str(currentLastActivity) + " days.")
            logFile.write("Found space has been inactive for " + str(currentLastActivity) + " days: " + str(resp) + "\r\n")


#Print some totals and counts
logFile.write("\r\nTotal spaces: " + str(count))
print("\r\nTotal spaces: " + str(count))
logFile.write("\r\nSpaces last active over " + str(lastActive) + " days ago: " + str(oldCount))
print("Spaces last active over " + str(lastActive) + " days ago: " + str(oldCount))
logFile.write("\r\nDeleted membership from " + str(deletedCount) + " spaces")
print("Deleted membership from " + str(deletedCount) + " spaces")

#Only print the failed to delete count if we were actually trying to delete
if executeDeleteMembership == True:
    logFile.write("\r\nFailed to delete membership of " + str(failedDeleted) + " spaces")
    print("Failed to delete membership of " + str(failedDeleted) + " spaces")

#print("\r\n")
logFile.close()
