import time
import multiprocessing

def estressar_cpu():
    """Cria um loop infinito com cálculos matemáticos pesados para forçar a CPU."""
    while True:
        _ = [x**2 for x in range(10000)]

def estressar_memoria():
    """Cria uma lista gigante para consumir a memória RAM gradativamente."""
    dados_pesados = []
    while True:
        dados_pesados.append('A' * 10**6)  # Adiciona 1MB de strings por iteração
        time.sleep(0.1) # Pausa leve para não travar a VM instantaneamente

if __name__ == '__main__':
    print("Iniciando Teste de Estresse! Pressione Ctrl+C para abortar.")
    print("Aviso: Sua VM pode ficar lenta.")
    
    # Inicia processos separados para estressar CPU e Memória simultaneamente
    processo_cpu = multiprocessing.Process(target=estressar_cpu)
    processo_mem = multiprocessing.Process(target=estressar_memoria)
    
    processo_cpu.start()
    processo_mem.start()
    
    try:
        # Deixa rodando por tempo indeterminado até você apertar Ctrl+C
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nFinalizando processos de estresse...")
        processo_cpu.terminate()
        processo_mem.terminate()
        print("Sistema normalizado.")
