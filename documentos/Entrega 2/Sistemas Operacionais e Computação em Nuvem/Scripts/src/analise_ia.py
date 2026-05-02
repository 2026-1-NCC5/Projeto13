import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest

# Configuração visual dos gráficos
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# 1. CARREGAR OS DADOS
df = pd.read_csv('dados_monitoramento.csv')

# ==========================================
# IA 1: REGRESSÃO LINEAR (Tendência da CPU)
# ==========================================
# Objetivo: Identificar a tendência de uso da CPU ao longo do tempo.
X_reg = df[['Tempo_Segundos']]
y_reg = df['CPU_Percentual']

modelo_regressao = LinearRegression()
modelo_regressao.fit(X_reg, y_reg)
df['Tendencia_CPU'] = modelo_regressao.predict(X_reg)

plt.figure()
plt.plot(df['Tempo_Segundos'], df['CPU_Percentual'], label='Uso Real de CPU', color='blue', alpha=0.6)
plt.plot(df['Tempo_Segundos'], df['Tendencia_CPU'], label='Tendência (Regressão)', color='red', linewidth=2)
plt.title('Regressão Linear: Tendência de Uso da CPU ao Longo do Tempo')
plt.xlabel('Tempo (Segundos)')
plt.ylabel('Uso da CPU (%)')
plt.legend()
plt.show()

# ==========================================
# IA 2: CLUSTERIZAÇÃO (K-Means)
# ==========================================
# Objetivo: Agrupar os estados do servidor (ex: Ocioso, Normal, Sobrecarga).
# Usaremos CPU e Memória como variáveis.
X_cluster = df[['CPU_Percentual', 'Memoria_Percentual']]

# Definimos 3 clusters (estados)
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df['Estado_Cluster'] = kmeans.fit_predict(X_cluster)

plt.figure()
sns.scatterplot(data=df, x='CPU_Percentual', y='Memoria_Percentual', hue='Estado_Cluster', palette='viridis', s=100)
plt.title('K-Means: Agrupamento de Estados do Servidor')
plt.xlabel('Uso da CPU (%)')
plt.ylabel('Uso da Memória (%)')
plt.legend(title='Clusters')
plt.show()

# ==========================================
# IA 3: DETECÇÃO DE ANOMALIAS (Isolation Forest)
# ==========================================
# Objetivo: Detectar comportamentos anômalos (como os picos do teste de estresse).
# contamination=0.1 significa que assumimos que ~10% dos dados são anomalias (picos).
iso_forest = IsolationForest(contamination=0.1, random_state=42)
df['Anomalia'] = iso_forest.fit_predict(X_cluster)

# O algoritmo retorna -1 para anomalias e 1 para dados normais.
df['Status_Anomalia'] = df['Anomalia'].apply(lambda x: 'Anomalia' if x == -1 else 'Normal')

plt.figure()
sns.scatterplot(data=df, x='Tempo_Segundos', y='CPU_Percentual', hue='Status_Anomalia', 
                palette={'Normal': 'green', 'Anomalia': 'red'}, s=80)
plt.title('Isolation Forest: Detecção de Picos Anômalos na CPU')
plt.xlabel('Tempo (Segundos)')
plt.ylabel('Uso da CPU (%)')
plt.show()

# Visualização final para o Relatório: Análise Conjunta no Tempo
plt.figure()
plt.plot(df['Tempo_Segundos'], df['CPU_Percentual'], label='CPU (%)', color='blue')
plt.plot(df['Tempo_Segundos'], df['Memoria_Percentual'], label='Memória (%)', color='orange')

# Destacar as anomalias detectadas no gráfico temporal
anomalias = df[df['Anomalia'] == -1]
plt.scatter(anomalias['Tempo_Segundos'], anomalias['CPU_Percentual'], color='red', label='Anomalia Detectada', zorder=5)

plt.title('Monitoramento Completo com Destaque de Anomalias')
plt.xlabel('Tempo (Segundos)')
plt.ylabel('Uso (%)')
plt.legend()
plt.show()
