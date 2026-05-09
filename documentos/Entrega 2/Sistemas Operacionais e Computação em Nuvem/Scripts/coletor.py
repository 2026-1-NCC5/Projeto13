import psutil
import csv
import time
from datetime import datetime

# Nome do arquivo de saída
ARQUIVO_CSV = 'dados_monitoramento.csv'

# Criar o arquivo e escrever o cabeçalho
with open(ARQUIVO_CSV, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['DataHora', 'Tempo_Segundos', 'CPU_Percentual', 'Memoria_Percentual'])

print(f"Iniciando coleta de dados em {ARQUIVO_CSV}. Pressione Ctrl+C para parar.")

tempo_inicial = time.time()

try:
    while True:
        agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        tempo_decorrido = int(time.time() - tempo_inicial)
        
        # Coletar uso de CPU e Memória
        uso_cpu = psutil.cpu_percent(interval=None) # interval=None para não travar o loop
        uso_memoria = psutil.virtual_memory().percent
        
        # Salvar no CSV
        with open(ARQUIVO_CSV, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([agora, tempo_decorrido, uso_cpu, uso_memoria])
        
        # Aguardar 2 segundos para a próxima coleta
        time.sleep(2)

except KeyboardInterrupt:
    print("\nColeta de dados finalizada pelo usuário.")
