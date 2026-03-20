import pandas as pd
import numpy as np

# ============================================================
# Paramètres généraux
# ============================================================
SEED = 42
TARGET_ROWS = 1200
OUTPUT_FILE = "production_data.csv"

rng = np.random.default_rng(SEED)

# ============================================================
# Schéma métier
# ============================================================
columns = [
    "Date",
    "Plant",
    "MachineID",
    "MachineType",
    "Shift",
    "Operator",
    "ProductionUnits",
    "DowntimeHours",
    "Defects",
    "MaintenanceEvent",
    "PlannedProduction",
    "UtilizationRate",
    "DefectRate",
    "PlantProductionCapacity",
    "MachineAge",
    "MachineAgeGroup",
    "YearMonth",
]

# ============================================================
# Référentiels usine / machines / opérateurs
# ============================================================
machine_info = {
    "M01": ("Plant A", "Cutting"),
    "M02": ("Plant A", "Cutting"),
    "M03": ("Plant A", "Assembly"),
    "M04": ("Plant A", "Packaging"),
    "M05": ("Plant A", "Packaging"),
    "M06": ("Plant B", "Cutting"),
    "M07": ("Plant B", "Assembly"),
    "M08": ("Plant B", "Assembly"),
    "M09": ("Plant B", "Packaging"),
    "M10": ("Plant B", "Packaging"),
    "M11": ("Plant C", "Cutting"),
    "M12": ("Plant C", "Cutting"),
    "M13": ("Plant C", "Assembly"),
    "M14": ("Plant C", "Assembly"),
    "M15": ("Plant C", "Packaging"),
}

machine_ids = list(machine_info.keys())

plant_capacity_map = {
    "Plant A": 6000,
    "Plant B": 4200,
    "Plant C": 3000,
}

machine_age_map = {
    "M01": 3,
    "M02": 4,
    "M03": 11,
    "M04": 5,
    "M05": 6,
    "M06": 7,
    "M07": 12,
    "M08": 4,
    "M09": 8,
    "M10": 6,
    "M11": 2,
    "M12": 9,
    "M13": 5,
    "M14": 3,
    "M15": 10,
}

# Plant A = plus gros site, Plant B = moyen, Plant C = plus petit
base_capacity = {
    "M01": 360, "M02": 345, "M03": 320, "M04": 375, "M05": 400,
    "M06": 315, "M07": 285, "M08": 295, "M09": 340, "M10": 355,
    "M11": 270, "M12": 255, "M13": 245, "M14": 235, "M15": 305,
}

# Facteur par shift : Morning > Afternoon > Night
shift_factor = {
    "Morning": 1.00,
    "Afternoon": 0.93,
    "Night": 0.86,
}

# Performance intrinsèque par shift
shift_perf = {
    "Morning": 0.985,
    "Afternoon": 0.970,
    "Night": 0.955,
}

# Base défauts par shift : Night un peu plus mauvais
shift_defect_base = {
    "Morning": 0.012,
    "Afternoon": 0.018,
    "Night": 0.026,
}

# Pools d'opérateurs réalistes et récurrents
operator_pools = {
    "Plant A": {
        "Morning": ["Liam", "Sofia", "Hugo"],
        "Afternoon": ["Mia", "Ethan", "Camille"],
        "Night": ["Noah", "Chloe", "Lucas"],
    },
    "Plant B": {
        "Morning": ["Ava", "Lucas", "Emma"],
        "Afternoon": ["Ella", "Mason", "Nathan"],
        "Night": ["James", "Harper", "Lina"],
    },
    "Plant C": {
        "Morning": ["Leo", "Zoe", "Nina"],
        "Afternoon": ["Owen", "Aria", "Mila"],
        "Night": ["Jack", "Mila", "Sami"],
    },
}

shifts_9 = [
    "Morning", "Morning", "Morning", "Morning",
    "Afternoon", "Afternoon", "Afternoon",
    "Night", "Night"
]

shifts_10 = [
    "Morning", "Morning", "Morning", "Morning",
    "Afternoon", "Afternoon", "Afternoon",
    "Night", "Night", "Night"
]

# ============================================================
# Fonctions utilitaires
# ============================================================
def month_output_factor(month: int) -> float:
    """
    Variation mois par mois :
    - Janvier un peu plus bas
    - Mars plus fort
    - Avril plus dégradé
    - Juin plus haut
    """
    factors = {
        1: 0.98,
        2: 1.00,
        3: 1.03,
        4: 0.95,
        5: 1.01,
        6: 1.05,
    }
    return factors[month]


def weekday_factor(weekday: int) -> float:
    """
    Petite variation selon le jour de semaine :
    lundi un peu plus lent, milieu de semaine meilleur.
    """
    factors = {
        0: 0.98,  # lundi
        1: 1.00,  # mardi
        2: 1.01,  # mercredi
        3: 1.00,  # jeudi
        4: 0.99,  # vendredi
    }
    return factors[weekday]


