#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 13:12:07 2020

@author: rgb
"""
import nazca as nd

@nd.bb_util.hashme('func')
def func(a=10, **kwargs):
    with nd.Cell() as C:
        print(kwargs)
    return C

cell = func(a=10)
print(cell.cell_name)