# 一个基于 Rasa 的音乐百科应用[Demo]

## 环境要求 ##
Mac OS X or Linux

Windows supporting is on the radar.

## 安装

### 安装依赖 ###
安装 python 等各种软件包依赖

```bash
make install
```

### 安装模型文件 ###
下载已经预先训练好的 MITIE 的模型文件

```bash
make download
```

## 训练

```bash
rasa train
```

## 启动

### Step 1: 启动 action server
```bash
rasa run actions
```

### Step 2: 启动rasa server ###

```bash
make run_model
```

### 启动 rasa x
我们可以使用 rasa x 作为客户端

```bash
rasa x --enable-api --auth-token 12345678
```

启动后会自动打开浏览器窗口
