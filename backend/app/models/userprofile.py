from sqlalchemy import Column, Integer, String, Date
from app.db import get_db, Base
from sqlalchemy.orm import Session 

class User(Base):
    __tablename__ = "userprofiles"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)

    # profile details
    full_name_kh = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    email = Column(String, nullable=True)
    position = Column(String, nullable=True)
    skills = Column(String, nullable=True)
    department = Column(String, nullable=True)
    profile = Column(String, nullable=True)
    address_line = Column(String, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)
    marital_status = Column(String, nullable=True)
    emergency_contact_name = Column(String, nullable=True)
    emergency_contact_phone = Column(String, nullable=True)
    aba_bank_account = Column(String, nullable=True)
    id_card = Column(String, nullable=True)
    nssf_card = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
