const express = require('express');
const mysql = require('mysql2');
const bodyParser = require('body-parser');
const path = require('path');
const cors = require('cors')
const multer = require('multer');
const dotenv = require('dotenv');
const fs = require('fs');

dotenv.config();

const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, path.join(__dirname, 'uploads')); 
    },
    filename: function (req, file, cb) {
        cb(null, file.originalname);
    }
});

const upload = multer({ storage: storage });

const app = express();
const port = process.env.PORT || 5000;

app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Middleware
app.use(cors());
app.use(bodyParser.json({ limit: '50mb' }));
app.use(bodyParser.urlencoded({ limit: '50mb', extended: true }));

// Conexão MySQL
const db = mysql.createConnection({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  ssl: {
    rejectUnauthorized: false
  }
});

db.connect((err) => {
  if (err) {
    console.error('Erro ao conectar a database', err);
    return;
  }
  console.log('Conectado a Database MySQL');
});

app.use(express.json()); // Json para POST

app.post("/cadastro", function (req, res){
    var nome = req.body.nome;
    var email = req.body.email;
    var senha = req.body.senha;
    var query = 'INSERT INTO usuario (NOME, EMAIL, SENHA) VALUES (?,?,?)'
    db.query(query, [nome, email, senha], (err, result) =>{
    if (err){
        console.error('Falha ao adicionar o usuario', err)
        return res.status(500).json({ error: 'Falha ao adicionar usuario' + err.message });
    }
    res.status(200).json({message: 'Usuario Adicionado!'})
    })
      
})

app.post("/login", function (req, res){
  var email = req.body.email;
  var senha = req.body.senha;
  var query1 = 'Select * from usuario where email = ?';
  db.query(query1, [email], (err, result)=>{
    if(err){
        console.error('Erro ao procurar usuario', err)
        return res.status(500).json({ error: 'Email não encontrado' + err.message });
    }
      if (result.length === 0) {
          return res.status(404).json({ error: 'Usuario não encontrado' });
      }
    if(result[0].senha === senha){
      if (result[0].idgrupo != null){
        query2 = "select * from grupo where id = ?"
        db.query(query2,[result[0].idgrupo],(err, result2)=>{
          if(err){
            console.error('Erro ao procurar grupo', err)
            return res.status(500).json({ error: 'Grupo não encontrado' + err.message });
        }
        var userData = {
          nome: result[0].nome,
          idgrupo: result[0].idgrupo,
          nomeGrupo: result2[0].nomeGrupo
        }
        res.status(200).json(userData)
        })
      }else{
        var userData = {
          nome: result[0].nome,
          idgrupo: result[0].idgrupo
      }
      res.status(200).json(userData);
      }
      
    }else{

      return res.status(404).json({ error: 'Senha Incorreta'})
    }
  })
})

app.get('/grupos', function(req, res){
  query = 'Select * from grupo';

  db.query(query,(err,result)=>{
    if(err){
      console.log("Erro ao buscar as informações", err)
      return res.status(500).json({erro: "Erro ao buscar as informações" + err})
    }
    return res.status(200).json(result)
  })
})

app.post("/buscarIntegrantes", function(req, res){
  var idGrupo = req.body.idGrupo;
  var query = "select * from usuario where idGrupo = ?"

  db.query(query, [idGrupo],(err,result)=>{
    if(err){
      console.log("Erro ao buscar as informações", err)
      return res.status(500).json({erro: "Erro ao buscar as informações" + err})
    }
    return res.status(200).json(result)
  })
})

app.post("/captura", function(req, res) {
  var idGrupo = req.body.idGrupo;
  var dados = req.body.dados;
  var nome = req.body.nome;

  // Objeto para garantir que salvemos a foto do frame apenas uma vez,
  // mesmo que múltiplos alimentos sejam detectados no mesmo segundo
  const imagensSalvas = {};

  const valores = dados.map(item => {
    let frameCaminho = null;
    
    if (item.Frame) {
        if (!imagensSalvas[item.Frame]) {
            // Limpa o cabeçalho do base64 gerado pelo frontend
            const base64Data = item.Frame.replace(/^data:image\/jpeg;base64,/, "");
            // Gera um nome de arquivo unico
            const fileName = 'captura_' + Date.now() + '_' + Math.floor(Math.random() * 1000) + '.jpg';
            const filePath = path.join(__dirname, 'uploads', fileName);
            
            // Salva o arquivo fisicamente na pasta uploads
            fs.writeFileSync(filePath, base64Data, 'base64');
            imagensSalvas[item.Frame] = fileName;
        }
        frameCaminho = imagensSalvas[item.Frame];
    }
    // Retorna a linha formatada para o Bulk Insert no MySQL
    return [
      item.Item,
      item.Marca,
      item.Quantidade,
      item.Peso,
      item.Data,
      frameCaminho, // Insere o nome do arquivo na tabela (ou null)
      idGrupo,
      nome
    ];
  });

  const query = 'INSERT INTO alimento (nome, marca, quantidade, peso, dataHora, framecaminho, idGrupo, nomeIntegrante) VALUES ?';

  db.query(query, [valores], (err, result) => {
    if (err) {
      console.error("Erro ao salvar alimentos e imagens", err);
      return res.status(500).json({ error: "Erro ao salvar alimentos e imagens" });
    }

    res.status(200).json({ message: "Alimentos e Frames salvos!" });
  });
});

app.post("/fotoperfil", upload.single("foto"), function(req,res){
  var email = req.body.email;
  var nomeFoto = req.file.filename;

  query = "update usuario set foto = ? where email = ?"

  db.query(query, [nomeFoto, email], (err, result)=>{
    if(err){
      console.error("Erro ao salvar foto", err)
      return res.status(500).json({error: "Erro ao salvar a foto"})
    }
    res.status(200).json({message:"Foto salva!"})
  })
})

