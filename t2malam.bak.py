import pymongo
import requests
import datetime
import time
from datetime import datetime


t2mdeveloperid = "8883a971-e4d8-4d62-ac41-3b4623cc0501"
# Replace with your Line Notify access token
LINE_NOTIFY_TOKEN = "hCCDUEMUbYWDWmYln9LubNa6CkmfuGZLCrDoKSsv8zz"


def logout(session_id):
    logout_url = f"https://m2web.talk2m.com/t2mapi/logout?t2msession={session_id}&t2mdeveloperid={t2mdeveloperid}"
    # Logout
    response = requests.get(logout_url)
    # Check if the request was successful (HTTP status code 200)
    if response.status_code == 200:
        # Parse the JSON response (assuming it's JSON)
        logout_status = response.json()
        return (logout_status)
    else:
        return (f"Logout failed with status code: {response.json()}")


def login_getewon():
    t2maccount = "Rid2017"
    t2musername = "rid2017"
    t2mpassword = "rid_2017"
    t2msession = None

    # Login
    login_url = f"https://m2web.talk2m.com/t2mapi/login?t2maccount={t2maccount}&t2musername={t2musername}&t2mpassword={t2mpassword}&t2mdeveloperid={t2mdeveloperid}"
    response = requests.get(login_url)

    if response.status_code != 200:
        raise Exception(
            f"Login failed with status code: {response.status_code}")

    # Parse the JSON response (assuming it's JSON)
    login = response.json()
    t2msession = login.get('t2msession')
    print(t2msession)
    if not t2msession:
        raise Exception("Login response does not contain t2msession")

    # Get eWON data
    getewon_url = f"https://m2web.talk2m.com/t2mapi/getewons?t2msession={t2msession}&t2mdeveloperid={t2mdeveloperid}&t2maccount={t2maccount}&t2musername={t2musername}&t2mpassword={t2mpassword}"
    getewon_response = requests.get(getewon_url)

    if getewon_response.status_code != 200:
        raise Exception(
            f"Getewon failed with status code: {getewon_response.status_code}")

    data = getewon_response.json()

    print(logout(t2msession))
    return data


def insertdata(ewon_data):
    # Connect to the MongoDB server
    client = pymongo.MongoClient(
        "mongodb://admin:pass@localhost:27017/?authMechanism=DEFAULT")

    # Create or access the database
    db = client["ewon"]

    # Create or access the collection
    collection = db["checkstatus"]
    # Insert the document
    # Add a timestamp to your data
    timestamp = datetime.now()
    ewon_data["timestamp"] = timestamp

    inserted_id = collection.insert_one(ewon_data).inserted_id

    print(f"Data inserted with ID: {inserted_id}")


def laststatus():
    # Connect to the MongoDB server
    client = pymongo.MongoClient(
        "mongodb://admin:pass@localhost:27017/?authMechanism=DEFAULT")

    # Create or access the database
    db = client["ewon"]

    # Create or access the collection
    collection = db["checkstatus"]

    # Query the latest document
    latest_data = collection.find_one(sort=[("timestamp", pymongo.DESCENDING)])

    if latest_data:
        print("Latest Checkstatus Information:")
        print(f"Timestamp: {latest_data['timestamp']}")
        return latest_data
        # Print other relevant data fields as needed
    else:
        print("No data found for checkstatus.")


