# Purpose: Add Auktoriteettitunnisteet-template to articles with relation to people
# Additionally, check some linefeeds in articles and fix those where needed when adding Auktoriteettitunnisteet.
# Currently relies on Petscan-query to find candidate-articles with some filtering as well.
#
# Running script: python auktorit.py

import pywikibot
import json
from urllib.request import urlopen

# vanhantyylinen viitelohko
def reftoviitteet(oldtext):
    if '<references/>' in oldtext:
        return oldtext.replace("<references/>", "{{Viitteet}}")
    if '<references />' in oldtext:
        return oldtext.replace("<references />", "{{Viitteet}}")
    return oldtext

# ei rivinvaihtoa viitemallineen perässä? -> lisätään puuttuva
def addnewline(oldtext):
    index = oldtext.find("iitteet}}")
    if (index < 0):
        return oldtext
    strlen = len("iitteet}}\n")
    tmpstr = oldtext[index:index+strlen]
    if tmpstr.endswith("\n"):
        return oldtext
    else:
        return oldtext.replace("iitteet}}", "iitteet}}\n")

# ei tyhjää riviä viitemallineen ja tynkämallineen välissä? -> lisätään
def nonewlinetemplate(oldtext,template):
    # find template..
    indextemp = oldtext.find(template)
    if (indextemp < 0):
        return oldtext

    # find where reference-template is and which type it is
    reftext = "iitteet}}"
    indexref = oldtext.find(reftext)
    if (indexref < 0):
        reftext = "iitteet|sarakkeet}}"
        indexref = oldtext.find(reftext)
        if (indexref < 0):
            #print("did not find referencetemplate")
            return oldtext

    # check if there is only one linechange separating
    singleline = reftext + "\n" + template;
    strlen = len(singleline)
    sub = oldtext[indexref:indexref+strlen]
    if (sub == singleline):
        # output start + newline + rest (can't modify otherwise)
        #print("adding linechange")
        return oldtext[:indextemp] + "\n" + oldtext[indextemp:]
        
    #print("no changes, oldtext")
    return oldtext

# ei tynkämallinetta tai muuta? -> etsitään luokka ja lisätään sitä ennen
def insertaboveclass(oldtext):
    indexluokka = oldtext.find("[[Luokka:")
    if (indexluokka > 0):
        return oldtext[:indexluokka] + "{{Auktoriteettitunnisteet}}\n" + oldtext[indexluokka:]
    return oldtext

def insertabovetemplate(oldtext,templatename):
    indexluokka = oldtext.find(templatename)
    if (indexluokka > 0):
        return oldtext[:indexluokka] + "{{Auktoriteettitunnisteet}}\n" + oldtext[indexluokka:]
    return oldtext

site = pywikibot.Site("fi", "wikipedia")
site.login()

# haku auktoriteettitunnisteiden luettelossa olevilla

# scopus url = "https://petscan.wmflabs.org/?psid=24596657"
url = "https://petscan.wmflabs.org/?psid=24602545"
url += "&format=json"
url += "&output_limit=5"
response = urlopen(url)
data_json = json.loads(response.read())

for row in data_json['*'][0]['a']['*']:
    page=pywikibot.Page(site, row['title'])
    oldtext=page.text
    
    print(" ======== ")
    print("Editing [ " + row['title'] + " ]")
    if (oldtext.find("{{Auktoriteettitunnisteet") > 0 or oldtext.find("{{auktoriteettitunnisteet") > 0):
        print("Skipping " + row['title'] + " - auktoriteetit already added.")
        continue

    #temptext = reftoviitteet(oldtext)
    #pywikibot.showDiff(oldtext, temptext,2)

    temptext = addnewline(oldtext)
    
    #if oldtext != temptext:
    #    pywikibot.showDiff(oldtext, temptext,2)
    
# onko käännösmallinetta tai tynkämallinetta? jos ei kumpaakaan, onko aakkostusmallinetta?
# jos ei ole sitäkään etsi luokka ja lisää sen ylle
    if (temptext.find("{{Käännös") > 0):
        temptext = nonewlinetemplate(temptext,"{{Käännös")
        temptext = insertabovetemplate(temptext,"{{Käännös")
    elif (temptext.find("{{käännös") > 0):
        temptext = nonewlinetemplate(temptext,"{{käännös")
        temptext = insertabovetemplate(temptext,"{{käännös")
    elif (temptext.find("{{Tynkä") > 0):
        temptext = nonewlinetemplate(temptext,"{{Tynkä")
        temptext = insertabovetemplate(temptext,"{{Tynkä")
    elif (temptext.find("{{tynkä") > 0):
        temptext = nonewlinetemplate(temptext,"{{tynkä")
        temptext = insertabovetemplate(temptext,"{{tynkä")
    elif (temptext.find("{{OLETUSAAKKOSTUS") > 0):
        temptext = nonewlinetemplate(temptext,"{{OLETUSAAKKOSTUS")
        temptext = insertabovetemplate(temptext,"{{OLETUSAAKKOSTUS")
    elif (temptext.find("{{AAKKOSTUS") > 0):
        temptext = nonewlinetemplate(temptext,"{{AAKKOSTUS")
        temptext = insertabovetemplate(temptext,"{{AAKKOSTUS")
    elif (temptext.find("{{DEFAULTSORT") > 0):
        temptext = nonewlinetemplate(temptext,"{{DEFAULTSORT")
        temptext = insertabovetemplate(temptext,"{{DEFAULTSORT")
    else:
        temptext = insertaboveclass(temptext)

    if oldtext == temptext:
        print("Exiting. " + row['title'] + " - old and new are equal.")
        exit

    pywikibot.info('----')
    pywikibot.showDiff(oldtext, temptext,2)
    summary='Lisätään auktoriteettitunnisteet -malline'
    pywikibot.info('Edit summary: {}'.format(summary))

    if site.userinfo['messages']:
        print("Warning: Talk page messages. Exiting.")
        exit()

    question='Do you want to accept these changes?'
    choice = pywikibot.input_choice(
                question,
                [('Yes', 'y'),('No', 'N')],
                default='N',
                automatic_quit=False
            )

    pywikibot.info(choice)
    if choice == 'y':
        page.text=temptext
        page.save(summary)

