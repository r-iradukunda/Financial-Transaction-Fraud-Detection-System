"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, TrendingDown, Download, FileText, Calendar } from "lucide-react"
import { 
  fetchDashboardStats, 
  fetchTrends, 
  fetchRiskDistribution,
  fetchTransactionTypes,
  fetchAlertsSummary,
  fetchRecentTransactions,
  type DashboardStats, 
  type TrendData,
  type RiskDistribution,
  type TransactionType,
  type AlertsSummary,
  type Transaction
} from "@/lib/api"

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [trends, setTrends] = useState<TrendData[]>([])
  const [riskDistribution, setRiskDistribution] = useState<RiskDistribution | null>(null)
  const [transactionTypes, setTransactionTypes] = useState<TransactionType[]>([])
  const [alertsSummary, setAlertsSummary] = useState<AlertsSummary | null>(null)
  const [recentTransactions, setRecentTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [generatingReport, setGeneratingReport] = useState(false)

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true)
        const [statsData, trendsData, riskData, typesData, alertsData, recentData] = await Promise.all([
          fetchDashboardStats(),
          fetchTrends(7),
          fetchRiskDistribution(),
          fetchTransactionTypes(),
          fetchAlertsSummary(),
          fetchRecentTransactions(5)
        ])
        setStats(statsData)
        setTrends(trendsData)
        setRiskDistribution(riskData)
        setTransactionTypes(typesData)
        setAlertsSummary(alertsData)
        setRecentTransactions(recentData)
        setError(null)
      } catch (err) {
        setError('Failed to load dashboard data. Please check if the API server is running.')
        console.error('Error loading dashboard data:', err)
      } finally {
        setLoading(false)
      }
    }

    loadData()
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [])

  const generateReport = () => {
    if (!stats || !riskDistribution || !alertsSummary) return

    setGeneratingReport(true)

    const reportData = {
      reportMetadata: {
        generatedAt: new Date().toISOString(),
        reportDate: new Date().toLocaleDateString('en-US', { 
          weekday: 'long', 
          year: 'numeric', 
          month: 'long', 
          day: 'numeric' 
        }),
        reportType: "Fraud Detection Dashboard Summary"
      },
      executiveSummary: {
        totalTransactions: stats.cards.total_transactions.value,
        fraudDetected: stats.cards.fraud_detected.value,
        fraudPercentage: ((stats.cards.fraud_detected.value / stats.cards.total_transactions.value) * 100).toFixed(2),
        totalAlerts: alertsSummary.total_alerts,
        pendingAlerts: alertsSummary.summary.pending,
      },
      riskAnalysis: {
        highRisk: {
          count: riskDistribution.distribution.High.count,
          amount: riskDistribution.distribution.High.amount,
          percentage: riskDistribution.distribution.High.percentage
        },
        mediumRisk: {
          count: riskDistribution.distribution.Medium.count,
          amount: riskDistribution.distribution.Medium.amount,
          percentage: riskDistribution.distribution.Medium.percentage
        },
        lowRisk: {
          count: riskDistribution.distribution.Low.count,
          amount: riskDistribution.distribution.Low.amount,
          percentage: riskDistribution.distribution.Low.percentage
        },
        totalTransactions: riskDistribution.total_transactions
      },
      transactionTypes: transactionTypes.map(type => ({
        type: type.type,
        total: type.total,
        fraudCount: type.fraud_count,
        fraudPercentage: type.fraud_percentage,
        totalAmount: type.total_amount
      })),
      weeklyTrends: trends.map(trend => ({
        date: trend.date,
        dateFormatted: trend.date_formatted,
        normal: trend.normal,
        fraudulent: trend.fraudulent,
        underReview: trend.under_review,
        total: trend.total
      })),
      alertsSummary: {
        pending: alertsSummary.summary.pending,
        investigating: alertsSummary.summary.investigating,
        resolved: alertsSummary.summary.resolved,
        falsePositive: alertsSummary.summary.false_positive,
        total: alertsSummary.total_alerts
      },
      recentTransactionsSample: recentTransactions.map(t => ({
        id: t._id,
        amount: t.transaction_amount,
        type: t.transaction_type,
        location: t.location,
        isFraud: t.is_fraud,
        riskLevel: t.risk_level,
        fraudProbability: t.fraud_probability,
        actionRecommended: t.action_recommended
      }))
    }

    // Create formatted JSON report
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `fraud-detection-report-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    setTimeout(() => setGeneratingReport(false), 1000)
  }

  
  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-cyan-400 border-r-transparent mb-4" />
          <p className="text-gray-400">Loading dashboard data...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-6">
        <div className="flex items-start gap-3">
          <svg className="h-6 w-6 text-red-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h3 className="text-lg font-semibold text-red-400 mb-1">Connection Error</h3>
            <p className="text-sm text-gray-300">{error}</p>
            <p className="text-xs text-gray-400 mt-2">Make sure the API server is running on http://localhost:5000</p>
          </div>
        </div>
      </div>
    )
  }

  const getChangeColor = (change: number) => change >= 0 ? 'text-green-400' : 'text-red-400'
  const getChangeIcon = (change: number) => change >= 0 ? TrendingUp : TrendingDown

  const chartWidth = 600
  const chartHeight = 280
  const maxValue = Math.max(...trends.map(t => t.total)) || 100
  const step = chartWidth / Math.max(trends.length - 1, 1)

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    } catch {
      return dateString
    }
  }

  return (
    <div className="space-y-6">
      {/* Header with Report Button */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-400">
          Real-time monitoring and prediction for Rwanda's financial ecosystem
        </p>
        <button
          onClick={generateReport}
          disabled={generatingReport}
          className="flex items-center gap-2 rounded-lg bg-cyan-500 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {generatingReport ? (
            <>
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-solid border-white border-r-transparent" />
              Generating...
            </>
          ) : (
            <>
              <Download className="h-4 w-4" />
              Generate Report
            </>
          )}
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {/* Total Transactions */}
        <Card className="border-white/10 bg-[#0f1632]">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">
              {stats?.cards.total_transactions.label}
            </CardTitle>
            <div className="rounded-lg bg-cyan-500/10 p-2">
              <svg className="h-5 w-5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
              </svg>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-white">
              {stats?.cards.total_transactions.value.toLocaleString()}
            </div>
            <p className={`flex items-center gap-1 text-xs ${getChangeColor(stats?.cards.total_transactions.change || 0)}`}>
              {(() => {
                const Icon = getChangeIcon(stats?.cards.total_transactions.change || 0)
                return <Icon className="h-3 w-3" />
              })()}
              <span>{Math.abs(stats?.cards.total_transactions.change || 0)}% vs yesterday</span>
            </p>
          </CardContent>
        </Card>

        {/* Fraud Detected */}
        <Card className="border-white/10 bg-[#0f1632]">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">
              {stats?.cards.fraud_detected.label}
            </CardTitle>
            <div className="rounded-lg bg-red-500/10 p-2">
              <svg className="h-5 w-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-white">
              {stats?.cards.fraud_detected.value.toLocaleString()}
            </div>
            <p className="text-xs text-gray-400">Real-time alerts</p>
          </CardContent>
        </Card>

        {/* Total Alerts */}
        <Card className="border-white/10 bg-[#0f1632]">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">
              Total Alerts
            </CardTitle>
            <div className="rounded-lg bg-orange-500/10 p-2">
              <svg className="h-5 w-5 text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-white">
              {alertsSummary?.total_alerts.toLocaleString() || 0}
            </div>
            <p className="text-xs text-orange-400">
              {alertsSummary?.summary.pending || 0} pending review
            </p>
          </CardContent>
        </Card>

        {/* High Risk Transactions */}
        <Card className="border-white/10 bg-[#0f1632]">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">
              High Risk Transactions
            </CardTitle>
            <div className="rounded-lg bg-purple-500/10 p-2">
              <svg className="h-5 w-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-white">
              {riskDistribution?.distribution.High.count.toLocaleString() || 0}
            </div>
            <p className="text-xs text-purple-400">
              {riskDistribution?.distribution.High.percentage.toFixed(1)}% of total
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Fraud Detection Trends */}
        <Card className="border-white/10 bg-[#0f1632]">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-white">
              Real-time Fraud Detection Trends
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              {trends.length > 0 ? (
                <div className="relative w-full h-full">
                  <svg className="w-full h-full" viewBox={`0 0 ${chartWidth} ${chartHeight}`}>
                    {[0, 1, 2, 3, 4].map((i) => (
                      <line key={i} x1="0" y1={i * (chartHeight / 4)} x2={chartWidth} y2={i * (chartHeight / 4)} stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
                    ))}
                    <path
                      d={trends.map((trend, i) => {
                        const x = i * step
                        const y = chartHeight - (trend.normal / maxValue) * chartHeight
                        return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
                      }).join(' ')}
                      fill="none" stroke="#22d3ee" strokeWidth="2"
                    />
                    <path
                      d={trends.map((trend, i) => {
                        const x = i * step
                        const y = chartHeight - (trend.fraudulent / maxValue) * chartHeight * 2
                        return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
                      }).join(' ')}
                      fill="none" stroke="#f87171" strokeWidth="2"
                    />
                    <path
                      d={trends.map((trend, i) => {
                        const x = i * step
                        const y = chartHeight - (trend.under_review / maxValue) * chartHeight * 1.5
                        return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
                      }).join(' ')}
                      fill="none" stroke="#fb923c" strokeWidth="2"
                    />
                    {trends.map((trend, i) => {
                      const x = i * step
                      const yNormal = chartHeight - (trend.normal / maxValue) * chartHeight
                      const yFraud = chartHeight - (trend.fraudulent / maxValue) * chartHeight * 2
                      const yReview = chartHeight - (trend.under_review / maxValue) * chartHeight * 1.5
                      return (
                        <g key={i}>
                          <circle cx={x} cy={yNormal} r="4" fill="#22d3ee" />
                          <circle cx={x} cy={yFraud} r="4" fill="#f87171" />
                          <circle cx={x} cy={yReview} r="4" fill="#fb923c" />
                        </g>
                      )
                    })}
                  </svg>
                  <div className="absolute top-0 right-0 flex gap-4 text-xs">
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full bg-cyan-400" />
                      <span className="text-gray-400">Normal</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full bg-red-400" />
                      <span className="text-gray-400">Fraudulent</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full bg-orange-400" />
                      <span className="text-gray-400">Under Review</span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center h-full">
                  <p className="text-gray-400">No trend data available</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Risk Distribution */}
        <Card className="border-white/10 bg-[#0f1632]">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-white">
              Risk Level Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80 flex flex-col justify-center space-y-6">
              {riskDistribution && (
                <>
                  {/* High Risk */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-400">High Risk</span>
                      <span className="text-white font-semibold">
                        {riskDistribution.distribution.High.count} ({riskDistribution.distribution.High.percentage.toFixed(1)}%)
                      </span>
                    </div>
                    <div className="relative h-8 bg-[#0a0e27] rounded-lg overflow-hidden">
                      <div
                        className="absolute inset-y-0 left-0 bg-gradient-to-r from-red-500 to-red-400 flex items-center justify-end pr-3"
                        style={{ width: `${riskDistribution.distribution.High.percentage}%` }}
                      >
                        <span className="text-xs text-white font-medium">
                          {formatCurrency(riskDistribution.distribution.High.amount)}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Medium Risk */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-400">Medium Risk</span>
                      <span className="text-white font-semibold">
                        {riskDistribution.distribution.Medium.count} ({riskDistribution.distribution.Medium.percentage.toFixed(1)}%)
                      </span>
                    </div>
                    <div className="relative h-8 bg-[#0a0e27] rounded-lg overflow-hidden">
                      <div
                        className="absolute inset-y-0 left-0 bg-gradient-to-r from-orange-500 to-orange-400 flex items-center justify-end pr-3"
                        style={{ width: `${riskDistribution.distribution.Medium.percentage}%` }}
                      >
                        <span className="text-xs text-white font-medium">
                          {formatCurrency(riskDistribution.distribution.Medium.amount)}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Low Risk */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-400">Low Risk</span>
                      <span className="text-white font-semibold">
                        {riskDistribution.distribution.Low.count} ({riskDistribution.distribution.Low.percentage.toFixed(1)}%)
                      </span>
                    </div>
                    <div className="relative h-8 bg-[#0a0e27] rounded-lg overflow-hidden">
                      <div
                        className="absolute inset-y-0 left-0 bg-gradient-to-r from-green-500 to-green-400 flex items-center justify-end pr-3"
                        style={{ width: `${riskDistribution.distribution.Low.percentage}%` }}
                      >
                        <span className="text-xs text-white font-medium">
                          {formatCurrency(riskDistribution.distribution.Low.amount)}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Total */}
                  <div className="pt-4 border-t border-white/10">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-300">Total Transactions</span>
                      <span className="text-lg font-bold text-white">
                        {riskDistribution.total_transactions.toLocaleString()}
                      </span>
                    </div>
                  </div>
                </>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Transaction Types and Recent Transactions */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Transaction Types */}
        <Card className="border-white/10 bg-[#0f1632]">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-white">
              Transaction Types Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {transactionTypes.map((type, index) => (
                <div key={index} className="rounded-lg bg-[#0a0e27] p-4 border border-white/5">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-lg bg-cyan-500/10 flex items-center justify-center">
                        <svg className="h-5 w-5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                        </svg>
                      </div>
                      <div>
                        <h4 className="text-sm font-semibold text-white">{type.type}</h4>
                        <p className="text-xs text-gray-400">{type.total.toLocaleString()} transactions</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-white">{formatCurrency(type.total_amount)}</p>
                      <p className="text-xs text-red-400">{type.fraud_count} fraud ({type.fraud_percentage.toFixed(1)}%)</p>
                    </div>
                  </div>
                  <div className="h-2 bg-[#0a0e27] rounded-full overflow-hidden border border-white/5">
                    <div
                      className="h-full bg-red-400"
                      style={{ width: `${type.fraud_percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Transactions */}
        <Card className="border-white/10 bg-[#0f1632]">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-white">
              Recent Transactions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentTransactions.map((transaction, index) => (
                <div key={index} className="rounded-lg bg-[#0a0e27] p-3 border border-white/5">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Badge variant={transaction.is_fraud ? "destructive" : "success"}>
                        {transaction.is_fraud ? "Fraud" : "Safe"}
                      </Badge>
                      <span className="text-xs text-gray-400">{transaction.transaction_type}</span>
                    </div>
                    <span className="text-sm font-semibold text-white">
                      {formatCurrency(transaction.transaction_amount)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-1 text-gray-400">
                      <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      <span>{transaction.location}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={
                        transaction.risk_level === "High" ? "destructive" :
                        transaction.risk_level === "Medium" ? "warning" : "success"
                      }>
                        {transaction.risk_level}
                      </Badge>
                      <span className="text-gray-500">{transaction.fraud_probability.toFixed(0)}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}