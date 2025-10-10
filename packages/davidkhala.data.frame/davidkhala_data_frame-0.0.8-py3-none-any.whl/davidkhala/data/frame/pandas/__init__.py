def upsert(df, primary_key:str, record:dict):
    df.loc[record[primary_key]] = record
    return df
