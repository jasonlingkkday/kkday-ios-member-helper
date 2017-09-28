import io
import json


def write_as_json_file(data, filename):
     with io.open(filename, mode='w', encoding='utf-8') as writer:
        to_write = json.dumps(data, ensure_ascii=False)
        if isinstance(to_write, str):
            to_write = unicode(to_write, 'utf-8')
        writer.write(to_write)

def load_json_file(filename):
    data = None
    with open(filename) as json_data:
        data = json.load(json_data)
    return data

def read_file(filename):
    lines = []
    with io.open(filename, encoding='utf-8') as reader:
        for line in reader:
            lines.append(line)
    return lines