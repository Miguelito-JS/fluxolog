"""Ponto de entrada: rode `python src/app.py` e acesse http://127.0.0.1:5000"""

from fluxolog import criar_app

app = criar_app()

if __name__ == "__main__":
    # debug=True recarrega o servidor ao salvar o código (use só em desenvolvimento).
    app.run(debug=True)