def send_line_notification(message):
    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"
    }
    data = {
        "message": f"\n---Status warning---\n{message}"
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        print("Notification sent successfully")
    else:
        print("Failed to send notification")


def offlinestatus(json_data):
    offline = []
    online = []
    text_offline = ""
    for ewon in json_data.get('ewons', []):
        # List of names to exclude
        excluded_names = [
            'Lam Phra Phloeng',
            'Huai Phu_New',
            'Huai Phu_New1',
            'Huai Sa Thot',
            'Lam Chae 1',
            'Lam Nang Rong_New'
        ]

        # Check if the ewon's name is not in the excluded names list
        if ewon.get('name') not in excluded_names:
            if ewon.get('status') == 'offline':
                offline.append(ewon.get('name'))
            elif ewon.get('status') == 'online':
                online.append(ewon.get('name'))
    for i in range(len(offline)):
        data = str(i+1) + ": " + offline[i] + "\n"
        text_offline = text_offline + data

    print(text_offline)

    current_datetime = datetime.now()
    # Format the current date and time as a string
    formatted_date = current_datetime.strftime("%d/%m/%Y ")
    formatted_time = current_datetime.strftime("%H:%M:%S")

    print(formatted_date)
    print(formatted_time)
    url = 'https://notify-api.line.me/api/notify'
    token = 'hCCDUEMUbYWDWmYln9LubNa6CkmfuGZLCrDoKSsv8zz'
    headers = {'content-type': 'application/x-www-form-urlencoded',
               'Authorization': 'Bearer '+token}

    msg = "\n" + "offline status\n" + "วันที่ :" + \
        str(formatted_date) + "\n" + "เวลา :" + str(formatted_time) + \
        "\n"+"-----------------\n" + text_offline
    r = requests.post(url, headers=headers, data={'message': msg})
    print(r.text)


def alertstatus(ewon_data, laststatus):
    current_datetime = datetime.now()
    # Format the current date and time as a string
    formatted_datetime = current_datetime.strftime("%d/%m/%Y %H:%M:%S")
    for i in range(len(laststatus['ewons'])):
        lastet_ewon_id = laststatus['ewons'][i]['id']
        lastet_ewon_status = laststatus['ewons'][i]['status']
        # print(f"{lastet_ewon_id} + {lastet_ewon_status}")
        for j in range(len(ewon_data['ewons'])):
            current_ewon_id = ewon_data['ewons'][j]['id']
            current_ewon_status = ewon_data['ewons'][j]['status']
            current_ewon_name = ewon_data['ewons'][j]['name']
            if lastet_ewon_id == current_ewon_id:
                if lastet_ewon_status == "offline" and current_ewon_status == "online":
                    print(
                        f"id: {current_ewon_id} ,name: {current_ewon_name} is online!! ({formatted_datetime})")
                    message = f"id: {current_ewon_id} ,name: {current_ewon_name} is online!! ({formatted_datetime})"
                    send_line_notification(message)
                elif lastet_ewon_status == "online" and current_ewon_status == "offline":
                    print(
                        f"id: {current_ewon_id} ,name: {current_ewon_name} is offline!! ({formatted_datetime})")
                    message = f"id: {current_ewon_id} ,name: {current_ewon_name} is offline!! ({formatted_datetime})"
                    send_line_notification(message)
                elif lastet_ewon_status == current_ewon_status:
                    print(
                        f"id: {current_ewon_id} ,name: {current_ewon_name} is same!! ({formatted_datetime})")
                    message = f"name: {current_ewon_name} is same!!"

                    # send_line_notification(message)
while True:
    try:
        ewon_data = login_getewon()
        # print(ewon_data)
        # insertdata = insertdata(ewon_data)
        laststatus = laststatus()
        # print(laststatus)
        alertstatus(ewon_data, laststatus)
        offlinestatus(ewon_data)
    except Exception as e:
        print(f"An error occurred: {e}")
    time.sleep(3600)
# while True:
#     for device in ewon_data:
#         status = check_eWON_status(device)
#         if status == "offline" and device["status"] == "online":
#             message = f"{device['name']} is offline!"
#             send_line_notification(message)
#             device["status"] = "offline"
#         elif status == "online" and device["status"] == "offline":
#             message = f"{device['name']} is online again!"
#             send_line_notification(message)
#             device["status"] = "online"
#     # Check every 5 minutes (adjust the interval as needed)
#     time.sleep(300)

# def run_script():
    # try:
    #     login_getewon()
    #     # line()
    # except Exception as e:
    #     print(f"An error occurred: {e}")
