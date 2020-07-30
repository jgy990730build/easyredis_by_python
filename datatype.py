import pickle

from database import DataBase
# 

# Set
class SetStore(DataBase):
    data_type = set

    def sadd(self, key, value):
        self.create_key(key)
        self.data[key].add(value)
        
    def smembers(self, key):
        print(self.data)
        return str(self.data[key])

    def load(self, nodes):
        for k, v in nodes.items():
            for x in v:
                self.sadd(k, x)

    def dump(self):
        nodes = {}
        for k, v in self.data.items():
            nodes[k] = v
        return nodes

    def register_command(self):
        commands = {}
        commands['SADD'] = self.sadd
        commands['SMEMBERS'] = self.smembers
        return commands


class StrStore(DataBase):
    data_type = str

    def set(self, key, value):
        self.create_key(key)
        self.data[key] = value

    def get(self, key):
        return self.data[key]

    def exists(self,key):
        if key in self.data.keys():
            return '(integer) 1'
        else:
            return '(integer) 0'

    def incr(self,key):
        afterdata = int(self.data[key])  
        afterdata += 1
        self.data[key] = str(afterdata)
        return self.data[key]

    def load(self, nodes):
        for k, v in nodes.items():
            self.set(k ,v)

    def dump(self):
        nodes = {}
        for k, v in self.data.items():
            nodes[k] = v
        return nodes

    def register_command(self):
        commands = {}
        commands['SET'] = self.set
        commands['GET'] = self.get
        commands['INCR'] = self.incr
        commands['EXISTS'] = self.exists
        return commands


class HashStore(DataBase):
    data_type = dict

    def hset(self, key, field, value ):
        self.create_key(key)
        self.data[key][field] = value

    def hget(self, key, field):
        return self.data[key][field]

    def load(self, nodes):
        for k, v in nodes.items():
            for field, value in v.items():
                self.hset(k, field, value)

    def dump(self):
        nodes = {}
        for k, v in self.data.items():
            nodes[k] = v
        return nodes
    
    def register_command(self):
        commands = {}
        commands['HSET'] = self.hset
        commands['HGET'] = self.hget
        return commands


class ListStore(DataBase):
    data_type = list

    def lpop(self, key):
        return self.data[key].pop(0)

    def rpop(self, key):
        return self.data[key].pop(-1)

    def lpush(self, key, value):
        if len(self.data) == 0:
            self.create_key(key)
        # print(self.data)
        if key not in self.data.keys():
            self.data[key] = []
        self.data[key].insert(0, value)
        # print(self.data)

    def lrange(self, key, value1, value2):
        number1 = int(value1)
        number2 = int(value2)
        leng = len(self.data[key])
        try:
            str1 = ''
            if number1 > leng:
                return "(empty list or set)"
            elif number2 > leng:
                for i in range(number1,leng):
                    str1 = str1 + self.data[key][i] + '\r\n'
                return str1
            elif number2 == 0:
                return self.data[key][0]
            else:
                for i in range(number1,number2):
                    str1 = str1 + self.data[key][i] + '\r\n'
                return str1
        except IndexError:
            return "(empty list or set)"
        

    def load(self, nodes):
        for k, v in nodes.items():
            for x in v:
                self.lpush(k,x)

    def dump(self):
        nodes = {}
        for k, v in self.data.items():
            nodes[k] = v
        return nodes
    
    def register_command(self):
        commands = {}
        commands['LPUSH'] = self.lpush
        commands['LPOP'] = self.lpop
        commands['LRANGE'] = self.lrange
        commands['RPOP'] = self.rpop
        return commands