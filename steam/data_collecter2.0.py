class Collector():
    def __init__(self):
        self.data = []

    def __add__(self, data):
        if isinstance(data, Collector):
            converted_set = set(self.data + data)

            result_collector = Collector()
            result_collector.set(converted_set)

            return result_collector
        else:
            self.data.append(data)

    def get(self):
        return self.data
    
    def set(self, data):
        if isinstance(data, list):
            self.data = data
        try:
            self.data = list(data)
        except TypeError as e:
            print(f"Error converting non iterable data to list {e}")
