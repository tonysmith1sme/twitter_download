#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合验证脚本 - 检查所有修改是否完整且正确
"""

import json
import os
import sys

def check_file_exists(file_path, description):
    """检查文件是否存在"""
    if os.path.exists(file_path):
        print(f"✓ {description}: {file_path}")
        return True
    else:
        print(f"✗ {description}: {file_path} 不存在")
        return False

def check_content_in_file(file_path, search_strings, description):
    """检查文件中是否包含特定内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        all_found = True
        for search_str in search_strings:
            if search_str not in content:
                print(f"  ✗ 缺少内容: {search_str}")
                all_found = False
        
        if all_found:
            print(f"✓ {description}")
            return True
        else:
            return False
    except Exception as e:
        print(f"✗ 检查文件 {file_path} 失败: {str(e)}")
        return False

print("=" * 60)
print("Twitter下载项目 - 书签功能修改验证")
print("=" * 60)

checks_passed = 0
checks_total = 0

# 检查1: 文件存在性
print("\n【文件检查】")
checks_total += 3
if check_file_exists('bookmark_util.py', '书签工具模块'):
    checks_passed += 1
if check_file_exists('settings.json', '配置文件'):
    checks_passed += 1
if check_file_exists('main.py', '主程序'):
    checks_passed += 1

# 检查2: settings.json配置
print("\n【配置文件检查】")
try:
    with open('settings.json', 'r', encoding='utf-8') as f:
        settings = json.load(f)
    
    checks_total += 2
    
    if 'enable_auto_bookmark' in settings:
        print(f"✓ enable_auto_bookmark 配置存在 (默认值: {settings['enable_auto_bookmark']})")
        checks_passed += 1
    else:
        print("✗ enable_auto_bookmark 配置缺失")
    
    if 'bookmark_account' in settings:
        print(f"✓ bookmark_account 配置存在 (默认值: '{settings['bookmark_account']}')")
        checks_passed += 1
    else:
        print("✗ bookmark_account 配置缺失")
        
except Exception as e:
    print(f"✗ settings.json读取失败: {str(e)}")

# 检查3: main.py集成检查
print("\n【main.py 集成检查】")
checks_to_verify = [
    'from bookmark_util import bookmark_util',
    'enable_auto_bookmark = False',
    'bookmark_ids = []',
    "if 'enable_auto_bookmark' in settings and settings['enable_auto_bookmark']:",
    'bm_util = bookmark_util(_headers, proxies, log_output)',
    'bm_results = bm_util.batch_add_bookmarks(bookmark_ids)',
    'tweet_id = a[\'id_str\']',
    'if enable_auto_bookmark and tweet_id and tweet_id not in bookmark_ids:',
]

checks_total += len(checks_to_verify)
for check_item in checks_to_verify:
    if check_content_in_file('main.py', [check_item], f"main.py包含: {check_item[:50]}..."):
        checks_passed += 1

# 检查4: bookmark_util.py结构检查
print("\n【bookmark_util.py 结构检查】")
checks_to_verify = [
    'class bookmark_util():',
    'def add_bookmark(self, tweet_id: str) -> bool:',
    'def batch_add_bookmarks(self, tweet_ids: list, delay: float = 0.5) -> dict:',
    'def get_stats(self) -> dict:',
    'httpx.post(',
    '"variables":',
    '"tweet_id": tweet_id',
]

checks_total += len(checks_to_verify)
for check_item in checks_to_verify:
    if check_content_in_file('bookmark_util.py', [check_item], f"bookmark_util.py包含: {check_item[:50]}..."):
        checks_passed += 1

# 检查5: 功能检查
print("\n【功能集成检查】")

# 检查推文ID的传递
checks_total += 1
with open('main.py', 'r', encoding='utf-8') as f:
    main_content = f.read()
    if 'url[3]' in main_content and 'down_save(url[0], url[1], url[2], url[3], order)' in main_content:
        print("✓ 推文ID正确传递到down_save函数")
        checks_passed += 1
    else:
        print("✗ 推文ID传递有问题")

# 检查async函数签名
checks_total += 1
if 'async def down_save(url, prefix, csv_info, tweet_id: str, order: int):' in main_content:
    print("✓ down_save函数签名正确包含tweet_id参数")
    checks_passed += 1
else:
    print("✗ down_save函数签名缺少tweet_id参数")

# 检查global声明
checks_total += 1
if 'global down_count, bookmark_ids' in main_content:
    print("✓ 正确声明了global变量")
    checks_passed += 1
else:
    print("✗ 缺少global变量声明")

# 最终报告
print("\n" + "=" * 60)
print(f"检查完成: {checks_passed}/{checks_total} 项通过")

if checks_passed == checks_total:
    print("✅ 所有检查通过！修改完整且正确。")
    sys.exit(0)
else:
    print(f"⚠️  有 {checks_total - checks_passed} 项检查未通过。")
    sys.exit(1)
