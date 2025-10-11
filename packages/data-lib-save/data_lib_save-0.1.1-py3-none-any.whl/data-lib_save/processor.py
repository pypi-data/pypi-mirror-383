class DataProcessor:
    def __init__(self, data: list):
        self.data = data

    def filter_by_key(self, key, value):
        return [item for item in self.data if item.get(key) == value]

    def search(self, key, query):
        return [item for item in self.data if query.lower() in str(item.get(key, '')).lower()]

    def sort_by_key(self, key, reverse=False):
        return sorted(self.data, key=lambda x: x.get(key), reverse=reverse)
