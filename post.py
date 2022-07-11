
class Post:
    __slots__ = ('id', 'title', 'subtitle', 'content')

    def __init__(self, post):
        self.id = post['id']
        self.title = post['title']
        self.subtitle = post['subtitle']
        self.content = post['body']

    def __str__(self):
        return f"{self.id} : {self.title}\n {self.subtitle}\n {self.content} "
