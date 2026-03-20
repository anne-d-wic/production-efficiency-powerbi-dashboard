import pandas as pd

df = pd.read_csv("production_data.csv")

#convertions
df["Date"] = pd.to_datetime(df["Date"])
df["YearMonth"] = df["Date"].dt.to_period("M")
df["PlantProductionCapacity"] = df["Plant"].map({
    "Plant A": 6000,
    "Plant B": 4200,
    "Plant C": 3000
})
df["MachineAge"] = df["MachineID"].map({
    "M01": 3, "M02": 4, "M03": 11, "M04": 5, "M05": 6,
    "M06": 7, "M07": 12, "M08": 4, "M09": 8, "M10": 6,
    "M11": 2, "M12": 9, "M13": 5, "M14": 3, "M15": 10
})
df["MachineAgeGroup"] = pd.cut(
    df["MachineAge"],
    bins=[0, 4, 8, 20],
    labels=["New", "Mid-life", "Old"]
)
df["DefectRate"] = df["Defects"] / df["ProductionUnits"]

#KPI columns
df["ProductionEfficiency"] = df["ProductionUnits"] / df["PlannedProduction"]
df["DowntimeImpact"] = 1 - df["ProductionEfficiency"]
df["DowntimeImpactUnits"] = df["PlannedProduction"] - df["ProductionUnits"]

df.to_csv("production_data_enriched.csv", index=False)

#Aggregate production data by plant
production_by_plant = (
    df.groupby("Plant")
    .agg(
        TotalProduction=("ProductionUnits", "sum"),
        TotalDowntime=("DowntimeHours", "sum"),
        AvgDefectRate=("DefectRate", "mean"),
        AvgUtilization=("UtilizationRate", "mean"),
        AvgProductionEfficiency=("ProductionEfficiency", "mean"),
        TotalDowntimeImpactUnits=("DowntimeImpactUnits", "sum")
    )
    .reset_index()
)
print(production_by_plant)
production_by_plant.to_csv("production_by_plant.csv", index=False)

#Aggregate production data by machine
machine_performance = (
    df.groupby("MachineID")
    .agg(
        TotalProduction=("ProductionUnits", "sum"),
        TotalDowntime=("DowntimeHours", "sum"),
        AvgDefectRate=("DefectRate", "mean"),
        AvgProductionEfficiency=("ProductionEfficiency", "mean"),
        TotalDowntimeImpactUnits=("DowntimeImpactUnits", "sum"),
        MachineAge=("MachineAge", "first"),
        MachineType=("MachineType", "first")
    )
    .reset_index()
)
print(machine_performance.head())
machine_performance.to_csv("machine_performance.csv", index=False)

#Aggregate production data by month
production_by_month = (
    df.groupby("YearMonth")
    .agg(
        TotalProduction=("ProductionUnits", "sum"),
        TotalDowntime=("DowntimeHours", "sum"),
        AvgDefectRate=("DefectRate", "mean")
    )
    .reset_index()
)
print(production_by_month)
production_by_month.to_csv("production_by_month.csv", index=False)

#Aggregate production data by shift
shift_performance = (
    df.groupby("Shift")
    .agg(
        AvgProduction=("ProductionUnits", "mean"),
        AvgDowntime=("DowntimeHours", "mean"),
        AvgDefectRate=("DefectRate", "mean")
    )
    .reset_index()
)
print(shift_performance)
shift_performance.to_csv("shift_performance.csv", index=False)