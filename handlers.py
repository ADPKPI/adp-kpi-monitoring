import requests
from config import chats
import paramiko
import logging
from config import servers


class FailureHandlingStrategy:
    """
    Базовий клас стратегії обробки збоїв.

    Методи:
    - handle: Обробляє збій для вказаного сервера та перевірки.
    """

    def handle(self, server_name, check_name):
        pass


class StrategyFactory:
    """
    Фабрика стратегій для обробки результатів перевірок.

    Атрибути:
    - notify_failure_strategy: Стратегія обробки збоїв.
    - notify_warning_strategy: Стратегія обробки попереджень.
    - move_services_strategy: Стратегія переміщення сервісів.

    Методи:
    - get_strategy: Повертає відповідну стратегію залежно від сервера та типу перевірки.
    """

    def __init__(self):
        self.notify_failure_strategy = NotifyFailureStrategy()
        self.notify_warning_strategy = NotifyWarningStrategy()
        self.move_services_strategy = MoveServicesStrategy()

    def get_strategy(self, server_name, check_type, other_checks):
        """
        Повертає відповідну стратегію залежно від сервера та типу перевірки.

        Аргументи:
        - server_name: Назва сервера.
        - check_type: Тип перевірки.
        - other_checks: Інші перевірки.

        Повертає:
        - FailureHandlingStrategy: Відповідна стратегія обробки.
        """
        if other_checks == 'warning':
            return self.notify_warning_strategy
        elif server_name == 'TG1':
            return self.move_services_strategy
        else:
            return self.notify_failure_strategy


class NotifyFailureStrategy(FailureHandlingStrategy):
    """
    Стратегія сповіщення про збої.

    Методи:
    - handle: Відправляє сповіщення про збій до всіх чатів.
    """

    def handle(self, server_name, check_name):
        """
        Відправляє сповіщення про збій до всіх чатів.

        Аргументи:
        - server_name: Назва сервера.
        - check_name: Назва перевірки.
        """
        url = 'http://127.0.0.1:5001/alert'
        for id in chats:
            data = {
                'chat_id': id,
                'message': f'❗❗❗ТРИВОГА\n\n{server_name}: {check_name} НЕ ВІДПОВІДАЄ'
            }
            response = requests.post(url, json=data)


class NotifyWarningStrategy(FailureHandlingStrategy):
    """
    Стратегія сповіщення про попередження.

    Методи:
    - handle: Відправляє сповіщення про попередження до всіх чатів.
    """

    def handle(self, server_name, check_name, value):
        """
        Відправляє сповіщення про попередження до всіх чатів.

        Аргументи:
        - server_name: Назва сервера.
        - check_name: Назва перевірки.
        - value: Значення попередження.
        """
        url = 'http://127.0.0.1:5001/alert'
        for id in chats:
            data = {
                'chat_id': id,
                'message': f'⚠️УВАГА\n\n{server_name}: {check_name} = {value}'
            }
            response = requests.post(url, json=data)


class MoveServicesStrategy(FailureHandlingStrategy):
    """
    Стратегія переміщення сервісів між серверами.

    Методи:
    - handle: Відключає сервіси на одному сервері та включає їх на іншому.
    """

    def handle(self, server_name, check_name):
        """
        Відключає сервіси на одному сервері та включає їх на іншому.

        Аргументи:
        - server_name: Назва сервера.
        - check_name: Назва перевірки.
        """
        tg1_server_info = next((server for server in servers if server['name'] == 'TG1'), None)
        tg2_server_info = next((server for server in servers if server['name'] == 'TG2'), None)
        message = f"❗❗❗ТРИВОГА\n\n{server_name} --- {check_name} НЕ ВІДПОВІДАЄ\n\n"

        if self.connect_and_disable_services(tg1_server_info):
            message += "Служби відключені на TG1\n"
        else:
            message += "Не вдалося під'єднатися до TG1\n"

        if self.connect_and_enable_services(tg2_server_info, ['adp-client-bot.service', 'adp-shop-bot.service']):
            message += "Служби включені на TG2\n"
        else:
            message += "Не вдалося під'єднатися до TG2\n"

        self.send_message(message)

    def connect_and_disable_services(self, server_info):
        """
        Підключається до сервера та відключає сервіси.

        Аргументи:
        - server_info: Інформація про сервер.

        Повертає:
        - bool: True, якщо сервіси успішно відключено, інакше False.
        """
        try:
            ssh = self.connect_ssh(server_info)
            if ssh:
                self.disable_services(ssh, server_info)
                ssh.close()
                return True
        except Exception as e:
            logging.error(f"Error disabling services on {server_info['name']}: {e}")
        return False

    def connect_and_enable_services(self, server_info, services):
        """
        Підключається до сервера та включає сервіси.

        Аргументи:
        - server_info: Інформація про сервер.
        - services: Список сервісів для включення.

        Повертає:
        - bool: True, якщо сервіси успішно включено, інакше False.
        """
        try:
            ssh = self.connect_ssh(server_info)
            if ssh:
                self.enable_services(ssh, services)
                ssh.close()
                return True
        except Exception as e:
            logging.error(f"Error enabling services on {server_info['name']}: {e}")
            return False

    def connect_ssh(self, server_info):
        """
        Підключається до сервера за допомогою SSH.

        Аргументи:
        - server_info: Інформація про сервер.

        Повертає:
        - paramiko.SSHClient: Об'єкт SSHClient, якщо підключення успішне, інакше None.
        """
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=server_info['host'],
                username=server_info['user'],
                password=server_info['password']
            )
            return ssh
        except Exception as e:
            logging.error(f"Failed to connect to {server_info['name']} via SSH: {e}")
            return None

    def disable_services(self, ssh, server_info):
        """
        Відключає сервіси на сервері.

        Аргументи:
        - ssh: Об'єкт SSHClient.
        - server_info: Інформація про сервер.
        """
        for check in server_info.get('checks', []):
            if check['type'] == 'service':
                self.manage_service(ssh, check['service'], 'stop')

    def enable_services(self, ssh, services):
        """
        Включає сервіси на сервері.

        Аргументи:
        - ssh: Об'єкт SSHClient.
        - services: Список сервісів для включення.
        """
        for service in services:
            self.manage_service(ssh, service, 'start')

    def manage_service(self, ssh, service_name, action):
        """
        Виконує вказану дію над сервісом на сервері.

        Аргументи:
        - ssh: Об'єкт SSHClient.
        - service_name: Назва сервісу.
        - action: Дія (start або stop).
        """
        try:
            stdin, stdout, stderr = ssh.exec_command(f'systemctl {action} {service_name}')
            stdout_text = stdout.read().decode()
            stderr_text = stderr.read().decode()
            if stdout_text:
                logging.info(
                    f"Output of {action} {service_name} on {ssh.get_transport().getpeername()[0]}: {stdout_text}")
            if stderr_text:
                logging.error(
                    f"Error in {action} {service_name} on {ssh.get_transport().getpeername()[0]}: {stderr_text}")
        except Exception as e:
            logging.error(f"Failed to {action} {service_name} on {ssh.get_transport().getpeername()[0]}: {e}")

    def send_message(self, message):
        """
        Відправляє повідомлення до всіх чатів.

        Аргументи:
        - message: Текст повідомлення.
        """
        url = 'http://127.0.0.1:5001/alert'
        for id in chats:
            data = {
                'chat_id': id,
                'message': message
            }
            response = requests.post(url, json=data)
