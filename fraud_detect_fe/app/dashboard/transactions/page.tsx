"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { fetchAllTransactions, type Transaction } from "@/lib/api"
import { Search, Filter, Download, RefreshCw, AlertTriangle, CheckCircle, XCircle } from "lucide-react"

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [filteredTransactions, setFilteredTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [riskFilter, setRiskFilter] = useState<string>("all")

  const loadTransactions = async () => {
    try {
      setLoading(true)
      const data = await fetchAllTransactions()
      setTransactions(data.transactions)
      setFilteredTransactions(data.transactions)
      setError(null)
    } catch (err) {
      setError('Failed to load transactions. Please check if the API server is running.')
      console.error('Error loading transactions:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadTransactions()
  }, [])

  useEffect(() => {
    let filtered = transactions

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(t =>
        t.location.toLowerCase().includes(searchQuery.toLowerCase()) ||
        t.transaction_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
        t._id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        t.sender_country.toLowerCase().includes(searchQuery.toLowerCase()) ||
        t.receiver_country.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    // Status filter
    if (statusFilter !== "all") {
      if (statusFilter === "fraud") {
        filtered = filtered.filter(t => t.is_fraud)
      } else if (statusFilter === "legitimate") {
        filtered = filtered.filter(t => !t.is_fraud)
      } else if (statusFilter === "reviewed") {
        filtered = filtered.filter(t => t.reviewed)
      } else if (statusFilter === "pending") {
        filtered = filtered.filter(t => !t.reviewed)
      }
    }

    // Risk filter
    if (riskFilter !== "all") {
      filtered = filtered.filter(t => t.risk_level.toLowerCase() === riskFilter.toLowerCase())
    }

    setFilteredTransactions(filtered)
  }, [searchQuery, statusFilter, riskFilter, transactions])

  const getRiskBadgeVariant = (risk: string) => {
    switch (risk.toLowerCase()) {
      case "high":
        return "destructive"
      case "medium":
        return "warning"
      case "low":
        return "success"
      default:
        return "secondary"
    }
  }

  const getActionBadgeVariant = (action: string) => {
    switch (action.toUpperCase()) {
      case "BLOCK":
        return "destructive"
      case "ALLOW":
        return "success"
      case "REVIEW":
        return "warning"
      default:
        return "secondary"
    }
  }

  const formatCurrency = (amount: number, currency: string = "USD") => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency === "Rwanda" ? "RWF" : currency,
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    } catch {
      return dateString
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-cyan-400 border-r-transparent mb-4" />
          <p className="text-gray-400">Loading transactions...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-6">
        <div className="flex items-start gap-3">
          <AlertTriangle className="h-6 w-6 text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-lg font-semibold text-red-400 mb-1">Connection Error</h3>
            <p className="text-sm text-gray-300">{error}</p>
            <p className="text-xs text-gray-400 mt-2">Make sure the API server is running on http://localhost:5000</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Transactions</h2>
          <p className="text-sm text-gray-400 mt-1">
            Showing {filteredTransactions.length} of {transactions.length} transactions
          </p>
        </div>
        <button
          onClick={loadTransactions}
          className="flex items-center gap-2 rounded-lg bg-cyan-500/10 px-4 py-2 text-sm font-medium text-cyan-400 hover:bg-cyan-500/20 transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="border-white/10 bg-[#0f1632]">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-400">Total</p>
                <p className="text-2xl font-bold text-white">{transactions.length}</p>
              </div>
              <div className="rounded-lg bg-cyan-500/10 p-2">
                <svg className="h-5 w-5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-white/10 bg-[#0f1632]">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-400">Fraudulent</p>
                <p className="text-2xl font-bold text-red-400">
                  {transactions.filter(t => t.is_fraud).length}
                </p>
              </div>
              <div className="rounded-lg bg-red-500/10 p-2">
                <XCircle className="h-5 w-5 text-red-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-white/10 bg-[#0f1632]">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-400">Legitimate</p>
                <p className="text-2xl font-bold text-green-400">
                  {transactions.filter(t => !t.is_fraud).length}
                </p>
              </div>
              <div className="rounded-lg bg-green-500/10 p-2">
                <CheckCircle className="h-5 w-5 text-green-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-white/10 bg-[#0f1632]">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-400">Under Review</p>
                <p className="text-2xl font-bold text-orange-400">
                  {transactions.filter(t => !t.reviewed).length}
                </p>
              </div>
              <div className="rounded-lg bg-orange-500/10 p-2">
                <AlertTriangle className="h-5 w-5 text-orange-400" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card className="border-white/10 bg-[#0f1632]">
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search by location, type, ID, country..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 bg-[#0a0e27] border-white/10 text-white placeholder:text-gray-500"
              />
            </div>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 rounded-lg bg-[#0a0e27] border border-white/10 text-white text-sm focus:outline-none focus:ring-2 focus:ring-cyan-400"
            >
              <option value="all">All Status</option>
              <option value="fraud">Fraudulent</option>
              <option value="legitimate">Legitimate</option>
              <option value="reviewed">Reviewed</option>
              <option value="pending">Pending Review</option>
            </select>

            {/* Risk Filter */}
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="px-4 py-2 rounded-lg bg-[#0a0e27] border border-white/10 text-white text-sm focus:outline-none focus:ring-2 focus:ring-cyan-400"
            >
              <option value="all">All Risk Levels</option>
              <option value="high">High Risk</option>
              <option value="medium">Medium Risk</option>
              <option value="low">Low Risk</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Transactions Table */}
      <Card className="border-white/10 bg-[#0f1632]">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-white">
            Transaction List
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg border border-white/10 overflow-hidden">
            <Table>
              <TableHeader className="bg-[#0a0e27]">
                <TableRow className="border-white/10 hover:bg-[#0a0e27]">
                  <TableHead className="text-gray-400 font-semibold">ID</TableHead>
                  <TableHead className="text-gray-400 font-semibold">Date</TableHead>
                  <TableHead className="text-gray-400 font-semibold">Type</TableHead>
                  <TableHead className="text-gray-400 font-semibold">Amount</TableHead>
                  <TableHead className="text-gray-400 font-semibold">Location</TableHead>
                  <TableHead className="text-gray-400 font-semibold">Route</TableHead>
                  <TableHead className="text-gray-400 font-semibold">Risk</TableHead>
                  <TableHead className="text-gray-400 font-semibold">Fraud Prob.</TableHead>
                  <TableHead className="text-gray-400 font-semibold">Status</TableHead>
                  <TableHead className="text-gray-400 font-semibold">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredTransactions.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={10} className="text-center py-8">
                      <div className="text-gray-400">
                        <Filter className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        <p>No transactions found</p>
                      </div>
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredTransactions.map((transaction) => (
                    <TableRow
                      key={transaction._id}
                      className="border-white/10 hover:bg-white/5"
                    >
                      <TableCell className="text-gray-300 font-mono text-xs">
                        {transaction._id.slice(-8)}
                      </TableCell>
                      <TableCell className="text-gray-300 text-xs whitespace-nowrap">
                        {formatDate(transaction.created_at)}
                      </TableCell>
                      <TableCell className="text-gray-300">
                        <span className="px-2 py-1 rounded-md bg-cyan-500/10 text-cyan-400 text-xs">
                          {transaction.transaction_type}
                        </span>
                      </TableCell>
                      <TableCell className="text-white font-semibold">
                        {formatCurrency(transaction.transaction_amount, transaction.sender_currency)}
                      </TableCell>
                      <TableCell className="text-gray-300">
                        <div className="flex items-center gap-1">
                          <svg className="h-3 w-3 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                          </svg>
                          <span className="text-xs">{transaction.location}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-gray-300 text-xs">
                        {transaction.sender_country} → {transaction.receiver_country}
                      </TableCell>
                      <TableCell>
                        <Badge variant={getRiskBadgeVariant(transaction.risk_level)}>
                          {transaction.risk_level}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-gray-300">
                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-[#0a0e27] rounded-full h-2 overflow-hidden">
                            <div
                              className={`h-full ${
                                transaction.fraud_probability > 70
                                  ? 'bg-red-400'
                                  : transaction.fraud_probability > 40
                                  ? 'bg-orange-400'
                                  : 'bg-green-400'
                              }`}
                              style={{ width: `${transaction.fraud_probability}%` }}
                            />
                          </div>
                          <span className="text-xs text-gray-400 w-10">
                            {transaction.fraud_probability.toFixed(0)}%
                          </span>
                        </div>
                      </TableCell>
                      <TableCell>
                        {transaction.is_fraud ? (
                          <Badge variant="destructive">Fraud</Badge>
                        ) : (
                          <Badge variant="success">Legitimate</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <Badge variant={getActionBadgeVariant(transaction.action_recommended)}>
                          {transaction.action_recommended}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
