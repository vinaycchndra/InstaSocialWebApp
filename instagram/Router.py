# defining other router
class OtherRouter:
    route_app_labels = {"auth", "contenttypes", "sessions", "admin", "user", "InstaService", "rest_framework"}

    def db_for_read(self, model, **hints):

        if model._meta.app_label in self.route_app_labels:
            return "auth_db"
        return None

    def db_for_write(self, model, **hints):

        if model._meta.app_label in self.route_app_labels:
            return "auth_db"
        return None

    def allow_relation(self, obj1, obj2, **hints):

        if (
            obj1._meta.app_label in self.route_app_labels
            or obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):

        if app_label in self.route_app_labels:
            return db == "auth_db"
        return None


# Route class for the feed router
class FeedRouter:

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'UserFeedService':
            return "db_feed"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'UserFeedService':
            return "db_feed"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'UserFeedService' and obj2._meta.app_label == 'UserFeedService':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'UserFeedService':
            return db == "db_feed"
        return None
