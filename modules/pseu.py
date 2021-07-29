import pandas as pd
# import gocept.pseudonymize
import base64


def pseudonymization(method, data_path, columns):

    if method == "Gocept":
        # nondecodable_method(data_path, columns)
        return
    elif method == "Base64":
        return base64_method(data_path, columns)


# def nondecodable_method(data_path, columns):
#     data = pd.read_csv(data_path)
#     existing_columns = list(data)
#     for column in columns:
#         if column in existing_columns:
#             data[column] = data[column].apply(lambda x: gocept.pseudonymize.text(x, 'secret'))
#     return data


def base64_method(data_path, columns):
    data = pd.read_csv(data_path)
    data.dropna()
    data.reset_index(drop=True, inplace=True)
    existing_columns = list(data)
    for column in columns:
        if column in existing_columns:
            data[column] = data[column].apply(str)
            data[column] = data[column].apply(lambda x: base64.b64encode(bytes(x, 'utf-8')))
    return data

