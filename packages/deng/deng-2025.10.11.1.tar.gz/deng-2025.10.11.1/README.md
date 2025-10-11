# 个人常用工具类封装


## 更新历史

### 2022-5-9  
* git.pull_repo方法增加consistency_check参数，默认启用分支一致性检查  

### 2022-4-24
* windows.py模块更新，集成一些常用方法  

### 2022-4-8  
* 增加get_uuid方法  
* get_current_time方法支持直接传递格式，支持纳秒级输出  
* 修复自定义文件缓存类中setex方法声明与redis中相映方法声明不一致的问题  
* 优化文件缓存类位置  
* 优化日志  

### 2022-4-7  
* 添加timestamp_to_str方法，快速将时间戳转换成指定格式的字符串  
* 优化日志  
* 优化缓存类，防止没有配置redis时报错  


### 2022-3-26  
* 优化压缩函数compress_tgz与compress_zip支持直接压缩文件（原来只支持压缩目录）  

### 2022-3-25
* 优化格式化输出函数format_output中的溯源日志信息  
* 增加控制参数，可控制接口请求失败时是否显示整个http报文  

### 2022-3-1
* 优化parse_url_to_dict方法  
* 优化部分日志级别及为部分方法添加注释说明  
* 添加AES CBC加解密算法  

### 2021-11-17  
* 重构  

### 2019-11-07
* 新增生成银联卡卡号方法，可通过[支付宝校验](https://ccdcapi.alipay.com/validateAndCacheCardInfo.json?_input_charset=utf-8&cardNo=9400621673734008267&cardBinCheck=true)

### 2018-04-20  
* 新增to_dict方法，将x-www-form-urlencoded格式字符串转换成dict  

### 2018-02-27  
* 新增mysql连接池类MysqlPool；  

## pip安装
```
# 此方式安装方法最简便，但可能不是最新的
pip install deng
# 安装最新的版本
pip install git+https://github.com/Deng2016/deng@201801
```

## requirements.txt引用
```
-e git+git@github.com:Deng2016/deng.git@master#egg=deng
```

## 安装应用
```
python setup.py install
```

## 开发模式安装
```
python setup.py develop
```

## 创建egg包
```
# 生成egg包
python setup.py bdist_egg

# 安装egg包
easy_install deng-0.1-py2.7.egg
```

## 创建tar.gz包
```
# 创建tar.gz包
python setup.py sdist --formats=gztar

# 将tar.gz包安装到别处
pip install deng-0.1.tar.gz
```

## 将包发布到pypi
```
# 先升级打包工具
pip install --upgrade setuptools wheel twine

# 打包
python setup.py sdist bdist_wheel

# 检查
twine check dist/*

# 上传pypi
twine upload dist/*
```

[打包参考资料](http://www.bjhee.com/setuptools.html)
