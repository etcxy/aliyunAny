# 阿里云实例方案：

##### 适用对象:
解决穷人买不起服务器，但又需要用CDH，Hadoop集群的困扰。

##### 运行环境：
`python3`

### 1.准备工作
#### 1.1 先安装相关库
```bash
pip install aliyun-python-sdk-bssopenapi
pip install aliyun-python-sdk-ecs
pip install aliyun-python-sdk-core 
```

#### 1.2 修改config.py.bak

填补`config.py.bak`所需要的各类参数，并将`config.py.bak`改名为`config.py`

### 2.运行

```shell
python3 console.py
```

### 3. 使用说明
```
|1.检查工作
```
> 1. 查询余额,余额小于100，将弹出充值页面
> 2. 将当前主机IP，添加至安全组

```
|2.创建实例
```
> 1. 选择主机类型，若没有想要的类型，则推出程序后，在`config.py`里，填写`instance_machine_type`
> 2. 选择镜像，若无自定义镜像，则可以选择使用纯净的centos7.8镜像
> 3. 从镜像启动三台主机节点

```
|3.查看实例
```
> 1. 我说，我懒得写这个了，你信么
```
|4.网络写入
```
> 1. 公网：每次启动集群，三台节点的公网节点IP都会变化。所以，程序会将IP映射写入本地hosts文件里。注意，此操作，需要管理员权限
> 2. 私网: 每次启动集群,三台节点的公网节点IP都会变化。所以，程序会远程连接主机，写入服务器hosts文件映射
```
|5.释放实例
```
> 1. 删除先前的快照，和镜像
> 2. 对开启的hadoop001~003节点主机，进行快照操作。并保存为镜像
> 3. 释放三台主机
```
|6.退出程序
```
