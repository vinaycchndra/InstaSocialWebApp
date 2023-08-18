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

3. To provide a like count on a post or on a comment we are looking for denormalization techniques which is storing it as a field 
   within the post or comment table field only to fasten the query for likes on a post. However, we have separate like model which separately creates a like object for either post or comment. 
   But this is not really helping because it will create issue as we apply locking of entry to avoid simultaneous updation such as if one is trying to update the post and simultaneously people are liking the post in that
   case user who owns the post will not be able to update the post as other users are liking the post continuously in such case we can create a one to one field in another table
   wich we can lock from the point of concurrency to update like count which will also enable the post editing simultaneously.
   
4. Creating tables to store like count for both 


APIs list:
1. List of all comments with added fields liked and your comment. 
2. Update a comment
3. delete a comment 
4. create a comment 
5. get a comment
6. like a comment 
7. unlike a comment
8. like a post
9. unlike a post
10. follow a user 
11. unfollow a user
12. create a post
13. get a post
14. delete a post
15. update a post
16. get feed for a user api