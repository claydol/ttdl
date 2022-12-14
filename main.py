from waybackpy import WaybackMachineSaveAPI
from bs4 import BeautifulSoup
from halo import Halo
import requests
import os

red = '\033[91m'
white = '\033[97m'
purple = '\033[95m'
green = '\033[92m'
grey = '\033[90m'
yellow = '\033[93m'

folder = "beats" # change this to use custom donwload path

def beatFolderCheck():
    if (not os.path.exists(folder)): 
        os.mkdir(folder)

def artistFolderCheck(name):
    beatFolderCheck()
    if (not os.path.exists(os.path.join(folder, name))):
        os.mkdir(os.path.join(folder, name))

def formatTimestamp(ts: str):
    return (f"{white}{ts[0:4]}-{ts[4:6]}-{ts[6:8]} {ts[8:10]}:{ts[10:12]}:{ts [12:14]}")

def single(user: str, autosave: bool):
    tracks = {}
    links = []
    
    for archive in (requests.get("https://web.archive.org/cdx/search/cdx?url=traktrain.com/" + user)).text.strip().split('\n'):
        arcSplit = archive.strip().split(' ')
        if ((len(arcSplit) == 1) and (len(arcSplit[0]) == 0)):
            if (autosave == False):
                print(f"\n{red}sorry! {grey}this artist has no backups on the wayback machine,")
                print(f"{grey}would you like to save this page on wayback now? {white}(y/n)")
                option = input(f'\n{white}   > {purple}')
                print()
            else:
                option = 'y'

            print()
            if (option == 'y'):
                userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0'
                wb = WaybackMachineSaveAPI("traktrain.com/" + user, userAgent)
                with Halo(text=f'{purple}saving {white}traktrain.com/' + user, spinner='star', color='white') as h:
                    if (requests.get(wb.save()).status_code == 200):
                        h.stop_and_persist(symbol = f'{green}✔', text = f'{purple}saved {white}traktrain.com/' + user)
                    else:
                        h.stop_and_persist(symbol = str(f'{red}✖'), text = f'{red}uh oh! {white}an error occured :(' + user) #.encode('utf-8')
                single(user, autosave)
                return
            
            else:
                menu()
                return

        if (len(archive.split(' ')) > 1):
            link = "https://web.archive.org/web/" + archive.split(' ')[1] + "/" + "traktrain.com/" + user
            links.append(link)

    print()
    for link in links:
        ts = formatTimestamp(str(link.split('/')[4]))
        with Halo(text=f'{purple}checking scrape from ' + ts, spinner='star', color='white') as h:
            bs = BeautifulSoup(requests.get(link).content, "html.parser")
            for track in bs.find_all(attrs={"class":["overlay__play play", "overlay__play play ga-test-play"]}):
                nickname = bs.find(attrs = {"class": "profile-bio__name"})
                if ((nickname is not None) and (nickname.get_text() in str(track["data-name"]))):
                    tracks[track["data-id"]] = track["data-name"].strip()
            h.stop_and_persist(symbol = f'{green}✔{purple}')

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Accept': 'audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://traktrain.com/',
        'Range': 'bytes=0-',
        'Origin': 'https://traktrain.com',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'audio',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
    }

    if (len(tracks.keys()) > 0):
        print()
        for url in tracks.keys():
            textFormat = f'{purple}downloading {white}"' + str(tracks.get(url)) + '"'
            with Halo(text=textFormat, spinner='star', color='white') as h:
                beat = requests.get('https://d2lvs3zi8kbddv.cloudfront.net/' + url.strip(), headers=headers)
                if (beat.status_code == 206):
                    artistFolderCheck(user)
                    open(os.path.join(os.path.join(folder, user), str(tracks.get(url)).replace("/", "_")) + ".mp3", 'wb').write(beat.content)
                    h.stop_and_persist(symbol = f'{green}✔', text = textFormat + f"{green} 206{grey}, downloaded successfully")
                else:
                    h.stop_and_persist(symbol = f'{red}✖', text = textFormat + f"{red} 404{grey}, deleted from servers")
    
    else:
        print(f'\n{red}sorry! {grey}this artist has no downloadable beats :(')
        return
    
    return

def multiple():
    print(f"\n{purple}would you like automatically save profiles that aren't on the wayback machine? {white}(y/n)")
    option = input(f'\n{white}   > {purple}')
    autosave = bool(option == 'y')

    if (not os.path.exists("profiles.txt")):
        print(f"\n{red}uh oh! {white}'profiles.txt' {grey}was deleted/not found :(")
        return
    
    profiles = []
    with open('profiles.txt', 'r') as profilesList:
        [profiles.append(line.rstrip("\n")) for line in profilesList]
        if (len(profiles) == 0):
            print(f"\n{red}uh oh! {white}'profiles.txt' {grey}was empty :(")
            return
    
    for profile in profiles:
        print(f"\n{purple}+{white}----------------------------------------------------------{purple}+")
        print(f"{purple} traktrain.com/{white}" + profile)
        print(f"{purple}+{white}----------------------------------------------------------{purple}+", end = '')
        single(profile.strip(), autosave)
        print()
    
    return
    
def menu():
    print(f"{white}[1]{purple} scrape single artist") # scrapes deleted beats for a single artist via username
    print(f"{white}[2]{purple} scrape multiple artists") # scrapes beats for list of users from a file
    print(f"{white}[3]{purple} exit")

    option = input(f'\n{white}   > {purple}')
    if (option == '1'):
        single(input(f"\n{white}username: {purple}"), False)
    if (option == '2'):
        multiple()
    else:
        exit(f'{purple}\ngoodbye :3')

print(f"{purple}  _____   _____             ___     _    ")
print(f"{purple} |_   _| |_   _|    {white}o O O  {purple}|   \\   | |    ")
print(f"{purple}   | |     | |     {white}o       {purple}| |) |  | |__  ")
print(f"{purple}   |_|     |_|    {white}TT__[O]  {purple}|___/   |____| ")
print(f'{white}_|"""""|_|"""""| ' + '{' + f'======|_|"""""|_|"""""|  ')
print(f"""{white}"`-0-0-'"`-0-0-'./o--000'"`-0-0-'"`-0-0-'  """)
print(f"{grey}                         code by @claydol\n")
menu()