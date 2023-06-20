from backend.settings import BASE_DIR
import json


def load_table_from_json(table, file_name):
    file = open(
        BASE_DIR / f'static/data/{file_name}.json',
        'r',
        encoding='utf-8'
    )
    json_data = json.load(file)
    for jd in json_data:
        t = table(**jd)
        t.save()
