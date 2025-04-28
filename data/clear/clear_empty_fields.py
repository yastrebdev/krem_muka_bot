def clear_empty_fields(data, np):
    missing_values_count = data.isnull().sum()

    total_cells = np.prod(data.shape)
    total_missing = missing_values_count.sum()

    percent_missing = (total_missing / total_cells) * 100

    columns_with_na_dropped = data.dropna(axis=1, how='all').dropna(how='all')

    return [columns_with_na_dropped, percent_missing]