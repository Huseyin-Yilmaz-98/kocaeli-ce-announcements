import json
import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
from utils import ann_to_string, send_mail, compare_announcements, print_with_time
import time


class Tracker():
    def __init__(self, announcements_filepath="announcements.json"):
        # path to the file that stores previously saved announcements
        self.announcements_filepath = announcements_filepath
        # get previously saved announcements
        self.announcements = self.get_saved_announcements()

    # when this function is called, current announcements are checked once every 5 minutes
    def start(self):
        while True:
            success, self.current_announcements = self.get_current_announcements()

            # if the control was successful, success variable is true, if success is false
            if success:
                self.update_announcements_and_notify()
                print_with_time("Fetched announcements from the website.")
            else:
                print_with_time("Unable to fetch announcements from the website.")

            time.sleep(300)

    # returns a list of the previously saved announcements, if none are found, returns an empty list instead
    def get_saved_announcements(self):
        try:
            with open(self.announcements_filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print_with_time("No previously saved announcements are found.")
            return {}
        except:
            print_with_time(
                "File that stores previously saved announcements is corrupt.")
            return {}

    # returns a boolean value for success and the current announcements fetched from the website
    def get_current_announcements(self):
        current_announcements = {}
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"
        }

        try:
            response = requests.get("http://bilgisayar.kocaeli.edu.tr/duyurular.php", headers=headers, timeout=10)
        except:
            print_with_time("Error loading the announcements page!")
            return False, {}
        
        try:
            soup = bs(response.content, "html.parser")
            panel = soup.find_all("div", class_="panel-body")

            if len(panel) == 0:
                print_with_time("Panel not found in the page!")
                return False, current_announcements

            panel = panel[0]
            announcements = panel.find_all("div", class_="col-md-6")

            for ann in announcements:
                ann_id = ann.find("div", class_="modal").get("id")
                announcement = {"date": ann.find("p").find("span").text,
                                "sender": ann.find("p").find_all("span")[1].text,
                                "title": ann.find("h2", class_="modal-title").text,
                                "tabs": {}}
                keys = ann.find_all("dt")
                values = ann.find_all("dd")

                for i in range(len(keys)):

                    #if the tab doesnt contain a link, saves the text
                    if len(values[i].find_all("a")) == 0:
                        announcement["tabs"].update(
                            {keys[i].text: values[i].text.replace("\n\n", "\n")}
                        )
                    #if the tab contains a link, gets the link and joins it with the url
                    else:
                        link = values[i].find("a").get("href")
                        announcement["tabs"].update(
                            {keys[i].text: urljoin("http://bilgisayar.kocaeli.edu.tr/", link)}
                        )

                current_announcements.update({ann_id: announcement})

            return True, current_announcements
        except:
            print_with_time("Error parsing the announcements page!")
            return False, current_announcements

    def update_announcements_and_notify(self):
        for ann in self.current_announcements:
            # if the announcement is new, send mail
            if ann not in self.announcements:
                try:
                    send_mail("Yeni Duyuru!", ann_to_string(self.current_announcements[ann]))
                    time.sleep(1)
                    self.announcements.update({ann: self.current_announcements[ann].copy()})
                    print_with_time("Sent mail for a new announcement")
                except Exception as e:
                    print_with_time(
                        "Failed to send mail for a new announcement. Error: "+str(e))

            #if the announcement isn't new, send mail if there are any changes
            else:
                if not compare_announcements(self.announcements[ann], self.current_announcements[ann]):
                    try:
                        send_mail("Duyuru Değişikliği!", "Yeni Hali:\n\n"+ann_to_string(
                            self.current_announcements[ann])+"\n"*5+"Eski Hali:\n\n"+ann_to_string(self.announcements[ann]))
                        time.sleep(1)
                        self.announcements.update({ann: self.current_announcements[ann].copy()})
                        print_with_time("Sent mail for changes in an announcement.")
                    except Exception as e:
                        print_with_time("Failed to send mail for changes in an announcement. Error: "+str(e))

        #save announcements to the json file
        with open(self.announcements_filepath, "w", encoding="utf-8") as f:
            return json.dump(self.announcements, f, indent=4)
