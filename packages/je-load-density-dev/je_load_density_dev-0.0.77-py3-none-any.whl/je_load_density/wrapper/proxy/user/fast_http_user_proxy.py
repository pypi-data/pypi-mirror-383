class ProxyFastHTTPUser(object):

    def __init__(self):
        self.user_detail_dict = None
        self.tasks = None

    def setting(self, user_detail_dict: dict, tasks):
        self.user_detail_dict = user_detail_dict
        self.tasks = tasks
