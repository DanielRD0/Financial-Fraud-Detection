
"""
Synthetic financial transactions dataset generator.

Generates:
- 500,000 valid records with business logic
- 100,000 dirty/noisy records for data cleaning practice
- 600,000 total rows

"""

from __future__ import annotations

import argparse
import math
import random
import string
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


# -----------------------------
# Global configuration
# -----------------------------

SEED = 42

VALID_RECORDS = 500_000
DIRTY_RECORDS = 100_000
TOTAL_CUSTOMERS = 7_000

VALID_FRAUD_RATIO = 0.10
VALID_REGULAR_RATIO = 0.90

# Customer segment mix chosen to exactly reach 500,000 transactions
CUSTOMER_SEGMENT_COUNTS = {
    "regular": 4_000,    # avg 71 tx in 3 months
    "high_flow": 1_200,  # avg 135 tx in 3 months
    "moderate": 1_800,   # avg 30 tx in 3 months
}

PRODUCT_TYPES = [
    "ahorro",
    "pago de prestamo",
    "pago de tarjeta",
    "transferencia cuenta a cuenta",
]

CHANNELS = ["app", "web", "sucursal", "ATM", "agente"]
TRANSACTION_STATUS = ["completada", "pendiente", "fallida", "reversada"]
TRANSACTION_DIRECTIONS = ["entrada", "salida"]
ACCOUNT_TYPES = ["ahorro", "corriente", "prestamo", "tarjeta"]

OCCUPATION_PROFILES = [
    {
        "occupation": "empleado privado",
        "industry": "servicios",
        "employment_type": "fijo",
        "income_range": (25_000, 85_000),
        "income_frequency": ["mensual", "quincenal"],
        "product_weights": [0.25, 0.20, 0.20, 0.35],
    },
    {
        "occupation": "docente",
        "industry": "educacion",
        "employment_type": "fijo",
        "income_range": (22_000, 65_000),
        "income_frequency": ["mensual", "quincenal"],
        "product_weights": [0.30, 0.25, 0.10, 0.35],
    },
    {
        "occupation": "independiente",
        "industry": "comercio",
        "employment_type": "independiente",
        "income_range": (18_000, 120_000),
        "income_frequency": ["semanal", "quincenal", "mensual"],
        "product_weights": [0.15, 0.10, 0.15, 0.60],
    },
    {
        "occupation": "microempresario",
        "industry": "negocios",
        "employment_type": "independiente",
        "income_range": (35_000, 180_000),
        "income_frequency": ["semanal", "quincenal", "mensual"],
        "product_weights": [0.10, 0.10, 0.15, 0.65],
    },
    {
        "occupation": "cajero",
        "industry": "retail",
        "employment_type": "fijo",
        "income_range": (20_000, 40_000),
        "income_frequency": ["mensual", "quincenal"],
        "product_weights": [0.25, 0.15, 0.15, 0.45],
    },
    {
        "occupation": "analista",
        "industry": "tecnologia",
        "employment_type": "fijo",
        "income_range": (45_000, 140_000),
        "income_frequency": ["mensual"],
        "product_weights": [0.20, 0.15, 0.25, 0.40],
    },
    {
        "occupation": "medico",
        "industry": "salud",
        "employment_type": "fijo",
        "income_range": (60_000, 220_000),
        "income_frequency": ["mensual", "quincenal"],
        "product_weights": [0.15, 0.15, 0.30, 0.40],
    },
    {
        "occupation": "chofer",
        "industry": "transporte",
        "employment_type": "informal",
        "income_range": (18_000, 55_000),
        "income_frequency": ["semanal", "quincenal"],
        "product_weights": [0.20, 0.10, 0.10, 0.60],
    },
    {
        "occupation": "pensionado",
        "industry": "hogar",
        "employment_type": "pensionado",
        "income_range": (18_000, 70_000),
        "income_frequency": ["mensual"],
        "product_weights": [0.40, 0.25, 0.05, 0.30],
    },
    {
        "occupation": "desempleado",
        "industry": "sin sector",
        "employment_type": "desempleado",
        "income_range": (0, 12_000),
        "income_frequency": ["mensual"],
        "product_weights": [0.20, 0.05, 0.05, 0.70],
    },
]

RISK_LEVELS = ["bajo", "medio", "alto"]
RISK_SCORES = {
    "bajo": (250, 499),
    "medio": (500, 699),
    "alto": (700, 900),
}

