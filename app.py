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

@app.route('/update_notes', methods=['POST'])
def update_notes():
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()

    for key, note in request.form.items():
        if key.startswith('note_'):
            num_vk = key.split('_')[1]
            cursor.execute("UPDATE vacations SET note = ? WHERE num_vk = ?", (note, num_vk))

    conn.commit()
    conn.close()
    return redirect(url_for('show_vacations'))  # Перенаправлення на сторінку vacations.html



@app.route('/return', methods=['POST'])
def process_return():
    selected_rows = request.form.getlist('selected_rows')
    conn = sqlite3.connect('excel_data.db')

    conditions = []
    params = []
    for row in selected_rows:
        num_vk, identifier = row.split('-')
        conditions.append("(v.num_vk = ? AND (v.ipn = ? OR v.pib = ? OR e.\"ПІБ\" = ?))")
        params.extend([num_vk, identifier, identifier, identifier])

    query = f"""
        SELECT e.\"ПІБ\", v.num_vk, v.date_vk, v.start, v.end, v.days, v.type, v.note
        FROM excel_data e
        JOIN vacations v ON e.\"ІПН\" = v.ipn OR e.\"ПІБ\" = v.pib
        WHERE {' OR '.join(conditions)}
    """
    cursor = conn.execute(query, params)
    data = cursor.fetchall()
    conn.close()
    return render_template('return.html', data=data)





if __name__ == '__main__':
    create_db()
    app.run(debug=True)
