import requests
import json
import time

# Devolver la data en un archivo .json
output_file_path = 'data.json'

# Establecer las credenciales para el login
username = 'AQUI_VA_EL_USUARIO'
password = 'AQUI_VA_LA_CONTRASEÑA'

# Funcion para obtener el token
def obtener_token():
    try:
        response = requests.post(
            'AQUI VA LA API PARA EL TOKEN',
            # Credenciales
            data={'username': username, 'password': password},
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        response.raise_for_status()
        #Se obtiene el token
        return response.json()['data']['token']
    except requests.RequestException as e:
        print(f"Error en la solicitud POST: {e}")
        raise

 # Funcion para consultar Dni o el dato de la api que se quiere dumpear
def consultar_dni(token, dni, sexo):
    try:
        response = requests.get(
            f'AQUI VA LA API CON EL ENDPOINT PARA CONSULTAR /?dni={dni}&sexo={sexo}',
            headers={'Authorization': f'Bearer {token}'}
        )
        response.raise_for_status()
        data = response.json()
        if not data:
            return {'dni': dni, 'sexo': sexo, 'mensaje': 'NO SE ENCONTRO INFORMACION'}
        return {'dni': dni, **data}
    except requests.RequestException as e:
        print(f"Error en la solicitud GET para DNI {dni} con sexo {sexo}: {e}")
        return {'dni': dni, 'sexo': sexo, 'mensaje': 'ERROR EN LA SOLICITUD'}

#Consultar la data, primero con el sexo femenino y si no encuentra el sexo masculino
def consultar_dni_flexible(token, dni):
    data = consultar_dni(token, dni, 'f')
    if data.get('mensaje') == 'NO SE ENCONTRO INFORMACION':
        # print(f"Reintentando con sexo masculino para DNI {dni}")
        data = consultar_dni(token, dni, 'm')
    return data

def main():
    try:
        token = obtener_token()
        start_dni = 0000000  # DNI inicial
        end_dni = 99999999  # DNI final para pruebas 
        batch_size = 200  # Tamaño del lote para consultas concurrentes (ajustar según tus necesidades)
        delay_between_batches = 3  # 3 segundos entre lotes

        for i in range(start_dni, end_dni + 1, batch_size):
            results = []
            for j in range(i, min(i + batch_size, end_dni + 1)):
                result = consultar_dni_flexible(token, j)
                results.append(result)
                print(f"Consultado DNI {j}: {result}")  # Mensaje de depuración
            
            valid_results = [result for result in results if result]

            # Guardar en el archivo JSON con codificación UTF-8
            with open(output_file_path, 'a', encoding='utf-8') as f:
                json.dump(valid_results, f, ensure_ascii=False, indent=2)
                f.write('\n')
            
            print(f"Lote {i} a {min(i + batch_size - 1, end_dni)} procesado.")

            # Espera antes de procesar el siguiente lote
            time.sleep(delay_between_batches)
        
        print('Proceso completado.')
    except Exception as e:
        print(f"Error en el proceso: {e}")

if __name__ == '__main__':
    main()