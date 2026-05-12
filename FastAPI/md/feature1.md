# 规则

数据非必要的情况下，都使用efinance
注释要写清楚

---

# api
v1文件夹下，新建一个fundation文件，里面的接口都属于公用的基础接口

---

# service
新建一个fundationService文件，v1中的逻辑实现都在fundation_service中实现

---

# provider
删除baostock，新增ef_provider和ak_provider，并删除原来文件夹下的akshare,baostock,base这三个文件

---

# dao