from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from decimal import Decimal
from enum import Enum


# Enums for various statuses and types
class UserRole(str, Enum):
    ADMIN = "admin"
    ACCOUNTANT = "accountant"
    MANAGER = "manager"


class AccountType(str, Enum):
    ASSET = "asset"  # Aset
    LIABILITY = "liability"  # Liabilitas
    EQUITY = "equity"  # Ekuitas
    REVENUE = "revenue"  # Pendapatan
    EXPENSE = "expense"  # Pengeluaran


class TransactionType(str, Enum):
    GENERAL_JOURNAL = "general_journal"  # Jurnal Umum
    ADJUSTMENT_JOURNAL = "adjustment_journal"  # Jurnal Penyesuaian
    SALES = "sales"  # Penjualan
    PURCHASE = "purchase"  # Pembelian
    PAYMENT = "payment"  # Pembayaran
    RECEIPT = "receipt"  # Penerimaan


class InvoiceStatus(str, Enum):
    DRAFT = "draft"  # Konsep
    SENT = "sent"  # Terkirim
    PAID = "paid"  # Terbayar
    OVERDUE = "overdue"  # Jatuh Tempo
    CANCELLED = "cancelled"  # Dibatalkan


class AssetDepreciationMethod(str, Enum):
    STRAIGHT_LINE = "straight_line"  # Garis Lurus
    DECLINING_BALANCE = "declining_balance"  # Saldo Menurun
    UNITS_OF_PRODUCTION = "units_of_production"  # Unit Produksi


class TaxType(str, Enum):
    PPN = "ppn"  # Pajak Pertambahan Nilai
    PPH21 = "pph21"  # Pajak Penghasilan Pasal 21
    PPH23 = "pph23"  # Pajak Penghasilan Pasal 23
    PPH4_2 = "pph4_2"  # Pajak Penghasilan Pasal 4 ayat 2


class RecurrenceType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


# User Management
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, max_length=255)
    password_hash: str = Field(max_length=255)
    full_name: str = Field(max_length=100)
    role: UserRole = Field(default=UserRole.ACCOUNTANT)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    # Relationships
    transactions: List["Transaction"] = Relationship(back_populates="created_by_user")
    invoices: List["Invoice"] = Relationship(back_populates="created_by_user")


# Chart of Accounts - Bagan Akun
class Account(SQLModel, table=True):
    __tablename__ = "accounts"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, max_length=20)  # Kode Akun
    name: str = Field(max_length=200)  # Nama Akun
    account_type: AccountType
    parent_id: Optional[int] = Field(default=None, foreign_key="accounts.id")
    is_active: bool = Field(default=True)
    description: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    parent: Optional["Account"] = Relationship(
        back_populates="children", sa_relationship_kwargs={"remote_side": "Account.id"}
    )
    children: List["Account"] = Relationship(back_populates="parent")
    journal_entries: List["JournalEntry"] = Relationship(back_populates="account")


# Transaction Categories
class TransactionCategory(SQLModel, table=True):
    __tablename__ = "transaction_categories"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    transactions: List["Transaction"] = Relationship(back_populates="category")


# Financial Transactions
class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_number: str = Field(unique=True, max_length=50)
    transaction_date: date
    transaction_type: TransactionType
    description: str = Field(max_length=500)
    reference_number: Optional[str] = Field(default=None, max_length=50)
    category_id: Optional[int] = Field(default=None, foreign_key="transaction_categories.id")
    created_by: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    category: Optional[TransactionCategory] = Relationship(back_populates="transactions")
    created_by_user: User = Relationship(back_populates="transactions")
    journal_entries: List["JournalEntry"] = Relationship(back_populates="transaction")


# Journal Entries (Double Entry Bookkeeping)
class JournalEntry(SQLModel, table=True):
    __tablename__ = "journal_entries"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_id: int = Field(foreign_key="transactions.id")
    account_id: int = Field(foreign_key="accounts.id")
    debit_amount: Decimal = Field(default=Decimal("0"), decimal_places=2)
    credit_amount: Decimal = Field(default=Decimal("0"), decimal_places=2)
    description: Optional[str] = Field(default=None, max_length=200)

    # Relationships
    transaction: Transaction = Relationship(back_populates="journal_entries")
    account: Account = Relationship(back_populates="journal_entries")


# Customer Management
class Customer(SQLModel, table=True):
    __tablename__ = "customers"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=500)
    tax_id: Optional[str] = Field(default=None, max_length=50)  # NPWP
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    invoices: List["Invoice"] = Relationship(back_populates="customer")


