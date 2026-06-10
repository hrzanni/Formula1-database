import csv
import io
from flask import (Flask, render_template, request, session,
                   redirect, url_for, flash)
from db import query, execute
import queries as Q

app = Flask(__name__)
app.secret_key = 'f1_scc541_g09_secret'

# ── TELA 1: LOGIN ─────────────────────────────────────────────────────────────

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        rows = query(Q.SQL_LOGIN, (
            request.form['login'].strip(),
            Q.sha256_hex(request.form['password'])
        ))
        if not rows:
            flash('Login ou senha inválidos.', 'danger')
            return render_template('login.html')
        u = rows[0]
        session.update(
            userid=u['userid'],
            login=u['login'],
            tipo=u['tipo'],
            id_original=u['id_original']
        )
        execute(Q.SQL_INSERT_LOG, (u['userid'], 'LOGIN'))
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    if 'userid' in session:
        execute(Q.SQL_INSERT_LOG, (session['userid'], 'LOGOUT'))
    session.clear()
    return redirect(url_for('login'))

# ── TELA 2: DASHBOARD ─────────────────────────────────────────────────────────

@app.route('/dashboard')
def dashboard():
    if 'userid' not in session:
        return redirect(url_for('login'))

    tipo = session['tipo']
    oid  = session['id_original']

    if tipo == 'Admin':
        return render_template('dashboard_admin.html',
            totais=query(Q.SQL_ADMIN_TOTAIS)[0],
            corridas=query(Q.SQL_ADMIN_CORRIDAS_RECENTES),
            escuderias=query(Q.SQL_ADMIN_STANDINGS_ESCUDERIAS),
            pilotos=query(Q.SQL_ADMIN_STANDINGS_PILOTOS))

    if tipo == 'Escuderia':
        return render_template('dashboard_escuderia.html',
            info=query(Q.SQL_ESCUDERIA_INFO, (oid,))[0])

    info = query(Q.SQL_PILOTO_INFO, (oid,))[0]
    return render_template('dashboard_piloto.html',
        info=info,
        desempenho=query(Q.SQL_PILOTO_DESEMPENHO, (oid,)))

# ── TELA 3: RELATÓRIOS ────────────────────────────────────────────────────────

@app.route('/relatorios')
def relatorios():
    if 'userid' not in session:
        return redirect(url_for('login'))
    pedir_cidade = request.args.get('pedir') == '2'
    return render_template('reports.html',
                           tipo=session['tipo'],
                           pedir_cidade=pedir_cidade)


@app.route('/relatorio/<int:num>')
def relatorio(num):
    if 'userid' not in session:
        return redirect(url_for('login'))

    tipo = session['tipo']
    oid  = session['id_original']

    MAPA = {
        (1, 'Admin'):     (Q.SQL_R1,  None,   'Resultados por Status'),
        (4, 'Escuderia'): (Q.SQL_R4,  (oid,), 'Pilotos e Vitórias da Escuderia'),
        (5, 'Escuderia'): (Q.SQL_R5,  (oid,), 'Resultados por Status da Escuderia'),
        (6, 'Piloto'):    (Q.SQL_R6,  (oid,), 'Pontos por Ano'),
        (7, 'Piloto'):    (Q.SQL_R7,  (oid,), 'Resultados por Status'),
    }

    if (num, tipo) in MAPA:
        sql, params, titulo = MAPA[(num, tipo)]
        return render_template('report_result.html',
                               titulo=titulo,
                               rows=query(sql, params))

    if num == 2 and tipo == 'Admin':
        cidade = request.args.get('cidade', '').strip()
        if not cidade:
            return redirect(url_for('relatorios', pedir='2'))
        return render_template('report_result.html',
                               titulo=f'Aeroportos próximos a "{cidade}"',
                               rows=query(Q.SQL_R2, (cidade,)))

    if num == 3 and tipo == 'Admin':
        return render_template('report_result.html',
                               titulo='Relatório Hierárquico de Circuitos',
                               hierarquico=True,
                               total=query(Q.SQL_R3_TOTAL)[0],
                               por_circuito=query(Q.SQL_R3_CIRCUITO),
                               por_corrida=query(Q.SQL_R3_CORRIDA))

    flash('Relatório indisponível para este perfil.', 'warning')
    return redirect(url_for('relatorios'))

# ── AÇÕES ADMIN ───────────────────────────────────────────────────────────────

