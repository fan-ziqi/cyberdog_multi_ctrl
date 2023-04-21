# cyberdog_multi_ctrl
cyberdog集群控制：使用python实现的[gRPC](http://doc.oschina.net/grpc?t=58008)client向cyberdog集群发送控制指令，通信协议为官方开源[cyberdog_app.proto](https://partner-gitlab.mioffice.cn/cyberdog/athena_cyberdog/-/tree/devel/athena_common/athena_grpc/protos) ，项目部分代码参考[CyberDog_Ctrl](https://github.com/Karlsx/CyberDog_Ctrl)项目。

### 依赖安装

- grpc：`sudo pip install grpcio` 

- grpc-tools：`sudo pip install grpcio-tools` 

- keyboard：`sudo pip install keyboard` 


### 协议编译

下载官方通信协议：[cyberdog_app.proto](https://partner-gitlab.mioffice.cn/cyberdog/athena_cyberdog/-/tree/devel/athena_common/athena_grpc/protos)

执行`python -m grpc_tools.protoc --python_out=. --grpc_python_out=. -I. cyberdog_app.proto`

成功后会生成`cyberdog_app_pb2.py`和`cyberdog_app_pb2_grpc.py`

### 使用

使用官方CyberdogApp正确连接铁蛋，进入遥控界面后左上角会显示铁蛋的IP地址。并将PC连接到铁蛋相同的网络环境下。

打开`ip.txt`，输入所有Cyberdog的ip地址，一行一个。（若文件为空，输出会提示输入IP地址）

运行：`sudo python3 cyberdog_multi_ctrl.py`，按提示选择模式。