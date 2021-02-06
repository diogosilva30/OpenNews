# task_queue
Implementing task queue using `Celery`, `Redis` & `Django Rest Framework`



## Steps to Setup and Run The Project
:heavy_check_mark: It is assumed that **Python >= 3.5** is installed in your system. And you are using debian distribution of **Linux**. Now, follow the below steps:
- [Setup Redis Server](#setup-redis-server)
- [Clone the Repository](#clone-the-repository)
- [Setup Virtual Environment and Install Required Packages](#setup-virtual-environment-and-install-required-packages)
- [Start Django Server and Celery](#start-django-server-and-celery)
- [Send Request Using Postman](#send-request-using-postman)



### Setup Redis Server
At first install **Redis** server using following commands:
```
sudo apt-get update
sudo apt-get install redis-server
```
After installation of the **redis server**, make sure the redis server is running. To check status:
```
sudo systemctl status redis
```
If it is not running, then start it using following command:
```
sudo systemctl start redis
```


### Clone the Repository
Make sure you have `git` installed in your syatem. <br><br>
Clone the repository using the following command:
```
git clone https://github.com/MhmdRyhn/task_queue.git
```


### Setup Virtual Environment and Install Required Packages
After cloning the repository, enter into the project directory.
```
cd task_queue/
```
NCreate virtual environment using following command. Make sure `virtualenv` package is installed in the system.
```
virtualenv -p python3 venv
```
If Python version 3.x is the default version in your system, you can use `python` instead of `python3` in the above command. <br><br>
Activate the virtual environment:
```
source venv/bin/activate
```
Install packages using `pip`:
```
pip3 install -r requirements.txt
```
If `pip3` doesn't work, use `pip` instead.



### Start Django Server and Celery
Open two terminal window or tab. Make sure that you are in the project root directory in both terminal window/tab. <br><br>
In one window/tab, start the **django server**.
```
python3 manage.py runserver
```
If Python version 3.x is the default version in your system, you can use `python` instead of `python3` in the above command. <br><br>
In another window/tab, start **Celery**.
```
celery -A task_queue worker -l info 
```


### Send Request Using Postman
Send a **Post** request using following payload to `http://127.0.0.1:8000/long-task/start/`
```
{"number": 900000008}
```
**Note:** Use a large number so that it takes 1-2 minute to get the result from the function. <br><br>
In response you will get a json like `{"task_id": "91247045-9a06-49d3-8ca3-a7421ac790a1"}`. <br><br>
Now, send a **Get** request to `http://127.0.0.1:8000/long-task/result/<task-id>/`. You will get the result if the operation is done, otherwise you will see the status as *PENDING*.





