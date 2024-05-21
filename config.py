response_time_limit = 200
resourse_limits = {
    "CPU":75,
    "RAM":75,
    "DISK SPACE":75
}

servers = [
    {
        "name": "DB-master",
        "host": "78.140.189.245",
        "checks": [
            {"type": "ping", "name": "PING"},
            {"type": "telnet", "name": "MySQL", "port": 3306},
            {"type": "telnet", "name": "SSH", "port": 22},
            {"type": "cpu", "name": "CPU"},
            {"type": "ram", "name": "RAM"},
            {"type": "disk_space", "name": "DISK SPACE"}
        ]
    },
    {
        "name": "DB-slave",
        "host": "206.54.170.119",
        "checks": [
            {"type": "ping", "name": "PING"},
            {"type": "telnet", "name": "MySQL", "port": 3306},
            {"type": "telnet", "name": "SSH", "port": 22},
            {"type": "cpu", "name": "CPU"},
            {"type": "ram", "name": "RAM"},
            {"type": "disk_space", "name": "DISK SPACE"}
        ]
    },
    {
        "name": "API1",
        "host": "206.54.170.126",
        "user": "root",
        "password": "O15v26LKb6mxjFX0eX",
        "checks": [
            {"type": "ping", "name": "PING"},
            {"type": "telnet", "name": "SSH", "port": 22},
            {"type": "telnet", "name": "API port", "port": 5000},
            {"type": "service", "name": "API service", "service": "adp-db-api.service"},
            {"type": "cpu", "name": "CPU"},
            {"type": "ram", "name": "RAM"},
            {"type": "disk_space", "name": "DISK SPACE"}
        ]
    },
    {
        "name": "API2",
        "host": "206.54.191.62",
        "user": "root",
        "password": "wQ5enUo7SP1d8rF9X5",
        "checks": [
            {"type": "ping", "name": "PING"},
            {"type": "telnet", "name": "SSH", "port": 22},
            {"type": "telnet", "name": "API port", "port": 5000},
            {"type": "service", "name": "API service", "service": "adp-db-api.service"},
            {"type": "cpu", "name": "CPU"},
            {"type": "ram", "name": "RAM"},
            {"type": "disk_space", "name": "DISK SPACE"}
        ]
    },
    {
        "name": "TG1",
        "host": "78.140.189.246",
        "user": "root",
        "password":"5q9fAM56B5iBL7wsoN",
        "checks": [
            {"type": "ping", "name": "PING"},
            {"type": "telnet", "name": "SSH", "port": 22},
            {"type": "service", "name": "Client Bot", "service":"adp-client-bot.service"},
            {"type": "service", "name": "Shop Bot", "service":"adp-shop-bot.service"},
            {"type": "cpu", "name": "CPU"},
            {"type": "ram", "name": "RAM"},
            {"type": "disk_space", "name": "DISK SPACE"}
        ]
    },
    {
        "name": "TG2",
        "host": "199.80.52.35",
        "user": "root",
        "password": "yPYyE83se79L5p3iMF",
        "checks": [
            {"type": "ping", "name": "PING"},
            {"type": "telnet", "name": "SSH", "port": 22},
            {"type": "service", "name": "Client Bot", "service": "adp-client-bot.service"},
            {"type": "service", "name": "Shop Bot", "service": "adp-shop-bot.service"},
            {"type": "cpu", "name": "CPU"},
            {"type": "ram", "name": "RAM"},
            {"type": "disk_space", "name": "DISK SPACE"}
        ]
    },
    {
        "name": "BACKUPS",
        "host": "78.140.162.131",
        "user": "root",
        "password": "0C4k9p3l9OZiTnFrM3",
        "checks": [
            {"type": "ping", "name": "PING"},
            {"type": "telnet", "name": "SSH", "port": 22},
            {"type": "service", "name": "Backup Service", "service": "backup.service"},
            {"type": "service", "name": "CRON", "service": "cron.service"},
            {"type": "cpu", "name": "CPU"},
            {"type": "ram", "name": "RAM"},
            {"type": "disk_space", "name": "DISK SPACE"}
        ]
    }
]

chats = [684172842]
