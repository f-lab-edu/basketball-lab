from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker

from app.database import Base


class Report(Base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True, autoincrement=True)
    report = Column(String)

    team_results = relationship('TeamResult', back_populates='report', cascade='all, delete, delete-orphan')

class TeamResult(Base):
    __tablename__ = 'team_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(Integer, ForeignKey('reports.id'), nullable=False)
    team = Column(String)
    result = Column(String)

    report = relationship('Report', back_populates='team_results')
    player_stats = relationship('PlayerStat', back_populates='team_result', cascade='all, delete, delete-orphan')

class PlayerStat(Base):
    __tablename__ = 'player_stats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_result_id = Column(Integer, ForeignKey('team_results.id'), nullable=False)
    backnumber = Column(Integer)
    player = Column(String)
    offense_rebound = Column(Integer)
    defense_rebound = Column(Integer)
    total_rebound = Column(Integer)
    assist = Column(Integer)
    steal = Column(Integer)
    block = Column(Integer)
    score_1Q = Column(Integer)
    score_2Q = Column(Integer)
    score_3Q = Column(Integer)
    score_4Q = Column(Integer)
    score_OT = Column(Integer)
    score_Total = Column(Integer)

    team_result = relationship('TeamResult', back_populates='player_stats')
