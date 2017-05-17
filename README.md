# apk-builder
APK build script

## Reference

 * [Android Apk打包过程概述](http://blog.csdn.net/jason0539/article/details/44917745)
 * [How to compile APK from command line?](http://stackoverflow.com/questions/15285331/how-to-compile-apk-from-command-line) stackoverflow 上提供的一种用使用[Android command line tools](https://developer.android.com/studio/index.html) 进行编译打包的方法
 * [使用 Gradle 进行打包](https://developer.android.google.cn/studio/build/building-cmdline.html)
 * [Android Studio2.2 APK打包机制的变化](http://www.jianshu.com/p/c549fce12310)
 
## 1. Android Command Line Tools 使用总结

### 1.1 环境设置
工具安装

	# android工具安装
	wget http://mirrors.tuna.tsinghua.edu.cn/apache//ant/binaries/apache-ant-1.10.1-bin.zip
	unzip apache-ant-1.10.1-bin.zip

	# android工具安装
	wget https://dl.google.com/android/repository/tools_r25.2.3-linux.zip
	unzip tools_r25.2.3-linux.zip 
	android list sdk --all #See Availiable downloads
	# install Tools/Platform-tools/Build-tools and Platform(Android 5.0.1, API 21, revision 2)
    android update sdk -u -a -t 1,2,5,40
    # install ABI for emulator
    android update sdk --no-ui --all --filter "sys-img-x86_64-android-21"
    android list target
    Available Android targets:
    ----------
    id: 1 or "android-21"
         Name: Android 5.0.1
         Type: Platform
         API level: 21
         Revision: 2
         Skins: HVGA, QVGA, WQVGA400, WQVGA432, WSVGA, WVGA800 (default), WVGA854, WXGA720, WXGA800, WXGA800-7in
     Tag/ABIs : default/x86_64

路径配置

    vi ~/.bash_profile 
    JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk1.8.0_20.jdk/Contents/Home
    ANT_HOME=/opt/local/tools/java/ant/apache-ant-1.8.0
    ANDROID_HOME=/opt/app/android/sdk
    PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools:$ANDROID_HOME/build-tools/25.0.3:$ANT_HOME/bin

打包测试

	# create hello world
	mkdir test_project
	cd test_project
	android create project \
	    --target 1 \
	    --name MyName \
	    --path . \
	    --activity MyActivity \
	    --package com.yourdomain.yourproject
	ant debug

### 1.2 打包配置文件介绍
local.properties

	➜  my_android android update project -p .
	Updated local.properties
	Updated file ./proguard-project.txt

ant.properties

	java.source=1.7
	java.target=1.7
	source.dir=src; test
    key.store=file.keystore
    key.store.password=mypasswd

### 1.3 打包命令

	➜  my_android android update project -p .
	Updated local.properties
	Updated file ./proguard-project.txt
	➜  my_android ant release

### 1.4 APK校验

#### 查看APK信息

    $ aapt dump badging <path-to-apk> | grep package
    package: name='com.shifen.xxxx.xxx' versionCode='1' \ 
versionName='1.0.2' platformBuildVersionName='5.0.1-1624448'

#### 查看APK签名信息

    # 查看签名信息
    jarsigner -verify -verbose -certs <apk file>

#### APK签名与keystore对比
[检查apk是用哪个keystore做的签名](http://stackoverflow.com/questions/11331469/how-do-i-find-out-which-keystore-was-used-to-sign-an-app)
    # 获取证书摘要(SHA1)
    -bash-4.1$ keytool -list -keystore <keystore file>
    Enter keystore password:  
    ...
    Certificate fingerprint (SHA1): xx:xx:....
    # 获取APK中的证书摘要
    keytool -list -printcert -jarfile <apk file>
    ...
    Certificate fingerprints:
         MD5:  E1:2B:2A:28:23:6D:39:1C:F3:D3:3F:80:B3:30:10:83
         SHA1: xx:xx:....

### 1.5 真机安装与卸载

	➜  my_android adb install bin/myapp-debug.apk
    ➜  my_android adb uninstall com.yourdomain.yourproject

### 1.6 模拟器中启动apk

 * 创建AVD: `android create avd -n android5 -t 1`
 * 查看已有AVD: `android list avd`
 * 启动模拟器: `emulator`
 * 安装到模拟器

➜  test adb devices
List of devices attached
emulator-5554   device
➜  test adb install bin/MyName-debug.apk 
bin/MyName-debug.apk: 1 file pushed. 2.6 MB/s (14455 bytes in 0.005s)
    pkg: /data/local/tmp/MyName-debug.apk
Success


## 2. 错误的解决
 
### 2.1 ant build failed: resolve to a path with no project.properties file for project

 * [build android.library.reference](http://stackoverflow.com/questions/21265111/android-ant-build-fails-with-google-play-services-lib-resolve-to-a-path-with)
 
### 2.2 ant build failed: (use -source 7 or higher to enable multi-catch statement)
 
 	➜  base cat ant.properties 
	java.source=1.7
	java.target=1.7

### 2.3 ant build failed: dx Exception in thread "main" java.lang.UnsupportedClassVersionError: com/android/dx/command/Main : Unsupported major.minor version 52.0
 
 * [Unable to build Android - Unsupported class file version 52.0](https://github.com/soomla/unity3d-store/issues/541)
 * [ant.properties file config](http://stackoverflow.com/questions/18051917/ant-properties-file-missing-in-android-project)

### 2.4 app运行时无法加载主类
参考[How to specify multiple source directory for Android library project](http://stackoverflow.com/questions/14605899/how-to-specify-multiple-source-directory-for-android-library-project)
apk安装后无法正常启动。用eclipse调试，提示没有找到MainActivity。

搜索工程目录，发现MainActivity没有放到src目录下。

解决方案：

	ant.properties中指定 source.dir=src; test
	
### 2.5 adb install Failure: INSTALL_FAILED_DEXOPT
参考[How to install Android SDK Build Tools on the command line?](http://stackoverflow.com/questions/17963508/how-to-install-android-sdk-build-tools-on-the-command-line)
使用了过高版本的 `getbuildtools`。推荐使用25.0.2版本

	android list sdk --all #See Availiable downloads
	tools/android update sdk -u -a -t 1,2,5,35

### 2.6 CentOS: version `GLIBC_2.14' not found
参考[分享Centos6.5升级glibc过程](https://cnodejs.org/topic/56dc21f1502596633dc2c3dc)

错误提示如下

    -code-gen:
        [mergemanifest] No changes in the AndroidManifest files.
         [echo] Handling aidl files...
         [aidl] No AIDL files to compile.
         [echo] ----------
         [echo] Handling RenderScript files...
         [echo] ----------
         [echo] Handling Resources...
         [aapt] Generating resource IDs...
         [aapt] /var/lib/jenkins/android/build-tools/25.0.2/aapt: /lib64/libc.so.   6: version `GLIBC_2.14' not found (required by     /var/lib/jenkins/android/build-tools/25.0.2/aapt)
         [aapt] /var/lib/jenkins/android/build-tools/25.0.2/aapt: /lib64/libc.so.   6: version `GLIBC_2.14' not found (required by     /var/lib/jenkins/android/build-tools/25.0.2/lib64/libc++.so)

    ## has busybox
    # busybox ln -sf /opt/glibc-2.14/lib/libc-2.14.so /lib64/libc.so.6
    # or
    LD_PRELOAD=/opt/glibc-2.14/lib/libc-2.14.so ln -sf /opt/glibc-2.14/lib/libc-2.14.so /lib64/libc.so.6
    # ll /lib64/libc.so*
    lrwxrwxrwx 1 root root 32 Apr 21 07:55 /lib64/libc.so.6 -> /opt/glibc-2.14/lib/libc-2.14.so

### 2.7 launch emulator on MacOS: CPU acceleration status: HAXM must be updated (version 1.1.4 < 6.0.1)
[参考](http://stackoverflow.com/questions/34282243/error-while-starting-emulator)

 1. Go To Your Android SDK ----> Run SDK Manager as Admin.
 2. GO down and check Extras---> Update Intel Emulator Accelator (HAXM installer).
 3. Then Restart Android Studio and Run Your AVD.
 4. if still not work, run command: `sudo $ANDROID_HOME/extras/intel/Hardware_Accelerated_Execution_Manager/silent_install.sh`
