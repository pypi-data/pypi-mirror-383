# -*- coding: UTF-8 -*-
__author__ = '余洋'
__doc__ = 'Main'
'''
  * @File    :   Main.py
  * @Time    :   2023/06/03 10:29:37
  * @Author  :   余洋
  * @Version :   1.0
  * @Contact :   yuyangit.0515@qq.com
  * @License :   (C)Copyright 2019-2024, Ship of Ocean
  * @Desc    :   None
'''
from xy_argparse.Runner import Runner

def main():
    if callable(Runner):
        executor = Runner()
        if executor and hasattr(executor, "main") and callable(getattr(executor, "main")):
            main_func = getattr(executor, "main")
            try:
                main_func()
            except Exception:
                print("main函数运行错误")

if __name__ == "__main__":
    main()