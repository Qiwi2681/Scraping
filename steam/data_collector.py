#class to handle whatever data we throw at it
#works with lists for recurring data, or sets for unique data
class collector():
    def __init__(self):
        self.unique_data = set()
        self.data = []

    def __add__(self, other):
        if isinstance(other, collector):
            self.unique_data.update(other.unique_data)
            self.data.extend(other.data)
        else:
            self.data.append(other)
        return self

    def __iadd__(self, other):
        return self.__add__(other)

    def submit_data(self, data):
        if not data:
            return
        if isinstance(data, set):
            self.unique_data.add(data)
        else:
            self.data.append(data)

    def get_data(self):
        if self.unique_data:
            return self.unique_data
        return self.data
