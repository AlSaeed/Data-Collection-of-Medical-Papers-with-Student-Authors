import unicodecsv as csv

###################################Constants####################################

INPUT_FILE_NAME='csv/Script2In.csv'
DETAILED_SHEET_NAME='csv/detailed.csv'
INCLUDED_SHEET_NAME='csv/included.csv'
EXCLUDED_SHEET_NAME='csv/excluded.csv'

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
PAPER_COUNTRY_KEY = u"Paper Country"
TIMES_CITED_KEY = u"Times Cited"
GRANT_LIST_KEY = u"Grants"
KEYWORD_LIST_KEY = u"Keywords"
WOS_RESEARCH_AREAS = u"WOS Research Areas"
WOS_CATEGORIES = u"WOS Categories"
MESH_HEADING_LIST_KEY = u"Mesh Headings"
NUMBER_OF_AUTHORS_KEY = u"Number of Authors"
NUMBER_OF_STUDENTS_KEY = u"Number of Student Authors"
PERC_OF_STUDENTS_KEY = u"Percentage of Students"
FIRST_AUTHOR_STUDENT_KEY = u"Is 1st Author a Student?"
SOLELY_BY_STUDENTS=u"Solely by students?"
AUTHOR_STUDENT_KEY = u"Is Student?"
AUTHOR_NAME_KEY = u"Author Name"
AUTHOR_AFFILIATION_KEY = u"Author Affiliation(s)"

EXTENDED_HEADERS = [
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
    PAPER_COUNTRY_KEY,
    TIMES_CITED_KEY,
    GRANT_LIST_KEY,
    KEYWORD_LIST_KEY,
    WOS_RESEARCH_AREAS,
    WOS_CATEGORIES,
    MESH_HEADING_LIST_KEY,
    NUMBER_OF_AUTHORS_KEY,
    NUMBER_OF_STUDENTS_KEY,
    PERC_OF_STUDENTS_KEY,
    FIRST_AUTHOR_STUDENT_KEY,
    SOLELY_BY_STUDENTS,
    AUTHOR_STUDENT_KEY,
    AUTHOR_NAME_KEY,
    AUTHOR_AFFILIATION_KEY
]

LIMITED_HEADERS=EXTENDED_HEADERS[1:-3]

##################################Main Section##################################

IMPACT_FACTOR_MAP={}#A map of (Journal ISSN) -> Its impact factors
ARTICLES=[]#Articles list

#Fills IMPACT_FACTOR_MAP & ARTICLES
with open(INPUT_FILE_NAME, 'r') as f:
    reader = csv.DictReader(f)
    prv = u'1'
    rows = []
    for row in reader:
        N = row[N_KEY]
        #If impact factors are present then adds it to IMPACT_FACTOR_MAP
        if row[JOURNAL_IF_KEY]:
            IMPACT_FACTOR_MAP[row[JOURNAL_ISSN_KEY]]=(row[JOURNAL_IF_KEY],row[JOURNAL_NIF_KEY],row[JOURNAL_5IF_KEY])
        if N!=prv:
            ARTICLES+=[rows]
            rows=[]
            prv=N
        rows+=[row]
    ARTICLES+=[rows]

INCLUDED_ARTICLES=[]#List of articles that has at least one student author and is published during or after 2012
EXCLUDED_ARTICLES=[]#List of articles with no student author or has been published before 2012

for article in ARTICLES:
    #Gets the remaining attributes (all dependent on status of author (student/or not))
    nAuthors=len(article)
    nStudents=len(filter(lambda x: x=='Yes',[row[AUTHOR_STUDENT_KEY] for row in article]))
    pStudents="%.2lf" % (100.0*nStudents/nAuthors)
    firstAuthorStudent=article[0][AUTHOR_STUDENT_KEY]
    solelyByStudents= "Yes" if nAuthors==nStudents else "No"
    for row in article:
        #Adds these attributes
        row[NUMBER_OF_AUTHORS_KEY]=nAuthors
        row[NUMBER_OF_STUDENTS_KEY]=nStudents
        row[PERC_OF_STUDENTS_KEY]=pStudents
        row[FIRST_AUTHOR_STUDENT_KEY]=firstAuthorStudent
        row[SOLELY_BY_STUDENTS]=solelyByStudents
        #Adds journal impact factors 
        if row[JOURNAL_ISSN_KEY] in IMPACT_FACTOR_MAP:
            (row[JOURNAL_IF_KEY],row[JOURNAL_NIF_KEY],row[JOURNAL_5IF_KEY])=IMPACT_FACTOR_MAP[row[JOURNAL_ISSN_KEY]]
    #Adds article either to the included list or to the excluded list
    if nStudents==0 or int(row[PUB_DATE_KEY])<2012:
        EXCLUDED_ARTICLES+=[article]
    else:
        INCLUDED_ARTICLES+=[article]

#Writes a sheet of all the available data
with open(DETAILED_SHEET_NAME, 'wb') as f:
    writer = csv.DictWriter(f, fieldnames=EXTENDED_HEADERS)
    writer.writeheader()
    for a in ARTICLES:
        for row in a:
            writer.writerow(row)

#Writes a breif sheet of the included articles
with open(INCLUDED_SHEET_NAME, 'wb') as f:
    writer = csv.DictWriter(f, fieldnames=LIMITED_HEADERS)
    writer.writeheader()
    for article in INCLUDED_ARTICLES:
        row = article[0]
        for h in EXTENDED_HEADERS:
            if h not in LIMITED_HEADERS:
                row.pop(h)
        writer.writerow(row)

#Writes a brief sheet of the excluded articles
with open(EXCLUDED_SHEET_NAME, 'wb') as f:
    writer = csv.DictWriter(f, fieldnames=LIMITED_HEADERS)
    writer.writeheader()
    for article in EXCLUDED_ARTICLES:
        row = article[0]
        for h in EXTENDED_HEADERS:
            if h not in LIMITED_HEADERS:
                row.pop(h)
        writer.writerow(row)
