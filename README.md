# Data Collection of Medical Papers with Student Authors

This project has the aim of collecting a dataset of medical journal papers that have at least one student author and was published during or after 2012. Almost all the steps of collecting this dataset are automated and this repository contains the source code. The code utilizes parsing XML files, crawling the web, and csv & xlsx files manipulation in the process of collecting the data.

## Overview:

The process of collecting the data is divided into the following steps:

### PubMed Query:

The first step was to run the following query against the [PubMed](https://www.ncbi.nlm.nih.gov/pubmed/) database:

```
(medical student[Affiliation] OR medical student's[Affiliation] OR medical students[Affiliation] OR medical students'[Affiliation]) OR (mbbs student[Affiliation] OR mbbs students[Affiliation]) AND (Journal Article[ptyp] AND hasabstract[text] AND ("2012/01/01"[PDAT] : "2017/10/31"[PDAT]))
```

This query was conducted in 12 Nov 2017 and the results of the query were exported as an XML file named *pubmed_result.xml* in the repository.

### First Script:

The second step in the process is to run *Script1.py*. This script parses the *pubmed_result.xml* file and extracts needed attributes for each paper. It also collects extra attributes by crawling [Web of Science](http://www.webofknowledge.com/) website. This script was run in 19 Nov 2017. The script reports failure when it gets unexpected page format, and it failed for 10 papers for which the attributes were collected by manual search on the website. The attributes collected through both sources were collected in *Script1Out.csv*.

### Classifying Authors:

One of the attributes collected by the first script is each author’s affiliation. In this step we read the affiliation of each author and filled the "Is Student?" column in *Script1Out.csv*, the resulting file was stored in *Script2In.csv*. In cases where the affiliation was not conclusive of the authors’ status we contacted them via email to confirm their status at the times of publishing the papers.

### Second & Third Scripts:

Then *Script2.py* was run which reads *Script2In.csv* and produces three files *detailed.csv*, *included.csv* & *excluded.csv*. *detailed.csv* includes all the attributes collected with a row per author. *included.csv* & *excluded.csv* include paper related attributes only with a row per paper, papers conforming to our criteria - published during or after 2012 and has at least one student author – are stored in the *included.csv* file while the rest were stored in the *excluded.csv* file.
Finally, *Script3.py* combines the three csv files into one xlsx workbook and does some styling.

## Dependencies:

The following python dependencies are required:

* [selenium](http://www.seleniumhq.org) – Browser driving.
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) – HTML documents parsing.
* [xlsxwriter](https://xlsxwriter.readthedocs.io) – Writing xlsx files.

## Authors:
* **Ali Al Hawaj** <ali.alhawaj@hotmail.com> – Medical Student.
* **Mousa Al Haddad** <mousa.j.alhaddad@gmail.com> – Medical Student.
* **Wael Al Saeed** <wael.h.alsaeed@gmail.com> - Developer.

## License:

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.