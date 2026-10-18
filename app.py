from flask import Flask, render_template, request, redirect, url_for
import time
from waitress import serve
import qrcode
import socket
import os

app = Flask(__name__)

PORT = 80
UPLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads", "FileSharing")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def up_stroke(lst):
    if not lst:
        return 'No network interfaces found, using localhost only', ''
    return 'Server is working on', '  |  '.join(lst)

def get_ips():
    full_address = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        full_address.connect(('8.8.8.8', 53)) #по UDP коннектится к днс гугла и смотрит сетевой интерфейс для выхода в интернет
        hostname = socket.gethostname()
        ips = socket.gethostbyname_ex(hostname)[2] #socket  .gethostbyname_ext дает кортеж (Имя машины, хз пусто, [Айпишники])
    except Exception:
        ips = [] #Возвращает Пустой список для функции up_stroke
    finally:
        full_address.close() #Закрывает сокет
    return ips


def startup(): # Консольная красота для RX устройства
    ip_addresses = get_ips()
    print("=" * 40)
    print("📁 Файлообменник запущен!")
    print("=" * 40)
    print("Доступные адреса:")
    for ip in ip_addresses:
        time.sleep(0.5)
        http_link = f"http://{ip}:{PORT}"
        qr = qrcode.QRCode(box_size=1, border=1)
        qr.add_data(http_link)
        qr.make(fit=True)
        print(f"\n📱 {http_link}")
        qr.print_ascii(invert=True)


    print('Перебирайте адреса или QR-Коды пока сайт не откроется')
    print('ВАЖНО: ОТПРАВЛЯЮЩЕЕ И ПРИНИМАЮЩЕЕ УСТРОЙСТВО ДОЛЖНО БЫТЬ В ОДНОЙ И ТОЙ ЖЕ СЕТИ')
    print('Скорее всего, нужный вам ip начинается на "192."')

def unique_name(request, lst): #Переименовывает файл в name_i.ext если такие name и ext есть в списке
    counter = 1

    for i, item in enumerate(lst):
        lst[i] = os.path.splitext(item)[0]

    request_name = os.path.splitext(request)[0]
    new_request_name = request_name
    request_ext = os.path.splitext(request)[1]

    while new_request_name in lst:
        new_request_name = f'{request_name}_{counter}'
        counter += 1
    request = f'{new_request_name}{request_ext}'
    return request

def all_files(): #Получает Список всех файлов из папки
    lst = os.listdir(UPLOAD_FOLDER)
    return lst

def get_file_names(): #Убирает чепуху из файлов и оставляет name.ext
    files_in_directory = all_files()
    file_names = []

    for full_file in files_in_directory: # Создание списка во всеми файлами из папки
        file = os.path.splitext(full_file)[0] + os.path.splitext(full_file)[1]
        file_names.append(file)
    return file_names


@app.route('/', methods=['GET', 'POST'])
def index():
    text = up_stroke(get_ips())

    return render_template('index3.html', server=text[0], ip=text[1])


@app.route('/upload', methods=['POST'])
def upload():
    client_ip = request.remote_addr

    requested_files = request.files.getlist('shared_file') #мультипл выборка файлов

    if not requested_files or requested_files[0].filename == '': #Защита от пустой отправки
        return redirect(url_for('index')) #* позже выводить /error.html с указанием ошибки

    else:
        files_in_directory = get_file_names()
        for requested_file in requested_files:
            full_requested_file = requested_file.filename #Перевожу в full_requsted_file но проверку все равно по requested_file.filename
            if '..' in requested_file.filename or '/' in requested_file.filename or '\\' in requested_file.filename or requested_file.filename == '':
                # Защита от опасных названий
                return redirect(url_for('index3.html')) #* Позже вывести другой /error.html с указанием ошибки
            else:
                file_path = os.path.join(UPLOAD_FOLDER, requested_file.filename)
                if full_requested_file not in files_in_directory: # Проверка на наличие файла в директории
                    requested_file.save(file_path)
                    print(f'{requested_file.filename} from {client_ip}')

                else:
                    file_name_for_print = unique_name(full_requested_file, files_in_directory)
                    requested_file.save(file_path)
                    print(f'{file_name_for_print} from {client_ip}')


        return redirect(url_for('index'))


if __name__ == '__main__':
    startup()
    serve(app, host='0.0.0.0', port=PORT, max_request_body_size= 100 * 1024 * 1024 * 1024)