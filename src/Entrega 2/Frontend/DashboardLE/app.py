import streamlit as st

home = st.Page("pages/Dashboard.py", title="Home", icon=":material/home:")
entrar = st.Page("pages/Entrar.py", title="Entrar", icon=":material/person:")
detalhes_grupo = st.Page("pages/1_Detalhes_do_Grupo.py", title="Detalhes do Grupo", icon=":material/details:")

#Usuário
captura = st.Page("pages/Captura.py", title="Captura", icon=":material/camera_video:")
grupo = st.Page("pages/Grupo.py", title="Meu Grupo",icon=":material/family_group:")
perfil = st.Page("pages/Perfil.py", title="Meu Perfil", icon=":material/frame_person:")

# 2. Group them in a dictionary to create the visual dividers
# The dictionary keys automatically become headers in your sidebar
pages = {
    "Área Pública": [home, entrar, detalhes_grupo],
    "Área do Usuário": [captura, grupo, perfil]
}

# 3. Pass the dictionary to st.navigation
pg = st.navigation(pages)

# 4. Run the navigation
pg.run()