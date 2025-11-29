import sqlite3
from db_manager import get_connection
import pandas as pd
from datetime import date

def test_ui_logic():
    project_id = 1
    conn = get_connection()
    
    # 1. Fetch Schedule (Simulating the main query in Planejamento.py)
    query = """
        SELECT DATA
        FROM EST_PROGRAMACAO
        WHERE COD_PROJETO = ?
        ORDER BY DATA
    """
    df = pd.read_sql_query(query, conn, params=(project_id,))
    
    if df.empty:
        print("No schedule found.")
        return

    dates = df['DATA'].unique()
    days_map = {0: 'Segunda', 1: 'Terça', 2: 'Quarta', 3: 'Quinta', 4: 'Sexta', 5: 'Sábado', 6: 'Domingo'}
    
    # 2. Calculate Study Day Indices (The Logic I Added)
    conn_timeline = get_connection()
    hist_dates = [row['DATA'] for row in conn_timeline.execute(
        "SELECT DISTINCT DATA FROM EST_ESTUDOS WHERE COD_PROJETO = ? AND TIPO > 0 ORDER BY DATA", 
        (project_id,)
    ).fetchall()]
    plan_dates = [row['DATA'] for row in conn_timeline.execute(
        "SELECT DISTINCT DATA FROM EST_PROGRAMACAO WHERE COD_PROJETO = ? AND TIPO > 0 ORDER BY DATA", 
        (project_id,)
    ).fetchall()]
    conn_timeline.close()
    
    all_study_dates = sorted(list(set(hist_dates + plan_dates)))
    study_day_map = {d: i+1 for i, d in enumerate(all_study_dates)}
    
    print(f"Total Unique Study Days found: {len(all_study_dates)}")
    print("-" * 40)
    
    # 3. Simulate Display Loop
    # Showing first 10 and some interesting dates
    count = 0
    for d in dates:
        try:
            dt_obj = pd.to_datetime(d)
            weekday = days_map[dt_obj.weekday()]
            
            day_num = study_day_map.get(d, "?")
            day_label = f" - Dia {day_num}" if day_num != "?" else ""
            
            formatted_date = f"{dt_obj.strftime('%d/%m/%Y')} - {weekday}{day_label}"
            
            print(f"📅 {formatted_date}")
            
            count += 1
        except Exception as e:
            print(f"Error processing {d}: {e}")

    conn.close()

if __name__ == "__main__":
    test_ui_logic()
