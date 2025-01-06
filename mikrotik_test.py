from flask import Flask, jsonify, request
from flask_cors import CORS
from librouteros import connect

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

# Conexión a MikroTik
api = None
try:
    api = connect(username='admin', password='3112233174', host='192.168.15.2')
except Exception as e:
    print(f"Error al conectar a MikroTik: {str(e)}")

# Obtener los usuarios en queues
@app.route('/api/queues', methods=['GET'])
def get_queues():
    try:
        if not api:
            return jsonify({'error': 'No se pudo conectar a MikroTik'}), 500

        queues = list(api('/queue/simple/print'))
        return jsonify(queues), 200
    except Exception as e:
        print(f"Error al obtener las queues: {str(e)}")
        return jsonify({'error': f'Error al obtener las queues: {str(e)}'}), 500

@app.route('/api/block_user', methods=['POST'])
def block_user():
    try:
        user_id = request.json.get('user_id')
        if not user_id:
            return jsonify({'error': 'El parámetro user_id es necesario'}), 400

        if not api:
            return jsonify({'error': 'No se pudo conectar a MikroTik'}), 500

        queues = api.path('queue', 'simple')

        # Reducir el ancho de banda y deshabilitar la queue
        queues.update(**{'.id': user_id, 'max-limit': '1k/1k'})

        return jsonify({'message': 'Usuario bloqueado exitosamente con ancho de banda limitado a 1k/1k'}), 200
    except Exception as e:
        print(f"Error al bloquear el usuario: {str(e)}")
        return jsonify({'error': f'Error al bloquear el usuario: {str(e)}'}), 500


@app.route('/api/unblock_user', methods=['POST'])
def unblock_user():
    # Obtener los datos del cuerpo de la solicitud
    data = request.get_json()
    user_id = data.get('user_id')
    comment = data.get('comment')
    
    # Verificar si los datos son correctos
    if not user_id or not comment:
        return jsonify({'message': 'Error: user_id and comment are required'}), 400
    
    print(f"Valor de comment recibido: {comment}")
    
    # Llamar a una función que actualiza la cola en la base de datos
    try:
        # Usar el comentario como el nuevo valor de 'max-limit'
        max_limit = comment
        
        # Aquí llamamos a la función que actualiza la cola del usuario
        success = update_queue(user_id, max_limit)
        
        if success:
            return jsonify({'message': 'Usuario desbloqueado y max-limit actualizado exitosamente'}), 200
        else:
            return jsonify({'message': 'Error al actualizar la cola del usuario'}), 500
    
    except Exception as e:
        return jsonify({'message': f'Error interno: {str(e)}'}), 500


# Aquí se debe definir la función 'update_queue', que debe actualizar la cola del usuario en la base de datos
def update_queue(user_id, max_limit):
    try:
        # Aquí debe ir la lógica real para actualizar la cola
        # Este es un ejemplo de cómo podrías hacerlo. Si estás utilizando MikroTik, necesitarás hacer algo similar a:
        
        queues = api.path('queue', 'simple')
        
        # Actualizar el max-limit de la cola del usuario
        queues.update(**{'.id': user_id, 'max-limit': max_limit})
        
        # Si todo va bien, devolvemos True
        return True
    except Exception as e:
        print(f"Error al actualizar la cola: {str(e)}")
        return False

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
