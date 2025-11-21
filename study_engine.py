import sqlite3
from datetime import date, timedelta, datetime
from db_manager import get_connection
import pandas as pd

def generate_schedule(project_id, start_date, days_to_generate=7):
    """
    Ports the logic from PCD_GERA_PROGRAMACAO.
    Generates schedule for X days starting from start_date.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    current_date = start_date
    
    # Get Project Info (including user)
    proj = cursor.execute("SELECT * FROM EST_PROJETO WHERE CODIGO = ?", (project_id,)).fetchone()
    if not proj:
        return "Projeto não encontrado"
    
    user_id = proj['COD_USUARIO']
        
    # Get Default Cycle and Grade FOR THIS USER
    # Try to find default first
    ciclo = cursor.execute(
        "SELECT CODIGO FROM EST_CICLO WHERE PADRAO = 'S' AND COD_USUARIO = ?", 
        (user_id,)
    ).fetchone()
    
    if not ciclo:
        # Fallback: Check if user has ONLY ONE cycle
        all_ciclos = cursor.execute("SELECT CODIGO FROM EST_CICLO WHERE COD_USUARIO = ?", (user_id,)).fetchall()
        if len(all_ciclos) == 1:
            ciclo = all_ciclos[0]
            
    grade = cursor.execute(
        "SELECT CODIGO FROM EST_GRADE_SEMANAL WHERE PADRAO = 'S' AND COD_USUARIO = ?", 
        (user_id,)
    ).fetchone()
    
    if not grade:
        # Fallback: Check if user has ONLY ONE grade
        all_grades = cursor.execute("SELECT CODIGO FROM EST_GRADE_SEMANAL WHERE COD_USUARIO = ?", (user_id,)).fetchall()
        if len(all_grades) == 1:
            grade = all_grades[0]
    
    if not ciclo or not grade:
        missing = []
        if not ciclo:
            missing.append("Ciclo de Estudos Padrão")
        if not grade:
            missing.append("Grade Semanal Padrão")
            
        msg = "⚠️ Configuração incompleta:\n"
        msg += f"Você precisa definir um { ' e uma '.join(missing) }.\n"
        msg += "Vá em 'Cadastros', crie o registro e marque a opção 'Padrão'.\n"
        msg += "(Ou se tiver apenas um registro, o sistema usará ele automaticamente)"
        return msg
        
    cod_ciclo = ciclo['CODIGO']
    cod_grade = grade['CODIGO']

    # --- Load Cycle Items in Order ---
    cycle_items = cursor.execute("""
        SELECT * FROM EST_CICLO_ITEM 
        WHERE COD_CICLO = ? 
        ORDER BY INDICE
    """, (cod_ciclo,)).fetchall()
    
    if not cycle_items:
        return "Ciclo sem itens cadastrados"
        
    # --- Determine Starting Point in Cycle ---
    # Check the very last scheduled item for this project to know where to continue from
    last_scheduled = cursor.execute("""
        SELECT COD_CICLO_ITEM FROM EST_PROGRAMACAO 
        WHERE COD_PROJETO = ? AND TIPO = 4 -- TIPO 4 = ESTUDO CICLO
        ORDER BY DATA DESC, CODIGO DESC LIMIT 1
    """, (project_id,)).fetchone()
    
    current_item_idx = 0
    if last_scheduled and last_scheduled['COD_CICLO_ITEM']:
        # Find index of last item
        for i, item in enumerate(cycle_items):
            if item['CODIGO'] == last_scheduled['COD_CICLO_ITEM']:
                current_item_idx = (i + 1) % len(cycle_items) # Move to next, wrap around
                break

    for _ in range(days_to_generate):
        # 1. Determine Study Day
        last_prog = cursor.execute("""
            SELECT MAX(DIA) as LAST_DIA FROM EST_PROGRAMACAO 
            WHERE COD_PROJETO = ?
        """, (project_id,)).fetchone()
        
        dia_estudo = (last_prog['LAST_DIA'] if last_prog['LAST_DIA'] else 0) + 1
        
        # 2. Check Revisions (24h, 7d, 30d)
        # Revisão 24 horas (10 minutos por hora estudada)
        rev_24 = cursor.execute("""
            SELECT SUM(HL_REALIZADA) as TOTAL FROM EST_ESTUDOS 
            WHERE COD_PROJETO = ? AND DIA = ? AND TIPO > 3
        """, (project_id, dia_estudo - 1)).fetchone()
        
        hl_revisao_24 = rev_24['TOTAL'] if rev_24['TOTAL'] else 0
        minutos_revisao_24h = hl_revisao_24 * 10
        
        # Revisão 7 dias (5 minutos por hora estudada)
        rev_7d = cursor.execute("""
            SELECT SUM(HL_REALIZADA) as TOTAL FROM EST_ESTUDOS 
            WHERE COD_PROJETO = ? AND DIA = ? AND TIPO > 3
        """, (project_id, dia_estudo - 7)).fetchone()
        
        hl_revisao_7d = rev_7d['TOTAL'] if rev_7d['TOTAL'] else 0
        minutos_revisao_7d = hl_revisao_7d * 5
        
        # Revisão 30 dias (3 minutos por hora estudada)
        rev_30d = cursor.execute("""
            SELECT SUM(HL_REALIZADA) as TOTAL FROM EST_ESTUDOS 
            WHERE COD_PROJETO = ? AND DIA = ? AND TIPO > 3
        """, (project_id, dia_estudo - 30)).fetchone()
        
        hl_revisao_30d = rev_30d['TOTAL'] if rev_30d['TOTAL'] else 0
        minutos_revisao_30d = hl_revisao_30d * 3
        
        # 3. Get Available Time for Today
        weekday = current_date.isoweekday() 
        db_weekday = weekday + 1 if weekday < 7 else 1
        
        slots = cursor.execute("""
            SELECT * FROM EST_GRADE_ITEM 
            WHERE COD_GRADE = ? AND DIA_SEMANA = ?
            ORDER BY HORA_INICIAL
        """, (cod_grade, db_weekday)).fetchall()
        
        for slot in slots:
            # Calculate duration from Start/End times
            try:
                fmt = "%H:%M:%S"
                # Handle cases where time might be just "HH:MM"
                h_ini = slot['HORA_INICIAL'] if len(slot['HORA_INICIAL']) >= 5 else slot['HORA_INICIAL'] + ":00"
                h_fim = slot['HORA_FINAL'] if len(slot['HORA_FINAL']) >= 5 else slot['HORA_FINAL'] + ":00"
                
                t_start = datetime.strptime(h_ini, fmt)
                t_end = datetime.strptime(h_fim, fmt)
                
                # Calculate difference in minutes
                diff = t_end - t_start
                slot_duration = diff.total_seconds() / 60
                
                # Current Time Cursor for this slot
                current_slot_time = t_start
            except Exception as e:
                # Fallback to QTDE_MINUTOS if parsing fails
                slot_duration = slot['QTDE_MINUTOS']
                current_slot_time = datetime.strptime("00:00:00", "%H:%M:%S") # Should not happen ideally

            # Allocate Revisions in Priority Order: 24h → 7d → 30d → Cycle
            
            # 1. Revisão 24h
            if minutos_revisao_24h > 0 and slot_duration >= 5:
                alloc_rev = min(minutos_revisao_24h, slot_duration)
                
                cursor.execute("""
                    INSERT INTO EST_PROGRAMACAO (COD_GRADE, COD_PROJETO, COD_CICLO, DATA, DIA, DESC_AULA, TIPO, HL_PREVISTA, STATUS, HR_INICIAL_PREVISTA)
                    VALUES (?, ?, ?, ?, ?, 'REVISÃO 24H', 1, ?, 'PENDENTE', ?)
                """, (cod_grade, project_id, cod_ciclo, current_date.isoformat(), dia_estudo, alloc_rev/60, current_slot_time.strftime("%H:%M:%S")))
                
                minutos_revisao_24h -= alloc_rev
                slot_duration -= alloc_rev
                current_slot_time += timedelta(minutes=alloc_rev)
            
            # 2. Revisão 7 dias
            if minutos_revisao_7d > 0 and slot_duration >= 5:
                alloc_rev = min(minutos_revisao_7d, slot_duration)
                
                cursor.execute("""
                    INSERT INTO EST_PROGRAMACAO (COD_GRADE, COD_PROJETO, COD_CICLO, DATA, DIA, DESC_AULA, TIPO, HL_PREVISTA, STATUS, HR_INICIAL_PREVISTA)
                    VALUES (?, ?, ?, ?, ?, 'REVISÃO 7 DIAS', 2, ?, 'PENDENTE', ?)
                """, (cod_grade, project_id, cod_ciclo, current_date.isoformat(), dia_estudo, alloc_rev/60, current_slot_time.strftime("%H:%M:%S")))
                
                minutos_revisao_7d -= alloc_rev
                slot_duration -= alloc_rev
                current_slot_time += timedelta(minutes=alloc_rev)
            
            # 3. Revisão 30 dias
            if minutos_revisao_30d > 0 and slot_duration >= 5:
                alloc_rev = min(minutos_revisao_30d, slot_duration)
                
                cursor.execute("""
                    INSERT INTO EST_PROGRAMACAO (COD_GRADE, COD_PROJETO, COD_CICLO, DATA, DIA, DESC_AULA, TIPO, HL_PREVISTA, STATUS, HR_INICIAL_PREVISTA)
                    VALUES (?, ?, ?, ?, ?, 'REVISÃO 30 DIAS', 3, ?, 'PENDENTE', ?)
                """, (cod_grade, project_id, cod_ciclo, current_date.isoformat(), dia_estudo, alloc_rev/60, current_slot_time.strftime("%H:%M:%S")))
                
                minutos_revisao_30d -= alloc_rev
                slot_duration -= alloc_rev
                current_slot_time += timedelta(minutes=alloc_rev)
                
            # Allocate Cycle Items
            while slot_duration >= 10: # Minimum 10 mins to schedule a block
                item = cycle_items[current_item_idx]
                item_duration = item['QTDE_MINUTOS'] if item['QTDE_MINUTOS'] else 60
                
                alloc_cycle = min(slot_duration, item_duration)
                
                cursor.execute("""
                    INSERT INTO EST_PROGRAMACAO (COD_GRADE, COD_PROJETO, COD_CICLO, COD_CICLO_ITEM, DATA, DIA, DESC_AULA, TIPO, HL_PREVISTA, STATUS, HR_INICIAL_PREVISTA)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 4, ?, 'PENDENTE', ?)
                """, (cod_grade, project_id, cod_ciclo, item['CODIGO'], current_date.isoformat(), dia_estudo, 
                      f"Estudar {item['MATERIA'] if 'MATERIA' in item else 'Item ' + str(item['CODIGO'])}", 
                      alloc_cycle/60, current_slot_time.strftime("%H:%M:%S")))
                
                slot_duration -= alloc_cycle
                current_slot_time += timedelta(minutes=alloc_cycle)
                
                # Advance Cycle
                current_item_idx = (current_item_idx + 1) % len(cycle_items)
        
        current_date += timedelta(days=1)

    conn.commit()
    conn.close()
    return "Programação Gerada com Sucesso"
