import paramiko

from instance.config import id_rsa_position


class ConnectShell:

    def __init__(self, hostname, username):
        # 服务器相关信息,下面输入你个人的用户名、密码、ip等信息
        port = 22
        self.hostname = hostname
        # 创建SSHClient 实例对象
        self.conn = paramiko.SSHClient()
        self.conn.load_system_host_keys()
        # 调用方法，表示没有存储远程机器的公钥，允许访问
        self.conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 连接远程机器，地址，端口，用户名密码
        if id_rsa_position:
            self.conn.connect(hostname, port, username, key_filename=id_rsa_position, timeout=10)
        else:
            self.conn.connect(hostname, port, username, key_filename=id_rsa_position, timeout=10)

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
        self.conn.close()


# 测试使用
if __name__ == '__main__':
    con = ConnectShell("xx.xx.xx.xx", "root")
    con.do_action("ls")
