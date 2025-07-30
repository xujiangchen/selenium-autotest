# Selenium auto test

基于 Python + Selenium + Pytest + allure 的自动化测试框架

目前Github上有很多python的自动化框架，但是大多数都是基于Selenium 3 进行封装的，相比与 Selenium 4 封装过于繁琐。

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
│   ├─ brower_operation.py  # 所有wbe页面常规操作的封装，每一个page都应该继承这个类
│   │
│   ├─ driver_config.py  # 获取浏览器驱动的类
│   │
│   └─ global_var.py # 全局变量，用于存储和销毁启动
│   
├─test_case # 用于存放测试用例的文件夹
│   │
│   └─ conftest.py  # 用于存放共用的fixture,解决多个测试文件间共享前置条件的问题
│ 
├─utils # 存放各种工具类的文件夹
│   │
│   ├─ file_utils.py  # 文件操作的相关方法
│   │
│   └─log_manager.py  # 日志工具类
│ 
├─pytest.ini  # 主配置文件
│
├─requirement.txt  # 第三方依赖
│
└─run.py  # 执行主函数
```

## 3. 执行Case