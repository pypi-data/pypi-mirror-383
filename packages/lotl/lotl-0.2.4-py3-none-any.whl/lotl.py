class lotl:
    def __init__(self,data,nth=-1):
        self.data = data
        self.nth = nth

    def all(self):
        for i in range(len(self.data)):
            if not self.data[i]:
                return False
        return True

    def any(self):
        for i in range(len(self.data)):
            if self.data[i]:
                return True
        return False

    def chain(self):
        hits = []
        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                hits.append(self.data[i][j])
        return hits

    def flatten(self):
        new_data = self.data
        if self.nth == -1:
            while True:
                if any([True if isinstance(i,list) or isinstance(i,tuple) else False for i in new_data]):
                    add = []
                    for i in new_data:
                        if isinstance(i,list) or isinstance(i,tuple):
                            add += i
                        else:
                            add.append(i)
                    new_data = list(add[:])
                else:
                    break
        else:
            for _ in range(self.nth):
                if any([True if isinstance(i,list) or isinstance(i,tuple) else False for i in new_data]):
                    add = []
                    for i in new_data:
                        if isinstance(i,list) or isinstance(i,tuple):
                            add += i
                        else:
                            add.append(i)
                    new_data = list(add[:])
                else:
                    break
        return new_data

    def mean(self):
        return lotl(self.data).sum() / len(self.data)

    def nested(self):
        count = 0
        new_data = self.data
        while True:
            if any([True if isinstance(i,list) or isinstance(i,tuple) else False for i in new_data]):
                count += 1
                add = []
                for i in new_data:
                    if isinstance(i,list) or isinstance(i,tuple):
                        add += i
                    else:
                        add.append(i)
                new_data = list(add[:])
            else:
                break
        return count

    def stdev(self):
        return (lotl([(i - lotl(self.data).mean()) ** 2 for i in self.data]).sum() / (len(self.data) - 1)) ** (1 / 2)
    
    def sum(self):
        hits = 0
        for i in range(len(self.data)):
            hits += self.data[i]
        return hits

    def zscore(self):
        return (self.nth - lotl(self.data).mean()) / lotl(self.data).stdev()
