from backend.settings import BASE_DIR
import json


def load_table_from_json(model, file_name):
    file = open(
        BASE_DIR / f'static/data/{file_name}.json',
        'r',
        encoding='utf-8'
    )
    json_data_list = json.load(file)
    model.objects.all().delete()
    for json_data_obj in json_data_list:
        model_obj = model(**json_data_obj)
        model_obj.save()