@app.route('/cadastrar/escuderia', methods=['GET', 'POST'])
def cadastrar_escuderia():
    if session.get('tipo') != 'Admin':
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        f = request.form
        ref = f['constructor_ref'].strip().lower().replace(' ', '_')
        try:
            execute(Q.SQL_INSERT_CONSTRUCTOR, (
                ref, ref,
                f['name'].strip(),
                f['nationality'].strip(),
                f.get('country_id') or None,
                f.get('wikipedia_url') or None,
            ))
            flash(f'Escuderia "{f["name"]}" cadastrada. Login: {ref}_c  Senha: {ref}', 'success')
        except Exception as e:
            flash(f'Erro: {e}', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('action_form.html',
                           titulo='Cadastrar Escuderia',
                           campos=[
                               ('constructor_ref', 'Referência (ex: new_team)', True),
                               ('name',            'Nome completo',             True),
                               ('nationality',     'Nacionalidade',             True),
                               ('country_id',      'ID do País (opcional)',     False),
                               ('wikipedia_url',   'URL Wikipedia (opcional)',  False),
                           ])


@app.route('/cadastrar/piloto', methods=['GET', 'POST'])
def cadastrar_piloto():
    if session.get('tipo') != 'Admin':
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        f = request.form
        ref = f['driver_ref'].strip().lower().replace(' ', '_')
        try:
            execute(Q.SQL_INSERT_DRIVER, (
                ref, ref,
                f['given_name'].strip(),
                f['family_name'].strip(),
                f.get('nationality') or None,
                f.get('date_of_birth') or None,
            ))
            flash(f'Piloto "{f["given_name"]} {f["family_name"]}" cadastrado. Login: {ref}_d  Senha: {ref}', 'success')
        except Exception as e:
            flash(f'Erro: {e}', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('action_form.html',
                           titulo='Cadastrar Piloto',
                           campos=[
                               ('driver_ref',    'Referência (ex: novo_piloto)', True),
                               ('given_name',    'Nome',                         True),
                               ('family_name',   'Sobrenome',                    True),
                               ('date_of_birth', 'Data de nascimento (AAAA-MM-DD)', False),
                               ('nationality',   'Nacionalidade (opcional)',      False),
                           ])

# ── AÇÕES ESCUDERIA ───────────────────────────────────────────────────────────

@app.route('/buscar/piloto', methods=['GET', 'POST'])
def buscar_piloto():
    if session.get('tipo') != 'Escuderia':
        return redirect(url_for('dashboard'))

    rows, sobrenome = [], ''
    if request.method == 'POST':
        sobrenome = request.form['sobrenome'].strip()
        rows = query(Q.SQL_BUSCA_PILOTO,
                     (f'%{sobrenome}%', session['id_original']))

    return render_template('search_result.html', rows=rows, sobrenome=sobrenome)


@app.route('/importar/pilotos', methods=['GET', 'POST'])
def importar_pilotos():
    if session.get('tipo') != 'Escuderia':
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        arq = request.files.get('arquivo')
        if not arq:
            flash('Nenhum arquivo enviado.', 'warning')
            return redirect(request.url)

        reader = csv.DictReader(io.StringIO(arq.read().decode('utf-8')))
        ok, erros = [], []

        for row in reader:
            gn = row.get('given_name', '').strip()
            fn = row.get('family_name', '').strip()
            if not gn or not fn:
                erros.append(f'Linha inválida: {row}')
                continue
            if query("SELECT 1 FROM drivers WHERE given_name ILIKE %s AND family_name ILIKE %s", (gn, fn)):
                erros.append(f'{gn} {fn} (já existe)')
                continue
            ref = row.get('driver_ref', '').strip().lower() or (gn + '_' + fn).lower().replace(' ', '_')
            try:
                execute(Q.SQL_INSERT_DRIVER, (
                    ref, ref, gn, fn,
                    row.get('nationality', '').strip() or None,
                    row.get('date_of_birth', '').strip() or None,
                ))
                ok.append(f'{gn} {fn}')
            except Exception as e:
                erros.append(f'{gn} {fn} — {e}')

        msg = f'{len(ok)} inserido(s).'
        if erros:
            msg += f' {len(erros)} ignorado(s): {"; ".join(erros)}'
        flash(msg, 'info')
        return redirect(url_for('dashboard'))

    return render_template('action_form.html',
                           titulo='Importar Pilotos por CSV',
                           upload=True)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
