import csv
from typing import List, Dict


def read_csv(path: str, columns: List[str] = None) -> List[Dict]:
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            if columns:
                filtered = {col: row[col] for col in columns if col in row}
                rows.append(filtered)
            else:
                rows.append(row)
        return rows

def add_row(path: str, row: Dict):
    with open(path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        writer.writerow(row)
    return {"status": "success", "row": row}


def compute_insight(rows: List[Dict], column: str, operation: str):
    values = [float(r[column]) for r in rows if r[column] != ""]
    if not values:
        return None
    if operation == "average":
        return sum(values)/len(values)
    if operation == "sum":
        return sum(values)
    if operation == "max":
        return max(values)
    if operation == "min":
        return min(values)
    if operation == "count":
        return len(values)
