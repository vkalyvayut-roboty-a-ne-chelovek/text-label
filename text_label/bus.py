
class Bus:
    def __init__(self):
        self.objects = {}

    def register(self, name, obj):
        self.objects[name] = obj

    def __getitem__(self, item):
        return self.objects.get(item, None)

    def __getattr__(self, item):
        return self.objects.get(item, None)



