# engine.py
import io
import zipfile
import requests
from typing import List, Dict, Iterable, Union, Optional

import pandas as pd

from beta_cynosure.utils.companies_data import companies
from beta_cynosure.utils.loaders import load_dfp_year, load_itr_year
from beta_cynosure.utils.cleaner import clean_financial_data
from beta_cynosure.utils.processor import prepare_quarterly_data

pd.set_option('display.max_columns', None) 

def _years(period: Union[int, str, Iterable[int]]) -> List[int]:
    if isinstance(period, int):
        return [period]
    if isinstance(period, str):
        s = period.strip()
        if "-" in s:
            a, b = s.split("-", 1)
            a, b = int(a), int(b)
            if a > b:
                a, b = b, a
            return list(range(a, b + 1))
        return [int(s)]
    return list(period)

def _filtered_names(prefix: Optional[Iterable[str]]) -> List[str]:
    if not prefix:
        return []
    pref = [p.upper() for p in prefix if p]
    found = set()
    for name, tickers in companies.items():
        for p in pref:
            if any(t and t.upper().startswith(p) for t in tickers):
                found.add(name)
                break
    return list(found)

def _filter_df_by_names(df: pd.DataFrame, names: List[str]) -> pd.DataFrame:
    if not names or "DENOM_CIA" not in df.columns:
        return df
    ups = [n.upper() for n in names]
    mask = df["DENOM_CIA"].astype("string").str.upper().apply(
        lambda s: any(n in s for n in ups)
    )
    return df[mask]

def _to_num_br(series: pd.Series) -> pd.Series:

    return pd.to_numeric(
        series.astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
        errors="coerce"
    )

def get_dfp(period: Union[int, str, Iterable[int]],
            prefix: Optional[Iterable[str]] = None) -> pd.DataFrame:
    years = _years(period)

    frames = []
    for y in years:
        dfp = load_dfp_year(y)

        dfp.columns = [str(c).upper() for c in dfp.columns]
        if "YEAR" not in dfp.columns:
            dfp["YEAR"] = y
        frames.append(dfp)

    dfp_all = clean_financial_data(pd.concat(frames, ignore_index=True))
    dfp_all.columns = [str(c).upper() for c in dfp_all.columns]

    names = _filtered_names(prefix)
    dfp_all = _filter_df_by_names(dfp_all, names)

    if "VL_CONTA" in dfp_all.columns:
        dfp_all["VL_CONTA"] = _to_num_br(dfp_all["VL_CONTA"])


    required = ["CNPJ_CIA", "DENOM_CIA", "CD_CONTA", "DS_CONTA", "GRUPO_DFP", "VL_CONTA", "YEAR"]
    for col in required:
        if col not in dfp_all.columns:
            dfp_all[col] = pd.NA

    return dfp_all[required].copy()

def get_itr(period: Union[int, str, Iterable[int]],
            prefix: Optional[Iterable[str]] = None) -> pd.DataFrame:
    years = _years(period)

    frames = []
    for y in years:
        itr = load_itr_year(y)
        itr.columns = [str(c).upper() for c in itr.columns]

        if "YEAR" not in itr.columns:
            for date_col in ("DT_FIM_EXERC", "DT_REFER", "DT_FIM_EXERCICIO", "DT_REFERENCIA", "DATA_FIM_EXERC"):
                if date_col in itr.columns:
                    itr["YEAR"] = pd.to_datetime(itr[date_col], errors="coerce").dt.year
                    break
            if "YEAR" not in itr.columns or itr["YEAR"].isna().all():
                itr["YEAR"] = y
        frames.append(itr)

    quarter_data = prepare_quarterly_data(frames)
    quarter_data.columns = [str(c).upper() for c in quarter_data.columns]

    for col in quarter_data.columns:
        if col.startswith("VL_") or col in ("VALOR", "VALOR_CONTA", "VL_CONTA_TRIMESTRE", "VL_CONTA"):
            try:
                quarter_data[col] = _to_num_br(quarter_data[col])
            except Exception:
                pass  

    names = _filtered_names(prefix)
    quarter_data = _filter_df_by_names(quarter_data, names)

    return quarter_data.copy()