MERCHANT_REFERENCES = [
    "transferencia propia",
    "cuota prestamo",
    "pago tarjeta principal",
    "fondo de emergencia",
    "cuenta familiar",
    "cuenta negocios",
    "ahorro personal",
    "pago planificado",
]

USUAL_HOUR_RANGES = {
    "mañana": (6, 11),
    "tarde": (12, 17),
    "noche": (18, 22),
}

DIRTY_LABELS = ["dirty", "duplicate", "null_issue", "invalid_format"]



def seeded_everything(seed: int = SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)


def weighted_choice(options: List[str], weights: List[float]) -> str:
    return random.choices(options, weights=weights, k=1)[0]


def make_customer_id(i: int) -> str:
    return f"CUST{i:05d}"


def make_transaction_id(i: int) -> str:
    return f"TX{i:09d}"


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def assign_tx_count(segment: str) -> int:
    if segment == "moderate":
        return random.randint(20, 40)
    if segment == "high_flow":
        return random.randint(120, 150)
    # regular centered near 71
    count = int(round(np.random.normal(71, 8)))
    return max(55, min(90, count))


def income_to_base_amount(monthly_income: float, segment: str) -> float:
    segment_multiplier = {
        "moderate": 0.045,
        "regular": 0.060,
        "high_flow": 0.080,
    }[segment]
    base = monthly_income * segment_multiplier
    return max(350.0, base)


def assign_risk(monthly_income: float, employment_type: str, segment: str, tx_count: int) -> Tuple[str, int]:
    score = 380
    if monthly_income < 20_000:
        score += 170
    elif monthly_income < 40_000:
        score += 80

    if employment_type in {"informal", "desempleado"}:
        score += 130
    elif employment_type == "independiente":
        score += 70

    if segment == "high_flow":
        score += 90
    elif segment == "moderate":
        score += 20

    if tx_count > 135:
        score += 40

    score = int(clamp(score + random.randint(-50, 50), 250, 900))

    if score >= 700:
        return "alto", score
    if score >= 500:
        return "medio", score
    return "bajo", score


def generate_customer_profiles(total_customers: int = TOTAL_CUSTOMERS) -> pd.DataFrame:
    profiles: List[Dict] = []
    customer_idx = 1

    for segment, count in CUSTOMER_SEGMENT_COUNTS.items():
        for _ in range(count):
            occ = random.choice(OCCUPATION_PROFILES)
            monthly_income = round(random.uniform(*occ["income_range"]), 2)
            income_frequency = random.choice(occ["income_frequency"])
            base_tx_count = assign_tx_count(segment)

            # Usual product influenced by occupation profile
            usual_product_type = weighted_choice(PRODUCT_TYPES, occ["product_weights"])
            usual_channel = weighted_choice(CHANNELS, [0.45, 0.20, 0.10, 0.10, 0.15])
            usual_hour = random.choice(list(USUAL_HOUR_RANGES.keys()))
            avg_amount = round(income_to_base_amount(monthly_income, segment) * random.uniform(0.7, 1.4), 2)

            risk_profile, risk_score = assign_risk(
                monthly_income=monthly_income,
                employment_type=occ["employment_type"],
                segment=segment,
                tx_count=base_tx_count,
            )

            fraud_susceptibility = clamp(
                (
                    (0.50 if risk_profile == "alto" else 0.30 if risk_profile == "medio" else 0.15)
                    + (0.10 if occ["employment_type"] in {"informal", "desempleado"} else 0.0)
                    + (0.08 if segment == "high_flow" else 0.0)
                ),
                0.05,
                0.90,
            )

            profiles.append(
                {
                    "customer_id": make_customer_id(customer_idx),
                    "customer_segment": segment,
                    "occupation": occ["occupation"],
                    "industry": occ["industry"],
                    "employment_type": occ["employment_type"],
                    "monthly_income": monthly_income,
                    "income_frequency": income_frequency,
                    "customer_tenure_months": random.randint(3, 120),
                    "avg_3m_transaction_count": base_tx_count,
                    "avg_3m_transaction_amount": avg_amount,
                    "usual_transaction_hour_range": usual_hour,
                    "usual_product_type": usual_product_type,
                    "usual_channel": usual_channel,
                    "risk_profile": risk_profile,
                    "risk_score": risk_score,
                    "fraud_susceptibility": round(fraud_susceptibility, 3),
                }
            )
            customer_idx += 1

    profiles_df = pd.DataFrame(profiles)
    if len(profiles_df) != total_customers:
        raise ValueError(f"Expected {total_customers} customers, generated {len(profiles_df)}")
    return profiles_df