app.post("/buscarfoto", function(req,res){
  var email = req.body.email;
  
  query = "select foto from usuario where email = ?"

  db.query(query,[email], (err, result)=>{
    if(err){
      console.error("Erro ao buscar foto", err)
      return res.status(500).json({error: "Erro ao buscar foto"})
    }
    res.status(200).json(result)
  })
})

app.post("/criargrupo", function(req,res){
  var nomeGrupo = req.body.nomegrupo;
  var mentor = req.body.mentor;
  var integrantes = [req.body.integrante1, req.body.integrante2, req.body.integrante3, req.body.integrante4]

  query1 = "Insert into grupo(nomeGrupo, mentor, kgArrecadados) values(?,?,?)"

  db.query(query1, [nomeGrupo, mentor, 0], (err, result)=>{
    if(err){
      console.error("Erro ao criar o grupo", err)
      return res.status(500).json({error:"Erro ao criar o grupo"})
    }
    query2 = "select id from grupo where nomeGrupo = ?"
    db.query(query2,[nomeGrupo], (err, result)=>{
      if(err){
      console.error("Erro ao buscar id", err)
      return res.status(500).json({error:"Erro ao buscar id"})
    }
    idgrupo = result[0].id;
    query3 = "update usuario set idGrupo = ? where nome = ?"
    let completo = 0;
    for(let i = 0; i<4;i++){
      db.query(query3,[idgrupo, integrantes[i]], (err,result)=>{
        if(err){
        console.error("Erro ao modificar o usuário", err)
        return res.status(500).json({error:"Erro ao modificar o usuário"})
      }
      completo++;
      if (completo === integrantes.length) {
        return res.status(200).json({ message: "Grupo criado com sucesso" });
      }
      })
    }
    })
    
  })
})


app.post("/buscargrupo", function(req,res){
  var email = req.body.email;
  //Busca o id do grupo com base no email do usuário
  query1 = "select idGrupo from usuario where email = ?"
  db.query(query1, [email],(err, result)=>{
    if(err){
      console.error("Erro ao buscar id do grupo", err)
      return res.status(500).json({error: "Erro ao buscar id do grupo"})
    }
    idgrupo = result[0].idGrupo;
    //Busca as informações do grupo com base no id do grupo
    query2 = 'select * from grupo where id = ?'
    db.query(query2,[idgrupo], (err,result)=>{
      if(err){
      console.error("Erro ao buscar dados do grupo", err)
      return res.status(500).json({error: "Erro ao buscar dados do grupo"})
    }
    nomeGrupo = result[0].nomeGrupo;
    mentor = result[0].mentor;
    kgs = result[0].kgArrecadados;
    //Busca os membros do grupo com base no id do grupo
    query3 = "select * from usuario where idGrupo = ?"
    db.query(query3,[idgrupo],(err, result)=>{
      if(err){
      console.error("Erro ao buscar usuários", err)
      return res.status(500).json({error: "Erro ao buscar usuários"})
    }
    integrante1 = result[0].nome;
    integrante1Foto = result[0].foto;
    integrante2 = result[1].nome;
    integrante2Foto = result[1].foto;
    integrante3 = result[2].nome;
    integrante3Foto = result[2].foto
    integrante4 = result[3].nome;
    integrante4Foto = result[3].foto;
    var dados = {
      "idgrupo":idgrupo,
      "nomeGrupo":nomeGrupo,
      "mentor":mentor,
      "kgs":kgs,
      "integrante1":integrante1,
      "integrante1Foto":integrante1Foto,
      "integrante2": integrante2,
      "integrante2foto": integrante2Foto,
      "integrante3": integrante3,
      "integrante3foto": integrante3Foto,
      "integrante4": integrante4,
      "integrante4foto": integrante4Foto,
    }
    return res.status(200).json(dados)
    })
    })
  })
})

app.post("/buscarAlimentosGrupo", function(req,res){
  var idGrupo = req.body.idgrupo;
  query = "Select * from alimento where idGrupo = ?"
  db.query(query, [idGrupo], (err, result)=>{
    if(err){
      console.error("Erro ao buscar alimentos", err)
      return res.status(500).json({error: "Erro ao buscar alimentos"})
    }
    res.status(200).json(result)
  })
})

app.post("/editarAlimento", function(req, res) {
  const { id, nome, marca, quantidade, peso } = req.body;

  const query = "UPDATE alimento SET nome = ?, marca = ?, quantidade = ?, peso = ? WHERE id = ?";
  
  db.query(query, [nome, marca, quantidade, peso, id], (err, result) => {
    if (err) {
      console.error("Erro ao editar alimento", err);
      return res.status(500).json({ error: "Erro ao editar alimento" });
    }
    console.log(peso)
    res.status(200).json({ message: "Alimento atualizado!" });
  });
});

app.post("/excluirAlimento", function(req, res) {
  const { id } = req.body;

  const query = "DELETE FROM alimento WHERE id = ?";
  
  db.query(query, [id], (err, result) => {
    if (err) {
      console.error("Erro ao excluir alimento", err);
      return res.status(500).json({ error: "Erro ao excluir alimento" });
    }
    res.status(200).json({ message: "Alimento excluído com sucesso!" });
  });
});

app.get("/buscaralunos", function(req,res){
  query = "select nome from usuario where idgrupo is null"

  db.query(query, (err, result)=>{
    if(err){
      console.error("Erro ao buscar usuários", err)
      return res.status(500).json({error: "Erro ao buscar foto"})
    }
    res.status(200).json(result)
  })
})

// Inicializar o Servidor
app.listen(port, () => {
  console.log(`Server running on ${port}`);
});