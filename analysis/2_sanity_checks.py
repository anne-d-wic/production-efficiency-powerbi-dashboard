import pandas as pd

df = pd.read_csv("production_data.csv")


print(df.head())
print(df.describe())
print(df["Plant"].value_counts())
print(df["MachineID"].value_counts())

production_by_plant = (
    df.groupby("Plant")["ProductionUnits"]
    .sum()
    .reset_index()
)

print(production_by_plant)

downtime_by_machine = (
    df.groupby("MachineID")["DowntimeHours"]
    .sum()
    .reset_index()
    .sort_values(by="DowntimeHours", ascending=False)
)

print(downtime_by_machine.head())

print("Missing values by column:")
print(df.isnull().sum())

print("\nShift distribution:")
print(df["Shift"].value_counts())

print("\nProduction range:")
print(df["ProductionUnits"].describe())

print("\nDowntime range:")
print(df["DowntimeHours"].describe())

print("\nDefect rate range:")
print(df["DefectRate"].describe())

print("\nProduction by plant:")
print(df.groupby("Plant")["ProductionUnits"].mean())

print("\nDowntime by machine:")
print(
    df.groupby("MachineID")["DowntimeHours"]
    .mean()
    .sort_values(ascending=False)
    .head()
)

correlation = df["ProductionUnits"].corr(df["DowntimeHours"])
print("\nCorrelation production vs downtime:", correlation)

print("\nMachine age distribution:")
print(df["MachineAge"].describe())

print("\nPlant capacity:")
print(df.groupby("Plant")["PlantProductionCapacity"].first())
