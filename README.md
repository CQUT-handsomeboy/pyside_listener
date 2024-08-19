![](./.asset/github-header-image.png)

# 🤗Quick Start

1.  需要一个Redis数据库，创建一个WSL，以ubuntu为例，然后：

```bash
sudo snap install redis # 首先安装
sudo snap start redis # 运行数据库
redis-cli # 连接数据库
BGRESTORE /path/to/dump.rdb # 导入数据
```

2. Clone项目

```powershell
git clone https://github.com/CQUT-handsomeboy/pyside_listener.git pyside_listener
cd pyside_listener
poetry install # 安装依赖项
```

3.  下载模型权重文件

自行去Sherpa-onnx官网下载，主要有这么几个文件

```powershell
 13876452 | decoder-epoch-99-avg-1.onnx
330083505 | encoder-epoch-99-avg-1.onnx
 12833618 | joiner-epoch-99-avg-1.onnx
    56317 | tokens.tx
```

4.  修改配置文件

编辑configs.json，修改相应的设置项。

5.  运行项目

```powershell
python3 main.py
```