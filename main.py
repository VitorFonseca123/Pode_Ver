from flask import Flask, render_template, redirect, request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'PODEVER'

@app.route('/')
def Home():
    return render_template('AdicionarFilme.html')

@app.route('/Search', methods=['POST'])
def search():
    MovieName = request.form.get('movie_name')
    # Aqui você pode adicionar a lógica para pesquisar o filme
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)