import time
import json
from urllib import request
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# set some variable
rootURL = "https://www.cermati.com/karir"
jobList = []

# function to get url data
def getFromURL(URL):
    page = request.urlopen(URL).read()
    return BeautifulSoup(page.decode('utf-8'),'html.parser')

# process job detail
def processDetail(val):
    # get job detail from api url    
    detailSoup = getFromURL(val['ref'])
    detail = json.loads(str(detailSoup))

    # set variabel to hold the value that we're looking for
    departement = detail['department']['label']
    title = detail['name']
    location = detail['location']['city'] + ', ' + getCountry(detail['customField'])
    jobType = detail['typeOfEmployment']['label']
    postedBy = detail['creator']['name']

    desc = []        
    descFull = BeautifulSoup(detail['jobAd']['sections']['jobDescription']['text'], "html.parser")
    descLists = descFull.find_all('li')
    for x in descLists:
        desc.append(x.text.strip())

    qual = []
    qualFull = BeautifulSoup(detail['jobAd']['sections']['qualifications']['text'], "html.parser")
    qualLists = qualFull.find_all('li')
    for x in qualLists:
        qual.append(x.text.strip())

    # print(departement, '|', title, '|', location)

    # # add job to job list
    # jobList.append({departement: {'title': title, 'location': location, 'jobType': jobType, 'postedBy': postedBy,
    #                               'description':desc, 'qualification': qual}})
    
    return {departement: {'title': title, 'location': location, 'description':desc, 'qualification': qual, 'jobType': jobType, 'postedBy': postedBy}} 
    
# Search full country name from custom field
def getCountry(data):
    returnValue = "N/A"
    for val in data:
        if val['fieldLabel'] == 'Country':
            returnValue = val['valueLabel']
    return returnValue

# write result to file
def writeResult(filename):
    print('Job(s) found : '+ str(len(jobList)))    
    json_dump = json.dumps(jobList, indent="\t")
    f = open(filename, 'w')
    f.write(json_dump)
    f.close()    
    print('Job(s) written to '+ filename)  

# DO it the old fashion single threaded way
def doSerial():
    # single process and thread
    jobList.clear()
    print('Start serial scrape')
    st = time.perf_counter()
    rootSoup = getFromURL(rootURL)
    data = json.loads(rootSoup.find('script', id="initials").string)    # get segment containing job listing data
    dataAll = list(data['smartRecruiterResult'].values())[-1]   # get last item on list, since it contains All job listing (not country specific)
    
    print('Processing job details')
    for val in dataAll['content']:    
        jobList.append(processDetail(val))
    
    et = time.perf_counter()
    print('Complete! Process elapsed time ' + str(et-st))

    writeResult('solution.json')

# let's do something new with thread and do some concurrent call
def doConcurrentThread():
    # do concurrent with thread    
    jobList.clear()
    print('Start concurent scrape')
    st = time.perf_counter()
    rootSoup = getFromURL(rootURL)
    data = json.loads(rootSoup.find('script', id="initials").string)    # get segment containing job listing data
    dataAll = list(data['smartRecruiterResult'].values())[-1]   # get last item on list, since it contains All job listing (not country specific)
    
    print('Processing job details')
    with ThreadPoolExecutor() as ex:
        results = ex.map(processDetail, dataAll['content']) 
    
    for result in results:
        jobList.append(result)

    et = time.perf_counter()
    print('Complete! Process elapsed time ' + str(et-st))

    writeResult('solution.json')

# let's do something new with process and do some parallel call
def doParallelProcess(core):    
    # do concurrent with thread
    jobList.clear()
    print('Start parallel scrape')
    st = time.perf_counter()
    rootSoup = getFromURL(rootURL)
    data = json.loads(rootSoup.find('script', id="initials").string)    # get segment containing job listing data
    dataAll = list(data['smartRecruiterResult'].values())[-1]   # get last item on list, since it contains All job listing (not country specific)
    
    print('Processing job details')
    with ProcessPoolExecutor(core) as ex:
        results = ex.map(processDetail, dataAll['content'])   
    
    et = time.perf_counter()
    print('Complete! Process elapsed time ' + str(et-st))

    for result in results:
        jobList.append(result)

    writeResult('solution.json')

# starting point
def main():
    if __name__ == '__main__':  
        # include all 3 solution . uncomment function call you want to run

        # single thread solution
        #doSerial()
        
        # do concurrent with thread pool
        doConcurrentThread()
        
        # do parallel with process pool (use process core count as parameter)
        # doParallelProcess(16)

# start
main()
