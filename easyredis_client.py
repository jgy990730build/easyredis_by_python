import sys
from socket import *

# 服务器状态
RUN = True
STOP = False

class Shell:
    def display_cmd_prompt(self):
        # 提示输入
        sys.stdout.write('py-redis >')
        # 刷新缓冲区
        sys.stdout.flush()

# 获取输入的内容
    def get_cmd(self):
        # 使用sys.stdin.readline()可以实现标准输入，其中默认输入的格式是字符串，如果是int，float类型则需要强制转换。
        cmd = sys.stdin.readline()
        # 拆分命令
        tokens = cmd.split()
        return tokens

class Client:
    # 确定客户端要连接的网络端口
    def __init__(self):
        self.client=socket()
        self.client.connect(('localhost',4396))
        self.shell = Shell()
        self.status = RUN

    def generate_requests(self, tokens):
        cmds = []
        # 设置退出客户端
        if tokens == ['exit']:
            self.status = STOP
            return ''

        for t in tokens:
            cmds.append("$%s\r\n%s\r\n" % (len(t), t))
        s = "*%s\r\n%s" % (len(tokens), "".join(cmds))
        # print('s:')
        # print(s)
        return s
# 启动客户端，发送命令到服务端
    def run(self):
        while self.status == RUN:
            self.shell.display_cmd_prompt()
            tokens = self.shell.get_cmd()
            request = self.generate_requests(tokens)
            if request == '':
                self.client.sendall('exit'.encode('utf8'))
                continue
            self.client.sendall(request.encode('utf8'))
            response = self.client.recv(1024).decode()
            print(response)
        self.client.close()


if __name__ == '__main__':
    client = Client()
    client.run()
