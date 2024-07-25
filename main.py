import requests
from bs4 import BeautifulSoup
import json
import logging
import time
from datetime import datetime

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

url = 'https://www.tokopedia.com/'

def with_req(link):
  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache'
  }
  try:
    response = requests.get(link, headers=headers, timeout=20, verify=True)
    response.raise_for_status()
    return response
  except Exception as e:
    logging.error("Terjadi error", exc_info=True)
    return False

def parse_categories(html_content):
  soup = BeautifulSoup(html_content, 'html.parser')
  container = soup.find('div', {'class': 'css-3966r0', 'data-ssr': 'belanjaCategorySSR'})

  if not container:
    logging.error('Container dengan kelas css-3966r0 dan data-ssr="belanjaCategorySSR" tidak ditemukan.')
    return []
  
  categories = container.find_all('div', {'class': 'css-s7tck8'})
  categories_json = []

  for category in categories:
    cats = category.find_all('a', {'class': 'css-1p4657n'})
    for c in cats:
      categories_json.append({
        'title': c.get_text(strip=True),
        'url': c['href']
      })
  
  return categories_json

def save_to_file(data, filename):
  with open(filename, 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=2)
  logging.info("JSON kategori berhasil disimpan ke file %s", filename)

def get_categories():
  start_time = time.time()
  start_time_formatted = datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S")
  print(f"TOKOPEDIA || Time Start: {start_time_formatted}")
  response = with_req(url + 'p')
  if response:
    categories_json = parse_categories(response.content)
    if categories_json:
      save_to_file(categories_json, 'tokopedia_categories.json')
    else:
      print('Tidak ada kategori yang ditemukan.')
  else:
    print('Permintaan gagal. Tidak ada respons yang valid.')

  end_time = time.time()
  duration = end_time - start_time
  stop_time_formatted = datetime.fromtimestamp(end_time).strftime("%Y-%m-%d %H:%M:%S")
  print(f"TOKOPEDIA || Time Stop: {stop_time_formatted}")
  print(f'Duration: {duration:.2f} detik')

def display_categories(categories_json):
  print("\nDaftar Kategori:")
  for idx, category in enumerate(categories_json):
    print(f"{idx + 1}. {category['title']}")
  choice = input("\nPilih kategori dengan nomor (atau ketik '0' untuk keluar): ")
  if choice.isdigit():
    choice = int(choice)
    if 1 <= choice <= len(categories_json):
      print(f"Anda memilih: {categories_json[choice - 1]['title']}")
      print(f"URL: {categories_json[choice - 1]['url']}")
    elif choice == 0:
      print("Keluar dari pilihan kategori.")
    else:
      print("Pilihan tidak valid.")
  else:
    print("Input tidak valid.")

def main():
  print("TOKOPEDIA SCRAPER")
  print("1. Cari Kategori")
  print("2. Pilih Kategori")

  choice = input("Masukkan pilihan (1 atau 2): ")

  if(choice == '1'):
    get_categories()
  elif(choice == '2'):
    try:
      with open('tokopedia_categories.json', 'r', encoding='utf-8') as file:
        categories_json = json.load(file)
      if categories_json:
        display_categories(categories_json)
      else:
        print('File JSON kategori kosong atau tidak ditemukan.')
    except FileNotFoundError:
      print('File JSON kategori tidak ditemukan. Ambil kategori terlebih dahulu.')
    except json.JSONDecodeError:
      print('Gagal membaca file JSON.')
  else:
    print('Permintaan gagal. Tidak ada respons yang valid.')
  

if __name__ == '__main__':
  main()