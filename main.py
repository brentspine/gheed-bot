from functools import partial
from raffle_info import RaffleInfo
from waytype import WayType
from waytype import RequestType
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from urllib.parse import urlencode
from inputimeout import inputimeout
import json
from tqdm import tqdm

def get_or_post_url(url, type, session):
    if type == RequestType.GET:
        return session.get(url)
    return session.post(url)

def simultaneosRequests(urls, type, session):
    try:
        with ThreadPoolExecutor(max_workers=50) as pool:
            partial_get_or_post = partial(get_or_post_url, type=type, session=session)
            responses = list(pool.map(partial_get_or_post, urls))
    except:
        print("Unknown error while requesting multiple urls")
        return []
    
    return responses


account_list = RaffleInfo.read_accounts()
account_amount = len(account_list)

print(str(len(account_list)) + " accounts in ownership")
print(" ")

skip_account_amount = 115

earned_session = 0
while True:
    if account_amount > skip_account_amount:
        giveaways = RaffleInfo.getRunningGiveaways()
    else:
        print("Get Running Skipped")
    answers = RaffleInfo.read_answers()
    remove_giveaways = []
    questions = []
    questions.append({"description": "Enter commands here (!help)", "title": "title", "EVENTID": "g-123", "BENEFICIARY": '{"question_text": ""}'})

    print(" ")

    i = 0
    earned_run = 0
    last_interaction_time = time.time()
    start_time = time.time()
    for account in account_list:
        i += 1
        # So on next run, all accounts will be included
        if skip_account_amount != 0:
            skip_account_amount = skip_account_amount - 1
            continue
        print(" ")
        print(" ")
        print(" \n")
        print("=====================================")
        print("Account " + str(i))
        print("Username: " + account["username"])
        print("Mail: " + account["mail"])
        print("Last Refresh: " + str(account["last_refresh"]))
        print("=====================================")
        print(" ")

        session = RaffleInfo.getSessionForAuth(account["cookies"])
        time.sleep(1)

        if time.time() - account["last_refresh"] > 60*60*24*5:
            print("Refreshing auth")
            session = RaffleInfo.updateAuth(session)
            time.sleep(1)
            print("Successfully refreshed auth")

        j = 0
        earned_account = 0
        for giveaway in giveaways:
            earned_giveaway = 0
            j += 1
            print(" ")
            print(" ")
            print("GIVEAWAY: " + giveaway["eventname"] + " von " + giveaway["host_info"]["username"] + " ("+giveaway["EVENTID"]+" - "+str(j)+")")
            if giveaway["EVENTID"] in remove_giveaways:
                print("Skipped, cause event over (Found in list)")
                continue
            if RaffleInfo.is_date_in_past(giveaway["active_to"]):
                print("Skipped, cause event over (Function check)")
                remove_giveaways.append(giveaway["EVENTID"])
                continue
            # time.sleep(1)
            complete_all = None
            ways_temp = RaffleInfo.getWays(giveaway["EVENTID"], session)
            if ways_temp == None:
                RaffleInfo.updateAuth(session)
                time.sleep(1)
                session = RaffleInfo.getSessionForAuth(i)
                time.sleep(0.75)
                ways_temp = RaffleInfo.getWays(giveaway["EVENTID"], session)
                time.sleep(0.25)
            ways = sorted(ways_temp, key=lambda x: not x["mandatory"])
            for c in ways:
                try:
                    print(str(c["WAYID"]) + " " + c["BENEFICIARY"])
                    if c["WAYTYPEID"] in [25, 26, 28, 33, 34, 35, 37, 38, 42, 45, 49, 51, 52, 53, 55, 56]:

                        # Amount fulfilled
                        if ((not c["earned_amount"] == None) and c["earned_amount"] >= c["amount"]):
                            # Cooldown set AND TRUE?
                            if (not c["cooldown"] == None and c["cooldown"]):
                                # Check if 1 day has passed
                                input_datetime = datetime.strptime(c["entry_date"], "%Y-%m-%dT%H:%M:%S")
                                current_datetime = datetime.now()
                                time_difference = current_datetime - input_datetime
                                if time_difference.days >= 1:
                                    print("Daily bonus available")
                                else:
                                    print("Daily bonus not available")
                                    continue
                            else:
                                print("Skipping, cause already done")
                                continue
                        if c["WAYTYPEID"] == 37:
                            complete_all = c
                            print("Saved Complete all for later")
                            continue

                        if c["WAYTYPEID"] == 42:
                            if not str(c["WAYID"]) in answers:
                                print("No answer for question found in data")
                                # Check if question id is already in list by using c["WAYID"]
                                if c["WAYID"] not in [question["WAYID"] for question in questions]:
                                    c["EVENTID"] = giveaway["EVENTID"]
                                    questions.append(c)
                                    print("Added question to unknown list")
                                continue
                            way_id = c["WAYID"]
                            url = f"https://gheed.com/prod/entryways/{way_id}?input=%7B%22answers%22%3A%5B%22{answers[str(way_id)]}%22%5D%7D"
                            res = session.post(url, json={"answers": [answers[str(way_id)]]})
                            d = res.json()
                            earned_way = d.get("earned_amount", 0)
                            earned_giveaway = earned_giveaway + earned_way
                            print("Earned: " + str(earned_way) + " entries (Tried answering question)")
                            continue

                        res = session.post("https://gheed.com/prod/entryways/"+str(c["WAYID"]))
                        if res.status_code == 403:
                            print("Cancelling, cause forbidden")
                            break
                        simultaneosRequests(["https://gheed.com/prod/raffles/"+giveaway["EVENTID"], "https://gheed.com/prod/raffles/"+giveaway["EVENTID"]+"/coupons/status"], RequestType.GET, session)
                        d = res.json()
                        earned_way = d.get("earned_amount", 0)
                        earned_giveaway = earned_giveaway + earned_way
                        print("Earned: " + str(earned_way) + " entries")
                        # time.sleep(0.75)
                except:
                    print("Unknown error")
                    continue
            if complete_all != None and earned_giveaway > 0:
                try:
                    print(str(c["WAYID"]) + " Complete all try")
                    res = session.post("https://gheed.com/prod/entryways/"+str(complete_all["WAYID"]))
                    simultaneosRequests(["https://gheed.com/prod/raffles/"+giveaway["EVENTID"], "https://gheed.com/prod/raffles/"+giveaway["EVENTID"]+"/coupons/status"], RequestType.GET, session)
                    d = res.json()
                    earned_way = d.get("earned_amount", 0)
                    earned_giveaway = earned_giveaway + earned_way
                    print("Earned: " + str(earned_way) + " entries")
                except:
                    print("Unknown error")
            earned_account = earned_account + earned_giveaway
            earned_run = earned_run + earned_giveaway
            earned_session = earned_session + earned_giveaway

            print(" ")
            print("Additional earned for giveaway " + giveaway["EVENTID"] + ": " + str(earned_giveaway))
            print("Additional earned for account (Session): " + str(earned_account))
            print("Additional earned in this run: " + str(earned_run))
            print("Additional earned in entire session: " + str(earned_session))
            print(" ")
            
    RaffleInfo.removeGiveawaysFromFile(remove_giveaways)
    print(f"Removed {str(len(remove_giveaways))} exceeded giveaways")
    print(" ")

    question_id = 0
    wait_time = 60*60*25
    question_time = 60*10
    print("Started at: " + str(start_time))
    print(" ")
    questions.append({"BENEFICIARY": '{"EVENTID" : "xqw", "question_text": "", "description": "Enter commmands here (!help)"}'})
    while True:
        if len(questions) < question_id:
            for i in tqdm(range(int(start_time + wait_time - time.time()))):
                time.sleep(1)
            break
        if len(questions) == question_id:
            question_id = len(questions) + 1
            print("No questions left")
            RaffleInfo.write_answers(answers)
            continue
        current_question = questions[question_id]
        question_bene = json.loads(current_question["BENEFICIARY"])
        print(" ")
        print("Link: " + "https://gheed.com/giveaways/"+ str(current_question["EVENTID"]) + "/")
        print("Question: " + question_bene["question_text"])
        print("Description: " + current_question["description"])

        if start_time + wait_time < time.time():
            if last_interaction_time + 60*1 < time.time():
                break
            timeout_for_question = question_time
        else:
            timeout_for_question = start_time + wait_time - time.time()

        try: 
            answer = inputimeout(prompt='Answer: ', timeout=timeout_for_question) 
            last_interaction_time = time.time()
            if answer.startswith("!"):
                if answer.lower() == "!help":
                    print("=" * 20)
                    print("!help - Hilfe")
                    print("!list - Liste aller Giveaways")
                    print(" - all")
                    print(" - YouTube")
                    print(" - public")
                    print(" - file")
                    print("!prob <id> - Probability zu gewinnen")
                    print("!details <id> - Details eines Giveaways")
                    print("!stats - Overall Stats")
                    print("=" * 20)
                    continue
                elif answer.lower().startswith("!list"):
                    try:
                        giveaways
                    except NameError:
                        giveaways = RaffleInfo.getRunningGiveaways()
                    gtype = "all"
                    if answer.lower().startswith("!list "):
                        args = answer.split(" ")
                        gtype = args[1]
                        if args[1].lower() != "all" and args[1].lower() != "public" and args[1].lower() != "youtube" and args[1].lower() != "file":
                            print("Unknown type '" + args[1] + "'")
                            continue
                    if gtype == "all":
                        for giveaway in giveaways: 
                            print(giveaway["eventname"] + " von " + giveaway["host_info"]["username"])
                            print(" - https://gheed.com/giveaways/" + str(c["EVENTID"]))
                        continue
                    elif gtype == "file":
                        fg = RaffleInfo.getGiveawaysFromFile()
                        for giveaway in giveaways: 
                            print(giveaway["eventname"] + " von " + giveaway["host_info"]["username"])
                            print(" - https://gheed.com/giveaways/" + str(c["EVENTID"]))
                        continue
                    elif gtype == "public":
                        print("Dikkah check doch einfach Website")
                        continue
                    continue
                elif answer.lower().startswith("!prob"):
                    giveaway_id = ""
                    args = answer.split(" ")
                    if len(args) <= 1:
                        print(" ")
                        try:
                            giveaways
                        except NameError:
                            giveaways = RaffleInfo.getRunningGiveaways()
                        for c in giveaways:
                            giveaway = RaffleInfo.getDetailsForRaffle(c["EVENTID"], True)
                            print("GIVEAWAY: " + giveaway["eventname"] + " von " + giveaway["host_info"]["username"] + " (https://gheed.com/giveaways/"+giveaway["EVENTID"]+")")
                            RaffleInfo.printProb(giveaway, account_amount)
                            print(" ")
                        continue
                    giveaway_id = args[1]
                    print(" ")
                    giveaway = RaffleInfo.getDetailsForRaffle(giveaway_id, True)
                    RaffleInfo.printProb(giveaway, account_amount)
                    continue
                elif answer.startswith("!details"):
                    print("Not yet done Faules Opfa")
                    continue
                elif answer.startswith("!stats"):
                    print("Noch nicht gemacht so Faul fr")
                    continue
            question_id = question_id + 1
            if len(answer) <= 0:
                print("No answer given")
                continue
            answers[str(current_question["WAYID"])] = answer
            print("Answer saved")
        except Exception as e:
            print(e)
            print("Question timeout") 
        
    print("Saving answers")
    RaffleInfo.write_answers(answers)
    print("Saved successfully")
    # time.sleep(60*60*12) # 12h
