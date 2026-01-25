from bs4 import BeautifulSoup
import os 
from get_html import Intyear
def parse_html(html_content):
    
    soap = BeautifulSoup(html_content, 'lxml')
    Lists = soap.find_all("li",class_="ng-scope")
    for List in Lists:
        Match_name= List.find("span",class_="vn-matchOrder ng-binding ng-scope").text
        Stadium_location = List.find("p",class_="ng-binding").text.split(",")[-1]
        Stadium_Name = List.find("span",class_="ng-binding ng-scope").text
        Winner_team = List.find("div",class_="vn-ticketTitle ng-binding ng-scope").text
        Team_name=[]
        for i ,name in enumerate(List.find_all("h3",class_="ng-binding ng-scope")):
            if i == 1 or i == 3 :
                Team_name.append(name.text.strip())

        with open(f"season_details{Intyear}.txt", "a", encoding="utf-8") as file:
            file.write(f"The match name is {Match_name}\n")
            file.write(f"The match was played between {Team_name[0]} and {Team_name[1]}\n ")
            file.write(f"The match was played at {Stadium_Name.strip()} , {Stadium_location.strip()}\n")
            file.write(f"The winner of the match is {Winner_team.strip()}\n")
            file.write("---------------------------------------------------\n")
            file.write("---------------------------------------------------\n")
            file.write("---------------------------------------------------\n")
if __name__ == "__main__":  
    with open(f"page_source{Intyear}.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    
    Team_name,Winner_team,Stadium_Name,Stadium_location,Match_name  = parse_html(html_content)
    