import paramiko


class ConnectShell:

    def __init__(self, hostname, username):
        # 服务器相关信息,下面输入你个人的用户名、密码、ip等信息
        port = 22
        self.hostname = hostname
        # 创建SSHClient 实例对象
        self.conn = paramiko.SSHClient()
        # 调用方法，表示没有存储远程机器的公钥，允许访问
        self.conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 连接远程机器，地址，端口，用户名密码
        self.conn.connect(hostname, port, username, timeout=10)

    def do_action(self, command):
        # 输入linux命令
        stdin, stdout, stderr = self.conn.exec_command(command)
        # 输出命令执行结果
        out_result = stdout.read()
        if out_result:
            print(str(out_result, encoding='utf-8'))
        err_result = stderr.read()
        if err_result:
            print(str(err_result, encoding='utf-8'))

    def __del__(self):
        print(self.hostname + " hosts 写入成功")
        self.conn.close()


# 测试使用
if __name__ == '__main__':
    con = ConnectShell("hadoop001", "root")
    con.do_action("sed -i '/hadoop001/d' /etc/hosts")
    con.do_action("ls")
