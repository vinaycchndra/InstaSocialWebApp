from celery import shared_task
import sqlite3


# when user starts following someone his/her recent 10 posts are added to the follower's feed
@shared_task(bind=True, queue='Feed_Service_Que')
def add_feed(self, post_list, followed_id, followe_by_id):
    if len(post_list) > 0:
        table_name = 'UserFeedService_streamtable'
        column1 = 'user_id'
        column2 = 'post_id'
        column3 = 'followed_user_id'

        query = "INSERT INTO %s (%s, %s, %s)" % (table_name, column1, column2, column3)
        query += "\nVALUES\n"

        for i in range(len(post_list) - 1):
            query += "({}, {}, {}), \n".format(str(followe_by_id), str(post_list[i]), str(followed_id))

        query += "({}, {}, {});".format(str(followe_by_id), str(post_list[-1]), str(followed_id))

        connection = sqlite3.connect('db_feed.sqlite3')
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        connection.close()

    return 'Added'


# when user unfollows another user he/she does not want to see the posts of the unfollowed user's
# so need to be removed from the feed of the user performing unfollow action
@shared_task(bind=True, queue='Feed_Service_Que')
def remove_feed(self, followed_id, followe_by_id):
    table_name = 'UserFeedService_streamtable'
    column1 = 'user_id'
    column3 = 'followed_user_id'
    query = "DELETE FROM {} WHERE {} = {} AND {} = {};".format(table_name, column1, followe_by_id, column3, followed_id)
    connection = sqlite3.connect('db_feed.sqlite3')
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    connection.close()
    return 'Removed'


# This task is called when the user adds a new post in that case it should be added to all the follwers feed table
@shared_task(bind=True, queue='Post_Feed_Que')
def after_post_feed(self, post_id, followers_list, followed_persons_id):
    if len(followers_list) > 0:
        table_name = 'UserFeedService_streamtable'
        column1 = 'user_id'
        column2 = 'post_id'
        column3 = 'followed_user_id'

        query = "INSERT INTO %s (%s, %s, %s)" % (table_name, column1, column2, column3)
        query += "\nVALUES\n"

        for i in range(len(followers_list) - 1):
            query += "({}, {}, {}), \n".format(str(followers_list[i]), str(post_id), str(followed_persons_id))

        query += "({}, {}, {});".format(str(followers_list[-1]), str(post_id), str(followed_persons_id))
        connection = sqlite3.connect('db_feed.sqlite3')
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        connection.close()
    return 'Added Post'


# This task is called when the user deletes a post in that case all the feed that have this post should be deleted...
@shared_task(bind=True, queue='Post_Feed_Que')
def remove_deleted_post(self, post_id):
    table_name = 'UserFeedService_streamtable'
    query = "DELETE FROM {} WHERE {} = {};".format(table_name, 'post_id', post_id)
    connection = sqlite3.connect('db_feed.sqlite3')
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    connection.close()
    return 'Removed Post'


