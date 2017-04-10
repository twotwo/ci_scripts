# apk-builder
APK build script

## Reference

 * [Android Apk打包过程概述](http://blog.csdn.net/jason0539/article/details/44917745)
 * [How to compile APK from command line?](http://stackoverflow.com/questions/15285331/how-to-compile-apk-from-command-line) stackoverflow 上提供的一种用使用[Android command line tools](https://developer.android.com/studio/index.html) 进行编译打包的方法
 * [使用 Gradle 进行打包](https://developer.android.google.cn/studio/build/building-cmdline.html)
 * [Android Studio2.2 APK打包机制的变化](http://www.jianshu.com/p/c549fce12310)
 * [Github: beanu/ant-android](https://github.com/beanu/ant-android) 打算以这个进行入门练手了
 
## 基于Android CLT的编译打包

### 本地环境变量

	JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk1.8.0_20.jdk/Contents/Home
	ANT_HOME=/opt/local/tools/java/ant/apache-ant-1.8.0
	ANDROID_HOME=/opt/app/android/sdk
	PATH=$PATH:$ANDROID_HOME/tools:$ANT_HOME/bin

### 生成打包脚本

	➜  my_android android update project -p .
	Updated local.properties
	Updated file ./proguard-project.txt
 
### 打包

	➜  my_android android update project -p .
	Updated local.properties
	Updated file ./proguard-project.txt
 
 
 ## ant运行时错误的解决
 
  ### resolve to a path with no project.properties file for project

 * [build android.library.reference](http://stackoverflow.com/questions/21265111/android-ant-build-fails-with-google-play-services-lib-resolve-to-a-path-with)
 
 ### [javac]   (use -source 7 or higher to enable multi-catch statement)
 
 	➜  base cat ant.properties 
	java.source=1.8
	java.target=1.8
