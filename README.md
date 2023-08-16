# Here are some special commands to interact with the project since we are using multiple databases
1. python manage.py createsuperuser --database=auth_db  
   (In above command users are stored into the auth_db database so we need to specify the name of database)
2. python manage.py migrate --database=db_feed
3. python manage.py migrate --database=auth_db
   (We do not need mentioning the databases while running makemigrations command)

We have mapped different task to the different queues in RabbitMQ brocker, for this one should create 
queues with name that are defined in the task.py files of the installed apps within the task decorators....
for example: we have one que with name 'Feed_Service_Que' for adding posts of a followee to the feed of a new follower.

And when starting a new celery worker we need to define all the queues names: 
ex: celery -A instagram.celery worker --pool=solo  -l info -Q Feed_Service_Que,Post_Feed_Que,Notification_Service_Que




Developement Notes:
1. Although there is a single model for the liking of both the types which are comment on the post or post itself we created two apis for liking either the post or comment 
to remove the complexity of handling both the types because in our model we have parent_comment_id and parent_post_id for specifying like on the comment or like on the post.

2. There is an API to send back all the comments on a particular post for any logged-in user which appears in either of user's feed or user sees it though other user's profile page....

