from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Union
from datetime import date, datetime


# ---------- Auth ----------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ManagerLite(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None


# ---------- Users ----------
class UserOut(BaseModel):
    id: int
    manager_id: Optional[int] = None
    manager: Optional[ManagerLite] = None
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role_id: Optional[int] = None
    is_active: bool
    profile_complete: bool

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    role_id: Optional[int] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    manager_id: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None


class ProfileUpdate(BaseModel):
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    address_line: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    skills: Optional[str] = None


# ---------- Extended User Profile ----------
class UserBase(BaseModel):
    full_name: str
    phone: str
    full_name_kh: Optional[str] = None
    gender: Optional[str] = None
    email: Optional[EmailStr] = None
    position: Optional[str] = None
    skills: Optional[str] = None
    department: Optional[str] = None
    profile: Optional[str] = None
    address_line: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    marital_status: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    aba_bank_account: Optional[str] = None
    id_card: Optional[str] = None
    nssf_card: Optional[str] = None
    date_of_birth: Optional[date] = None


class UserProfileCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Recruitment ----------
class RecruitmentCreate(BaseModel):
    name: str
    position: str
    project: str
    hiring_manager: str
    request_date: date
    start_date: date
    status: Optional[str] = "Pending"


class RecruitmentResponse(BaseModel):
    id: int
    name: str
    position: str
    project: str
    hiring_manager: str
    request_date: datetime
    start_date: datetime
    created_at: datetime


    class Config:
        from_attributes = True


# ---------- Projects / Contracts ----------
class ContractCreate(BaseModel):
    office_id: Optional[int] = None
    code: str
    name: str
    client_type: str  # "external" | "internal"
    status: str = "active"  # active | on_hold | to_be_liquidated | archived
    description: Optional[str] = None


class ContractUpdate(BaseModel):
    office_id: Optional[int] = None
    code: Optional[str] = None
    name: Optional[str] = None
    client_type: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None


# ---------- Finance ----------
class BudgetCreate(BaseModel):
    contract_id: int
    amount: float
    currency: str = "USD"
    approved: bool = False


class InvoiceCreate(BaseModel):
    contract_id: int
    amount: float
    currency: str = "USD"
    issued_date: date
    status: str = "draft"  # draft | sent | paid | overdue


# ---------- HR ----------
class LeaveCreate(BaseModel):
    start_date: date
    end_date: date
    leave_type: str
    reason: Optional[str] = None


class TimesheetCreate(BaseModel):
    contract_id: Optional[int] = None
    work_date: date
    hours_worked: float = Field(ge=0, le=24)
    description: Optional[str] = None

class TimesheetBase(BaseModel):
    user_id: int
    contract_id: int | None = None
    work_date: date
    hours_worked: float
    description: str | None = None
    status: str = "pending"

class TimesheetCreate(TimesheetBase):
    pass

class TimesheetUpdate(BaseModel):
    contract_id: int | None = None
    work_date: date | None = None
    hours_worked: float | None = None
    description: str | None = None
    status: str | None = None

class TimesheetOut(TimesheetBase):
    id: int

    class Config:
        from_attributes = True 


class TicketCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "normal"  # low | normal | high | urgent


# ---------- Clients ----------
class ClientCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


# ---------- Roles ----------
class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


# ---------- Messages ----------
class MessageCreate(BaseModel):
    content: str


# ---------- Files ----------
class FileOut(BaseModel):
    id: int
    original_name: str
    size_bytes: int
    content_type: Optional[str] = None
    uploaded_at: Optional[Union[date, str]] = None


# ---------- SCHEMA FOR LEAVE REQUESTS ----------
class LeaveRequestCreate(BaseModel):
    user_id: int
    start_date: date
    end_date: date
    leave_type: str
    reason: Optional[str] = None
    status: Optional[str] = "pending"
    approver_id: Optional[int] = None
    days: float

class LeaveRequestUpdate(BaseModel):
    user_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    leave_type: Optional[str] = None
    reason: Optional[str] = None
    status: Optional[str] = None
    approver_id: Optional[int] = None
    days: Optional[float] = None




class LeaveRequestResponse(BaseModel):
    id: int
    user_id: int
    start_date: date
    end_date: date
    leave_type: str
    reason: Optional[str] = None
    status: str
    approver_id: Optional[int] = None
    days: float
    created_at: datetime

    class Config:
        from_attributes = True

# ---------- SCHEMA FOR LEASE REQUESTS ----------
class LeaveRequestCreate(BaseModel):
    user_id: int
    start_date: date
    end_date: date
    leave_type: str
    reason: Optional[str] = None
    status: Optional[str] = "pending"
    approver_id: Optional[int] = None
    days: float

class LeaveRequestUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    leave_type: Optional[str] = None
    reason: Optional[str] = None
    status: Optional[str] = None
    approver_id: Optional[int] = None
    days: Optional[float] = None

class LeaveRequestResponse(BaseModel):
    id: int
    user_id: int
    start_date: date
    end_date: date
    leave_type: str
    reason: Optional[str]
    status: str
    approver_id: Optional[int]
    days: float
    class Config:
        from_attributes = True

class TicketBase(BaseModel):
    title: str
    description: str
    quantity: int
    deadline: date
    priority: Optional[str] = "normal"

class TicketCreate(TicketBase):
    pass

class TicketResponse(TicketBase):
    id: int
    boq: Optional[str] = None
    status: str

    class Config:
      from_attributes = True 
# -------------- Contact Directory---------------
class ContactCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    address: Optional[str] = None
class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    address: Optional[str] = None
class ContactDirectoryCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    office: Optional[str] = None


class ContactDirectoryResponse(BaseModel):
    id: int
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    office: Optional[str] = None

    class Config:
        from_attributes = True
class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    deadline: Optional[date] = None
    priority: Optional[str] = None
    boq: Optional[str] = None
    status: Optional[str] = None
class TicketResponse(TicketBase):
    id: int
    boq: Optional[str] = None
    status: str

    class Config:
      from_attributes = True
class CuterCreate(BaseModel):
    name: str
    description: str

class CuterResponse(CuterCreate):
    id: int

    class Config:
        orm_mode = True