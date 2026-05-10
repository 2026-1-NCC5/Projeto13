# FECAP - Fundação de Comércio Álvares Penteado

<p align="center">
<a href= "https://www.fecap.br/"><img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRhZPrRa89Kma0ZZogxm0pi-tCn_TLKeHGVxywp-LXAFGR3B1DPouAJYHgKZGV0XTEf4AE&usqp=CAU" alt="FECAP - Fundação de Comércio Álvares Penteado" border="0"></a>
</p>

## Enrolados

## Integrantes: <a href="https://github.com/guibarioni"> Guilherme Barioni</a>, <a href=https://github.com/IuryXa>Iury Xavier</a>, <a href="https://github.com/lilianconde">Lilian Conde</a>, <a href="https://github.com/marcusduquee">Marcus Duque</a>

## Professores Orientadores: <a href="https://www.linkedin.com/in/rafael-diogo-rossetti/">Rafael Diogo Rossetti</a>, <a href="https://www.linkedin.com/in/professorrodnil/">Rodnil Lisbôa</a>, <a href="https://www.linkedin.com/in/victorbarq/">Victor Bruno Alexander Rosetti de Quiroz</a>, <a href="https://www.linkedin.com/in/marcosminorunakatsugawa/">Marcos Minoru Nakatsugawa</a>, <a href="https://www.linkedin.com/in/rodrigo-da-rosa-phd/">Rodrigo da Rosa</a>

## Descrição

<p align="center">
<img src="https://raw.githubusercontent.com/2026-1-NCC5/Projeto13/refs/heads/main/imagens/logo.png" alt="Logo do Visão Empática" border="0">
  Logo by <a href="https://github.com/2026-1-NCC5/Projeto13/tree/main">Enrolados</a> <a rel="license" href="https://creativecommons.org/licenses/by-sa/3.0/">CC BY-SA 3.0</a>
</p>

O visão empática busca facilitar o desafio da contagem manual de alimentos do projeto lideranças empáticas. Com o auxílio de tecnologias de inteligência artificial e visão computacional, o nosso sistema é capaz de contar e identificar diferentes tipos de alimentos e sintetizar os dados coletados em uma dashboard interativa, possibilitando não somente o acompanhamento do progresso dos grupos, mas permitindo também o processo de auditoria pelos professores.
<br><br>
O nosso modelo foi treinado utilizando o modelo Yolov8n, com um dataset de 1107 imagens. Na versão atual o modelo é capaz de identificar os seguintes alimentos:
<ul>
  <li>Arroz</li>
  <li>Feijão carioca</li>
  <li>Óleo de soja</li>
  <li>Açúcar Refinado</li>
  <li>Café</li>
  <li>Fubá</li>
  <li>Macarrão</li>
</ul>
<br><br>

## 🛠 Estrutura de pastas

-Raiz<br>
|<br>
|-->documentos<br>
  &emsp;|-->Entrega 1<br>
  &emsp;|-->Entrega 2<br>
  &emsp;|Banner_FECAP_CCOMP5_Enrolados.pdf<br>
  &emsp;|Documento - Projeto de Extensão - COM Empresa - 2026_1.pdf<br>
|-->imagens<br>
  &emsp;|logo.png<br>
|-->src<br>
  &emsp;|-->Backend<br>
  &emsp;|-->Frontend<br>
|readme.md<br>

## 💻 Configuração para Desenvolvimento

### Requisitos

Para abrir este projeto você necessita das seguintes ferramentas:

Para a dashboard:<br>
-<a href="https://www.python.org/downloads/">Python</a>:<br>
Para o backend:<br>
-<a href="https://nodejs.org/pt-br/download">Node.js</a>:<br>
Para o Banco de dados:<br>
-<a href="https://www.mysql.com/downloads/">MySQL</a> ou <a href="https://mariadb.org/download/">MariaDB</a>:<br>
Para clonar o repositório:<br>
-<a href="https://git-scm.com/install/windows">Git</a>:<br>

> [!Linux]
> Você pode baixar as ferramentas necessárias diretamente do repositório da sua distribuição.

## Inicializando o ambiente

Clone o repositório com:
```sh
git clone https://github.com/2026-1-NCC5/Projeto13/
```

### Banco de dados

Com o MySQL/MariaDB instalado, crie um usuário e utilize o arquivo db.sql na pasta /src/Entrega 2/Backend para criar o seu banco de dados.

### Backend

Entre na pasta src/Entrega 2/Backend e crie um arquivo ".env" e insira os seguintes valores:
```sh
DB_HOST="localhost"
DB_NAME="LE"
DB_USER="Nome do banco de dados criado"
DB_PASSWORD="Senha do banco de dados criado"
```

Instale as seguintes dependências com o npm:
```sh
npm install express mysql2 body-parser cors multer dotenv fs
```

Inicialize o backend com:
```sh
node server.js
```

### Dashboard

Com o Python instalado, entre na pasta src/Entrega 2/Frontend/DashboardLE e crie o ambiente virtual com:
Linux:
```sh
python -m venv .venv
source ./.venv/bin/activate
```
Windows:
```sh
python -m venv .venv
source .\.venv\bin\activate
```
Crie um arquivo ".env" e insira os seguintes valores:
```sh
API_URL="Coloque o endereço do backend"
SECRET_KEY="Crie uma chave"
VIDEO_URL="Se você vai utilizar uma câmera via internet, coloque a url aqui"
```
Depois instale as seguintes dependências com o pip:
```sh
pip install streamlit streamlit_cookies_manager streamlit_shortcuts dotenv pandas ploty numpy opencv-python ultralytics
```
Inicialize a dashboard com:
```sh
streamlit run app.py
```

## 📋 Licença/License
<a href="https://github.com/2026-1-NCC5/Projeto13">Enrolados</a> © 2026 by <a href="https://example.com">Guilherme Barioni, Iury Xavier, Lilian Conde, Marcus Duque, FECAP</a> is licensed under <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a><img src="https://mirrors.creativecommons.org/presskit/icons/cc.svg" alt="" style="max-width: 1em;max-height:1em;margin-left: .2em;"><img src="https://mirrors.creativecommons.org/presskit/icons/by.svg" alt="" style="max-width: 1em;max-height:1em;margin-left: .2em;">

## 🎓 Referências

Aqui estão as referências usadas no projeto.

1. Lideranças Empáticas. Disponível em: <https://liderancasempaticas.com/>. Acesso em: 9 Maio 2026
2. ORGANIZAÇÃO DAS NAÇÕES UNIDAS (ONU). Transformando Nosso Mundo: A Agenda 2030 para o Desenvolvimento Sustentável. (Objetivo 2). Disponível em: <https://brasil.un.org/pt-br/sdgs>. Acesso em: 9 Maio 2026
3. AI to support humanitarian response in emergencies. Disponível em: <https://wfpinnovation.medium.com/how-wfp-and-partners-are-using-ai-to-support-humanitarian-response-in-emergencies-60a329d688fb>. Acesso em: 9 maio. 2026.
4. Automated Package Counting Using Vision AI. Disponível em:<https://imagevision.ai/blog/automated-package-counting-using-vision-ai-for-high-volume-facilities/> Acesso em: 9 maio. 2026.
5. POLO, Luis. A Supply Chain Approach Highlighting the Use of Artificial Intelligence and Computer Vision to Improve the Efficiency of Food Supply Chains in the United States. International Journal for Multidisciplinary Field, v. 7, mar. 2025. Disponível em:<https://www.ijfmr.com/papers/2025/2/38464.pdf> Acesso em: 9 maio. 2026
