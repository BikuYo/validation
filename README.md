1. install mysql database system . since mysql client has been used in this system or else change the database setting in setting.py for your desire database
2.  download or clone project in designated dir
3. check for python in your system. if not then install python
4. check for virtualenv --version  .if not exist then install in your system
5. then  type below cmd in your terminal
6. pip install virtualenv
7. virtualenv venv   # creat venv in root folder of your main dir
8. venv\Scripts\activate   # for windows user
9. source myenv/bin/activate  #mac or linux user
10. pip install -r ../requirements.txt   # for installing all dependencies
11. cd cms_project  # move your cmd to actual project folder
12. python manage.py makemigrations
13. python manage.py migrate
14. python manage.py runserver  # for running server. on runnig this cmd at the end of terminal link to open on url will be given . eg. link likes http://127.0.0.1:8000/



