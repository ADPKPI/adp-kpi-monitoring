from flask import Flask, jsonify
import json

app = Flask(__name__)

def read_results():
    """
    Зчитує результати перевірок з файлу aggregate_results.json.

    Повертає:
    - dict: Дані з файлу у вигляді словника.
    """
    with open("./aggregate_results.json", "r") as file:
        data = json.load(file)
    return data

@app.route('/results', methods=['GET'])
def get_results():
    """
    Обробляє GET-запит для отримання всіх результатів перевірок.

    Повертає:
    - jsonify: Всі результати перевірок у форматі JSON.
    """
    data = read_results()
    return jsonify(data)

@app.route('/results/<server_name>', methods=['GET'])
def get_server_results(server_name):
    """
    Обробляє GET-запит для отримання результатів перевірок конкретного сервера.

    Аргументи:
    - server_name: Назва сервера.

    Повертає:
    - jsonify: Результати перевірок для вказаного сервера у форматі JSON або повідомлення про помилку.
    """
    data = read_results()
    server_data = data.get(server_name, {})
    if not server_data:
        return jsonify({"error": "Server not found"}), 404
    return jsonify(server_data)

if __name__ == "__main__":
    app.run(debug=True, host='206.54.170.102', port=5000)
