def drop_columns(df, cols: list[str]):
    new_df = df.drop(columns=cols)

    return new_df