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
        # include all 3 solution  

        # single thread solution
        #doSerial()
        
        # do concurrent with thread pool
        doConcurrentThread()
        
        # do parallel with process pool (use process core count as parameter)
        # doParallelProcess(16)

    # # Notes :
    # best performant way to scrap cermati job page would be using concurreny with threading. though concurrency is not the same with multiple process parallel execution.
    # this due to threads still fall under GIL, but it offer more performance in this case. we don't need to do much heavy CPU work for scrapping cermati job posting, 
    # the main time wasted is on waiting for network call when we need to get job details. this is due to jobs details need to be called through API,  
    # and the resulting response is already in a json format that we can use directly (no need to process further, ex: doing regex search on page like what we did on root 'karir' page).
    # on a task that is less cpu heavy, threading excel due to thread switching upon idle. so more thread can be done in this case.
    # while on multi process, each process still bound on to this idle task. multi process will excel on when there's no cpu idle time that won't allow thread switchinng.
    # on larger dataset (job listing), this time difference will get even larger.
    #
    # concurrency also have access to direct access to main process variable (since it's basically singel process), unlike parallel process that need to implement routine or other ways to manage passing data between each process.
    # this because threads are still running on a single python interpreter, while multiple process run on their own python interpreter (hence the isolated data). 
    # coding for multi processing must consider this issue on a case by case basis.
    # 
    # here are the performance result on all 3 type of solution
    # tested AMD Ryzen 7 4800HS (8 CPU core, 16 Logical processor) with 24GB RAM
    # Run	serial	concurrent	pararrel (16)	parallel (8)	parallel (4)
    # 1	    31,361	2,248	    3,171	        5,082	        8,599
    # 2	    30,494	2,278	    3,138	        4,966	        8,467
    # 3	    30,542	2,355	    3,279	        5,117	        8,386
    # 4	    30,592	2,286	    3,188	        4,817	        8,625
    # 5	    30,631	2,306	    3,147	        4,880	        8,413
    # Avg	30,724	2,295	    3,184	        4,972	        8,498


# start
main()
