# Data Collection of Medical Papers with Student Authors

**Objective:** Collecting a dataset of medical journal papers that have at least one student author and was published during the period 01/01/2012 to 31/12/2017.

**Aim:** To describe and analyze the progress of biomedical research conducted by medical students during the period 01/01/2012 to 31/12/2017.

Almost all the steps of collecting this dataset are automated and this repository contains the source code. The code utilizes parsing XML files, crawling the web, and csv & xlsx files manipulation in the process of collecting the data.

## Overview of Collection Process:

The process of collecting the data is divided into the following steps:

### PubMed Query:

The first step was to run the following query against the [PubMed](https://www.ncbi.nlm.nih.gov/pubmed/) database:

```
(medical student[Affiliation] OR medical student's[Affiliation] OR medical students[Affiliation] OR medical students'[Affiliation]) OR (mbbs student[Affiliation] OR mbbs students[Affiliation]) AND (Journal Article[ptyp] AND hasabstract[text] AND ("2012/01/01"[PDAT] : "2017/12/31"[PDAT]))
```

This query was conducted in 28 Apr 2018 and the results of the query were exported as an XML file named *pubmed_result.xml* in the repository.

### First Script:

The second step in the process is to run *Script1.py*. This script parses the *pubmed_result.xml* file and extracts needed attributes for each paper. It also collects extra attributes by crawling [Web of Science](http://www.webofknowledge.com/) website. This script was run in 5 May 2018, and the results were stored in *csv/Script1Out.csv*.

### Classifying Authors:

One of the attributes collected by the first script is each author’s affiliation(s). In this step we read the affiliation(s) of each author and filled the "Is Student?" column in *csv/Script1Out.csv*, the resulting file was stored in *csv/Script2In.csv*. In cases where the affiliation(s) were not conclusive of the authors’ status we contacted them via email to confirm their status at the times of publishing the papers.

### Second & Third Scripts:

Then *Script2.py* was run which reads *csv/Script2In.csv* and produces three files *csv/detailed.csv*, *csv/included.csv* & *csv/excluded.csv*. *csv/detailed.csv* includes all the attributes collected with a row per author. *csv/included.csv* & *csv/excluded.csv* include paper related attributes only with a row per paper, papers conforming to our criteria - published during or after 2012 and has at least one student author – are stored in the *csv/included.csv* file while the rest were stored in the *csv/excluded.csv* file.
Finally, *Script3.py* combines the three csv files into one xlsx workbook and does some styling.

## Dependencies:

The following python dependencies are required:

* [selenium](http://www.seleniumhq.org) – Browser driving.
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) – HTML documents parsing.
* [xlsxwriter](https://xlsxwriter.readthedocs.io) – Writing xlsx files.
* [unicodecsv](https://github.com/jdunck/python-unicodecsv) - Handling csv files encoded in Unicode.

## Authors:
* **Ali Al Hawaj** <ali.alhawaj@hotmail.com> – Medical Student.
* **[Mousa Al Haddad](https://github.com/MousaAlhaddad)** <mousa.j.alhaddad@gmail.com> – Medical Student.
* **Wael Al Saeed** <wael.h.alsaeed@gmail.com> - Developer.

## License:

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