def get_fre(period: Union[int, str, Iterable[int]],
            prefix: Optional[Iterable[str]] = None) -> pd.DataFrame:

    years = _years(period)

    dfp_all = get_dfp(period, prefix)
    if not dfp_all.empty:
        cnpjs = set(dfp_all["CNPJ_CIA"].dropna().astype(str).unique())
    else:
        quarter_data = get_itr(period, prefix)
        cnpjs = set(quarter_data["CNPJ_CIA"].dropna().astype(str).unique()) if not quarter_data.empty else set()

    cnpj_to_name: Dict[str, str] = {}
    if 'quarter_data' not in locals():
        quarter_data = get_itr(period, prefix)
    if not quarter_data.empty and {"CNPJ_CIA", "DENOM_CIA"}.issubset(quarter_data.columns):
        subset = quarter_data[["CNPJ_CIA", "DENOM_CIA"]].drop_duplicates()
        cnpj_to_name = dict(zip(subset["CNPJ_CIA"], subset["DENOM_CIA"]))

    rows = []
    for year in years:
        url = f"https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/fre/DADOS/fre_cia_aberta_{year}.zip"
        try:
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
            with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
                names = {n.lower(): n for n in z.namelist()}
                cap_name = next((names[k] for k in names if "capital_social" in k), None)
                dist_name = next((names[k] for k in names if "distribuicao_capital" in k), None)
                if not cap_name or not dist_name:
                    continue

                df_cap = pd.read_csv(z.open(cap_name), sep=';', encoding='latin1', dtype=str)
                df_dist = pd.read_csv(z.open(dist_name), sep=';', encoding='latin1', dtype=str)

                if cnpjs:
                    df_cap = df_cap[df_cap["CNPJ_Companhia"].isin(cnpjs)].drop_duplicates("CNPJ_Companhia")
                    df_dist = df_dist[df_dist["CNPJ_Companhia"].isin(cnpjs)].drop_duplicates("CNPJ_Companhia")

                # conversão numérica BR
                if "Quantidade_Total_Acoes" in df_cap.columns:
                    df_cap["Quantidade_Total_Acoes"] = _to_num_br(df_cap["Quantidade_Total_Acoes"])
                if "Quantidade_Total_Acoes_Circulacao" in df_dist.columns:
                    df_dist["Quantidade_Total_Acoes_Circulacao"] = _to_num_br(df_dist["Quantidade_Total_Acoes_Circulacao"])

                df_cap = df_cap[["CNPJ_Companhia", "Quantidade_Total_Acoes"]]
                df_dist = df_dist[["CNPJ_Companhia", "Quantidade_Total_Acoes_Circulacao"]]

                merged = pd.merge(df_cap, df_dist, on="CNPJ_Companhia", how="inner")
                merged.insert(0, "YEAR", year)
                merged = merged.rename(columns={"CNPJ_Companhia": "CNPJ"})
                if cnpj_to_name:
                    merged["DENOM_CIA"] = merged["CNPJ"].map(cnpj_to_name).astype("string")
                rows.append(merged)
        except Exception:
            continue  # segue pros próximos anos

    if rows:
        return pd.concat(rows, ignore_index=True)
    return pd.DataFrame(columns=["YEAR", "CNPJ", "DENOM_CIA",
                                 "Quantidade_Total_Acoes", "Quantidade_Total_Acoes_Circulacao"])


def get_all(period: Union[int, str, Iterable[int]],
            prefix: Optional[Iterable[str]] = None):
    return {
        "dfp": get_dfp(period, prefix),
        "itr": get_itr(period, prefix),
        "fre": get_fre(period, prefix),
    }