# Invoice Management
class Invoice(SQLModel, table=True):
    __tablename__ = "invoices"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    invoice_number: str = Field(unique=True, max_length=50)
    customer_id: int = Field(foreign_key="customers.id")
    invoice_date: date
    due_date: date
    status: InvoiceStatus = Field(default=InvoiceStatus.DRAFT)
    subtotal: Decimal = Field(default=Decimal("0"), decimal_places=2)
    tax_amount: Decimal = Field(default=Decimal("0"), decimal_places=2)
    total_amount: Decimal = Field(default=Decimal("0"), decimal_places=2)
    paid_amount: Decimal = Field(default=Decimal("0"), decimal_places=2)
    notes: Optional[str] = Field(default=None, max_length=1000)
    created_by: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    customer: Customer = Relationship(back_populates="invoices")
    created_by_user: User = Relationship(back_populates="invoices")
    invoice_items: List["InvoiceItem"] = Relationship(back_populates="invoice")


# Invoice Items
class InvoiceItem(SQLModel, table=True):
    __tablename__ = "invoice_items"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    invoice_id: int = Field(foreign_key="invoices.id")
    product_name: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    quantity: Decimal = Field(decimal_places=2)
    unit_price: Decimal = Field(decimal_places=2)
    total_price: Decimal = Field(decimal_places=2)

    # Relationships
    invoice: Invoice = Relationship(back_populates="invoice_items")


# Fixed Assets Management
class FixedAsset(SQLModel, table=True):
    __tablename__ = "fixed_assets"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    purchase_date: date
    purchase_cost: Decimal = Field(decimal_places=2)
    useful_life_years: int  # Masa manfaat dalam tahun
    depreciation_method: AssetDepreciationMethod = Field(default=AssetDepreciationMethod.STRAIGHT_LINE)
    salvage_value: Decimal = Field(default=Decimal("0"), decimal_places=2)  # Nilai sisa
    accumulated_depreciation: Decimal = Field(default=Decimal("0"), decimal_places=2)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    depreciation_entries: List["DepreciationEntry"] = Relationship(back_populates="asset")


# Depreciation Entries
class DepreciationEntry(SQLModel, table=True):
    __tablename__ = "depreciation_entries"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    asset_id: int = Field(foreign_key="fixed_assets.id")
    period_date: date  # Bulan/tahun periode penyusutan
    depreciation_amount: Decimal = Field(decimal_places=2)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    asset: FixedAsset = Relationship(back_populates="depreciation_entries")


# Tax Configuration
class TaxRate(SQLModel, table=True):
    __tablename__ = "tax_rates"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    tax_type: TaxType
    rate: Decimal = Field(decimal_places=4)  # Tarif pajak dalam persen (misal: 0.1100 untuk 11%)
    effective_from: date
    effective_to: Optional[date] = None
    description: Optional[str] = Field(default=None, max_length=200)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Recurring Transactions
class RecurringTransaction(SQLModel, table=True):
    __tablename__ = "recurring_transactions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    recurrence_type: RecurrenceType
    start_date: date
    end_date: Optional[date] = None
    next_execution_date: date
    amount: Decimal = Field(decimal_places=2)
    account_debit_id: int = Field(foreign_key="accounts.id")
    account_credit_id: int = Field(foreign_key="accounts.id")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships - using string references to avoid circular imports
    debit_account: Account = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[RecurringTransaction.account_debit_id]",
            "primaryjoin": "RecurringTransaction.account_debit_id == Account.id",
        }
    )
    credit_account: Account = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[RecurringTransaction.account_credit_id]",
            "primaryjoin": "RecurringTransaction.account_credit_id == Account.id",
        }
    )


# Payment Tracking
class Payment(SQLModel, table=True):
    __tablename__ = "payments"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    invoice_id: Optional[int] = Field(default=None, foreign_key="invoices.id")
    payment_date: date
    amount: Decimal = Field(decimal_places=2)
    payment_method: str = Field(max_length=50)  # Transfer, Tunai, Cek, dll
    reference_number: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    invoice: Optional[Invoice] = Relationship()


# Accounts Receivable (Piutang)
class AccountsReceivable(SQLModel, table=True):
    __tablename__ = "accounts_receivable"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customers.id")
    invoice_id: Optional[int] = Field(default=None, foreign_key="invoices.id")
    amount: Decimal = Field(decimal_places=2)
    due_date: date
    description: str = Field(max_length=500)
    is_collected: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    customer: Customer = Relationship()
    invoice: Optional[Invoice] = Relationship()


