from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Column, Integer, String, DateTime, Date, Text, Boolean, ForeignKey
from sqlalchemy import Date, Enum
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, date
from sqlalchemy.ext.declarative import declarative_base
from ..db import Base
import enum


Base = declarative_base() 

class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str | None] = mapped_column(String(255))


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    manager_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    username: Mapped[str | None] = mapped_column(String(100), unique=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    profile_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    role_id: Mapped[int | None] = mapped_column(ForeignKey("roles.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    full_name_kh: Mapped[str | None] = mapped_column(String(255))
    gender: Mapped[str | None] = mapped_column(String(10))
    position: Mapped[str | None] = mapped_column(String(100))
    skills: Mapped[str | None] = mapped_column(String(255))
    department: Mapped[str | None] = mapped_column(String(100))
    profile: Mapped[str | None] = mapped_column(String(255))
    address_line: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(100))
    country: Mapped[str | None] = mapped_column(String(100))
    marital_status: Mapped[str | None] = mapped_column(String(50))
    emergency_contact_name: Mapped[str | None] = mapped_column(String(255))
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(20))
    aba_bank_account: Mapped[str | None] = mapped_column(String(50))
    id_card: Mapped[str | None] = mapped_column(String(50))
    nssf_card: Mapped[str | None] = mapped_column(String(50))
    date_of_birth: Mapped[date | None] = mapped_column(Date)


    
class LeaveRequest(Base):
    __tablename__ = "leave_requests_staff"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    start_date: Mapped[date]
    end_date: Mapped[date]
    leave_type: Mapped[str] = mapped_column(String(50))
    reason: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    approver_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    days: Mapped[float]
     
class UserProfile(Base):
    __tablename__ = "user_profiles"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    emergency_contact_name: Mapped[str | None] = mapped_column(String(255))
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(50))
    address_line: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(255))
    country: Mapped[str | None] = mapped_column(String(255))
    skills: Mapped[str | None] = mapped_column(Text)


class Office(Base):
    __tablename__ = "offices"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)


class Contract(Base):
    __tablename__ = "contracts"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    office_id: Mapped[int] = mapped_column(ForeignKey("offices.id"))
    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    client_type: Mapped[str] = mapped_column(String(20), default="external")
    status: Mapped[str] = mapped_column(String(30), default="active")
    created_by: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    scope_of_work: Mapped[str | None] = mapped_column(Text)
    brief: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class UserFavorite(Base):
    __tablename__ = "user_favorites"
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    contract_id: Mapped[int] = mapped_column(
        ForeignKey("contracts.id", ondelete="CASCADE"), primary_key=True
    )


class ContractAccess(Base):
    __tablename__ = "contract_access"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contract_id: Mapped[int] = mapped_column(
        ForeignKey("contracts.id", ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(50), default="member")


class ContractClientToken(Base):
    __tablename__ = "contract_client_tokens"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contract_id: Mapped[int] = mapped_column(
        ForeignKey("contracts.id", ondelete="CASCADE")
    )
    token: Mapped[str] = mapped_column(String(64), unique=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


# class LeaveRequest(Base):
#     __tablename__ = "leave_requests"
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
#     start_date: Mapped[date]
#     end_date: Mapped[date]
#     leave_type: Mapped[str] = mapped_column(String(50))
#     reason: Mapped[str | None] = mapped_column(Text)
#     status: Mapped[str] = mapped_column(String(20), default="pending")
#     approver_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
#     days: Mapped[float]


class Timesheet(Base):
    __tablename__ = "timesheets"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    contract_id: Mapped[int | None]
    work_date: Mapped[date]
    hours_worked: Mapped[float]
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="pending")

class TimesheetStaff(Base):
    __tablename__= "timesheet_staff"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id",ondelete="CASCADE"))
    contract_id: Mapped[int | None]
    work_date: Mapped[date]
    hours_worked: Mapped[float]
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="pending")


