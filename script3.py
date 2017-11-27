import unicodecsv as csv
import xlsxwriter

###################################Constants####################################

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
NUMBER_OF_AUTHORS_KEY = u"Number of Authors"
NUMBER_OF_STUDENTS_KEY = u"Number of Student Authors"
PERC_OF_STUDENTS_KEY = u"Percentage of Students"
FIRST_AUTHOR_STUDENT_KEY = u"Is 1st Author a Student?"
SOLELY_BY_STUDENTS=u"Solely by students?"
AUTHOR_STUDENT_KEY = u"Is Student?"
AUTHOR_NAME_KEY = u"Author Name"
AUTHOR_AFFILIATION_KEY = u"Author Affiliation"

EXTENDED_HEADERS = [
    N_KEY,
    PMID_KEY,
    JOURNAL_ISSN_KEY,
    JOURNAL_TITLE_KEY,
    JOURNAL_ISO_KEY,
    JOURNAL_COUNTRY_KEY,
    JOURNAL_IF_KEY,
    JOURNAL_NIF_KEY,
    JOURNAL_5IF_KEY,
    PUB_DATE_KEY,
    ARTICLE_TITLE_KEY,
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

################################Helper Functions################################

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

def isint(value):
  try:
    int(value)
    return True
  except ValueError:
    return False

def mergeHelper(start,end,toWrite):
  if start==end:
    return
  global detailed
  for i in range(len(EXTENDED_HEADERS)-3):
    detailed.merge_range(start,i,end,i,toWrite[i])

################################Helper Functions################################


workbook = xlsxwriter.Workbook('final_result/combined.xlsx')

detailed=workbook.add_worksheet('detailed')
included=workbook.add_worksheet('included')
excluded=workbook.add_worksheet('excluded')

#Format of all cells aligned left horizantlly and center vertically
generalFormat = workbook.add_format()
generalFormat.set_align('left')
generalFormat.set_align('vcenter')

#Format of cells with percentages
percentageFormat = workbook.add_format()
percentageFormat.set_num_format('0.00%')
percentageFormat.set_align('left')
percentageFormat.set_align('vcenter')

#Format of cells with floating point numbers
floatingFormat = workbook.add_format()
floatingFormat.set_num_format('0.000')
floatingFormat.set_align('left')
floatingFormat.set_align('vcenter')

included.set_column('A:U',None,generalFormat)
included.set_column('S:S',None,percentageFormat)
included.set_column('F:H',None,floatingFormat)

excluded.set_column('A:U',None,generalFormat)
excluded.set_column('S:S',None,percentageFormat)
excluded.set_column('F:H',None,floatingFormat)

detailed.set_column('A:Y',None,generalFormat)
detailed.set_column('T:T',None,percentageFormat)
detailed.set_column('G:I',None,floatingFormat)

#Writes the detailed sheet of the workbook
with open('csv/detailed.csv','r') as f:
  reader = csv.DictReader(f)
  detailed.write_row(0,0,EXTENDED_HEADERS)
  prv=u'1'
  start=1
  for e in enumerate(reader):
    n = e[0]+1
    row = e[1]
    if row[N_KEY]!=prv:
      mergeHelper(start,n-1,toWrite)
      start=n
      prv=row[N_KEY]
    toWrite = [row[h] for h in EXTENDED_HEADERS]
    #converts from string to int
    for i in [0,1,9,11,17,18]:
      if isint(toWrite[i]):
        toWrite[i]=int(toWrite[i])
    #converts from string to float
    for i in [6,7,8]:
      if isfloat(toWrite[i]):
        toWrite[i]=float(toWrite[i])
    toWrite[19]=1.0*toWrite[18]/toWrite[17]
    detailed.write_row(n,0,toWrite)
  mergeHelper(start,n,toWrite)

#Writes the included sheet of the workbook
with open('csv/included.csv', 'r') as f:
  reader = csv.DictReader(f)
  included.write_row(0,0,LIMITED_HEADERS)
  for e in enumerate(reader):
    n = e[0]+1
    row = e[1]
    toWrite = [row[h] for h in LIMITED_HEADERS]
    #converts from string to int
    for i in [0,8,10,16,17]:
      if isint(toWrite[i]):
        toWrite[i]=int(toWrite[i])
    #converts from string to float
    for i in [5,6,7]:
      if isfloat(toWrite[i]):
        toWrite[i]=float(toWrite[i])
    toWrite[18]=1.0*toWrite[17]/toWrite[16]
    included.write_row(n,0,toWrite)
  included.add_table(0,0,n,len(LIMITED_HEADERS)-1,
    {'style': 'Table Style Medium 17','columns':[{'header':h} for h in LIMITED_HEADERS]})

#Writes the excluded sheet of the workbook
with open('csv/excluded.csv', 'r') as f:
  reader = csv.DictReader(f)
  excluded.write_row(0,0,LIMITED_HEADERS)
  for e in enumerate(reader):
    n = e[0]+1
    row = e[1]
    toWrite = [row[h] for h in LIMITED_HEADERS]
    #converts from string to int
    for i in [0,8,10,16,17]:
      if isint(toWrite[i]):
        toWrite[i]=int(toWrite[i])
    #converts from string to float
    for i in [5,6,7]:
      if isfloat(toWrite[i]):
        toWrite[i]=float(toWrite[i])
    toWrite[18]=1.0*toWrite[17]/toWrite[16]
    excluded.write_row(n,0,toWrite)
  excluded.add_table(0,0,n,len(LIMITED_HEADERS)-1,
    {'style': 'Table Style Medium 17','columns':[{'header':h} for h in LIMITED_HEADERS]})

workbook.close()
