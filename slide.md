# APK Builder
[sdk-u3d-plugins](http://172.16.100.90/gerrit/sdk-u3d-plugins)

 * Author: liyan
 * Date: 2017-04-20
 * Ver: 1.0

---
# Table of Contents

## 1. 配置 ant 打包 apk 基础环境

 * Android 提供了基于 ant 的 apk 打包工具
 * 测试生成 Android 工程、编译 apk 的命令

## 2. 生成 demos 和 plugins

## 3. 合成最终发布工程

## 4. 集成到 Jenkins

---
# 1. 配置 ant 打包 apk 基础环境

        $ android create project \
            --target 1 \
            --name MyName \
            --path . \
            --activity MyActivity \
            --package com.yourdomain.yourproject
        ...
        Added file ./AndroidManifest.xml
        Added file ./build.xml
        Added file ./proguard-project.txt
        
        $ ant debug
        ...
        debug:

        BUILD SUCCESSFUL
        Total time: 7 seconds
        $ ll bin/*.apk     
        14444 Apr 21 07:41 bin/MyName-debug-unaligned.apk
        14452 Apr 21 07:41 bin/MyName-debug.apk

---
# 1.1 确保以下内容正确安装

    1. java 1.8.x
    2. apache ant 1.8+
    2. python 2.7.x
    3. Android SDK command line tools
    4. git 2.x

        ➜  ~ java -version
        java version "1.8.0_20"
        ➜  ~  python -V
        Python 2.7.11
        ➜  ~ ant -version
        Apache Ant version 1.8.0 compiled on February 1 2010
        ➜  ~ git --version
        git version 2.11.0 (Apple Git-81)
        ➜  ~ android list target
        Available Android targets:
        ----------
        id: 6 or "android-21"
             Name: Android 5.0.1
             Type: Platform
             API level: 21
             Revision: 2
             Skins: HVGA, QVGA, WQVGA400, WQVGA432, WSVGA, WVGA800 (default), WVGA854, WXGA720, WXGA800, WXGA800-7in
         Tag/ABIs : no ABIs.
         ...

---
# 2. 生成 demos 和 plugins

    ➜  sdk-u3d-plugins git:(master) ✗ python apk_builder.py -s demo.ini -d /tmp/apk_builder/dist_0424 -c demo

    ➜  sdk-u3d-plugins git:(master) ✗  ll /tmp/apk_builder/dist_0424 
    total 143664
    -rw-r--r--  1 liyan  wheel    11M Apr 24 19:54 360-r23546.apk
    -rw-r--r--  1 liyan  wheel   5.1M Apr 24 19:58 UC-r23535.apk
    -rw-r--r--  1 liyan  wheel   3.5M Apr 24 19:54 anzhi-r23538.apk
    -rw-r--r--  1 liyan  wheel   4.7M Apr 24 19:55 baidu-r23516.apk
    -rw-r--r--  1 liyan  wheel   3.3M Apr 24 19:55 coolpad-r23262.apk
    -rw-r--r--  1 liyan  wheel   5.3M Apr 24 19:56 dangle-r23537.apk
    -rw-r--r--  1 liyan  wheel   1.8M Apr 24 19:56 feiliu-r23566.apk
    -rw-r--r--  1 liyan  wheel   1.0M Apr 24 19:56 huawei-r23567.apk
    -rw-r--r--  1 liyan  wheel   5.9M Apr 24 19:56 jinli-r23551.apk
    -rw-r--r--  1 liyan  wheel   2.7M Apr 24 19:57 lenovo-r23569.apk
    -rw-r--r--  1 liyan  wheel   7.8M Apr 24 19:57 mz-r23514.apk
    -rw-r--r--  1 liyan  wheel   3.5M Apr 24 19:57 oppo-r23541.apk
    -rw-r--r--  1 liyan  wheel   3.3M Apr 24 19:57 tencent-r23570.apk
    -rw-r--r--  1 liyan  wheel   5.9M Apr 24 19:58 vivo-r23562.apk
    -rw-r--r--  1 liyan  wheel   5.6M Apr 24 19:59 xiaomi-r23568.apk
---
# 3. 合成最终发布工程

## 3.1 初始化

## 3.1 打渠道包

---
# 4. 集成到 Jenkins
![打出来的工程包](slide/build_on_jenkins.png)

---
END