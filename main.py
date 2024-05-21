#!/usr/bin/python3

from abc import ABC, abstractmethod
import subprocess
import psutil
import telnetlib
import time
import paramiko
from config import servers, resourse_limits, response_time_limit
from threading import Thread
import logging
import json
from datetime import datetime
from handlers import StrategyFactory


class IMonitorStrategy(ABC):
    """
    Інтерфейс стратегії моніторингу.

    Методи:
    - check: Перевіряє стан сервера.
    - response_time: Повертає час відгуку сервера.
    """

    @abstractmethod
    def check(self) -> bool:
        pass

    @abstractmethod
    def response_time(self) -> float:
        pass


class ServerPingMonitor(IMonitorStrategy):
    """
    Клас для моніторингу сервера за допомогою ping.

    Аргументи:
    - host: Адреса хоста для моніторингу.
    """

    def __init__(self, host):
        self.host = host

    def check(self) -> bool:
        """
        Перевіряє доступність хоста за допомогою команди ping.

        Повертає:
        - bool: True, якщо хост доступний, інакше False.
        """
        response = subprocess.run(['ping', '-c', '1', self.host], stdout=subprocess.PIPE)
        return response.returncode == 0

    def response_time(self) -> float:
        """
        Вимірює час відгуку хоста за допомогою ping.

        Повертає:
        - float: Час відгуку в мілісекундах або -1.0, якщо не вдалося визначити.
        """
        response = subprocess.run(['ping', '-c', '1', self.host], stdout=subprocess.PIPE)
        output = response.stdout.decode('cp1251')
        time_pos = output.find('time=')
        if time_pos != -1:
            start = time_pos + 5
            end = output.find(' ', start)
            return float(output[start:end])
        return -1.0