def seasonal_factor(day_index: int) -> float:
    """
    Variation naturelle douce dans le temps.
    """
    return 1 + 0.03 * np.sin(day_index / 9) + 0.015 * np.cos(day_index / 17)


def degraded_period_impact(date: pd.Timestamp, machine_id: str, plant: str, machine_type: str) -> dict:
    """
    Quelques périodes de performance dégradée.
    """
    impact = {
        "downtime_add": 0.0,
        "perf_penalty": 0.0,
        "defect_add": 0.0,
    }

    # Problèmes ciblés sur M03 et M07 (machines peu fiables)
    if pd.Timestamp("2025-02-17") <= date <= pd.Timestamp("2025-02-21") and machine_id == "M03":
        impact["downtime_add"] += 1.8
        impact["perf_penalty"] += 0.08
        impact["defect_add"] += 0.010

    if pd.Timestamp("2025-04-07") <= date <= pd.Timestamp("2025-04-18") and machine_id == "M07":
        impact["downtime_add"] += 2.1
        impact["perf_penalty"] += 0.10
        impact["defect_add"] += 0.012

    # Dégradation modérée sur une partie du packaging Plant A en avril
    if pd.Timestamp("2025-04-01") <= date <= pd.Timestamp("2025-04-10") and plant == "Plant A" and machine_type == "Packaging":
        impact["downtime_add"] += 0.6
        impact["perf_penalty"] += 0.03
        impact["defect_add"] += 0.004

    # Léger ralentissement saisonnier mi-avril sur Plant C
    if pd.Timestamp("2025-04-14") <= date <= pd.Timestamp("2025-04-24") and plant == "Plant C":
        impact["downtime_add"] += 0.4
        impact["perf_penalty"] += 0.02
        impact["defect_add"] += 0.003

    # Mini dégradation fin mai sur M07
    if pd.Timestamp("2025-05-19") <= date <= pd.Timestamp("2025-05-21") and machine_id == "M07":
        impact["downtime_add"] += 1.5
        impact["perf_penalty"] += 0.07
        impact["defect_add"] += 0.008

    return impact


def planned_production(machine_id: str, shift: str, date: pd.Timestamp, day_index: int) -> int:
    base = base_capacity[machine_id]
    value = (
        base
        * shift_factor[shift]
        * month_output_factor(date.month)
        * weekday_factor(date.weekday())
        * seasonal_factor(day_index)
    )
    value += rng.normal(0, 4)  # petite variation naturelle
    return max(120, int(round(value)))


# ============================================================
# Construction de la série temporelle sur 6 mois
# ============================================================
dates = pd.bdate_range("2025-01-01", "2025-06-30")  # jours ouvrés sur 6 mois

# Répartition exacte pour arriver à 1200 lignes
n_days = len(dates)
base_rows_per_day = TARGET_ROWS // n_days
extra_rows = TARGET_ROWS - (base_rows_per_day * n_days)

rows_per_day = np.full(n_days, base_rows_per_day, dtype=int)

# Répartit les jours à +1 ligne de façon régulière
for j in range(extra_rows):
    idx = int(j * n_days / extra_rows)
    rows_per_day[idx] += 1

assert rows_per_day.sum() == TARGET_ROWS

# Suivi des effets de maintenance : amélioration les jours suivants
recovery_days_left = {machine_id: 0 for machine_id in machine_ids}

# Dates de maintenance planifiée sur machines fragiles
scheduled_maintenance = {
    ("M03", pd.Timestamp("2025-02-20")),
    ("M03", pd.Timestamp("2025-04-15")),
    ("M07", pd.Timestamp("2025-04-16")),
    ("M07", pd.Timestamp("2025-05-21")),
}

# ============================================================
# Génération des lignes
# ============================================================
rows = []

