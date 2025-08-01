# Selenium auto test

基于 Python + Selenium + Pytest + allure 的自动化测试框架（Windows）

目前Github上有很多Web自动化框架，但是大多数都是基于Selenium 3 进行封装的，相比与 Selenium 4 封装过于繁琐。

**本框架基于现实工作中的项目进行梳理的框架，尽量做到没有冗余代码，浅封装，上手快，可以自行改造**

> 本框架中没有添加 Selenium 分布式部署功能，如果有需要请自行添加
>
> 没有添加 Selenium Grid 的理由 （个人见解）：
> - Selenium Grid 对case的独立性有很高的要求，它要求每个case都需要独立运行，在实际的项目中其实很难做到
> - Selenium Grid 其实对机器的数量有很高的要求，中小公司少量的测试机器，使用Grid反而加重的代码的复杂性
> - Web TA 和 E2E TA 当深入业务的时候，前置后置步骤其实会很复杂，如果让每个case相互独立其实很困难且难以维护
>
> 我个人感觉使用Jenkins 进行Job 维度的调度，反而更加合理

## 1. 版本要求

Python 版本要求 3.13 版本以上

Selenium 版本要求 4.32.0 版本以上

2025年7月后 Google 浏览器更新了安全规范，Selenium 3 很多功能都已经无法再使用，需要Selenium 4 的新特性才能完成

## 2. 项目结构

```
selenium-autotest
│
├─common
│   ├─ browser_operation.py  # 所有wbe页面常规操作的封装，每一个page都应该继承这个类
│   │
│   ├─ driver_config.py  # 获取浏览器驱动的类
│   │
│   └─ global_var.py # 全局变量，用于存储和销毁驱动
│   
├─test_case # 用于存放测试用例的文件夹
│   │
│   └─ conftest.py  # 用于存放共用的fixture,解决多个测试文件间共享前置条件的问题
│ 
├─utils # 存放各种工具类的文件夹
│   │
│   ├─ file_utils.py  # 文件操作的相关方法
│   │
│   ├─ screen_recording.py  # windows 录制视频工具类
│   │
│   ├─ time_utils.py  # 时间工具类
│   │
│   └─ log_manager.py  # 日志工具类
│ 
├─pytest.ini  # 主配置文件
│
├─requirement.txt  # 第三方依赖
│
├─win_setup_env.bat  # windows第三方依赖初始化脚本
│
├─.gitignore  # 让git忽略部分文件，避免误提交
│
└─run.py  # 执行主函数
```

## 3. 说明

### 3.1 browser_operation.py

这是一个封装了各种操作的公共类，所有的page都需要继承这个类，

page中封业务规操作方法的时候，需要避免使用原生写法，如果operation没有想要的操作应该将这个操作在 operation 中进行封装，再调用

### 3.2 获取驱动

- chrome 浏览器的驱动使用的是 webdriver-manager 这个第三方库进行管理
- Edge 浏览器，由于 2025年，microsoft官方对 Edge 浏览器驱动整个存放位置进行了迁移，webdriver-manager 4.0.2
  的最新版本还不支持，所以是手动下载
- FireFox 驱动 [TODO]

### 3.3 conftest.py

这个是所有case 的前置和后置步骤，这里面有两个基本方法

- def driver(): 这个是用来获取驱动的前置
- def capture_case_recording(): 这个是用来录制case执行的video
    - 这个方法目前只支持在windows上进行录屏
    - 要求windows不能是锁屏状态，如果虚拟机的话，可以使用realvnc等软件构建虚拟桌面

### 3.4 win_setup_env.bat

用来在windows机器上进行初始化虚拟环境的 **（非必须操作）**

当TA 机器被共用的时候，会存在不同项目使用的第三方依赖版本不一致的问题，这个时候就需要初始化虚拟环境，保障每个项目的TA
都使用自己的虚拟环境

在windows 机器上执行该命令，就会在当前文件夹中创建了一叫 `%JOB_NAME%` 的虚拟环境

```
call win_setup_env.bat %JOB_NAME%
```

这时候在windows上执行TA 的时候，需要指定python的虚拟环境

```
set venv_py=.venv_%JOB_NAME%\Scripts\python
call %venv_py% -m run.py
```

### 3.5 run.py

case运行的公共类，所有case的执行入口都在这里，不应该直接调用pytest来进行操作

- `-m`: pytest 的标签
- `-k`: 通过关键字表达式筛选测试用例
- `-e`: 指定测试环境, 这个会被塞到环境变量里面，后续可以使用 `os.getenv['TEST_ENV']` 获取，默认dev环境
- `-b`: 浏览器类型，这个会被塞到环境变量里面，后续可以使用 `os.getenv['TEST_BROWSER']` 获取，默认Chrome环境
- `--allure`: allure测试报告的存放位置，默认在当前文件夹下创建一个 allure-results 文件夹存放
- `--clean`: 是否要清理往期的测试结果数据，默认True