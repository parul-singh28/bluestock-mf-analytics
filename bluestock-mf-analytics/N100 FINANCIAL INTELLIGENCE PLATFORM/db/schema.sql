-- SQLite schema for Nifty100 Sprint 1
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS companies (
  company_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  sector_id TEXT,
  ticker TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS sectors (
  sector_id TEXT PRIMARY KEY,
  sector_name TEXT
);

CREATE TABLE IF NOT EXISTS profitandloss (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_id TEXT NOT NULL,
  year INTEGER NOT NULL,
  sales REAL,
  opm REAL,
  FOREIGN KEY(company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS balancesheet (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_id TEXT NOT NULL,
  year INTEGER NOT NULL,
  total_assets REAL,
  total_liabilities REAL,
  FOREIGN KEY(company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cashflow (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_id TEXT NOT NULL,
  year INTEGER NOT NULL,
  net_cash REAL,
  FOREIGN KEY(company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS analysis (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_id TEXT NOT NULL,
  year INTEGER,
  metric TEXT,
  value REAL,
  FOREIGN KEY(company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS documents (
  doc_id TEXT PRIMARY KEY,
  company_id TEXT,
  url TEXT,
  description TEXT,
  FOREIGN KEY(company_id) REFERENCES companies(company_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS prosandcons (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_id TEXT,
  note TEXT,
  FOREIGN KEY(company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS stock_prices (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_id TEXT,
  trade_date TEXT,
  close_price REAL,
  FOREIGN KEY(company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS financial_ratios (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_id TEXT,
  year INTEGER,
  ratio_name TEXT,
  ratio_value REAL,
  FOREIGN KEY(company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS peer_groups (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_id TEXT,
  peer_company_id TEXT,
  FOREIGN KEY(company_id) REFERENCES companies(company_id) ON DELETE CASCADE,
  FOREIGN KEY(peer_company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);
