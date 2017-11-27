from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import xml.etree.ElementTree
import unicodecsv as csv

###################################Constants####################################

OUTPUT_FILE_NAME='csv/Script1Out.csv'
with open('credentials.txt','r') as f:
    USERNAME,PASSWORD = f.read().split()
LOGIN_URL = 'https://ezp.uod.edu.sa/login'
WOS_URL = 'http://ezp.uod.edu.sa/login?url=http://www.webofknowledge.com/'

N_KEY = u"#"
PMID_KEY = u"PMID"
JOURNAL_ISSN_KEY = u"Journal ISSN"
PUB_DATE_KEY = u"Publication Year"
JOURNAL_TITLE_KEY = u"Journal Title"
JOURNAL_ISO_KEY = u"Journal ISO"
JOURNAL_COUNTRY_KEY = u"Journal Country"
JOURNAL_IF_KEY = u"Journal Impact Factor"
JOURNAL_NIF_KEY = u"Impact Factor Without Journal Self Cites"
JOURNAL_5IF_KEY = u"Five Year Impact Factor"
ARTICLE_TITLE_KEY = u"Article Title"
TIMES_CITED_KEY = u"Times Cited"
GRANT_LIST_KEY = u"Grants"
KEYWORD_LIST_KEY = u"Keywords"
WOS_RESEARCH_AREAS = u"WOS Research Areas"
WOS_CATEGORIES = u"WOS Categories"
MESH_HEADING_LIST_KEY = u"Mesh Headings"
AUTHOR_STUDENT_KEY = u"Is Student?"
AUTHOR_NAME_KEY = u"Author Name"
AUTHOR_AFFILIATION_KEY = u"Author Affiliation"

ROW_HEADERS = [
    N_KEY,
    PMID_KEY,
    JOURNAL_ISSN_KEY,
    PUB_DATE_KEY,
    JOURNAL_TITLE_KEY,
    JOURNAL_ISO_KEY,
    JOURNAL_COUNTRY_KEY,
    JOURNAL_IF_KEY,
    JOURNAL_NIF_KEY,
    JOURNAL_5IF_KEY,
    ARTICLE_TITLE_KEY,
    TIMES_CITED_KEY,
    GRANT_LIST_KEY,
    KEYWORD_LIST_KEY,
    WOS_RESEARCH_AREAS,
    WOS_CATEGORIES,
    MESH_HEADING_LIST_KEY,
    AUTHOR_STUDENT_KEY,
    AUTHOR_NAME_KEY,
    AUTHOR_AFFILIATION_KEY
]

##############################XML Helper Functions##############################

def getAuthorInfo(a):
    name = ""
    affiliation = ""
    if a.find("CollectiveName")!=None:
        name = a.find("CollectiveName").text
    else:
        name = a.find("LastName").text
        if a.find("ForeName")!=None:
            name+=", "+a.find("ForeName").text
        elif a.find("Initials")!=None:
            name += ", "+a.find("Initials").text+"."
        if a.find("Suffix")!=None:
            name = name+" "+a.find("Suffix").text
    if a.find("AffiliationInfo")!=None:
        affiliation = a.find("AffiliationInfo").find("Affiliation").text
    return (name,affiliation)

def getProperty(e,seq):
    for s in seq:
        e = e.find(s)
        if e==None:
            return '-'
    return e.text

def PMID(e):
    return getProperty(e,["MedlineCitation","PMID"])

def ArticleTitle(e):
    return getProperty(e,["MedlineCitation","Article","ArticleTitle"])

def ISSN(e):
    return getProperty(e,["MedlineCitation","Article","Journal","ISSN"])

def JournalTitle(e):
    return getProperty(e,["MedlineCitation","Article","Journal","Title"])

def ISOAbbreviation(e):
    return getProperty(e,["MedlineCitation","Article","Journal","ISOAbbreviation"])

def JournalCountry(e):
    return getProperty(e,["MedlineCitation","MedlineJournalInfo","Country"])

def PubDate(e):
    x = getProperty(e,["MedlineCitation","Article","Journal","JournalIssue","PubDate","Year"])
    if x!='-':
        return x
    x = getProperty(e,["MedlineCitation","Article","Journal","JournalIssue","PubDate","MedlineDate"])
    if x=='-':
        return x
    return x[:4]

