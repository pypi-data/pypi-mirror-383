# XGO Blockly 图形化编程服务器

## 简介

XGO Blockly 是专为陆吾机器人系列设计的图形化编程和AI编程服务器。通过简单的安装和启动，您可以在电脑浏览器中进行图形化编程，控制您的陆吾机器人。

## 安装要求

该 pip 包需要安装在陆吾机器人系列的树莓派机器上。

## 安装步骤

1. **进入指定目录**
   ```bash
   cd /home/pi/RaspberryPi-CM5/
   ```

2. **创建或激活虚拟环境**
   
   首先检查是否已存在 `blockvenv` 虚拟环境：
   ```bash
   ls blockvenv
   ```
   
   如果不存在，请创建虚拟环境（注意：使用 `--system-site-packages` 参数确保继承系统包，避免 Picamera2 和 libcamera 依赖问题）：
   ```bash
   python3 -m venv --system-site-packages blockvenv
   ```
   
   激活虚拟环境：
   ```bash
   source blockvenv/bin/activate
   ```

3. **安装 xgo-blockly 包**
   ```bash
   pip install xgo-blockly
   ```

## 启动服务

安装成功后，运行以下命令启动图形化编程和AI编程服务器：

```bash
xgo-blockly
```

## 使用方法

服务器启动后，在电脑上打开浏览器，访问树莓派的IP地址即可开始图形化编程和AI编程。

## 功能特性

- 🎯 **图形化编程**：拖拽式编程界面，简单易用
- 🤖 **AI编程辅助**：智能代码生成和优化建议
- 🔗 **实时控制**：直接控制陆吾机器人硬件
- 🌐 **Web界面**：跨平台浏览器访问
- 📱 **响应式设计**：支持电脑、平板等设备

## 技术支持

如有问题或需要技术支持，请联系陆吾机器人技术团队。