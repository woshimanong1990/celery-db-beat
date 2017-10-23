# celery-db-beat

## Goal
  The goal of the project is to configure the schedule of the celery in the database.I use the project in Django,So this is a app for djanog.Maybe you can change it !
## Feature
  - database config ,so you don't need to restart celery.
  - config one machine ,schedule task to all machines 
  - you can easyily see the task last running time
## Requirement
  - django>=1.8,<1.9
  - celery == 3.1.23

## Using
  the schedule is similar to celery config.The diff is that the config  is string.
  - add the project(app) in django.settings
  - add the schedule config in the database
  
   


