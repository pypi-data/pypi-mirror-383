# -*- coding: UTF-8 -*-
__author__ = '余洋'
__doc__ = 'Runner'
'''
  * @File    :   Runner.py
  * @Time    :   2023/06/03 10:29:52
  * @Author  :   余洋
  * @Version :   1.0
  * @Contact :   yuyangit.0515@qq.com
  * @License :   (C)Copyright 2019-2024, Ship of Ocean
  * @Desc    :   None
'''
from .ModuleData import ModuleData
from .Resource import Resource


class Runner():
    _module_data = ModuleData()
    _resource = Resource()

    def main(self):
        pass