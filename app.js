const express = require('express');
const bodyParser = require('body-parser');
const mysql = require('mysql2');
const cors = require('cors');
const bcrypt = require('bcrypt'); // Importação do bcrypt para criptografar senhas

const app = express();
app.use(bodyParser.json());
app.use(cors());

// Conectar ao banco de dados MySQL
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',          // Seu usuário MySQL (geralmente 'root')
    password: 'Cl#101387',          // Sua senha MySQL
    database: 'vreslogin'  // Nome do banco de dados que você criou
});

db.connect((err) => {
    if (err) {
        console.error('Erro ao conectar ao banco de dados:', err);
        return;
    }
    console.log('Conectado ao banco de dados MySQL.');
});

// Rota para cadastro
app.post('/register', async (req, res) => {
    const { username, email, password } = req.body;

    // Verificar se o nome de usuário ou email já existe
    const queryCheck = 'SELECT * FROM usuarios WHERE username = ? OR email = ?';
    db.query(queryCheck, [username, email], async (err, results) => {
        if (err) {
            console.error('Erro ao buscar usuário:', err);
            return res.status(500).json({ message: 'Erro no servidor' });
        }

        if (results.length > 0) {
            return res.status(400).json({ message: 'Nome de usuário ou email já existe' });
        }

        try {
            // Criptografar a senha
            const hashedPassword = await bcrypt.hash(password, 10);

            // Inserir novo usuário no banco de dados
            const queryInsert = 'INSERT INTO usuarios (username, email, password) VALUES (?, ?, ?)';
            db.query(queryInsert, [username, email, hashedPassword], (err, result) => {
                if (err) {
                    console.error('Erro ao inserir usuário:', err);
                    return res.status(500).json({ message: 'Erro no servidor' });
                }

                res.status(201).json({ message: 'Cadastro realizado com sucesso' });
            });
        } catch (error) {
            console.error('Erro ao criptografar senha:', error);
            res.status(500).json({ message: 'Erro no servidor' });
        }
    });
});

// Rota para login
app.post('/login', (req, res) => {
    const { username, password } = req.body;

    // Verificar se o usuário existe no banco de dados
    const query = 'SELECT * FROM usuarios WHERE username = ?';
    db.query(query, [username], async (err, results) => {
        if (err) {
            console.error('Erro ao buscar usuário:', err);
            return res.status(500).json({ message: 'Erro no servidor' });
        }

        const user = results[0];
        if (!user) {
            return res.status(404).json({ message: 'Usuário não encontrado' });
        }

        try {
            // Comparar a senha fornecida com a senha criptografada armazenada no banco
            const isPasswordValid = await bcrypt.compare(password, user.password);
            if (!isPasswordValid) {
                return res.status(401).json({ message: 'Senha incorreta' });
            }

            res.status(200).json({ message: 'Login bem-sucedido' });
        } catch (error) {
            console.error('Erro ao verificar senha:', error);
            res.status(500).json({ message: 'Erro no servidor' });
        }
    });
});

// Configuração do servidor na porta 3000
app.listen(3000, () => {
    console.log('Servidor rodando na porta 3000');
});