def GrantList(e):
    e = e.find("MedlineCitation")
    if e==None:
        return "-"
    e = e.find("Article")
    if e==None:
        return "-"
    e = e.find("GrantList")
    if e==None:
        return "-"
    L = set()
    for a in e:
        L.add("( "+a.find("Agency").text+" / "+a.find("Country").text+" )")
    if len(L)==0:
        return "-"
    if len(L)==1:
        return L.pop()
    S = L.pop()
    while len(L)!=0:
        S+=" , "+L.pop()
    return S
def KeywordList(e):
    e = e.find("MedlineCitation")
    if e==None:
        return "-"
    e = e.find("KeywordList")
    if e==None:
        return "-"
    L = set()
    for a in e:
        L.add(a.text)
    if len(L)==0:
        return "-"
    if len(L)==1:
        return L.pop()
    S = L.pop()
    while len(L)!=0:
        S+=", "+L.pop()
    return S
def MeshHeadingList(e):
    e = e.find("MedlineCitation")
    if e==None:
        return "-"
    e = e.find("MeshHeadingList")
    if e==None:
        return "-"
    L = set()
    for a in e:
        T = []
        for x in a:
            T.append(x.text)
        if len(T)==0:
            j = 4
        elif len(T)==1:
            L.add(T[0])
        else:
            t = "("+T[0]
            for i in range(1,len(T)):
                t+="/"+T[i]
            t+=")"
            L.add(t)
    if len(L)==0:
        return "-"
    if len(L)==1:
        return L.pop()
    S = L.pop()
    while len(L)!=0:
        S+=", "+L.pop()
    return S
def AuthorList(e):
    e = e.find("MedlineCitation")
    if e==None:
        return "-"
    e = e.find("Article")
    if e==None:
        return "-"
    e = e.find("AuthorList")
    if e==None:
        return "-"
    RST = []
    for a in e:
        RST.append(getAuthorInfo(a))
    return RST

############################Crawler Helper Functions############################
def restartDriver():
    #closes the current driver (if any) then launches a new one and logges in
    global driver
    if driver:
        driver.quit()
    driver = webdriver.Chrome("./chromedriver")
    driver.get(LOGIN_URL)
    driver.find_element_by_name('user').send_keys(USERNAME)
    driver.find_element_by_name('pass').send_keys(PASSWORD)
    driver.find_element_by_name('login').click()

def crawlWebOfScience(PMID):
    #Navigates to WOS main page
    driver.get(WOS_URL)
    
    #Types the PMID in the search box
    driver.find_element_by_id('clearIcon1').click()
    driver.find_element_by_id('value(input1)').send_keys(str(PMID))
    
    #Chooses PubMed ID as the search criterion
    driver.find_element_by_id('select2-select1-container').click()
    o = driver.find_element_by_class_name('select2-search__field')
    o.send_keys('PubMed')
    o.send_keys(Keys.ENTER)
    driver.find_element_by_id('WOS_GeneralSearch_input_form_sb').click()

    #Parses the resulting page into a soup
    soup = BeautifulSoup(driver.page_source,'html.parser')
    
    #If no results found
    if len([s for s in soup.find(id='client_error_input_message').strings])>1:
        return False

    #Otherwise navigate to the page of the first (and only) result
    driver.find_element_by_css_selector('#RECORD_1 a').click()

    #Parse that page into a soup
    soup = BeautifulSoup(driver.page_source,'html.parser')
    
    #Gets the Times cited, Research areas,& WoS Categories attributes from the soup
    TimesCited = soup.find(attrs={'class':'block-text-content'}).find('p').find('span').string
    block = filter(lambda b: b.div and b.div.string and b.div.string=='Categories / Classification',soup.find_all(attrs={'class':'block-record-info'}))[0]
    p = block.find_all('p')
    ResearchAreas=[s for s in p[0].strings][-1]
    WoSCategories=[s for s in p[1].strings][-1]

    #If there is no Impact factor report then returns the available attributes
    if not(soup.find(id='links_isi_product_1') and soup.find(id='links_isi_product_1').find('li') and soup.find(id='links_isi_product_1').find('li').find('a')):
        return (TimesCited,ResearchAreas,WoSCategories,'','','')

    #Otherwise opens the Impact factor report
    driver.find_element_by_css_selector('#links_isi_product_1 li a').click()
    time.sleep(1)
    driver.switch_to_window(driver.window_handles[-1])
    time.sleep(1)
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#gridview-1012-body tr"))
    )

    #Parses the impact factor report page
    soup = BeautifulSoup(driver.page_source,'html.parser')

    #Selects the row corrosponding to the most recent year
    trs = map(lambda tr:(int(tr.find('td').find('a').string),tr),soup.find(id='gridview-1012-body').find_all('tr'))
    trs.sort(reverse=True)
    tr = trs[0][1]

    #Retrieves the impact factors out of that row
    JournalImpactFactor=tr.find(attrs={'class':'x-grid-cell-JournalImpactFactor'}).find('a').string
    ImpactFactorWithoutJournalSelfCites=tr.find(attrs={'class':'x-grid-cell-ImpactFactorWithoutJournalSelfCites'}).find('a').string
    FiveYearImpactFactor=tr.find(attrs={'class':'x-grid-cell-FiveYearImpactFactor'}).find('a').string

    #Closes the tab used for impact factor page
    driver.close()
    driver.switch_to_window(driver.window_handles[0])
    return (TimesCited,ResearchAreas,WoSCategories,JournalImpactFactor,ImpactFactorWithoutJournalSelfCites,FiveYearImpactFactor)