# Accounts Payable (Utang)
class AccountsPayable(SQLModel, table=True):
    __tablename__ = "accounts_payable"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    vendor_name: str = Field(max_length=200)
    amount: Decimal = Field(decimal_places=2)
    due_date: date
    description: str = Field(max_length=500)
    is_paid: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Budget Planning
class Budget(SQLModel, table=True):
    __tablename__ = "budgets"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    account_id: int = Field(foreign_key="accounts.id")
    budget_year: int
    budget_month: Optional[int] = None  # Null untuk budget tahunan
    budgeted_amount: Decimal = Field(decimal_places=2)
    actual_amount: Decimal = Field(default=Decimal("0"), decimal_places=2)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    account: Account = Relationship()


# Company Settings
class CompanySettings(SQLModel, table=True):
    __tablename__ = "company_settings"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    company_name: str = Field(max_length=200)
    address: Optional[str] = Field(default=None, max_length=500)
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=255)
    tax_id: Optional[str] = Field(default=None, max_length=50)  # NPWP
    logo_url: Optional[str] = Field(default=None, max_length=500)
    fiscal_year_start_month: int = Field(default=1)  # Bulan mulai tahun fiskal (1-12)
    currency: str = Field(default="IDR", max_length=3)
    settings: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Audit Trail
class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    table_name: str = Field(max_length=100)
    record_id: int
    action: str = Field(max_length=20)  # CREATE, UPDATE, DELETE
    old_values: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    new_values: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship()


# Non-persistent schemas for validation and API


# User schemas
class UserCreate(SQLModel, table=False):
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=100)
    full_name: str = Field(max_length=100)
    role: UserRole = Field(default=UserRole.ACCOUNTANT)


class UserUpdate(SQLModel, table=False):
    email: Optional[str] = Field(default=None, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


# Account schemas
class AccountCreate(SQLModel, table=False):
    code: str = Field(max_length=20)
    name: str = Field(max_length=200)
    account_type: AccountType
    parent_id: Optional[int] = None
    description: Optional[str] = Field(default=None, max_length=500)


class AccountUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: Optional[bool] = None


# Transaction schemas
class TransactionCreate(SQLModel, table=False):
    transaction_date: date
    transaction_type: TransactionType
    description: str = Field(max_length=500)
    reference_number: Optional[str] = Field(default=None, max_length=50)
    category_id: Optional[int] = None


class JournalEntryCreate(SQLModel, table=False):
    account_id: int
    debit_amount: Decimal = Field(default=Decimal("0"), decimal_places=2)
    credit_amount: Decimal = Field(default=Decimal("0"), decimal_places=2)
    description: Optional[str] = Field(default=None, max_length=200)


# Invoice schemas
class InvoiceCreate(SQLModel, table=False):
    customer_id: int
    invoice_date: date
    due_date: date
    notes: Optional[str] = Field(default=None, max_length=1000)


class InvoiceItemCreate(SQLModel, table=False):
    product_name: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    quantity: Decimal = Field(decimal_places=2)
    unit_price: Decimal = Field(decimal_places=2)


# Customer schemas
class CustomerCreate(SQLModel, table=False):
    name: str = Field(max_length=200)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=500)
    tax_id: Optional[str] = Field(default=None, max_length=50)


class CustomerUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=200)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=500)
    tax_id: Optional[str] = Field(default=None, max_length=50)
    is_active: Optional[bool] = None


# Financial Report schemas (for API responses)
class BalanceSheetData(SQLModel, table=False):
    assets: Dict[str, Decimal]
    liabilities: Dict[str, Decimal]
    equity: Dict[str, Decimal]
    total_assets: Decimal
    total_liabilities_equity: Decimal
    report_date: date


class IncomeStatementData(SQLModel, table=False):
    revenues: Dict[str, Decimal]
    expenses: Dict[str, Decimal]
    total_revenue: Decimal
    total_expenses: Decimal
    net_income: Decimal
    period_start: date
    period_end: date


class CashFlowData(SQLModel, table=False):
    operating_activities: Dict[str, Decimal]
    investing_activities: Dict[str, Decimal]
    financing_activities: Dict[str, Decimal]
    net_cash_flow: Decimal
    period_start: date
    period_end: date
