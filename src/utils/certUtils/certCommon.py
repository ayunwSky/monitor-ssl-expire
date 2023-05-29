#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# *******************************************
# -*- CreateTime  :  2023/05/29 10:21:21
# -*- Author      :  ayunwSky
# -*- FileName    :  certCommon.py
# *******************************************

import socket


def get_domain_ip(domain_name):
    """
    根据域名获取域名解析的IP地址
    :param domain_name: 域名,str
    :return: str
    """
    return socket.gethostbyname(domain_name)


if __name__ == '__main__':
    domain_list = ["www.cnsre.cn", "www.baidu.com", "www.sina.com"]
    try:
        for domain in domain_list:
            resp = get_domain_ip(domain)
            print(f"Domain: {domain}, IP: {resp}")
    except socket.gaierror as e:
        print(f"Error message: {e}")
