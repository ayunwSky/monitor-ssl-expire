#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# *******************************************
# -*- CreateTime  :  2023/05/22 09:19:42
# -*- Author      :  Allen_Jol
# -*- FileName    :  __init__.py
# -*- Desc        :  None
# *******************************************

import os
import sys

# 把项目根目录加入到 sys.path 中
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
if root_path not in sys.path:
    sys.path.insert(0, root_path)
