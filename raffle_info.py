import requests
import json
import time
from datetime import datetime, date, timedelta
import re
from googleapiclient.discovery import build

class RaffleInfo():

    def cookie_jar_to_list(cookie_jar):
        cookie_list = {}
        for cookie in cookie_jar:
            cookie_list[cookie.name] = cookie.value

        return cookie_list

    def read_answers():
        with open("answers.json", "r") as file:
            data = json.load(file)
        return data

    def write_answers(data):
        with open("answers.json", "w") as file:
            json.dump(data, file, indent=2)

    def add_answer(new_answer):
        answers = RaffleInfo.read_answers()
        answers.append(new_answer)
        RaffleInfo.write_answers(answers)
        print("Addition successful.")

    def read_accounts():
        with open("accounts.json", "r") as file:
            data = json.load(file)
        return data

    def write_accounts(data):
        with open("accounts.json", "w") as file:
            json.dump(data, file, indent=2)

    def update_account(index=None, authorization=None, username=None, new_data=None, updated_at = None):
        print("Data: " + str(new_data))
        accounts = RaffleInfo.read_accounts()

        if new_data is None:
            print("Please provide new data for updating.")
            return

        if index is not None:
            if 0 <= index < len(accounts):
                accounts[index]['cookies'].update(new_data)
                if updated_at is not None:
                    accounts[index]['last_refresh'] = updated_at
            else:
                print("Invalid index. No changes made.")
        elif authorization is not None:
            found = False
            for account in accounts:
                if account['cookies'].get("Authorization") == authorization:
                    account['cookies'].update(new_data)
                    found = True
                    if updated_at is not None:
                        account['last_refresh'] = updated_at
                    break
            if not found:
                print("Authorization not found. No changes made.")
        elif username is not None:
            found = False
            for account in accounts:
                if account['username'] == username:
                    account['cookies'].update(new_data)
                    found = True
                    if updated_at is not None:
                        account['last_refresh'] = updated_at
                    break
            if not found:
                print("Username not found. No changes made.")
        else:
            print("Please provide either index or authorization for updating.")
            return

        RaffleInfo.write_accounts(accounts)
        print("Update successful.")

    def delete_account(index=None, authorization=None):
        accounts = RaffleInfo.read_accounts()

        if index is not None:
            if 0 <= index < len(accounts):
                del accounts[index]
            else:
                print("Invalid index. No changes made.")
        elif authorization is not None:
            accounts = [account for account in accounts if account['cookies'].get("Authorization") != authorization]
        else:
            print("Please provide either index or authorization for deletion.")
            return

        RaffleInfo.write_accounts(accounts)
        print("Deletion successful.")

    def add_account(new_account):
        accounts = RaffleInfo.read_accounts()
        accounts.append(new_account)
        RaffleInfo.write_accounts(accounts)
        print("Addition successful.")

    def getGiveawaysFromFile():
        file_path = "private_raffles.txt"
        # Initialize an empty array to store the results
        r = []

        # Read IDs from the file
        with open(file_path, 'r') as file:
            ids = file.readlines()

        # Remove leading and trailing whitespaces from each ID
        ids = [id.strip() for id in ids]

        # Send requests for each ID
        for id in ids:
            url = f'https://gheed.com/prod/raffles/{id}'
            try:
                # Send GET request to the URL
                response = requests.get(url)

                # Check if the request was successful (status code 200)
                if response.status_code == 200:
                    data = response.json()
                    for c in data["raffles"]:
                        r.append(c) 
                else:
                    # Handle unsuccessful response (e.g., print an error message)
                    print(f"Request for ID {id} failed with status code {response.status_code}")

            except requests.RequestException as e:
                # Handle any exception that might occur during the request
                print(f"Error occurred while fetching data for ID {id}: {e}")

        return r
    
    def removeGiveawaysFromFile(remove):
        file_path = "private_raffles.txt" 
        try:
            # Read existing IDs from the file
            with open(file_path, 'r') as file:
                existing_ids = file.readlines()

            # Remove leading and trailing whitespaces from each existing ID
            existing_ids = [id.strip() for id in existing_ids]

            # Remove the specified IDs from the existing ones
            updated_ids = [id for id in existing_ids if id not in remove]

            # Write the updated IDs back to the file
            with open(file_path, 'w') as file:
                file.write('\n'.join(updated_ids))

        except Exception as e:
            print(f"Error occurred while removing IDs: {e}")
            
    def addGiveawaysToFile(new_ids):
        file_path = "private_raffles.txt"
        
        try:
            # Read existing IDs from the file
            with open(file_path, 'r') as file:
                existing_ids = file.readlines()

            # Remove leading and trailing whitespaces from each existing ID
            existing_ids = [id.strip() for id in existing_ids]

            # Add the new IDs to the existing ones
            updated_ids = existing_ids + new_ids

            # Deduplicate the IDs to avoid duplicates in the file
            updated_ids = list(set(updated_ids))

            # Write the updated IDs back to the file
            with open(file_path, 'w') as file:
                file.write('\n'.join(updated_ids))

        except Exception as e:
            print(f"Error occurred while adding IDs: {e}")

    def getRunningGiveaways():
        r = []
        req = requests.get("https://gheed.com/prod/raffles/active/mostpopular?limit=20&mode=preview&region_mode=some&region=DE")
        data = req.json()
        r = r+data["raffles"]
        pages = data["total_pages"]
        for i in range(2, pages + 1):
            req = requests.get("https://gheed.com/prod/raffles/active/mostpopular?limit=20&mode=preview&region_mode=some&region=DE&page="+str(i))
            data = req.json()
            r = r+data["raffles"]
        r = RaffleInfo.removeDuplicatesFromArray(r)
        public_i = len(r)
        youtube_raffles = RaffleInfo.get_raffle_ids_youtube()
        for c in youtube_raffles:
            r.append(c)
        r = RaffleInfo.removeDuplicatesFromArray(r)
        youtube_i = len(r) - public_i
        file_raffles = RaffleInfo.getGiveawaysFromFile()
        for c in file_raffles:
            r.append(c)
        r = RaffleInfo.removeDuplicatesFromArray(r)
        file_i = len(r) - public_i - youtube_i
        
        for c in r:
            print(c["EVENTID"])
        print(str(public_i) + " public giveaways found")
        print(str(youtube_i) + " scraped from YouTube")
        print(str(file_i) + " additional private giveaways found (File)")
        return r
    
    def getDailyBonusGiveaways():
        r = []
        req = requests.get("https://gheed.com/prod/raffles/participated?limit=8&page=1&orderby=active_to%20desc&has_cooldown=true&has_coins=false")
        data = req.json()
        r = r+data["raffles"]
        pages = data["total_pages"]
        for i in range(2, pages + 1):
            req = requests.get("https://gheed.com/prod/raffles/active/mostpopular?limit=20&mode=preview&featured_included=true&page="+str(i))
            data = req.json()
            r = r+data["raffles"]
        for c in r:
            print(c["EVENTID"])
        print(str(len(r)) + " daily bonuses found")
        return r
    
    def getWays(event_id, session):
        r = []
        req = session.get("https://gheed.com/prod/raffles/"+str(event_id)+"/ways/status")
        data = req.json()
        if "message" in data:
            return None
        for c in data["eventways"]:
            r = r+c["ways"]
        return r

    def updateAuth(session):
        print("Updating auth")
        

        old_auth = session.cookies.get("Authorization")
        # Use a copy of the cookie jar
        new_auth = requests.cookies.RequestsCookieJar()
        new_auth.update(session.cookies)

        headers = {"Access-Token": session.cookies["Refresh"]}
        update = session.get("https://gheed.com/prod/jwt/refresh", headers=headers)
        update_data = update.json()
        print(update_data)
        
        # Set the updated Authorization cookie in the new cookie jar
        try:
            new_auth.set("Authorization", update_data["access_token"])
        except KeyError:
            print("KeyError, skipping... for now ig")
            RaffleInfo.update_account(None, old_auth, None, None, time.time())

        print(RaffleInfo.cookie_jar_to_list(new_auth))
        
        RaffleInfo.update_account(None, old_auth, None, RaffleInfo.cookie_jar_to_list(new_auth), time.time())
        
        r_session = requests.Session()
        r_session.cookies = new_auth
        return r_session

        
    def get_account(index=None, authorization=None):
        accounts = RaffleInfo.read_accounts()

        if index is not None:
            if 0 <= index < len(accounts):
                return accounts[index]
            else:
                return None
        elif authorization is not None:
            for account in accounts:
                if account.get("Authorization") == authorization:
                    return account
            return None
        else:
            print("Please provide either index or authorization for retrieval.")
            return None
    
    def getSessionForAuth(cookies):
        try:
            session = requests.Session()
            session.get("https://amiunique.org")
            session.cookies.update(cookies)
            return session
        except:
            print("Unknwon error while applying account details")
            return None
            
    def is_date_in_past(date_string):
        # Convert the input string to a datetime object
        input_date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")

        # Get the current date and time
        current_date = datetime.now() - timedelta(0,3700*100)

        # Compare the input date with the current date
        if input_date < current_date:
            return True
        else:
            return False
            
    def get_raffle_ids_youtube():
        search_url = "https://gheed.com/giveaways"
        api_key = "CENSORED-GETYOUROWN"
        # Set up the YouTube API
        youtube = build("youtube", "v3", developerKey=api_key)

        # Get the current date and time
        now = datetime.utcnow()

        # Calculate the date one week ago
        four_week_ago = now - timedelta(days=2)

        # Format the dates for the API request
        now_str = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        four_week_ago_str = four_week_ago.strftime("%Y-%m-%dT%H:%M:%SZ")

        giveaway_ids = []

        try:
            # Function to process search results
            def process_search_results(response, giveaway_ids):
                # Iterate through the search results
                for search_result in response.get("items", []):
                    video_id = search_result["id"]["videoId"]

                    # Get the video details
                    video_response = youtube.videos().list(
                        id=video_id,
                        part="snippet"
                    ).execute()
                    
                    print(video_id)

                    # Extract the video URL and description
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    video_description = video_response["items"][0]["snippet"]["description"]

                    # Use regular expressions to find giveaway IDs in the description
                    giveaway_urls = re.findall(r'https://gheed\.com/giveaways/([^\s/]+)', video_description)

                    # Check if any giveaway IDs were found
                    if giveaway_urls:
                        # Add the giveaway IDs to the list
                        giveaway_ids.extend(giveaway_urls)

            # Search for videos within the last week
            search_response = youtube.search().list(
                q=search_url,
                part="id",
                type="video",
                publishedAfter=four_week_ago_str,
                publishedBefore=now_str
            ).execute()

            # Process the initial search results
            process_search_results(search_response, giveaway_ids)

            # Continue to retrieve additional pages
            while "nextPageToken" in search_response:
                next_page_token = search_response["nextPageToken"]
                search_response = youtube.search().list(
                    q=search_url,
                    part="id",
                    type="video",
                    publishedAfter=four_week_ago_str,
                    publishedBefore=now_str,
                    pageToken=next_page_token
                ).execute()

                # Process the additional search results
                process_search_results(search_response, giveaway_ids)

        except Exception as e:
            print(f"An error occurred: {e}")

        giveaway_ids = RaffleInfo.removeExceededRaffles(giveaway_ids)
        
        for c in giveaway_ids:
            RaffleInfo.addGiveawaysToFile([c["EVENTID"]])
        
        print("Youtube done")
        
        return giveaway_ids
        
    def removeExceededRaffles(raffles):
        raffles = RaffleInfo.removeDuplicatesFromArray(raffles)
        r = []
        for c in raffles:
            if isinstance(c, (dict)):
                if not RaffleInfo.is_date_in_past(c["active_to"]):
                    r.append(c)
            url = 'https://gheed.com/prod/raffles/' + c
            try:
                # Send GET request to the URL
                response = requests.get(url)

                # Check if the request was successful (status code 200)
                if response.status_code == 200:
                    data = response.json()
                    for c in data["raffles"]:
                        if not RaffleInfo.is_date_in_past(c["active_to"]):
                            r.append(c)
                else:
                    # Handle unsuccessful response (e.g., print an error message)
                    print(f"Request for ID {c} failed with status code {response.status_code}")
            except requests.RequestException as e:
                # Handle any exception that might occur during the request
                print(f"Error occurred while fetching data for ID {c}: {e}")
                
        return r
            
    def saveToData(data):
        filename = "data.json"
        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=2)

    def readFromData():
        filename = "data.json"
        try:
            with open(filename, 'r') as json_file:
                data = json.load(json_file)
            return data
        except FileNotFoundError:
            return None

    def updateData(key, value):
        filename = "data.json"
        data = read_from_json(filename)
        if data is not None:
            data[key] = value
            save_to_json(filename, data)
        else:
            print(f"File {filename} not found.")

    def deleteFromData(key):
        filename = "data.json"
        data = read_from_json(filename)
        if data is not None and key in data:
            del data[key]
            save_to_json(filename, data)
        else:
            print(f"Key '{key}' not found in {filename}.")
            
    def removeDuplicatesFromArray(l):
        r = []
        [r.append(x) for x in l if x not in r]
        return r
        
    def getProbForGiveaways(id):
        if type(id) != "dict":
            giveaway = RaffleInfo.getDetailsForRaffle(id)
        else:
            giveaway = id
        return giveaway["total_entries"] / giveaway["user_entries"]
            
    def getDetailsForRaffle(id, require_session = False):
        account = None
        if require_session:
            account = RaffleInfo.read_accounts()[100]["cookies"]
            session = RaffleInfo.getSessionForAuth(account)
        url = f'https://gheed.com/prod/raffles/{id}'
        try:
            # Send GET request to the URL
            if require_session:
                response = session.get(url)
            else:
                response = requests.get(url)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                data = response.json()
                for c in data["raffles"]:
                    if c["user_entries"] == None:    
                        c["user_entries"] = RaffleInfo.getEntriesForRaffle(id, account)
                    return c
                return None
            else:
                # Handle unsuccessful response (e.g., print an error message)
                print(f"Request for ID {id} failed with status code {response.status_code}")

        except requests.RequestException as e:
            # Handle any exception that might occur during the request
            print(f"Error occurred while fetching data for ID {id}: {e}")
            
    def getEntriesForRaffle(id, account=None):
        if account == None:
            account = RaffleInfo.read_accounts()[100]
        session = RaffleInfo.getSessionForAuth(account)
        try:
            response = session.get(f"https://gheed.com/prod/raffles/{id}/entries")
            data = response.json()
            return data["raffles"][0]["user_entries"]
        except e:
            print(f"Ne Bruda: {e}")
            
    def printProb(giveaway, account_amount):
        if giveaway["user_entries"] == None or giveaway["user_entries"] <= 0:
            return
        print("Participants: " + str(giveaway["participants"]))
        print("Total Entries: " + str(giveaway["total_entries"]))
        print("Average Entries/User: " + str(giveaway["user_entries"]))
        print("Expected Bot Entries: " + str(giveaway["user_entries"] * account_amount))
        print("Probability: " + str(giveaway["total_entries"] / (giveaway["user_entries"] * account_amount)))
