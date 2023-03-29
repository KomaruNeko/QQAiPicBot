## QQai涩图机器人
### 介绍
(注：**该文档内的“涩图”指的是单个美少女的图)
这个bot可以实时生成涩图发给群友或好友。生成图片用的时自己电脑的gpu。
- 召唤关键词：
  - **怎么搞图** - 查看ai生成图功能的使用说明
  - **来张xx图** - ai生成图，关键词用空格或逗号隔开。中文关键词会自动机翻成英文
  - **怎么搞涩图** - 查看ai生成涩图功能的使用说明
  - **来张xx涩图** - ai生成涩图，关键词用空格或逗号隔开。中文关键词会自动机翻成英文
  - **aipic xxx** - ai生成涩图，xxx直接输入英文prompt
- 由于会爆显存，ai智能聊天助手目前属于关闭状态。想开启的话（非常不建议），把modules里面的_chat.py改为chat.py即可。日后可能会换成使用线上服务器的gpt模型，目前只考虑离线是因为科学上网不方便会被封号。

### 安装配置
该说明仅适用windows系统，作者没有准备其他系统进行测试。请确保的你的电脑至少有8G显存。
#### 1. 以api形式启动stable diffusion webui:
以下说明修改自 AUTOMATIC1111 的 stable-diffusion-webui, 只列举必要步骤，具体如何使用 stable-diffusion-webui 请参考 [stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui/)。已安装stable-diffusion-webui的只需从**第5步**开始执行
1. 安装 [Python 3.10.6](https://www.python.org/downloads/windows/), 勾选 "Add Python to PATH"
2. 安装 [git](https://git-scm.com/download/win)
3. 下载 stable-diffusion-webui, 比如在你想要安装stable-diffusion的目录下右键打开git, 输入命令行 `git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git` ，然后按回车
4. 至少在 stable-diffusion-webui\models\Stable-diffusion\ 下载一个可用的模型，以下是参考网址：
   1. 官方网址：https://huggingface.co/CompVis/stable-diffusion-v-1-4-original
   2. Civitiai: https://civitai.com/
5. 编辑 stable-diffusion-webui文件夹里面的webui-user.bat, 把 `set COMMANDLINE_ARGS=` 这一行改为 `set COMMANDLINE_ARGS=--api`
   
#### 2. 手动安装mcl
1. 手动安装 [mirai-console-loader](https://github.com/iTXTech/mirai-console-loader)，参考该repo的**手动安装**部分
2. 安装[mirai-api-http](https://github.com/project-mirai/mirai-api-http)，参考该repo的**安装mirai-api-http**和**开始使用**部分
3. 在[fix-protocol-version](https://github.com/cssxsh/fix-protocol-version/releases/tag/v1.3.0)，下载fix-protocol-version-1.3.0.mirai2.jar，并移入 [你的mcl地址]\plugins 目录中


#### 3. 安装requirements
1. 在命令行中，运行`pip install -r requirements.txt`

### 开始使用
1. 根据说明，修改 config.ini
2. 运行 stable diffusion webui 目录的 webui-user.bat
3. 运行 mcl 目录的 mcl.cmd, 或者在命令行中，运行`.\mcl`，显示 mirai-console started successfully 后，输入`login [你的qq号] [密码] MACOS`，如`login 1919810 114514 MACOS`，确保你输入的qq和config里的qq一致。
4. 运行 bot.bat