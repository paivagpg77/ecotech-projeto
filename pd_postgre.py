import requests
import random
import time

API_URL   = "http://127.0.0.1:5000"
SENSOR_ID = "7b7fc478-f32b-4a2a-b4a8-1f2904f8a426"

QUANTIDADE = 20
INTERVALO  = 2

print(f"Enviando {QUANTIDADE} leituras para {API_URL}/receber")
print(f"Sensor ID: {SENSOR_ID}\n")

for i in range(1, QUANTIDADE + 1):
    umidade = round(random.uniform(30.0, 90.0), 2)
    try:
        resposta = requests.get(
            f"{API_URL}/receber",
            params={"umidade": umidade, "sensor_id": SENSOR_ID}
        )
        print(f"[{i}/{QUANTIDADE}] umidade={umidade}%  ->  {resposta.status_code} {resposta.text}")
    except Exception as e:
        print(f"[{i}/{QUANTIDADE}] ERRO ao conectar: {e}")
    time.sleep(INTERVALO)

print("\nPronto! Verifique os dados no Postman:")
print(f"  GET {API_URL}/dados")
print(f"  GET {API_URL}/ultima") 