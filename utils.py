import io
import pandas as pd
import chardet

def detect_encoding(path_or_bytes):
    if isinstance(path_or_bytes, str):
        with open(path_or_bytes, "rb") as f:
            sample = f.read(50000)
    else:
        sample = path_or_bytes.read(50000)
        path_or_bytes.seek(0)
    result = chardet.detect(sample)
    return result.get("encoding", "utf-8")

def load_zomato_csv(path_or_buffer):
    import csv
    # Uploaded file
    if not isinstance(path_or_buffer, str):
        raw = path_or_buffer.read()
        enc = chardet.detect(raw).get("encoding", "latin1")
        path_or_buffer.seek(0)
        # detect delimiter
        sample = raw[:50000].decode(enc, errors="ignore")
        try:
            delimiter = csv.Sniffer().sniff(sample).delimiter
        except Exception:
            delimiter = ','
        return pd.read_csv(io.BytesIO(raw), encoding=enc, delimiter=delimiter)
    # File path
    try:
        return pd.read_csv(path_or_buffer, encoding="utf-8")
    except Exception:
        enc = detect_encoding(path_or_buffer)
        # detect delimiter from sample
        with open(path_or_buffer, "r", encoding=enc, errors="ignore") as f:
            sample = f.read(50000)
            try:
                delimiter = csv.Sniffer().sniff(sample).delimiter
            except Exception:
                delimiter = ','
        return pd.read_csv(path_or_buffer, encoding=enc, delimiter=delimiter)

def clean_zomato_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    if "Cuisines" in df.columns:
        df["Cuisines"] = df["Cuisines"].fillna("Unknown")
    for col in ["Aggregate rating", "Votes", "Average Cost for two", "Price range"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in ["Latitude", "Longitude"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df