class Budget(Base):
    __tablename__ = "budgets"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contract_id: Mapped[int]
    amount: Mapped[float]
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class Invoice(Base):
    __tablename__ = "invoices"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contract_id: Mapped[int]
    amount: Mapped[float]
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    issued_date: Mapped[date]
    status: Mapped[str] = mapped_column(String(20), default="draft")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class QAChecklist(Base):
    __tablename__ = "qa_checklists"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contract_id: Mapped[int]
    title: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(10), default="open")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class SafetyReport(Base):
    __tablename__ = "safety_reports"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contract_id: Mapped[int]
    report_date: Mapped[date]
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class EnvironmentReport(Base):
    __tablename__ = "environment_reports"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contract_id: Mapped[int]
    report_date: Mapped[date]
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class HelpdeskTicket(Base):
    __tablename__ = "helpdesk_tickets"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_by: Mapped[int]
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(10), default="normal")
    status: Mapped[str] = mapped_column(String(20), default="open")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class Client(Base):
    __tablename__ = "clients"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(100))


class FileShare(Base):
    __tablename__ = "file_shares"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int]
    original_name: Mapped[str] = mapped_column(String(255))
    stored_name: Mapped[str] = mapped_column(String(255))
    stored_path: Mapped[str] = mapped_column(String(1000))
    size_bytes: Mapped[int]
    mime_type: Mapped[str | None] = mapped_column(String(100))
    token: Mapped[str] = mapped_column(String(255))
    downloads: Mapped[int] = mapped_column(default=0)
    last_download_at: Mapped[datetime | None]


class FileDownloadLog(Base):
    __tablename__ = "file_download_logs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_id: Mapped[int]
    ip_address: Mapped[str | None] = mapped_column(String(45))
    downloaded_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class LibraryCategory(Base):
    __tablename__ = "library_categories"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(255))


class LibraryItem(Base):
    __tablename__ = "library_items"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int | None]
    title: Mapped[str] = mapped_column(String(255))
    path: Mapped[str] = mapped_column(String(1000))
    uploaded_by: Mapped[int | None]


class ProjectMessage(Base):
    __tablename__ = "project_messages"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("contracts.id", ondelete="CASCADE")
    )
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class ProjectFile(Base):
    __tablename__ = "project_files"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contract_id: Mapped[int] = mapped_column(
        ForeignKey("contracts.id", ondelete="CASCADE")
    )
    original_name: Mapped[str] = mapped_column(String(255))
    stored_path: Mapped[str] = mapped_column(String(500))
    content_type: Mapped[str | None] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(default=0)
    folder: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    uploaded_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)


class Holiday(Base):
    __tablename__ = "holidays"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), default="Holiday")
    country: Mapped[str | None] = mapped_column(String(2))


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="todo")
    order_index: Mapped[int] = mapped_column(default=0)
    color: Mapped[str | None] = mapped_column(String(16))
    deadline: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
)
class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    quantity = Column(Integer, nullable=False)
    deadline = Column(Date, nullable=False)
    boq = Column(String(255), nullable=True)
    status = Column(String(50), default="Pending")
    priority = Column(String(50), default="normal")




class TicketStatus(enum.Enum):
    Pending = "Pending"
    Approved = "Approved"
    Rejected = "Rejected"

class TicketRequest(Base):
    __tablename__ = "tickets_request"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    deadline: Mapped[date] = mapped_column(Date, nullable=False)
    boq: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Store file path
    status: Mapped[TicketStatus] = mapped_column(Enum(TicketStatus), default=TicketStatus.Pending, nullable=False)
    priority: Mapped[str] = mapped_column(String(50), default="normal")

class TestTable(Base):
    __tablename__ = "test_table"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

class ContactDirectory(Base):
    __tablename__ = "contact_directory"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    position: Mapped[str] = mapped_column(String(100), nullable=True)  # ✅ add this
    department: Mapped[str] = mapped_column(String(100), nullable=True)
    office: Mapped[str] = mapped_column(String(100), nullable=True)

class Cute(Base):
    __tablename__ = "cutes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

class TestMore(Base):
    __tablename__ = "test_more"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)