class TelnetMonitor(IMonitorStrategy):
    """
    Клас для моніторингу сервера за допомогою Telnet.

    Аргументи:
    - host: Адреса хоста для моніторингу.
    - port: Порт для підключення.
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def check(self) -> bool:
        """
        Перевіряє можливість підключення до хоста за допомогою Telnet.

        Повертає:
        - bool: True, якщо підключення вдалося, інакше False.
        """
        try:
            with telnetlib.Telnet(self.host, self.port, timeout=10) as tn:
                return True
        except Exception as e:
            logging.error(f"Error connecting to {self.host}:{self.port}: {e}")
            return False

    def response_time(self) -> float:
        """
        Вимірює час відгуку хоста за допомогою Telnet.

        Повертає:
        - float: Час відгуку в секундах.
        """
        try:
            start_time = time.time()
            with telnetlib.Telnet(self.host, self.port, timeout=10) as tn:
                end_time = time.time()
                return end_time - start_time
        except Exception as e:
            end_time = time.time()
            logging.error(f"Failed to connect to {self.host}:{self.port}: {e}")
            return end_time - start_time


class ServiceMonitor(IMonitorStrategy):
    """
    Клас для моніторингу сервісу на сервері за допомогою SSH.

    Аргументи:
    - hostname: Ім'я хоста для підключення.
    - port: Порт для підключення (за замовчуванням 22).
    - username: Ім'я користувача для підключення.
    - password: Пароль для підключення.
    - service_name: Назва сервісу для моніторингу.
    """

    def __init__(self, hostname, port, username, password, service_name):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.service_name = service_name

    def check(self) -> bool:
        """
        Перевіряє стан сервісу на сервері за допомогою команди systemctl.

        Повертає:
        - bool: True, якщо сервіс активний, інакше False.
        """
        command = f"systemctl is-active {self.service_name}"
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.hostname, port=self.port, username=self.username, password=self.password)
            stdin, stdout, stderr = ssh.exec_command(command)
            output = stdout.read().decode().strip()
            ssh.close()

            return output == 'active'
        except Exception as e:
            logging.error(f"Ошибка при подключении или выполнении команды на сервере: {e}")
            return False

    def response_time(self) -> float:
        """
        Повертає нуль як час відгуку, оскільки перевірка стану сервісу не залежить від часу.

        Повертає:
        - float: 0.
        """
        return 0


class CPUMonitor(IMonitorStrategy):
    """
    Клас для моніторингу завантаження CPU.
    """

    def check(self) -> bool:
        """
        Завжди повертає True, оскільки перевірка завантаження CPU не залежить від доступності сервера.

        Повертає:
        - bool: True.
        """
        return True

    def response_time(self) -> float:
        """
        Вимірює завантаження CPU у відсотках.

        Повертає:
        - float: Завантаження CPU у відсотках.
        """
        load1, _, _ = psutil.getloadavg()
        cpu_usage = (load1 / psutil.cpu_count()) * 100
        return cpu_usage


class RAMMonitor(IMonitorStrategy):
    """
    Клас для моніторингу використання оперативної пам'яті.
    """

    def check(self) -> bool:
        """
        Завжди повертає True, оскільки перевірка використання оперативної пам'яті не залежить від доступності сервера.

        Повертає:
        - bool: True.
        """
        return True

    def response_time(self) -> float:
        """
        Вимірює використання оперативної пам'яті у відсотках.

        Повертає:
        - float: Використання оперативної пам'яті у відсотках.
        """
        mem = psutil.virtual_memory()
        return mem.percent


class DiskMonitor(IMonitorStrategy):
    """
    Клас для моніторингу використання дискового простору.

    Аргументи:
    - disk: Шлях до диску для моніторингу (за замовчуванням '/').
    """

    def __init__(self, disk='/'):
        self.disk = disk

    def check(self) -> bool:
        """
        Завжди повертає True, оскільки перевірка використання дискового простору не залежить від доступності сервера.

        Повертає:
        - bool: True.
        """
        return True

    def response_time(self) -> float:
        """
        Вимірює використання дискового простору у відсотках.

        Повертає:
        - float: Використання дискового простору у відсотках.
        """
        usage = psutil.disk_usage(self.disk)
        return usage.percent


class CheckManager:
    """
    Клас для керування перевірками серверів.

    Атрибути:
    - handlers: Фабрика стратегій для обробки результатів перевірок.
    - aggregate_results: Зібрані результати перевірок.
    - threads: Список потоків для паралельного виконання перевірок.
    """

    def __init__(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        self.handlers = StrategyFactory()
        self.aggregate_results = {}
        self.threads = []

    def run_check(self, server, check):
        """
        Виконує перевірку сервера.

        Аргументи:
        - server: Словник з даними про сервер.
        - check: Словник з даними про перевірку.
        """
        host = server.get("host")
        check_name = check.get("name")
        try:
            if check['type'] == 'ping':
                monitor = ServerPingMonitor(host)
            elif check['type'] == 'telnet':
                monitor = TelnetMonitor(host, check['port'])
            elif check['type'] == 'service':
                monitor = ServiceMonitor(host, 22, server['user'], server['password'], check['service'])
            elif check['type'] == 'cpu':
                monitor = CPUMonitor()
            elif check['type'] == 'ram':
                monitor = RAMMonitor()
            elif check['type'] == 'disk_space':
                monitor = DiskMonitor()
            else:
                return

            result = monitor.check()
            response_time = monitor.response_time()
            self.log_result(server["name"], check["name"], result, response_time)
            if check['type'] not in 'cpu ram disk_space':
                if not result:
                    self.handle_failure(server["name"], check["name"], check['type'])
                elif response_time >= response_time_limit:
                    self.handle_warning(server["name"], check["name"], response_time)
            elif check['type'] in 'cpu ram disk_space' and response_time >= resourse_limits[check_name]:
                self.handle_warning(server["name"], check["name"], response_time)
        except Exception as e:
            logging.error(e)

    def log_result(self, server_name, check_name, result, response_time=None):
        """
        Логує результати перевірки.

        Аргументи:
        - server_name: Назва сервера.
        - check_name: Назва перевірки.
        - result: Результат перевірки.
        - response_time: Час відгуку (за замовчуванням None).
        """
        logger = logging.getLogger(server_name)
        if not logger.handlers:
            handler = logging.FileHandler(f"logs/{server_name}_checks.log")
            handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', '%Y-%m-%d %H:%М:%S'))
            logger.addHandler(handler)

        if (check_name in ["CPU", "RAM", "DISK SPACE"]):
            logger.info(
                f"{server_name} --- {check_name} --- {'Success' if result else 'Failure'} | {f'Usage: {round(response_time, 3)}%' if response_time is not None else ''}")
        else:
            logger.info(
                f"{server_name} --- {check_name} --- {'Success' if result else 'Failure'} | {f' Response Time: {round(response_time, 3)} seconds' if response_time is not None else ''}")
        if server_name not in self.aggregate_results:
            self.aggregate_results[server_name] = []
        self.aggregate_results[server_name].append({
            "check_name": check_name,
            "result": 'Success' if result else 'Failure',
            "response_time": round(response_time, 3) if response_time is not None else None,
        })

    def handle_failure(self, server_name, check_name, check_type):
        """
        Обробляє помилки перевірок.

        Аргументи:
        - server_name: Назва сервера.
        - check_name: Назва перевірки.
        - check_type: Тип перевірки.
        """
        with open('./aggregate_results.json', 'r') as file:
            data = json.load(file)
        handler = self.handlers.get_strategy(server_name, check_type, data)
        handler.handle(server_name, check_name)

    def handle_warning(self, server_name, check_name, value):
        """
        Обробляє попередження.

        Аргументи:
        - server_name: Назва сервера.
        - check_name: Назва перевірки.
        - value: Значення попередження.
        """
        handler = self.handlers.get_strategy(server_name, check_name, 'warning')
        handler.handle(server_name, check_name, value)

    def save_aggregate_results(self):
        """
        Зберігає зібрані результати перевірок у файл.
        """
        self.aggregate_results['last-check-time'] = datetime.now().strftime('%Y-%м-%д %H:%M:%S')
        with open("./aggregate_results.json", "w") as json_file:
            json_str = json.dumps(self.aggregate_results, indent=4)
            json_file.write(json_str)

    def start(self):
        """
        Запускає процес моніторингу серверів у циклі.
        """
        while True:
            for server in servers:
                for check in server['checks']:
                    thread = Tфhread(target=self.run_check, args=(server, check,))
                    self.threads.append(thread)
                    thread.start()

            for thread in self.threads:
                thread.join()

            self.save_aggregate_results()
            self.threads = []
            time.sleep(60)


def start_monitoring():
    """
    Функція для запуску процесу моніторингу.
    """
    manager = CheckManager()
    manager.start()


if __name__ == "__main__":
    start_monitoring()
