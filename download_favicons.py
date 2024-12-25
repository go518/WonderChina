import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import cairosvg

def create_favicon_dir():
    """创建favicon存储目录"""
    favicon_dir = 'images/favicons'
    if not os.path.exists(favicon_dir):
        os.makedirs(favicon_dir)
    return favicon_dir

def get_website_links():
    """从index.html中提取所有网站链接"""
    with open('index.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    links = []
    for a in soup.find_all('a', href=True):
        href = a.get('href')
        if href.startswith('http'):
            links.append(href)
    return links

def download_favicon(url, favicon_dir):
    """下载单个网站的favicon"""
    domain = urlparse(url).netloc.replace('www.', '')
    base_domain = domain.split('.')[0]
    favicon_path = os.path.join(favicon_dir, f'{base_domain}.ico')
    
    # 如果文件已存在，跳过下载
    if os.path.exists(favicon_path):
        print(f'已存在: {favicon_path}')
        return True
    
    try:
        # 先尝试获取 favicon.png
        favicon_url = f"{url.rstrip('/')}/static/favicon.png"
        response = requests.get(favicon_url, timeout=5)
        
        if response.status_code == 200:
            with open(favicon_path, 'wb') as f:
                f.write(response.content)
            print(f'下载成功: {favicon_path}')
            return True
        
        # 如果png不存在，尝试获取ico
        favicon_url = f"{url.rstrip('/')}/favicon.ico"
        response = requests.get(favicon_url, timeout=5)
        
        if response.status_code == 200:
            with open(favicon_path, 'wb') as f:
                f.write(response.content)
            print(f'下载成功: {favicon_path}')
            return True
            
        # 如果直接获取失败，尝试从HTML中查找favicon链接
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        favicon_link = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
        
        if favicon_link and favicon_link.get('href'):
            favicon_url = favicon_link['href']
            if not favicon_url.startswith('http'):
                favicon_url = f"{url.rstrip('/')}/{favicon_url.lstrip('/')}"
            
            response = requests.get(favicon_url, timeout=5)
            if response.status_code == 200:
                with open(favicon_path, 'wb') as f:
                    f.write(response.content)
                print(f'下载成功: {favicon_path}')
                return True
        
        # 使用默认图标
        print(f'未找到favicon，使用默认图标: {url}')
        default_svg = os.path.join(favicon_dir, 'default.svg')
        cairosvg.svg2png(url=default_svg, write_to=favicon_path, output_width=32, output_height=32)
        return True
        
    except Exception as e:
        print(f'下载失败，使用默认图标 {url}: {str(e)}')
        default_svg = os.path.join(favicon_dir, 'default.svg')
        cairosvg.svg2png(url=default_svg, write_to=favicon_path, output_width=32, output_height=32)
        return True

def main():
    """主函数"""
    favicon_dir = create_favicon_dir()
    links = get_website_links()
    
    print(f'找到 {len(links)} 个网站链接')
    
    success_count = 0
    for url in links:
        if download_favicon(url, favicon_dir):
            success_count += 1
        time.sleep(1)  # 添加延迟，避免请求过快
    
    print(f'\n下载完成: 成功 {success_count}/{len(links)}')

if __name__ == '__main__':
    main() 