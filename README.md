# apk-builder
APK build script

## Reference

 * [Android Apk打包过程概述](http://blog.csdn.net/jason0539/article/details/44917745)
 * [How to compile APK from command line?](http://stackoverflow.com/questions/15285331/how-to-compile-apk-from-command-line) stackoverflow 上提供的一种用使用[Android command line tools](https://developer.android.com/studio/index.html) 进行编译打包的方法
 * [使用 Gradle 进行打包](https://developer.android.google.cn/studio/build/building-cmdline.html)
 * [Android Studio2.2 APK打包机制的变化](http://www.jianshu.com/p/c549fce12310)
 * [Github: beanu/ant-android](https://github.com/beanu/ant-android) 打算以这个进行入门练手了
 
## 基于Android CLT的编译、打包及安装

### 本地环境

	vi ~/.bash_profile 
	JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk1.8.0_20.jdk/Contents/Home
	ANT_HOME=/opt/local/tools/java/ant/apache-ant-1.8.0
	ANDROID_HOME=/opt/app/android/sdk
	PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools:$ANT_HOME/bin

	# android工具安装
	wget http://mirrors.tuna.tsinghua.edu.cn/apache//ant/binaries/apache-ant-1.10.1-bin.zip
	unzip apache-ant-1.10.1-bin.zip

	# android工具安装
	wget https://dl.google.com/android/repository/tools_r25.2.3-linux.zip
	unzip tools_r25.2.3-linux.zip 
	android list sdk --all #See Availiable downloads
	tools/android update sdk -u -a -t 1,2,5,35
	
	# create hello world，打包测试
	mkdir test_project
	cd test_project
	android create project \
	    --target 1 \
	    --name MyName \
	    --path . \
	    --activity MyActivity \
	    --package com.yourdomain.yourproject

	ant debug

### 生成打包脚本

	➜  my_android android update project -p .
	Updated local.properties
	Updated file ./proguard-project.txt

### 添加配置参数

	cat ant.properties 
	java.source=1.7
	java.target=1.7
	source.dir=src; test

### 打包

	➜  my_android android update project -p .
	Updated local.properties
	Updated file ./proguard-project.txt
	➜  my_android ant release
 
### 安装

	➜  my_android adb install bin/sdk_res-debug.apk


## ant执行错误的解决
 
### resolve to a path with no project.properties file for project

 * [build android.library.reference](http://stackoverflow.com/questions/21265111/android-ant-build-fails-with-google-play-services-lib-resolve-to-a-path-with)
 
### [[javac]] (use -source 7 or higher to enable multi-catch statement)
 
 	➜  base cat ant.properties 
	java.source=1.7
	java.target=1.7

### [[dx]] Exception in thread "main" java.lang.UnsupportedClassVersionError: com/android/dx/command/Main : Unsupported major.minor version 52.0
 
 * [Unable to build Android - Unsupported class file version 52.0](https://github.com/soomla/unity3d-store/issues/541)
 * [ant.properties file config](http://stackoverflow.com/questions/18051917/ant-properties-file-missing-in-android-project)

## app运行时错误的解决

### 无法加载主类
参考[How to specify multiple source directory for Android library project](http://stackoverflow.com/questions/14605899/how-to-specify-multiple-source-directory-for-android-library-project)
apk安装后无法正常启动。用eclipse调试，提示没有找到MainActivity。

搜索工程目录，发现MainActivity没有放到src目录下。

解决方案：

	ant.properties中指定 source.dir=src; test
	
### adb install Failure: INSTALL_FAILED_DEXOPT
参考[How to install Android SDK Build Tools on the command line?](http://stackoverflow.com/questions/17963508/how-to-install-android-sdk-build-tools-on-the-command-line)
使用了过高版本的 `getbuildtools`。推荐使用25.0.2版本

	android list sdk --all #See Availiable downloads
	tools/android update sdk -u -a -t 1,2,5,35
