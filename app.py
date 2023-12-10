from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3
import pandas as pd

app = Flask(__name__)


def create_db():
    conn = sqlite3.connect('excel_data.db')
    conn.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        filename = os.path.join("uploaded_files", file.filename)
        file.save(filename)
        df = pd.read_excel(filename)
        print(df.columns)
        # Зберігання першого рядка
        first_row = df.iloc[0]

        # Видалення рядків, де 'ПІБ' є None
        df = df[df['ПІБ'].notna()]

        # Додавання першого рядка назад до DataFrame
        df = pd.concat([pd.DataFrame([first_row]), df]).reset_index(drop=True)

        conn = sqlite3.connect('excel_data.db')
        df.to_sql('excel_data', conn, if_exists='replace', index=False)
        conn.close()
        return 'Файл успішно завантажено'
    else:
        return 'Помилка при завантаженні файлу'


@app.route('/vacations')
def show_vacations():
    conn = sqlite3.connect('excel_data.db')
    df = pd.read_sql_query("SELECT * FROM vacations", conn)
    conn.close()
    return render_template('vacations.html', data=df.to_dict(orient='records'))

#NOTE

if __name__ == '__main__':
    create_db()
    app.run(debug=True)
