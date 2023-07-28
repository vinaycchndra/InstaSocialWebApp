from celery import shared_task
import sqlite3


# when user starts following someone his/her recent 10 posts are added to the follower's feed
@shared_task(bind=True, queue='Feed_Service_Que')
def add_feed(self, post_list, followed_id, followe_by_id):
    if len(post_list) > 0:
        table_name = 'UserFeedService_streamtable'
        column1 = 'user_id'
        column2 = 'post_id'
        column3 = 'follower_id'

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

    return 'Done'



# when user unfollows another user he/she does not want to see the posts of the unfollowed user's so need to be removed from the feed of the user
# performing unfollow action
@shared_task(bind=True, queue='Feed_Service_Que')
def remove_feed(self, post_list, followed_id, followe_by_id):
    if len(post_list) > 0:
        table_name = 'UserFeedService_streamtable'
        column1 = 'user_id'
        column2 = 'post_id'
        column3 = 'follower_id'

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

    return 'Done'




