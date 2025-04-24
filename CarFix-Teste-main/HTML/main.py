from flask import Flask, render_template, request, flash, redirect, session, g, url_for
import sqlite3
from flask_socketio import SocketIO, send
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'joaopedro'
app.config['DATABASE'] = 'usuarios.db'

# Inicialize o SocketIO
socketio = SocketIO(app)

# Função para conectar ao banco
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def create_table():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            senha TEXT NOT NULL,
            tema TEXT DEFAULT '#3b5998',
            img_perfil TEXT DEFAULT '/static/imagens/user.png',
            img_capa TEXT DEFAULT '/static/imagens/fundo.jpg',
            email TEXT NOT NULL
        );
    ''')
    db.commit()

with app.app_context():
    create_table()


@app.route("/")
def login():
    return render_template('login.html')


@app.route("/acesso", methods=['POST'])
def acesso():
    nome = request.form.get('email')
    senha = request.form.get('senha')

    db = get_db()
    usuario = db.execute('SELECT * FROM usuario WHERE (nome = ? OR email = ?) AND senha = ?', (nome, nome, senha)).fetchone()

    if usuario:
        session['id'] = usuario['id']
        return redirect('/home')
    else:
        flash('nome e/ou senha inválidos, tente novamente!!')
        return redirect('/')


@app.route("/cadastro")
def cadastro():
    return render_template('cadastro.html')


@app.route("/cadastrando", methods=['POST'])
def cadastrando():
    nome = request.form.get('nome')
    senha = request.form.get('senha')
    email = request.form.get('email')
    tema = '#3b5998'
    img_capa = '/static/imagens/Fundo.png'
    img_perfil = '/static/imagens/user.png'

    db = get_db()
    cursor = db.execute('''
        INSERT INTO usuario (nome, senha, tema, img_perfil, img_capa, email)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nome, senha, tema, img_perfil, img_capa, email))
    db.commit()

    flash(f'seja bem-vindo, {nome}!!')
    session['id'] = cursor.lastrowid
    return redirect('/home')


@app.route("/verificador")
def verificador():
    return render_template('verificador.html')


@app.route("/home")
def home():
    if 'id' in session:
        id_usuario = session['id']
        db = get_db()
        usuario = db.execute('SELECT * FROM usuario WHERE id = ?', (id_usuario,)).fetchone()
        if usuario:
            nome = usuario['nome']
            tema = usuario['tema']
            img_capa = usuario['img_capa']
            img_perfil = usuario['img_perfil']
            return render_template('home.html', nome=nome, tema=tema, img_capa=img_capa, img_perfil=img_perfil)
        else:
            flash('Usuário não encontrado...')
            return redirect('/')
    else:
        return redirect('/')

import os

@app.route("/perfil")
def perfil():
    if 'id' in session:
        id_usuario = session['id']
        db = get_db()
        usuario = db.execute('SELECT * FROM usuario WHERE id = ?', (id_usuario,)).fetchone()
        if usuario:
            # Caminho da pasta de fotos
            pasta_fotos = f'static/usuarios/{id_usuario}/fotos'
            if os.path.exists(pasta_fotos):
                fotos = [f"/{pasta_fotos}/{img}" for img in os.listdir(pasta_fotos) if img.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            else:
                fotos = []
            
            return render_template(
                'perfil.html',
                nome=usuario['nome'],
                email=usuario['email'],
                img_perfil=usuario['img_perfil'],
                fotos=fotos
            )
    return redirect('/')

@app.route('/upload_foto', methods=['POST'])
def upload_foto():
    if 'id' not in session:
        return redirect('/')

    id_usuario = session['id']
    if 'foto' not in request.files:
        flash('Nenhum arquivo enviado.')
        return redirect('/perfil')

    file = request.files['foto']
    if file.filename == '':
        flash('Nenhum arquivo selecionado.')
        return redirect('/perfil')

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        pasta_usuario = os.path.join(app.config['UPLOAD_FOLDER'], str(id_usuario), 'fotos')
        os.makedirs(pasta_usuario, exist_ok=True)
        caminho = os.path.join(pasta_usuario, filename)
        file.save(caminho)
        flash('Foto enviada com sucesso!')
        return redirect('/perfil')
    
    flash('Tipo de arquivo não permitido.')
    return redirect('/perfil')


@app.route("/fotos")
def fotos():
    return render_template('fotos.html')

@app.route("/chat")
def chat():
    if 'id' in session:
        id_usuario = session['id']
        db = get_db()
        usuario = db.execute('SELECT * FROM usuario WHERE id = ?', (id_usuario,)).fetchone()
        if usuario:
            # Buscar mensagens
            mensagens = db.execute('''
                SELECT m.mensagem, u.nome, m.timestamp 
                FROM mensagens m 
                JOIN usuario u ON m.usuario_id = u.id 
                ORDER BY m.timestamp ASC
            ''').fetchall()
            return render_template("chat.html", nome_usuario=usuario['nome'], mensagens=mensagens)
    return redirect('/')


# WebSocket para lidar com as mensagens
@socketio.on('message')
def handle_message(msg):
    print(f'Mensagem recebida: {msg}')
    usuario_id = session.get('id')

    if usuario_id:
        db = get_db()
        db.execute('INSERT INTO mensagens (usuario_id, mensagem) VALUES (?, ?)', (usuario_id, msg))
        db.commit()

        usuario = db.execute('SELECT nome FROM usuario WHERE id = ?', (usuario_id,)).fetchone()
        nome = usuario['nome'] if usuario else 'Desconhecido'

        send(f'{nome}: {msg}', broadcast=True)
    else:
        print("Usuário não autenticado para enviar mensagem.")


@app.route("/configuracoes")
def configuracoes():
    return render_template('configuracoes.html')


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))


# Rodar o servidor com Flask-SocketIO
if __name__ == '__main__':
    socketio.run(app, debug=True)

# Configurações de upload
UPLOAD_FOLDER = 'static/usuarios'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
