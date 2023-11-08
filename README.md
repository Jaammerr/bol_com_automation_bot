## How it works:

1) The data is loaded from the file "input.xlsx" and stored in a list of lists. Each list in the list represents a row in the file.
2) After run the program, all tasks is waiting to be executed (random time sleep) with proxies (if it enabled in settings). 
3) When the tasks are executing - script is searching for the selected items using search term and url, opening the page and doing random actions. 
4) After the task is completed, the script is waiting for the next task to be executed.
5) Every browser session has a random stealth settings to prevent detect bot automation.


## List of actions:
* Page scrolling
* Dynamic page scrolling
* Clicking on "Alle productspecificaties"
* Clicking on "Toon meer"
* Clicking on "Toon minder"
* Clicking on "Vergelijk met andere artikelen"
* Clicking on product share ("Delen")
* Add product to wishlist
* Remove product from wishlist
* Clicking on forward / backward arrows in image gallery of the product
* Clicking on image


## Input file (input.xlsx):
~~~text
Column A - Product name
Column B - EAN
Column C - Search term
Column D - Link
~~~
Link must be in full format, example: https://www.bol.com/nl/nl/p/kingsowned-wimperserum-extra-sterk-het-unieke-kingsowned-lash-serum/9300000161235462/


## Config (settings.yaml):
~~~yaml
use_proxy: True/False # If True - script will use proxies from proxies.txt file, format "ip:port:user:pass"
sleep_between_tasks: True/False # If True - script will sleep between tasks 
launch_per_24h: 100 # How many times every value (from Excel) will be executed per 24 hours
concurrency_limit: 3 # How many tasks can be executed at the same time (Threads)
~~~
Proxy supported type - HTTP


## Installation:
1) Install Python 3.10+
2) Clone this repository to your computer/server
3) Open terminal and go to the project folder
4) Install requirements: `pip install -r requirements.txt`
5) Run the script: `python main.py`

##
All done :)