for day_idx, date in enumerate(dates):
    day_row_count = rows_per_day[day_idx]

    # Rotation des machines pour couvrir les 15 machines sur toute la période
    start_idx = (day_idx * 4) % len(machine_ids)
    ordered_machines = machine_ids[start_idx:] + machine_ids[:start_idx]
    selected_machines = ordered_machines[:day_row_count]

    day_shifts = shifts_10 if day_row_count == 10 else shifts_9

    for slot_idx, machine_id in enumerate(selected_machines):
        plant, machine_type = machine_info[machine_id]
        shift = day_shifts[slot_idx]

        planned = planned_production(machine_id, shift, date, day_idx)

        # ----------------------------
        # Downtime
        # ----------------------------
        base_downtime_shift = {
            "Morning": 0.5,
            "Afternoon": 0.9,
            "Night": 1.2,
        }[shift]

        plant_downtime = {
            "Plant A": 0.00,
            "Plant B": 0.10,
            "Plant C": 0.18,
        }[plant]

        type_downtime = {
            "Cutting": 0.12,
            "Assembly": 0.18,
            "Packaging": 0.15,
        }[machine_type]

        reliability_downtime = 0.0
        if machine_id == "M03":
            reliability_downtime += 0.65
        if machine_id == "M07":
            reliability_downtime += 0.85

        degraded = degraded_period_impact(date, machine_id, plant, machine_type)

        recovery_bonus = 0.35 if recovery_days_left[machine_id] > 0 else 0.0

        downtime = (
            base_downtime_shift
            + plant_downtime
            + type_downtime
            + reliability_downtime
            + degraded["downtime_add"]
            - recovery_bonus
            + rng.normal(0, 0.20)
        )

        downtime = float(np.clip(downtime, 0.0, 6.0))
        downtime = round(downtime, 1)

        # ----------------------------
        # Maintenance
        # ----------------------------
        maintenance_event = "No"

        if (machine_id, date) in scheduled_maintenance:
            maintenance_event = "Yes"
            downtime = round(min(6.0, max(downtime, 2.5) + rng.uniform(0.2, 0.8)), 1)
            recovery_days_left[machine_id] = 4
        elif downtime >= 3.2 and rng.random() < 0.18:
            maintenance_event = "Yes"
            downtime = round(min(6.0, downtime + rng.uniform(0.2, 0.7)), 1)
            recovery_days_left[machine_id] = 3

        # ----------------------------
        # Utilisation
        # ----------------------------
        utilization = round(max(0.0, (8.0 - downtime) / 8.0), 4)

        # ----------------------------
        # Production réelle
        # ----------------------------
        perf = (
            shift_perf[shift]
            - degraded["perf_penalty"]
            + (0.018 if recovery_days_left[machine_id] > 0 else 0.0)
            + rng.normal(0, 0.012)
        )

        perf = float(np.clip(perf, 0.78, 1.02))

        production = int(round(planned * utilization * perf))
        production = max(60, min(production, planned))

        # ----------------------------
        # Défauts
        # ----------------------------
        defect_rate = (
            shift_defect_base[shift]
            + {"Plant A": 0.000, "Plant B": 0.002, "Plant C": 0.003}[plant]
            + (0.007 if machine_id == "M03" else 0.0)
            + (0.009 if machine_id == "M07" else 0.0)
            + max(0.0, downtime - 1.0) * 0.0022
            + degraded["defect_add"]
            - (0.003 if recovery_days_left[machine_id] > 0 else 0.0)
            + rng.normal(0, 0.0015)
        )

        defect_rate = float(np.clip(defect_rate, 0.005, 0.05))

        defects = int(round(production * defect_rate))
        defects = max(1, min(defects, max(1, int(production * 0.05))))

        # Recalcul cohérent du taux à partir des défauts réels
        final_defect_rate = round(defects / production, 4) if production > 0 else 0.0

        # ----------------------------
        # Opérateur
        # ----------------------------
        operator_list = operator_pools[plant][shift]
        operator = operator_list[(day_idx + slot_idx) % len(operator_list)]

        # ----------------------------
        # Ajout ligne
        # ----------------------------
        rows.append({
            "Date": date.strftime("%Y-%m-%d"),
            "Plant": plant,
            "MachineID": machine_id,
            "MachineType": machine_type,
            "Shift": shift,
            "Operator": operator,
            "ProductionUnits": production,
            "DowntimeHours": downtime,
            "Defects": defects,
            "MaintenanceEvent": maintenance_event,
            "PlannedProduction": planned,
            "UtilizationRate": utilization,
            "DefectRate": final_defect_rate,
        })

    # Décrément des jours de récupération après maintenance
    for machine_id in recovery_days_left:
        if recovery_days_left[machine_id] > 0:
            recovery_days_left[machine_id] -= 1

# ============================================================
# DataFrame final
# ============================================================
df = pd.DataFrame(rows, columns=columns)

df["PlantProductionCapacity"] = df["Plant"].map(plant_capacity_map)
df["MachineAge"] = df["MachineID"].map(machine_age_map)
df["MachineAgeGroup"] = pd.cut(
    df["MachineAge"],
    bins=[0, 4, 8, 20],
    labels=["New", "Mid-life", "Old"],
)

df["Date"] = pd.to_datetime(df["Date"])
df["DefectRate"] = df["Defects"] / df["ProductionUnits"]
df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

# Vérifications
assert len(df) == TARGET_ROWS, f"Le dataset doit contenir {TARGET_ROWS} lignes, trouvé : {len(df)}"
assert list(df.columns) == columns, "Le schéma des colonnes ne correspond pas"
assert df["DowntimeHours"].between(0, 6).all(), "DowntimeHours doit être entre 0 et 6"
assert ((df["Defects"] / df["ProductionUnits"]) <= 0.05 + 1e-9).all(), "Les défauts dépassent 5%"
assert set(df["MaintenanceEvent"].unique()).issubset({"Yes", "No"})

# Export CSV
df.to_csv(OUTPUT_FILE, index=False)

print(f"Fichier créé : {OUTPUT_FILE}")
print(f"Nombre de lignes : {len(df)}")
print(df.head(10).to_string(index=False))
