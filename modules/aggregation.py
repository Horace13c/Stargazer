import pandas as pd
import numpy as np


def calculate_statistics(data_path, groupbycol, statistics_list, targetcol):
    dataset = pd.read_csv(data_path)
    dataset.dropna()
    dataset.reset_index(drop=True, inplace=True)
    grouped = dataset[targetcol].groupby(dataset[groupbycol])

    result_dict = {groupbycol: list(grouped.groups.keys())}

    for statistics in statistics_list:
        try:
            result_dict[statistics] = list(getattr(grouped, statistics)())
        except:
            pass

    return pd.DataFrame(result_dict)
    # return grouped

# # %%
#
#
# result = calculate_statistics("D:/programs/Stargazer/uploads/0bbcea8067634acfb0e548f97e3cb702.csv",
#                               "education",
#                               ["max", "min", "median", "mean", "count", "sum", "std", "quantile", "var", "nunique"], "age")
#
# # %%
#
# result.nunique()