def allocate_customer_transaction_counts(customers_df: pd.DataFrame, target_total: int = VALID_RECORDS) -> np.ndarray:
    counts = customers_df["avg_3m_transaction_count"].to_numpy(dtype=int).copy()
    diff = int(target_total - counts.sum())

    idx_regular = customers_df.index[customers_df["customer_segment"] == "regular"].to_numpy()
    idx_high = customers_df.index[customers_df["customer_segment"] == "high_flow"].to_numpy()
    idx_mod = customers_df.index[customers_df["customer_segment"] == "moderate"].to_numpy()

    # Adjust up/down while respecting segment limits
    while diff != 0:
        if diff > 0:
            if len(idx_regular) > 0:
                i = int(random.choice(idx_regular))
                if counts[i] < 90:
                    counts[i] += 1
                    diff -= 1
                    continue
            if len(idx_mod) > 0:
                i = int(random.choice(idx_mod))
                if counts[i] < 40:
                    counts[i] += 1
                    diff -= 1
                    continue
            i = int(random.choice(idx_high))
            if counts[i] < 150:
                counts[i] += 1
                diff -= 1
        else:
            if len(idx_regular) > 0:
                i = int(random.choice(idx_regular))
                if counts[i] > 55:
                    counts[i] -= 1
                    diff += 1
                    continue
            if len(idx_mod) > 0:
                i = int(random.choice(idx_mod))
                if counts[i] > 20:
                    counts[i] -= 1
                    diff += 1
                    continue
            i = int(random.choice(idx_high))
            if counts[i] > 120:
                counts[i] -= 1
                diff += 1

    return counts


def get_datetime_from_range(start_date: datetime, end_date: datetime, hour_range_label: str) -> datetime:
    hour_lo, hour_hi = USUAL_HOUR_RANGES[hour_range_label]
    total_days = (end_date.date() - start_date.date()).days
    rand_day = random.randint(0, total_days)
    date_part = start_date + timedelta(days=rand_day)
    hour = random.randint(hour_lo, hour_hi)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return datetime(date_part.year, date_part.month, date_part.day, hour, minute, second)


def choose_status(is_fraud: bool) -> str:
    if is_fraud:
        return weighted_choice(TRANSACTION_STATUS, [0.76, 0.10, 0.09, 0.05])
    return weighted_choice(TRANSACTION_STATUS, [0.90, 0.04, 0.03, 0.03])


def choose_direction(product_type: str) -> str:
    # Simplified financial movement rules
    if product_type in {"pago de prestamo", "pago de tarjeta", "ahorro"}:
        return "salida"
    return weighted_choice(TRANSACTION_DIRECTIONS, [0.35, 0.65])


def choose_product(customer_row: pd.Series, is_fraud: bool) -> str:
    normal_weights = [0.15, 0.15, 0.15, 0.55]
    # boost usual product
    product_to_ix = {p: i for i, p in enumerate(PRODUCT_TYPES)}
    normal_weights[product_to_ix[customer_row["usual_product_type"]]] += 0.25
    if customer_row["occupation"] in {"pensionado", "docente"}:
        normal_weights[0] += 0.05
        normal_weights[1] += 0.05
    if is_fraud:
        # Fraud more likely to be transfers or unexpected card payments
        fraud_weights = [0.10, 0.08, 0.22, 0.60]
        fraud_weights[product_to_ix[customer_row["usual_product_type"]]] -= 0.10
        fraud_weights = [max(0.01, x) for x in fraud_weights]
        return weighted_choice(PRODUCT_TYPES, fraud_weights)
    return weighted_choice(PRODUCT_TYPES, normal_weights)


