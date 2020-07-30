# 数据储存方式
class DataBase:
    data_type = None

    def __init__(self, data=None):
        self.data = {}
        self.value_type = data or self.data_type()

    # 区分存储方式（命令）
    def create_key(self, key):
        self.data[key] = self.value_type

    # NotImplementedError抛出没实现方法的错误
    # 声明抽象方法
    def load(self):
        raise NotImplementedError
    
    def dump(self):
        raise NotImplementedError
