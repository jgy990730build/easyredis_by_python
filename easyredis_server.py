import socket
import selectors
from threading import Lock
from multiprocessing.dummy import Pool as ThreadPool
from datatype import *
import os
import pickle

from logger import logger

# tcp通信接受和返回信息
# 5/6 命令执行和序列化存储
# 5/22 set不能使用‘’赋值，lrange使用负数会有bug
# 5/30 添加save命令

class RedisServer:
    def __init__(self, selector, sock, host='localhost', port=4396):
        self.datas = {
                'STR': StrStore(),
                'SET': SetStore(),
                'HASH': HashStore(),
                'LIST': ListStore()
                }
        self.host = host
        self.port = port
        self.sock = sock
        self.selector = selector
        self.commands_map = {}
        self.pool = ThreadPool(processes=4)
        self.lock = Lock()
    
    
    # 数据库反序列化
    def load(self):
        if os.path.exists('redis.db'):
            with open('redis.db', 'rb') as f:
                    datas = pickle.load(f)
            for k in self.datas:
                self.datas[k].load(datas[k])
        else:
            self.dump()
    

    # 数据序列化
    def dump(self):
        with self.lock:
            datas = {}
            for k in self.datas:
                datas[k] = self.datas[k].dump()
            with open('redis.db', 'wb') as f:
                pickle.dump(datas, f)


    def run(self):
        self.register_commands()
        self.load()
        self.process_request()
    

    def register_commands(self):
        for k in self.datas:
            command_map = self.datas[k].register_command()
            self.commands_map.update(command_map)


    def process_request(self):
        logger.info("listen  to %s:%s"%(self.host, self.port))
        self.sock.bind((self.host, self.port))
        self.sock.listen(1000)
        self.sock.setblocking(False)
        self.selector.register(self.sock, selectors.EVENT_READ, self.accept)
        while True:
            events = self.selector.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)


    # 等待连接
    def accept(self, sock, mask):
        conn, addr = sock.accept()
        logger.info("accepted conn from %s", addr)
        conn.setblocking(False)
        self.selector.register(conn, selectors.EVENT_READ, self.read)
    

    # 执行命令 
    def execute_command(self, command):
        # r , n 回车
        # 去掉回车
        commands = command.split('\r\n')
        # 命令的长度（现阶段4）
        rows = int(commands[0][1])
        method = commands[2].upper()
        
        # 判断命令
        if rows == 1:
            if(method == "SAVE"):
                self.dump()
                return 'OK'
            else:
                return 'Error'
        elif rows == 2:
            method , key = method, commands[4]
            try:
                message = self.commands_map[method](key)
                logger.info("execute %s", ' '.join([method, key]))
            except Exception:
                logger.error("execute %s", ' '.join([method, key]))
                return 'Error'
            return message
        elif rows == 3:
            method, key, value = method, commands[4], commands[6]
            try:
                message = self.commands_map[method](key, value)
                logger.info("execute %s", ' '.join([method, key, value]))
                if message == None:
                    message = 'OK'
            except Exception:
                logger.error("execute %s", ' '.join([method, key, value]))
                return 'Error'
            return message
        elif rows == 4:
            method, key, value, value2 = method, commands[4], commands[6], commands[8]
            logger.info("execute %s", ' '.join([method, key, value, value2]))
            try:
                message = self.commands_map[method](key, value, value2)
                if message == None:
                    message = 'OK'
            except Exception:
                logger.error("execute %s", ' '.join([method, key, value, value2]))
                return 'Error'
            return message
        else:
            logger.error("execute %s", ''.join(commands))
            return 'Error'


    # 读命令
    def read(self, conn, mask):
        data = conn.recv(1024)
        command = str(data, encoding="utf8")
        if command == 'exit':
            # print('closing', conn)
            self.selector.unregister(conn)
            conn.close()
        else:
            message = self.pool.apply(self.execute_command, (command,))
            # 持久化
            self.dump()
            conn.send(message.encode('utf8'))

def create_server():
    selector = selectors.DefaultSelector()
    sock = socket.socket()
    server = RedisServer(selector, sock)
    return server

if __name__ == '__main__':
    redis =create_server()
    redis.run()
