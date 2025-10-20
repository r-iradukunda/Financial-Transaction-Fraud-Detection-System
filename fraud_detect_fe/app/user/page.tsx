"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowRight, CheckCircle, Loader2, Shield, Clock } from "lucide-react"

interface TransactionData {
  TransactionAmount: number
  TransactionDate: string
  TransactionType: string
  Location: string
  Channel: string
  CustomerAge: number
  CustomerOccupation: string
  TransactionDuration: number
  LoginAttempts: number
  AccountBalance: number
  PreviousTransactionDate: string
  "Sender Country": string
  "Receiver Country": string
  "Sender Currency": string
  "Receiver Currency": string
  "Account Status": string
  "Invalid Pin Status": string
  "Invalid pin retry limits": number
  "Invalid pin retry count": number
}

export default function UserTransactionPage() {
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [step, setStep] = useState(1)
  const [startTime, setStartTime] = useState<number>(Date.now())

  const [formData, setFormData] = useState<TransactionData>({
    TransactionAmount: 0,
    TransactionDate: new Date().toLocaleString("en-GB", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    }).replace(",", ""),
    TransactionType: "Transfer",
    Location: "Kigali",
    Channel: "Mobile",
    CustomerAge: 30,
    CustomerOccupation: "",
    TransactionDuration: 0,
    LoginAttempts: 1,
    AccountBalance: 0,
    PreviousTransactionDate: new Date(Date.now() - 86400000).toLocaleString("en-GB", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    }).replace(",", ""),
    "Sender Country": "Rwanda",
    "Receiver Country": "Rwanda",
    "Sender Currency": "RWF",
    "Receiver Currency": "RWF",
    "Account Status": "Active",
    "Invalid Pin Status": "Valid",
    "Invalid pin retry limits": 3,
    "Invalid pin retry count": 0
  })

  const [recipient, setRecipient] = useState({
    name: "",
    account: "",
    bank: "Bank of Kigali"
  })

  const [pinAttempts, setPinAttempts] = useState(0)
  const [enteredPin, setEnteredPin] = useState("")

  useEffect(() => {
    // Track when user starts the transaction
    setStartTime(Date.now())
  }, [])

  const handlePinSubmit = () => {
    const newAttempts = pinAttempts + 1
    setPinAttempts(newAttempts)
    handleChange("LoginAttempts", newAttempts)
    
    if (enteredPin === "1234") {
      handleChange("Invalid Pin Status", "Valid")
      handleChange("Invalid pin retry count", 0)
      return true
    } else {
      handleChange("Invalid Pin Status", "Invalid")
      handleChange("Invalid pin retry count", newAttempts)
      setError("Invalid PIN. Please try again.")
      setEnteredPin("")
      return false
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validate PIN first
    if (!handlePinSubmit()) {
      return
    }

    setLoading(true)
    setError(null)

    // Calculate transaction duration in seconds
    const duration = Math.floor((Date.now() - startTime) / 1000)

    try {
      const transactionData = {
        ...formData,
        TransactionDuration: duration,
        TransactionDate: new Date().toLocaleString("en-GB", {
          day: "2-digit",
          month: "2-digit",
          year: "numeric",
          hour: "2-digit",
          minute: "2-digit"
        }).replace(",", ""),
      }

      const response = await fetch("http://127.0.0.1:5000/api/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(transactionData),
      })

      if (!response.ok) {
        throw new Error(`Transaction failed: ${response.status}`)
      }

      await response.json()
      setSuccess(true)
      
      // Reset form after 3 seconds
      setTimeout(() => {
        setSuccess(false)
        setStep(1)
        setStartTime(Date.now())
        setPinAttempts(0)
        setEnteredPin("")
        setFormData(prev => ({ 
          ...prev, 
          TransactionAmount: 0,
          CustomerOccupation: "",
          LoginAttempts: 1,
          "Invalid Pin Status": "Valid",
          "Invalid pin retry count": 0
        }))
        setRecipient({ name: "", account: "", bank: "Bank of Kigali" })
      }, 3000)

    } catch (err) {
      setError(err instanceof Error ? err.message : "Transaction failed. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (field: keyof TransactionData, value: string | number) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  if (success) {
    return (
      <div className="min-h-screen bg-[#0a0e27] flex items-center justify-center p-8">
        <Card className="border-white/10 bg-[#0f1632] max-w-md w-full">
          <CardContent className="pt-6">
            <div className="text-center space-y-4">
              <div className="mx-auto rounded-full bg-green-500/10 p-4 w-fit">
                <CheckCircle className="h-16 w-16 text-green-400" />
              </div>
              <h2 className="text-2xl font-bold text-white">Payment Successful!</h2>
              <p className="text-gray-400">
                Your payment of <span className="text-white font-semibold">{formData.TransactionAmount.toLocaleString()} RWF</span> has been processed.
              </p>
              <div className="text-sm text-gray-500 space-y-1">
                <p>Transaction is being analyzed by our fraud detection system...</p>
                <div className="flex items-center justify-center gap-2 text-xs text-gray-600">
                  <Clock className="h-3 w-3" />
                  <span>Duration: {formData.TransactionDuration}s</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#0a0e27] p-8">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="flex items-center justify-center gap-2 mb-4">
            <div className="h-12 w-12 rounded-full bg-cyan-500 flex items-center justify-center">
              <Shield className="h-6 w-6 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-white">Rwanda Secure Pay</h1>
          </div>
          <p className="text-gray-400">Fast, secure, and protected by AI fraud detection</p>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center gap-4 mb-8">
          {[1, 2, 3].map((num) => (
            <div key={num} className="flex items-center gap-2">
              <div className={`h-8 w-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                step >= num ? "bg-cyan-500 text-white" : "bg-white/10 text-gray-500"
              }`}>
                {num}
              </div>
              {num < 3 && (
                <div className={`h-0.5 w-12 ${step > num ? "bg-cyan-500" : "bg-white/10"}`} />
              )}
            </div>
          ))}
        </div>

        {/* Error Alert */}
        {error && (
          <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-4">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Step 1: Amount & Type */}
          {step === 1 && (
            <Card className="border-white/10 bg-[#0f1632]">
              <CardHeader>
                <CardTitle className="text-xl font-semibold text-white">Payment Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">Amount (RWF)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.TransactionAmount || ""}
                    onChange={(e) => handleChange("TransactionAmount", parseFloat(e.target.value) || 0)}
                    placeholder="Enter amount"
                    className="w-full rounded-lg bg-[#0a0e27] border border-white/10 px-4 py-3 text-2xl font-bold text-white focus:border-cyan-500 focus:outline-none"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">Transaction Type</label>
                  <select
                    value={formData.TransactionType}
                    onChange={(e) => handleChange("TransactionType", e.target.value)}
                    className="w-full rounded-lg bg-[#0a0e27] border border-white/10 px-4 py-3 text-white focus:border-cyan-500 focus:outline-none"
                  >
                    <option value="Transfer">Transfer</option>
                    <option value="Payment">Payment</option>
                    <option value="Withdrawal">Withdrawal</option>
                    <option value="Deposit">Deposit</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">Payment Channel</label>
                  <select
                    value={formData.Channel}
                    onChange={(e) => handleChange("Channel", e.target.value)}
                    className="w-full rounded-lg bg-[#0a0e27] border border-white/10 px-4 py-3 text-white focus:border-cyan-500 focus:outline-none"
                  >
                    <option value="Mobile">Mobile Banking</option>
                    <option value="Online">Online Banking</option>
                    <option value="ATM">ATM</option>
                    <option value="Branch">Bank Branch</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">Location</label>
                  <input
                    type="text"
                    value={formData.Location}
                    onChange={(e) => handleChange("Location", e.target.value)}
                    placeholder="e.g., Kigali, New York"
                    className="w-full rounded-lg bg-[#0a0e27] border border-white/10 px-4 py-3 text-white focus:border-cyan-500 focus:outline-none"
                    required
                  />
                </div>

                <button
                  type="button"
                  onClick={() => setStep(2)}
                  disabled={!formData.TransactionAmount}
                  className="w-full flex items-center justify-center gap-2 rounded-lg bg-cyan-500 px-6 py-3 font-semibold text-white hover:bg-cyan-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Continue
                  <ArrowRight className="h-5 w-5" />
                </button>
              </CardContent>
            </Card>
          )}

          {/* Step 2: Recipient & Account Details */}
          {step === 2 && (
            <Card className="border-white/10 bg-[#0f1632]">
              <CardHeader>
                <CardTitle className="text-xl font-semibold text-white">Account & Recipient Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Customer Information */}
                <div className="border-b border-white/10 pb-4">
                  <h3 className="text-sm font-semibold text-gray-400 mb-3">Your Information</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-300">Your Age</label>
                      <input
                        type="number"
                        value={formData.CustomerAge}
                        onChange={(e) => handleChange("CustomerAge", parseInt(e.target.value))}
                        className="w-full rounded-lg bg-[#0a0e27] border border-white/10 px-4 py-2 text-white focus:border-cyan-500 focus:outline-none"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-300">Occupation</label>
                      <input
                        type="text"
                        value={formData.CustomerOccupation}
                        onChange={(e) => handleChange("CustomerOccupation", e.target.value)}
                        placeholder="e.g., Teacher"
                        className="w-full rounded-lg bg-[#0a0e27] border border-white/10 px-4 py-2 text-white focus:border-cyan-500 focus:outline-none"
                        required
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mt-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-300">Account Balance (RWF)</label>
                      <input
                        type="number"
                        step="0.01"
                        value={formData.AccountBalance}
                        onChange={(e) => handleChange("AccountBalance", parseFloat(e.target.value))}
                        className="w-full rounded-lg bg-[#0a0e27] border border-white/10 px-4 py-2 text-white focus:border-cyan-500 focus:outline-none"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-300">Account Status</label>
                      <select
                        value={formData["Account Status"]}
                        onChange={(e) => handleChange("Account Status", e.target.value)}
                        className="w-full rounded-lg bg-[#0a0e27] border border-white/10 px-4 py-2 text-white focus:border-cyan-500 focus:outline-none"
                      >
                        <option value="Active">Active</option>
                        <option value="Inactive">Inactive</option>
                        <option value="Suspended">Suspended</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Recipient Information */}
                <div className="border-b border-white/10 pb-4">
                  <h3 className="text-sm font-semibold text-gray-400 mb-3">Recipient Details</h3>
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-300">Recipient Name</label>
                      <input
                        type="text"
                        value={recipient.name}
                        onChange={(e) => setRecipient(prev => ({ ...prev, name: e.target.value }))}
                        placeholder="Enter recipient name"
                        className="w-full rounded-lg bg-[#0a0e27] border border-white/10 px-4 py-3 text-white focus:border-cyan-500 focus:outline-none"
                        required
                      />
                    </div>

                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-300">Account Number</label>
                      <input
                        type="text"
                        value={recipient.account}
                        onChange={(e) => setRecipient(prev => ({ ...prev, account: e.target.value }))}
                        placeholder="Enter account number"
                        className="w-full rounded-lg bg-[#0a0e27] border border-white/10 px-4 py-3 text-white focus:border-cyan-500 focus:outline-none"
                        required
                      />
                    </div>

                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-300">Bank</label>
                      <select
                        value={recipient.bank}
                        onChange={(e) => setRecipient(prev => ({ ...prev, bank: e.target.value }))}
                        className="w-full rounded-lg bg-[#0a0e27] border border-white/10 px-4 py-3 text-white focus:border-cyan-500 focus:outline-none"
                      >
                        <option value="Bank of Kigali">Bank of Kigali</option>
                        <option value="Equity Bank">Equity Bank</option>
                        <option value="I&M Bank">I&M Bank</option>
                        <option value="KCB Bank">KCB Bank</option>
                        <option value="Cogebanque">Cogebanque</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Transaction Geography */}
                <div>
                  <h3 className="text-sm font-semibold text-gray-400 mb-3">Transaction Details</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-300">Sender Country</label>
                      <input
                        type="text"
                        value={formData["Sender Country"]}
                        onChange={(e) => handleChange("Sender Country", e.target.value)}
                        className="w-full rounded-lg bg-[#0a0e27] border border-white/10 px-4 py-2 text-white focus:border-cyan-500 focus:outline-none"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-300">Receiver Country</label>
                      <input
                        type="text"
                        value={formData["Receiver Country"]}
                        onChange={(e) => handleChange("Receiver Country", e.target.value)}
                        className="w-full rounded-lg bg-[#0a0e27] border border-white/10 px-4 py-2 text-white focus:border-cyan-500 focus:outline-none"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-300">Sender Currency</label>
                      <input
                        type="text"
                        value={formData["Sender Currency"]}
                        onChange={(e) => handleChange("Sender Currency", e.target.value)}
                        className="w-full rounded-lg bg-[#0a0e27] border border-white/10 px-4 py-2 text-white focus:border-cyan-500 focus:outline-none"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-300">Receiver Currency</label>
                      <input
                        type="text"
                        value={formData["Receiver Currency"]}
                        onChange={(e) => handleChange("Receiver Currency", e.target.value)}
                        className="w-full rounded-lg bg-[#0a0e27] border border-white/10 px-4 py-2 text-white focus:border-cyan-500 focus:outline-none"
                        required
                      />
                    </div>
                  </div>
                </div>

                <div className="flex gap-4 pt-4">
                  <button
                    type="button"
                    onClick={() => setStep(1)}
                    className="w-full rounded-lg bg-white/5 px-6 py-3 font-semibold text-white hover:bg-white/10 transition-colors"
                  >
                    Back
                  </button>
                  <button
                    type="button"
                    onClick={() => setStep(3)}
                    disabled={!recipient.name || !recipient.account || !formData.CustomerOccupation}
                    className="w-full flex items-center justify-center gap-2 rounded-lg bg-cyan-500 px-6 py-3 font-semibold text-white hover:bg-cyan-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Continue
                    <ArrowRight className="h-5 w-5" />
                  </button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Step 3: Security & Confirm */}
          {step === 3 && (
            <Card className="border-white/10 bg-[#0f1632]">
              <CardHeader>
                <CardTitle className="text-xl font-semibold text-white">Security & Confirmation</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Transaction Summary */}
                <div className="rounded-lg bg-[#0a0e27] p-4 space-y-3">
                  <h3 className="text-sm font-semibold text-gray-400">Transaction Summary</h3>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Amount</span>
                    <span className="text-white font-semibold">{formData.TransactionAmount.toLocaleString()} RWF</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Transaction Type</span>
                    <span className="text-white">{formData.TransactionType}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Channel</span>
                    <span className="text-white">{formData.Channel}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Location</span>
                    <span className="text-white">{formData.Location}</span>
                  </div>
                  <div className="border-t border-white/10 pt-3 mt-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Recipient</span>
                      <span className="text-white">{recipient.name}</span>
                    </div>
                    <div className="flex justify-between text-sm mt-1">
                      <span className="text-gray-400">Account</span>
                      <span className="text-white">{recipient.account}</span>
                    </div>
                    <div className="flex justify-between text-sm mt-1">
                      <span className="text-gray-400">Bank</span>
                      <span className="text-white">{recipient.bank}</span>
                    </div>
                  </div>
                </div>

                {/* PIN Security Section */}
                <div className="rounded-lg bg-[#0a0e27] border border-white/10 p-4 space-y-4">
                  <h3 className="text-sm font-semibold text-gray-300 flex items-center gap-2">
                    <Shield className="h-4 w-4 text-cyan-400" />
                    Security Verification
                  </h3>
                  
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-300">
                      Enter PIN to Confirm (Use: 1234)
                    </label>
                    <input
                      type="password"
                      maxLength={4}
                      value={enteredPin}
                      onChange={(e) => {
                        setEnteredPin(e.target.value)
                        setError(null)
                      }}
                      placeholder="••••"
                      className="w-full rounded-lg bg-[#0f1632] border border-white/10 px-4 py-3 text-center text-2xl font-bold text-white tracking-widest focus:border-cyan-500 focus:outline-none"
                      required
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-xs">
                    <div className="rounded bg-white/5 p-2">
                      <p className="text-gray-400">PIN Retry Limit</p>
                      <p className="text-white font-semibold">{formData["Invalid pin retry limits"]}</p>
                    </div>
                    <div className="rounded bg-white/5 p-2">
                      <p className="text-gray-400">Attempts Made</p>
                      <p className={`font-semibold ${pinAttempts >= formData["Invalid pin retry limits"] ? "text-red-400" : "text-white"}`}>
                        {pinAttempts} / {formData["Invalid pin retry limits"]}
                      </p>
                    </div>
                  </div>

                  {pinAttempts > 0 && (
                    <div className="text-xs text-gray-400">
                      Login attempts this session: {formData.LoginAttempts}
                    </div>
                  )}
                </div>

                {/* Previous Transaction Info */}
                <div className="text-xs text-gray-500 bg-[#0a0e27] rounded p-3">
                  <p>Previous transaction: {formData.PreviousTransactionDate}</p>
                </div>

                {/* AI Protection Notice */}
                <div className="rounded-lg bg-cyan-500/10 border border-cyan-500/20 p-4">
                  <div className="flex gap-3">
                    <Shield className="h-5 w-5 text-cyan-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-cyan-400">AI-Protected Transaction</p>
                      <p className="text-xs text-gray-400 mt-1">
                        This payment is protected by our advanced fraud detection system. Your transaction will be analyzed in real-time for security.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex gap-4">
                  <button
                    type="button"
                    onClick={() => setStep(2)}
                    className="w-full rounded-lg bg-white/5 px-6 py-3 font-semibold text-white hover:bg-white/10 transition-colors"
                  >
                    Back
                  </button>
                  <button
                    type="submit"
                    disabled={loading || !enteredPin || enteredPin.length !== 4 || pinAttempts >= formData["Invalid pin retry limits"]}
                    className="w-full flex items-center justify-center gap-2 rounded-lg bg-green-500 px-6 py-3 font-semibold text-white hover:bg-green-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="h-5 w-5 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <CheckCircle className="h-5 w-5" />
                        Confirm & Pay
                      </>
                    )}
                  </button>
                </div>
              </CardContent>
            </Card>
          )}
        </form>
      </div>
    </div>
  )
}