def crawl(PMID):
    #It will try 5 times to crawl the data
    rst = None
    attempts = 5
    while attempts>0 and rst==None:
        try:
            rst = crawlWebOfScience(PMID)
        except Exception as  e:
            pass
        attempts-=1
        
    #If it failed 5 times or search query resulted in no match
    if not rst:
        #If it failed it will report it so it can be done manually
        if rst==None:
            print PMID,"[Problem]"
        #In eiter cases it will return empty attributes
        return ("","","","","","")
    return rst

##################################Main Section##################################

def writeRow(attrib):
    #Gets dictionary of attributes and writes a row
    global writer
    eAttrib = {}
    for key in attrib:
        eAttrib[key] = unicode(attrib[key])
    writer.writerow(eAttrib)

#Opens output file
OUTPUT_FILE = open(OUTPUT_FILE_NAME, 'wb')
writer = csv.DictWriter(OUTPUT_FILE, fieldnames=ROW_HEADERS)
writer.writeheader()

#Initializes the web driver
driver = webdriver.Chrome("./chromedriver")
restartDriver()

#Reads the xml file
root = xml.etree.ElementTree.parse('pubmed_result.xml').getroot()

#Main loop
for element in enumerate(root):
    e = element[1]
    N = element[0]+1
    
    #Restarts the driver every 100 entries
    if N%100==0:
        restartDriver()

    #List of authors
    AList = AuthorList(e)

    #Gets attributes from the XML file
    ATR = {}
    ATR[N_KEY]=str(N)
    ATR[PMID_KEY]= PMID(e)
    ATR[JOURNAL_ISSN_KEY]= ISSN(e)
    ATR[PUB_DATE_KEY] = PubDate(e)
    ATR[JOURNAL_TITLE_KEY] = JournalTitle(e)
    ATR[JOURNAL_ISO_KEY] = ISOAbbreviation(e)
    ATR[JOURNAL_COUNTRY_KEY] = JournalCountry(e)
    ATR[ARTICLE_TITLE_KEY] = ArticleTitle(e)
    ATR[GRANT_LIST_KEY] = GrantList(e)
    ATR[KEYWORD_LIST_KEY] = KeywordList(e)
    ATR[MESH_HEADING_LIST_KEY] = MeshHeadingList(e)
    ATR[AUTHOR_STUDENT_KEY]=""

    #Gets the rest of attributes from the crawler
    CRW = crawl(ATR[PMID_KEY])
    ATR[TIMES_CITED_KEY] = CRW[0]
    ATR[WOS_RESEARCH_AREAS] = CRW[1]
    ATR[WOS_CATEGORIES] = CRW[2]
    ATR[JOURNAL_IF_KEY] = CRW[3]
    ATR[JOURNAL_NIF_KEY] = CRW[4]
    ATR[JOURNAL_5IF_KEY] = CRW[5]

    #Writes the rows
    for i in range(len(AList)):
        ATR[AUTHOR_NAME_KEY]=AList[i][0]
        ATR[AUTHOR_AFFILIATION_KEY]=AList[i][1]
        writeRow(ATR)

OUTPUT_FILE.close()
driver.quit()
