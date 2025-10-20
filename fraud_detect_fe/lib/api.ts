const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

export interface DashboardStats {
  cards: {
    total_transactions: {
      value: number;
      change: number;
      label: string;
    };
    fraud_detected: {
      value: number;
      change: number;
      label: string;
    };
    model_accuracy: {
      value: number;
      change: number;
      label: string;
    };
    false_positive_rate: {
      value: number;
      change: number;
      label: string;
    };
  };
  timestamp: string;
}

export interface TrendData {
  date: string;
  date_formatted: string;
  normal: number;
  fraudulent: number;
  under_review: number;
  total: number;
}

export interface Hotspot {
  location: string;
  coordinates: {
    lat: number;
    lng: number;
    name: string;
  };
  fraud_count: number;
  total_amount: number;
}

export interface Transaction {
  _id: string;
  account_balance: number;
  account_status: string;
  action_recommended: string;
  channel: string;
  confidence: number;
  created_at: string;
  customer_age: number;
  customer_occupation: string;
  fraud_probability: number;
  invalid_pin_retry_count: number;
  invalid_pin_retry_limits: number;
  invalid_pin_status: string;
  is_cross_border: boolean;
  is_fraud: boolean;
  location: string;
  login_attempts: number;
  previous_transaction_date: string;
  receiver_country: string;
  receiver_currency: string;
  review_notes: string | null;
  reviewed: boolean;
  risk_level: string;
  sender_country: string;
  sender_currency: string;
  transaction_amount: number;
  transaction_date: string;
  transaction_duration: number;
  transaction_type: string;
  updated_at: string;
}

export interface TransactionsResponse {
  success: boolean;
  count: number;
  transactions: Transaction[];
}

export interface RiskDistribution {
  distribution: {
    Low: {
      count: number;
      amount: number;
      percentage: number;
    };
    Medium: {
      count: number;
      amount: number;
      percentage: number;
    };
    High: {
      count: number;
      amount: number;
      percentage: number;
    };
  };
  total_transactions: number;
}

export interface TransactionType {
  type: string;
  total: number;
  fraud_count: number;
  fraud_percentage: number;
  total_amount: number;
}

export interface AlertsSummary {
  summary: {
    pending: number;
    investigating: number;
    resolved: number;
    false_positive: number;
  };
  total_alerts: number;
  recent_critical: any[];
}

export async function fetchDashboardStats(): Promise<DashboardStats> {
  const response = await fetch(`${API_BASE_URL}/api/stats/dashboard`);
  const data = await response.json();
  if (!data.success) throw new Error('Failed to fetch dashboard stats');
  return data.data;
}

export async function fetchTrends(days: number = 7): Promise<TrendData[]> {
  const response = await fetch(`${API_BASE_URL}/api/stats/trends?days=${days}`);
  const data = await response.json();
  if (!data.success) throw new Error('Failed to fetch trends');
  return data.data.trends;
}

export async function fetchHotspots(): Promise<Hotspot[]> {
  const response = await fetch(`${API_BASE_URL}/api/stats/hotspots`);
  const data = await response.json();
  if (!data.success) throw new Error('Failed to fetch hotspots');
  return data.data.hotspots;
}

export async function fetchAllTransactions(): Promise<TransactionsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/transactions/all`);
  const data = await response.json();
  if (!data.success) throw new Error('Failed to fetch transactions');
  return data;
}

export async function fetchRiskDistribution(): Promise<RiskDistribution> {
  const response = await fetch(`${API_BASE_URL}/api/stats/risk-distribution`);
  const data = await response.json();
  if (!data.success) throw new Error('Failed to fetch risk distribution');
  return data.data;
}

export async function fetchTransactionTypes(): Promise<TransactionType[]> {
  const response = await fetch(`${API_BASE_URL}/api/stats/transaction-types`);
  const data = await response.json();
  if (!data.success) throw new Error('Failed to fetch transaction types');
  return data.data.transaction_types;
}

export async function fetchAlertsSummary(): Promise<AlertsSummary> {
  const response = await fetch(`${API_BASE_URL}/api/stats/alerts/summary`);
  const data = await response.json();
  if (!data.success) throw new Error('Failed to fetch alerts summary');
  return data.data;
}

export async function fetchRecentTransactions(limit: number = 10): Promise<Transaction[]> {
  const response = await fetch(`${API_BASE_URL}/api/stats/recent-transactions?limit=${limit}`);
  const data = await response.json();
  if (!data.success) throw new Error('Failed to fetch recent transactions');
  return data.data.transactions;
}
