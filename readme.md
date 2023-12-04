# Project Description
Creating a web scrapper using python to learn about performance optimation and compare difference between concurency and pararellism in python.

So here's the constraint / goals for this project :
- listing all job posting from cermati career page
- output job information and details into a json file
- employ performance optimation as much as possible

# Analysis
## Disclaimer
Fisrt of all, web scraping process is very dependent to target site and would need different processing depending on the site you're working on and the target data that you want to scrap.

## Game Plan
- use cermati career page as starting point and go from there. we cna simply hardcode this root page as this scrapper will only work on this use case.
- do http request and check the response, proceed based on the data. create flow to process the data as we see fit.
- will do several way to compare performance
	- single thread / serial process (default)
	- concurency using thread pool
	- do parallel processing with process poll

# Implementation
## Perfomance Table
Here are the performance result on all 3 type of solution.
Tested on:
- CPU	: AMD Ryzen 7 4800HS (8 CPU core, 16 Logical processor)
- RAM	: 24GB

Run | serial | concurrent | pararrel (16) | parallel (8) | parallel (4)
--- | --- | --- | --- | --- | ---
1 | 31,361 | 2,248 | 3,171 | 5,082 | 8,599
2 | 30,494 | 2,278 | 3,138 | 4,966 | 8,467
3 | 30,542 | 2,355 | 3,279 | 5,117 | 8,386
4 | 30,592 | 2,286 | 3,188 | 4,817 | 8,625
5 | 30,631 | 2,306 | 3,147 | 4,880 | 8,413
Avg | 30,724 | 2,295 | 3,184 | 4,972 | 8,498

## Deep Dive
### Requests vs urllib
My first attempt at this project is using `Requests` for my http library. It's easy enough to implement and working just fine.
For the sake of performance comparison, i switch to standard python `urllib`. And i found some shocking result. `urllib` process the scrape way faster than `requests`, i can easily get 2x as fast on serial processing and even more than 3x-4x with concurreny and pararellism.

Note : Performance table listing performance using `urllib`
### Serial, Thread and process
Best performant way to scrap cermati job page would be using concurreny with threading. Though concurrency is not the same with multiple process parallel execution. This due to threads still fall under GIL, but it offer more performance in this case. We don't need to do much heavy CPU work for scrapping cermati job posting, the main time wasted is on waiting for network call when we need to get job details. This is due to jobs details need to be called through API,and the resulting response is already in a json format that we can use directly (no need to process further, ex: doing regex search on page like what we did on root 'karir' page). On a task that is less cpu heavy, threading excel due to thread switching upon idle. So more thread can be done in this case. While on multi process, each process still bound on to this idle task. Multi process will excel on when there's no cpu idle time that won't allow thread switchinng. On larger dataset (job listing), this time difference will get even larger.

Concurrency also have access to direct access to main process variable (since it's basically single process), unlike parallel process that need to implement routine or other ways to manage passing data between each process. This because threads are still running on a single python interpreter, while multiple process run on their own python interpreter (hence the isolated data). Coding for multi processing must consider this issue on a case by case basis.