def generate_valid_transactions(customers_df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    start_dt = datetime.fromisoformat(start_date)
    end_dt = datetime.fromisoformat(end_date)

    tx_counts = allocate_customer_transaction_counts(customers_df, VALID_RECORDS)
    customers_df = customers_df.copy()
    customers_df["assigned_tx_count"] = tx_counts

    fraud_weights = customers_df["fraud_susceptibility"].to_numpy()
    fraud_weight_sum = fraud_weights.sum()
    fraud_weights = fraud_weights / fraud_weight_sum

    fraud_target = int(VALID_RECORDS * VALID_FRAUD_RATIO)
    regular_target = VALID_RECORDS - fraud_target

    fraud_alloc = np.random.multinomial(fraud_target, fraud_weights)
    regular_alloc = tx_counts - fraud_alloc

    # Ensure no negative values after fraud allocation
    over_idx = np.where(regular_alloc < 0)[0]
    for i in over_idx:
        fraud_alloc[i] = tx_counts[i]
        regular_alloc[i] = 0

    # Rebalance exact fraud target if needed
    current_fraud = int(fraud_alloc.sum())
    diff = fraud_target - current_fraud
    while diff != 0:
        if diff > 0:
            cand = np.where(fraud_alloc < tx_counts)[0]
            i = int(np.random.choice(cand))
            fraud_alloc[i] += 1
            regular_alloc[i] -= 1
            diff -= 1
        else:
            cand = np.where(fraud_alloc > 0)[0]
            i = int(np.random.choice(cand))
            fraud_alloc[i] -= 1
            regular_alloc[i] += 1
            diff += 1

    rows: List[Dict] = []
    tx_id = 1

    for idx, customer in customers_df.iterrows():
        total_regular = int(regular_alloc[idx])
        total_fraud = int(fraud_alloc[idx])

        def build_row(is_fraud: bool) -> Dict:
            product_type = choose_product(customer, is_fraud=is_fraud)

            if is_fraud:
                dt = get_datetime_from_range(start_dt, end_dt, random.choice(list(USUAL_HOUR_RANGES.keys())))
                channel = weighted_choice(CHANNELS, [0.20, 0.35, 0.05, 0.05, 0.35])
                amount = round(
                    max(
                        customer["avg_3m_transaction_amount"] * random.uniform(3.0, 12.0),
                        customer["monthly_income"] * random.uniform(0.60, 2.20),
                    ),
                    2,
                )
                anomaly_flag = 1
            else:
                dt = get_datetime_from_range(start_dt, end_dt, customer["usual_transaction_hour_range"])
                channel = weighted_choice(CHANNELS, [0.55 if c == customer["usual_channel"] else 0.1125 for c in CHANNELS])
                amount = round(
                    max(
                        50.0,
                        np.random.normal(
                            loc=customer["avg_3m_transaction_amount"],
                            scale=max(120.0, customer["avg_3m_transaction_amount"] * 0.35),
                        ),
                    ),
                    2,
                )
                # Keep within plausible economic behavior
                amount = round(min(amount, max(customer["monthly_income"] * 0.75, customer["avg_3m_transaction_amount"] * 2.2)), 2)
                anomaly_flag = 0

            deviation_pct = round(
                ((amount - customer["avg_3m_transaction_amount"]) / max(customer["avg_3m_transaction_amount"], 1.0)) * 100.0,
                2,
            )

            merchant_ref = random.choice(MERCHANT_REFERENCES)
            source_type = weighted_choice(ACCOUNT_TYPES, [0.35, 0.25, 0.10, 0.30])
            destination_type = weighted_choice(ACCOUNT_TYPES, [0.35, 0.20, 0.15, 0.30])
            status = choose_status(is_fraud=is_fraud)

            risk_profile = customer["risk_profile"]
            risk_score = int(customer["risk_score"])
            if is_fraud:
                if risk_profile == "bajo":
                    risk_profile = "medio"
                    risk_score = min(900, risk_score + random.randint(80, 140))
                elif risk_profile == "medio":
                    risk_profile = "alto"
                    risk_score = min(900, risk_score + random.randint(70, 120))
                else:
                    risk_score = min(900, risk_score + random.randint(20, 90))

            return {
                "transaction_id": make_transaction_id(tx_id),
                "customer_id": customer["customer_id"],
                "transaction_datetime": dt,
                "transaction_date": dt.date(),
                "transaction_time": dt.time().strftime("%H:%M:%S"),
                "product_type": product_type,
                "transaction_amount": amount,
                "transaction_direction": choose_direction(product_type),
                "channel": channel,
                "transaction_status": status,
                "merchant_or_destination": merchant_ref,
                "source_account_type": source_type,
                "destination_account_type": destination_type,
                "customer_segment": customer["customer_segment"],
                "occupation": customer["occupation"],
                "industry": customer["industry"],
                "employment_type": customer["employment_type"],
                "monthly_income": round(float(customer["monthly_income"]), 2),
                "income_frequency": customer["income_frequency"],
                "customer_tenure_months": int(customer["customer_tenure_months"]),
                "avg_3m_transaction_amount": round(float(customer["avg_3m_transaction_amount"]), 2),
                "avg_3m_transaction_count": int(customer["assigned_tx_count"]),
                "usual_transaction_hour_range": customer["usual_transaction_hour_range"],
                "usual_product_type": customer["usual_product_type"],
                "usual_channel": customer["usual_channel"],
                "deviation_from_usual_amount_pct": deviation_pct,
                "anomaly_flag": anomaly_flag,
                "risk_profile": risk_profile,
                "risk_score": int(risk_score),
                "fraud_label": 1 if is_fraud else 0,
                "data_quality_flag": "valid",
            }

        for _ in range(total_regular):
            row = build_row(is_fraud=False)
            rows.append(row)
            tx_id += 1

        for _ in range(total_fraud):
            row = build_row(is_fraud=True)
            rows.append(row)
            tx_id += 1

    df = pd.DataFrame(rows)
    # Shuffle valid rows
    df = df.sample(frac=1.0, random_state=SEED).reset_index(drop=True)

    # Rebuild transaction ids after shuffle so they stay unique and simple
    df["transaction_id"] = [make_transaction_id(i + 1) for i in range(len(df))]

    if len(df) != VALID_RECORDS:
        raise ValueError(f"Expected {VALID_RECORDS} valid records, got {len(df)}")

    return df



def introduce_dirty_patterns(base_valid_df: pd.DataFrame, dirty_records: int = DIRTY_RECORDS) -> pd.DataFrame:
    sampled = base_valid_df.sample(n=dirty_records, replace=True, random_state=SEED + 7).copy()
    records = sampled.to_dict("records")

    n_null = int(dirty_records * 0.35)
    n_dup = int(dirty_records * 0.20)
    n_business = int(dirty_records * 0.20)
    n_format = int(dirty_records * 0.15)
    n_invalid = dirty_records - n_null - n_dup - n_business - n_format

    # 1) Null issues
    for i in range(n_null):
        row = dict(records[i])
        cols = random.sample(
            [
                "customer_id", "transaction_datetime", "transaction_date", "product_type",
                "transaction_amount", "occupation", "monthly_income", "risk_profile"
            ],
            k=random.randint(1, 3)
        )
        for c in cols:
            row[c] = None
        row["data_quality_flag"] = "null_issue"
        records[i] = row

    # 2) Duplicates
    for i in range(n_null, n_null + n_dup):
        source_ix = random.randint(0, max(0, n_null - 1))
        row = dict(records[source_ix])
        row["data_quality_flag"] = "duplicate"
        records[i] = row

    # 3) Business incoherence
    for i in range(n_null + n_dup, n_null + n_dup + n_business):
        row = dict(records[i])
        pattern = random.choice(["huge_amount", "negative_amount", "wrong_risk", "impossible_count"])
        if pattern == "huge_amount":
            row["transaction_amount"] = round(random.uniform(500_000, 5_000_000), 2)
            row["monthly_income"] = round(random.uniform(0, 20_000), 2)
        elif pattern == "negative_amount":
            row["transaction_amount"] = round(random.uniform(-50_000, -50), 2)
        elif pattern == "wrong_risk":
            row["risk_profile"] = random.choice(["super alto", "999", "none", "???"])
        elif pattern == "impossible_count":
            row["avg_3m_transaction_count"] = random.choice([0, 1, 999, 1500])
            row["customer_segment"] = random.choice(["moderate", "regular", "high_flow"])
        row["anomaly_flag"] = 1
        row["data_quality_flag"] = "dirty"
        records[i] = row

    # 4) Invalid formats
    for i in range(n_null + n_dup + n_business, n_null + n_dup + n_business + n_format):
        row = dict(records[i])
        pattern = random.choice(["bad_date", "bad_amount", "bad_id", "bad_time"])
        if pattern == "bad_date":
            row["transaction_datetime"] = random.choice(["2025/99/88 99:99:99", "no_date", "13-2025-40"])
            row["transaction_date"] = random.choice(["2099-15-77", "1900-00-00", "bad_date"])
        elif pattern == "bad_amount":
            row["transaction_amount"] = random.choice(["abc", "mil", "??", "12,34,56"])
        elif pattern == "bad_id":
            row["transaction_id"] = random.choice(["", "TX###", "123", None])
            row["customer_id"] = random.choice(["CUST?", "UNKNOWN", "", None])
        elif pattern == "bad_time":
            row["transaction_time"] = random.choice(["25:61:99", "99:99", "badtime"])
        row["data_quality_flag"] = "invalid_format"
        records[i] = row

    # 5) Invalid categories / coherence issues
    start = n_null + n_dup + n_business + n_format
    for i in range(start, dirty_records):
        row = dict(records[i])
        row["product_type"] = random.choice(["unknown_product", "crypto_mars", "xxx", "ahoro", "saving"])
        row["channel"] = random.choice(["???", "mobile_phone", "desk", " ", None])
        row["transaction_status"] = random.choice(["done", "ok", "null", "missing_status"])
        row["risk_profile"] = random.choice(["HIGH", "none", "super high++", "999"])
        row["data_quality_flag"] = random.choice(DIRTY_LABELS)
        records[i] = row

    # Intentionally leave duplicated transaction IDs on some rows
    valid_ids = base_valid_df["transaction_id"].tolist()
    for i in random.sample(range(dirty_records), k=min(5_000, dirty_records)):
        records[i]["transaction_id"] = random.choice(valid_ids)

    return pd.DataFrame.from_records(records)


def build_final_dataset(start_date: str, end_date: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    seeded_everything(SEED)
    customers_df = generate_customer_profiles(TOTAL_CUSTOMERS)
    valid_df = generate_valid_transactions(customers_df, start_date=start_date, end_date=end_date)
    dirty_df = introduce_dirty_patterns(valid_df, DIRTY_RECORDS)
    final_df = pd.concat([valid_df, dirty_df], ignore_index=True)
    final_df = final_df.sample(frac=1.0, random_state=SEED + 11).reset_index(drop=True)
    return customers_df, valid_df, final_df


def save_outputs(output_dir: Path, customers_df: pd.DataFrame, valid_df: pd.DataFrame, final_df: pd.DataFrame) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    customers_df.to_csv(output_dir / "customers_profile.csv", index=False)
    valid_df.to_csv(output_dir / "transactions_valid_only.csv", index=False)
    final_df.to_csv(output_dir / "transactions_full_with_dirty_records.csv", index=False)

    summary = {
        "customers": int(len(customers_df)),
        "valid_records": int(len(valid_df)),
        "final_records": int(len(final_df)),
        "fraud_count_valid_only": int(valid_df["fraud_label"].sum()),
        "regular_count_valid_only": int((valid_df["fraud_label"] == 0).sum()),
        "dirty_count_in_final": int((final_df["data_quality_flag"] != "valid").sum()),
        "segment_distribution_customers": customers_df["customer_segment"].value_counts().to_dict(),
        "risk_distribution_customers": customers_df["risk_profile"].value_counts().to_dict(),
    }
    pd.Series(summary).to_json(output_dir / "dataset_summary.json", force_ascii=False, indent=2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a synthetic financial transactions dataset.")
    parser.add_argument("--start-date", type=str, default="2025-01-01", help="Start date in YYYY-MM-DD format")
    parser.add_argument("--end-date", type=str, default="2025-03-31", help="End date in YYYY-MM-DD format")
    parser.add_argument("--output-dir", type=str, default="output_financial_dataset", help="Directory to save outputs")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    customers_df, valid_df, final_df = build_final_dataset(args.start_date, args.end_date)
    save_outputs(Path(args.output_dir), customers_df, valid_df, final_df)

    print("Dataset generation completed successfully.")
    print(f"Customers: {len(customers_df):,}")
    print(f"Valid transactions: {len(valid_df):,}")
    print(f"Final transactions (with dirty records): {len(final_df):,}")
    print(f"Fraud transactions in valid set: {valid_df['fraud_label'].sum():,}")
    print(f"Dirty records in final set: {(final_df['data_quality_flag'] != 'valid').sum():,}")
    print(f"Output directory: {Path(args.output_dir).resolve()}")


if __name__ == "__main__":
    main()
