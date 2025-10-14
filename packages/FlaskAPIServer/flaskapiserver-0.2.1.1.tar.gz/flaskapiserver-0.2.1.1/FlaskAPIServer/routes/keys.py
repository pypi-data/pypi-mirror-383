from . import *


logger = logger.setup(DEBUG, name="API_KEYS", log_path=LOG_PATH)

@api.route(f'{PREFIX_KEYS}', methods=['GET'])
@key_role('api_key')
def get_all_keys():
    try:
        keys = SQL_request(
            "SELECT key, role, is_active, created_at, updated_at FROM api_keys ORDER BY created_at DESC",
            fetch='all'
        )
        return jsonify({"keys": keys}), 200
    except Exception as e:
        logger.error(f"Ошибка при получении списка ключей: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

@api.route(f'{PREFIX_KEYS}', methods=['POST'])
@key_role('api_key')
def api_create_key():
    try:
        data = request.get_json()
        if not data or 'role' not in data:
            return jsonify({"error": "Не указана роль ключа"}), 400
        
        role = data['role']
        api_key = str(uuid.uuid4()).replace('-', '')
        SQL_request(
            "INSERT INTO api_keys (key, role) VALUES (?, ?)",
            (api_key, role),
            fetch=None
        )
        
        refresh_api_keys()
        
        logger.info(f"Создан новый API-ключ с ролью {role}")
        return jsonify({"key": api_key, "role": role, "message": "Ключ создан"}), 201
        
    except Exception as e:
        logger.error(f"Ошибка при создании ключа: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

@api.route(f'{PREFIX_KEYS}/<key>', methods=['PATCH'])
@key_role('api_key')
def update_key(key):
    try:
        data = request.get_json()
        if not data or 'role' not in data:
            return jsonify({"error": "Не указана роль ключа"}), 400
        
        role = data['role']
        is_active = data.get('is_active', True)
        
        SQL_request(
            "UPDATE api_keys SET role = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?",
            (role, is_active, key),
            fetch=None
        )
        
        refresh_api_keys()
        
        logger.info(f"Обновлен API-ключ {key}: роль={role}, активен={is_active}")
        return jsonify({"message": "Ключ обновлен"}), 200
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении ключа: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

@api.route(f'{PREFIX_KEYS}/<key>', methods=['DELETE'])
@key_role('api_key')
def delete_key(key):
    try:
        SQL_request(
            "DELETE FROM api_keys WHERE key = ?",
            (key,),
            fetch=None
        )
        
        refresh_api_keys()
        
        logger.info(f"Удален API-ключ {key}")
        return jsonify({"message": "Ключ удален"}), 200
        
    except Exception as e:
        logger.error(f"Ошибка при удалении ключа: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

@api.route(f'{PREFIX_KEYS}/refresh', methods=['GET'])
@key_role('api_key')
def refresh_keys():
    try:
        refresh_api_keys()
        return jsonify({"message": "Кеш API-ключей обновлен"}), 200
    except Exception as e:
        logger.error(f"Ошибка при обновлении кеша: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

@api.route(f'{PREFIX_KEYS}/jwt', methods=['GET', "POST"])
def generate_token():
    try:
        token = generate_jwt_token()
        return jsonify({'token': token}), 200
    except Exception as e:
        logger.error(f"Ошибка при обновлении кеша: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500