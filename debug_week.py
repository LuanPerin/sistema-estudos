from datetime import date, timedelta

dt_today = date.today()
print(f"Hoje: {dt_today} ({dt_today.strftime('%A')})")

# Cálculo da semana (Domingo a Sábado como no código)
idx_weekday = (dt_today.weekday() + 1) % 7  # Mon=0 -> Sun=0
start_week = dt_today - timedelta(days=idx_weekday)
end_week = start_week + timedelta(days=6)

print(f"\nCálculo da semana:")
print(f"  idx_weekday: {idx_weekday}")
print(f"  Início da semana (Domingo): {start_week}")
print(f"  Fim da semana (Sábado): {end_week}")

print(f"\nDatas que estão no banco:")
print(f"  EST_ESTUDOS: 2025-11-19, 2025-11-20")
print(f"  EST_PROGRAMACAO: 2025-11-20, 2025-11-21, 2025-11-22, 2025-11-24, 2025-11-26")

print(f"\n2025-11-19 está entre {start_week} e {end_week}? {start_week <= date(2025,11,19) <= end_week}")
print(f"2025-11-20 está entre {start_week} e {end_week}? {start_week <= date(2025,11,20) <= end_week}")
