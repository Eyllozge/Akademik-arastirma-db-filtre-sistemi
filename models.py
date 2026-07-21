from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class articles(Base):
    __tablename__ = "articles"

    art_id = Column(Integer, primary_key=True)
    article_name = Column(String, nullable=False)
    upload_date = Column(Date)


class members(Base):
    __tablename__ = "members"

    mem_id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)


class authors(Base):
    __tablename__ = "authors"

    auth_id = Column(Integer, primary_key=True)
    uye_id = Column(Integer, ForeignKey("members.mem_id"), nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    institution_id = Column(Integer, ForeignKey("institutions.inst_id"))
    
class institutions(Base):
    __tablename__ = "institutions"

    inst_id = Column(Integer, primary_key=True)
    inst_name = Column(String, nullable=False)

class middle(Base):
    __tablename__ = "middle"
    
    mid_id = Column(Integer, primary_key=True)
    art_id = Column(Integer, ForeignKey("articles.art_id"), nullable=False)
    auth_id = Column(Integer, ForeignKey("authors.auth_id"), nullable=False)
    
    
class search_history(Base):
    __tablename__ = "search_history"

    search_id = Column(Integer, primary_key=True)
    mem_id = Column(Integer, ForeignKey("members.mem_id"), nullable=False)
    search_date = Column(Date, nullable=False)
    search_name = Column(String, nullable=False)
    
class saved_searches(Base):
    __tablename__ = "saved_searches"

    saveds_id = Column(Integer, primary_key=True)
    mem_id = Column(Integer, ForeignKey("members.mem_id"), nullable=False)
    search_name = Column(String, nullable=False)
    saved_date = Column(Date, nullable=False)
    
class citations(Base):
    __tablename__ = "citations"

    cit_id = Column(Integer, primary_key=True)
    art_id = Column(Integer, ForeignKey("articles.art_id"), nullable=False)
    other_art_id = Column(Integer, ForeignKey("articles.art_id"), nullable=False)