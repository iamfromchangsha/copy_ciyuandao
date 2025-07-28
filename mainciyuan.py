import requests 
import os
from bs4 import BeautifulSoup
import html
from urllib.parse import quote
import re
import time
from datetime import datetime

def rename_folder(target_folder, new_name_suffix):
    try:
        parent_dir = os.path.dirname(target_folder)
        folder_name = os.path.basename(target_folder)
        new_path = os.path.join(parent_dir, folder_name + new_name_suffix)
        
        if not os.path.exists(target_folder):
            raise FileNotFoundError(f"目标文件夹不存在: {target_folder}")
        if os.path.exists(new_path):
            raise FileExistsError(f"名称 '{new_path}' 已存在")
            
        os.rename(target_folder, new_path)
        return True
    except Exception as e:
        print(f"重命名失败: {str(e)}")
        return False

# 主程序
file_path = ''
base_url = 'http://ciyuandao.com/photo/list/'

a = input('分类：不限：0\n正片：1\n私影：2\n预告：3\n\n请选择：')
b = input('榜单：最新：0\n精选：1\n周榜：2\n月榜：3\n获赞数：4\n分享数：5\n\n请选择：')
yema = int(input('页数：'))
sou = input('搜索：')
encoded_sou = quote(sou)

while True:
    url = base_url + a + '-' + b + '-' + str(yema) + '?key=' + encoded_sou
    yema += 1
    print("请求URL:", url)

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}")
        exit()

    soup = BeautifulSoup(response.text, 'html.parser')
    pics_div = soup.find('div', class_='pics')
    target_links = []

    if pics_div:
        for li in pics_div.find_all('li', class_='font12 fleft'):
            first_a = li.find('a')
            if first_a and first_a.has_attr('href') and first_a['href'].startswith('/photo/show/'):
                target_links.append(first_a['href'])

    print(f"共提取到 {len(target_links)} 个目标链接")

    for link in target_links:
        full_url = 'http://ciyuandao.com' + link
        print("\n处理作品:", full_url)
        
        try:
            response = requests.get(full_url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"请求作品页面失败: {str(e)}")
            continue
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 获取标题
        h1_title = soup.find('h1')
        if not h1_title:
            print("未找到h1标题，跳过此作品")
            continue
            
        title_text = html.unescape(h1_title.get_text(strip=True))
        print(f"作品标题: {title_text}")
        
        # 清理标题中的非法字符
        clean_title = re.sub(r'[<>:"/\\|?*]', '', title_text)
        clean_title = clean_title.strip()
        
        # 获取链接的最后6位作为唯一标识
        link_suffix = link.split('/')[-1]
        unique_id = link_suffix[-6:] if len(link_suffix) >= 6 else link_suffix.zfill(6)
        
        # 构建唯一标题
        unique_title = f"{clean_title}_{unique_id}"
        
        # 检查作品是否已存在
        base_path = os.path.join(file_path, unique_title)
        finish_path = base_path + '【舔舔脚趾】'
        
        if os.path.exists(finish_path):
            print(f"作品 '{unique_title}' 已完成，跳过下载")
            continue
            
        # 创建作品文件夹
        if not os.path.exists(base_path):
            os.makedirs(base_path)
            print(f"创建文件夹: {base_path}")
        else:
            print(f"文件夹已存在: {base_path}")
        
        # 查找图片
        img_div = soup.find('div', class_='talk_pic hauto')
        if not img_div:
            print("未找到图片区域，跳过此作品")
            continue
            
        img_tags = img_div.find_all('img')
        if not img_tags:
            print("未找到图片，跳过此作品")
            continue
            
        # 下载图片
        print(f"找到 {len(img_tags)} 张图片")
        for i, img in enumerate(img_tags, 1):
            if 'src' not in img.attrs:
                continue
                
            img_url = img['src']
            print(f"下载图片 {i}/{len(img_tags)}: {img_url}")
            
            try:
                img_response = requests.get(img_url)
                img_response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"下载图片失败: {str(e)}")
                continue
            
            # 保存图片 - 注意这里的缩进，确保在循环内
            filename = f"{i}.jpg"
            save_path = os.path.join(base_path, filename)
            
            with open(save_path, 'wb') as f:
                f.write(img_response.content)
                print(f"图片保存到: {save_path}")
        
        # 重命名文件夹（添加后缀）
        if rename_folder(base_path, '【舔舔脚趾】'):
            print(f"文件夹重命名成功: {base_path} -> {base_path}【舔舔脚趾】")
        else:
            print("文件夹重命名失败，请手动重命名")