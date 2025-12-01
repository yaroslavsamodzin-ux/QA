import requests
from bs4 import BeautifulSoup
import csv

urls = [
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&ma=792&doSearch=1",   
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&1&ma=791&doSearch=1",    
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&ma=795&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=790&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1063&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1273&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=789&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=788&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=787&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=786&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1563&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=785&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=784&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=783&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1942&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=782&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1232&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=781&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=780&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=779&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1941&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=866&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=778&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=777&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=776&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=775&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1937&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=774&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=773&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1541&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=772&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=728&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=771&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=770&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=769&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=768&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=767&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1542&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=766&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=765&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=764&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=762&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=761&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=760&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1546&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=759&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=758&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=756&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1062&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=755&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=754&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=753&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=752&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1543&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=751&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=750&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1938&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=749&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=748&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=747&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1696&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1940&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=746&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=745&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=744&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=743&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=742&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=741&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=740&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=739&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=738&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=794&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=737&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1162&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=736&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1251&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=735&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=734&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1636&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=727&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=733&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=732&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1274&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1544&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=731&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1545&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1231&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=730&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=729&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1230&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=763&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=796&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1160&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1255&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1229&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1169&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
]

results = []

for url in urls:
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    # кількість
    count_el = soup.select_one("span.result-count")
    count = count_el.get_text(strip=True).strip("()") if count_el else "?"

    
    # бренд з <h1>, очищений від "Легковые автомобили"
    h1_el = soup.select_one("h1")
    brand = h1_el.get_text(strip=True) if h1_el else "?"
    brand = brand.replace("Легковые автомобили", "").strip()
    
    print(f"{brand} {count}")
    results.append([brand, count])


# збереження у CSV
with open("vuvod/LV_autobonus_avto.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=";")
    writer.writerow(["Brand", "Count"])  # заголовки
    writer.writerows(results)

print("\n✅ Дані збережено у vuvod/LV_autobonus_avto.csv")
