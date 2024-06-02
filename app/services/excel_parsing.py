import io
import json
import pandas as pd
from sqlalchemy.orm import Session
from app.models.match import Report, TeamResult, PlayerStat
from fastapi import UploadFile

def parse_row(index: int, d: dict, db: Session, report_id=None, team_result_id=None):
    if index == 0:
        report_text = d['Unnamed: 17']
        new_report = Report(report=report_text)
        db.add(new_report)
        db.commit()
        db.refresh(new_report)
        print(new_report)
        return new_report.id
    
    elif index == 2:
        teamA = d['Unnamed: 3']
        result = d['Unnamed: 12']
        new_team_result = TeamResult(team=teamA, result=result, report_id=report_id)
        db.add(new_team_result)
        db.commit()
        db.refresh(new_team_result)
        print(new_team_result)
        return new_team_result.id
    
    elif index >= 6 and index <= 17:
        if type(d['Unnamed: 1']) == float: # "Unnamed: N": NaN
            return None    
        backnumber = d['Unnamed: 1']
        player = d['Unnamed: 2']
        offense_rebound = d['Unnamed: 3']
        defense_rebound = d['Unnamed: 4']
        total_rebound = d['Unnamed: 5']
        assist = d['Unnamed: 6']
        steal = d['Unnamed: 7']
        block = d['Unnamed: 8']
        score_1Q = d['Unnamed: 9']
        score_2Q = d['Unnamed: 10']
        score_3Q = d['Unnamed: 11']
        score_4Q = d['Unnamed: 12']
        score_OT = d['Unnamed: 13']
        score_Total = d['Unnamed: 14']
        new_player_stat = PlayerStat(
            team_result_id=team_result_id,
            backnumber=backnumber,
            player=player,
            offense_rebound=offense_rebound,
            defense_rebound=defense_rebound,
            total_rebound=total_rebound,
            assist=assist,
            steal=steal,
            block=block,
            score_1Q=score_1Q,
            score_2Q=score_2Q,
            score_3Q=score_3Q,
            score_4Q=score_4Q,
            score_OT=score_OT,
            score_Total=score_Total
        )
        db.add(new_player_stat)
        db.commit()
        db.refresh(new_player_stat)
        print(new_player_stat)

    elif index == 18: #teamA total score_chart
        pass
    
    elif index == 20:
        teamB = d['Unnamed: 3']
        result = d['Unnamed: 12']
        new_team_result = TeamResult(team=teamB, result=result, report_id=report_id)
        db.add(new_team_result)
        db.commit()
        db.refresh(new_team_result)
        print(new_team_result)
        return new_team_result.id

    elif index >= 24 and index <= 35:
        backnumber = d['Unnamed: 1']
        player = d['Unnamed: 2']
        offense_rebound = d['Unnamed: 3']
        defense_rebound = d['Unnamed: 4']
        total_rebound = d['Unnamed: 5']
        assist = d['Unnamed: 6']
        steal = d['Unnamed: 7']
        block = d['Unnamed: 8']
        score_1Q = d['Unnamed: 9']
        score_2Q = d['Unnamed: 10']
        score_3Q = d['Unnamed: 11']
        score_4Q = d['Unnamed: 12']
        score_OT = d['Unnamed: 13']
        score_Total = d['Unnamed: 14']
        new_player_stat = PlayerStat(
            team_result_id=team_result_id,
            backnumber=backnumber,
            player=player,
            offense_rebound=offense_rebound,
            defense_rebound=defense_rebound,
            total_rebound=total_rebound,
            assist=assist,
            steal=steal,
            block=block,
            score_1Q=score_1Q,
            score_2Q=score_2Q,
            score_3Q=score_3Q,
            score_4Q=score_4Q,
            score_OT=score_OT,
            score_Total=score_Total
        )
        db.add(new_player_stat)
        db.commit()
        db.refresh(new_player_stat)
        print(new_player_stat)

    else:
        return None

def parsing_excel_file(file: UploadFile, db: Session):
    content = file.file.read()
    df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
    data = df.to_dict(orient='records')
    report_id = None
    team_result_id = None

    for index,row in enumerate(data):
        if index == 0:
            report_id = parse_row(index, row, db)
        elif index == 2 or index == 20:
            team_result_id = parse_row(index, row, db, report_id=report_id)
        elif 6 <= index <= 17 or 24 <= index <= 35:
            parse_row(index, row, db, team_result_id=team_result_id)

    with open("log.txt", mode="w", encoding="utf-8") as data_file:
        json.dump(data, data_file, ensure_ascii=False, indent=4)

    return data
