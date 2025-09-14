"use client"

import { useEffect, useMemo, useRef, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogTrigger,
  DialogDescription,
} from "@/components/ui/dialog"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

// Icons
import {
  Home,
  RefreshCw,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Trash2,
  Edit,
  Plus,
  DollarSign,
  User,
  Building,
} from "lucide-react"
import { API_BASE } from "@/lib/api"

const API_URL = `${API_BASE}/income-sources/`
const USER_ID = typeof window !== "undefined" ? localStorage.getItem("userId") : null

// ---------- helpers ----------
const GRAD_COLORS = ["red", "orange", "amber", "emerald", "teal", "cyan", "blue", "indigo", "violet", "purple", "pink"]
function randomGradient() {
  const c = GRAD_COLORS[Math.floor(Math.random() * GRAD_COLORS.length)]
  const c2 = GRAD_COLORS[Math.floor(Math.random() * GRAD_COLORS.length)]
  return `from-${c}-500 to-${c2}-600`
}

// Backend id may come as id / _id / _id.$oid
function normalizeId(raw) {
  if (!raw) return ""
  if (typeof raw === "string") return raw
  if (raw.id) return raw.id
  if (raw._id && typeof raw._id === "string") return raw._id
  if (raw._id && typeof raw._id === "object" && raw._id.$oid) return raw._id.$oid
  if (raw.pk) return raw.pk
  return ""
}

function normalizeIncomeSource(raw) {
  const id = normalizeId(raw)
  const startDateValue =
    raw?.start_date ?? raw?.startDate ?? (raw?.start_date ? String(raw.start_date).split("T")[0] : "") ?? ""

  return {
    id,
    name: raw?.name ?? "",
    type: raw?.type ?? "Property Rent",
    amount: Number(raw?.amount ?? 0),
    frequency: raw?.frequency ?? "Monthly",
    startDate: startDateValue,
    color: raw?.color || randomGradient(),
    user_id: normalizeId(raw?.user_id) || USER_ID || "",
    raw,
  }
}

function showToast(msg, color = "blue") {
  const div = document.createElement("div")
  div.className = `fixed top-4 right-4 bg-${color}-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-slide-in-right`
  div.innerText = msg
  document.body.appendChild(div)
  setTimeout(() => document.body.removeChild(div), 2500)
}

const IncomeSource = () => {
  const [incomeSources, setIncomeSources] = useState([])
  const [loading, setLoading] = useState(true)

  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [editingIncomeSource, setEditingIncomeSource] = useState(null)
  const [showLoginPopup, setShowLoginPopup] = useState(false)
  const [dialogOpen, setDialogOpen] = useState(false)

  const checkLoginBeforeAction = () => {
    const token = localStorage.getItem("userId")
    if (!token) {
      setShowLoginPopup(true)
      return false
    }
    return true
  }

  async function collectRent(incomeSource, amount) {
    if (!checkLoginBeforeAction()) return

    try {
      const payload = {
        income_source_id: normalizeId(incomeSource.id),
        amount: Number(amount || incomeSource.amount),
        collection_date: new Date().toISOString().split("T")[0],
        user_id: USER_ID || null,
      }

      const res = await fetch(`${API_BASE}/income-collections/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })

      if (!res.ok) {
        const t = await res.text()
        throw new Error(t || "Failed to collect rent")
      }

      showToast(
        `Collected ₹${Number(amount || incomeSource.amount).toLocaleString()} from ${incomeSource.name}`,
        "green",
      )
      await fetchIncomeSources() // Refresh the list
    } catch (err) {
      console.error("Error collecting rent:", err)
      showToast("Failed to collect rent", "red")
    }
  }

  const [formData, setFormData] = useState({
    name: "",
    type: "Property Rent",
    amount: "",
    frequency: "Monthly",
    startDate: "",
  })

  const mountedRef = useRef(false)

  const incomeTypes = ["Property Rent", "Other"]
  const frequencyTypes = ["Daily", "Weekly", "Monthly", "Yearly"]

  const handleChange = (e) => setFormData((f) => ({ ...f, [e.target.name]: e.target.value }))

  async function fetchIncomeSources() {
    try {
      setLoading(true)
      if (!USER_ID || USER_ID === "null" || USER_ID === "undefined") {
        if (mountedRef.current) setIncomeSources([])
        return
      }

      const url = `${API_URL}?user_id=${encodeURIComponent(USER_ID)}`
      const res = await fetch(url)
      const data = await res.json()
      const normalized = Array.isArray(data) ? data.map(normalizeIncomeSource) : []
      if (mountedRef.current) setIncomeSources(normalized)
    } catch (err) {
      console.error("Error fetching income sources:", err)
      showToast("Failed to fetch income sources", "red")
    } finally {
      setLoading(false)
    }
  }

  async function createIncomeSource() {
    try {
      const payload = {
        name: formData.name,
        type: formData.type,
        amount: Number(formData.amount || 0),
        frequency: formData.frequency,
        start_date: formData.startDate || null,
        user_id: USER_ID || null,
      }
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })
      if (!res.ok) {
        const t = await res.text()
        throw new Error(t || "Failed to create income source")
      }
      await fetchIncomeSources()
      setDialogOpen(false)
      resetForm()
      showToast("Income source created!", "green")
    } catch (err) {
      console.error("Error creating income source:", err)
      showToast("Create failed", "red")
    }
  }

  function resetForm() {
    setFormData({
      name: "",
      type: "Property Rent",
      amount: "",
      frequency: "Monthly",
      startDate: "",
    })
  }

  useEffect(() => {
    mountedRef.current = true
    fetchIncomeSources()
    return () => {
      mountedRef.current = false
    }
  }, [])

  async function updateIncomeSource(id, patch) {
    const incomeSourceId = typeof id === "string" ? id : normalizeId(id)
    if (!incomeSourceId) return showToast("Invalid id", "red")
    try {
      const res = await fetch(`${API_URL}${incomeSourceId}/`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...patch, user_id: USER_ID || null }),
      })
      if (!res.ok) {
        const t = await res.text()
        throw new Error(t || "Failed to update")
      }
      await fetchIncomeSources()
      setEditDialogOpen(false)
      setEditingIncomeSource(null)
      resetForm()
      showToast("Income source updated", "blue")
    } catch (err) {
      console.error("Error updating income source:", err)
      showToast("Update failed", "red")
    }
  }

  async function deleteIncomeSource(id) {
    const incomeSourceId = typeof id === "string" ? id : normalizeId(id)
    if (!incomeSourceId) return showToast("Invalid id", "red")
    try {
      const res = await fetch(`${API_URL}${incomeSourceId}/`, { method: "DELETE" })
      if (!res.ok && res.status !== 204) {
        const t = await res.text()
        throw new Error(t || "Failed to delete")
      }
      setIncomeSources((list) => list.filter((d) => normalizeId(d.id) !== incomeSourceId))
      showToast("Income source deleted", "red")
    } catch (err) {
      console.error("Error deleting income source:", err)
      showToast("Delete failed", "red")
    }
  }

  function handleAddSubmit() {
    createIncomeSource()
  }

  function handleEditOpen(incomeSource) {
    setEditingIncomeSource(incomeSource)
    setFormData({
      name: incomeSource.name || "",
      type: incomeSource.type || "Property Rent",
      amount: String(incomeSource.amount ?? ""),
      frequency: incomeSource.frequency || "Monthly",
      startDate: (incomeSource.startDate && String(incomeSource.startDate).split("T")?.[0]) || "",
    })
    setEditDialogOpen(true)
  }

  function handleEditSubmit() {
    if (!editingIncomeSource) return
    const id = editingIncomeSource.id
    const payload = {
      name: formData.name,
      type: formData.type,
      amount: Number(formData.amount || 0),
      frequency: formData.frequency,
      start_date: formData.startDate || null,
    }
    updateIncomeSource(id, payload)
  }

  const totalAmount = useMemo(() => incomeSources.reduce((sum, d) => sum + (Number(d.amount) || 0), 0), [incomeSources])

  const getFrequencyDisplay = (frequency) => {
    const frequencyMap = {
      Daily: "per day",
      Weekly: "per week",
      Monthly: "per month",
      Yearly: "per year",
    }
    return frequencyMap[frequency] || "per month"
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 sm:p-6 space-y-6 sm:space-y-8">
      {/* Alert Dialog for Not Logged In */}
      <Dialog open={showLoginPopup} onOpenChange={setShowLoginPopup}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-yellow-500" />
              Login Required
            </DialogTitle>
            <DialogDescription>You need to login before adding an Income Source.</DialogDescription>
          </DialogHeader>
          <div className="flex items-center p-4 text-sm text-yellow-700 bg-yellow-50 rounded-lg">
            <AlertTriangle className="w-5 h-5 mr-2" />
            <span>Please login to continue.</span>
          </div>
          <DialogFooter className="sm:justify-start">
            <Button
              type="button"
              className="bg-gradient-to-r from-green-600 to-blue-600"
              onClick={() => (window.location.href = "/login")}
            >
              <User className="w-4 h-4 mr-2" />
              Go to Login
            </Button>
            <Button type="button" variant="outline" onClick={() => setShowLoginPopup(false)}>
              Cancel
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {loading && (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-green-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600">Loading your income sources...</p>
          </div>
        </div>
      )}

      {!loading && (
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-4xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
              Income Sources
            </h1>
            <p className="text-gray-600 mt-1 sm:mt-2 text-sm sm:text-base">
              Track and manage your income streams for financial growth
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Button variant="outline" onClick={fetchIncomeSources} disabled={loading}>
              <RefreshCw className="w-4 h-4 mr-2" />
              {loading ? "Loading..." : "Refresh"}
            </Button>
            <Badge variant="secondary" className="px-3 py-1">
              <Building className="w-4 h-4 mr-1" />
              {incomeSources.length} Active Sources
            </Badge>
          </div>
        </div>
      )}

      {!loading && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6">
          <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
            <CardContent className="p-4 sm:p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 font-medium">Total Income Sources</p>
                  <p className="text-xl sm:text-2xl font-bold text-green-600">{incomeSources.length}</p>
                  <p className="text-sm text-gray-500 mt-1">Active sources</p>
                </div>
                <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-r from-green-500 to-green-600 rounded-lg flex items-center justify-center">
                  <TrendingUp className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
            <CardContent className="p-4 sm:p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 font-medium">Property Rent Sources</p>
                  <p className="text-xl sm:text-2xl font-bold text-blue-600">
                    {incomeSources.filter((s) => s.type === "Property Rent").length}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">Rental properties</p>
                </div>
                <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                  <Home className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
            <CardContent className="p-4 sm:p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 font-medium">Other Sources</p>
                  <p className="text-xl sm:text-2xl font-bold text-purple-600">
                    {incomeSources.filter((s) => s.type === "Other").length}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">Other income types</p>
                </div>
                <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <DollarSign className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {!loading && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
          {incomeSources.map((incomeSource, index) => {
            return (
              <Card
                key={String(incomeSource.id)}
                className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 animate-fade-in-up"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div
                        className={`w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-r ${
                          incomeSource.color || randomGradient()
                        } rounded-lg flex items-center justify-center`}
                      >
                        <Home className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                      </div>
                      <div>
                        <CardTitle className="text-base sm:text-lg font-semibold text-gray-900">
                          {incomeSource.name}
                        </CardTitle>
                        <Badge variant="secondary" className="text-xs">
                          {incomeSource.type}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">Amount</p>
                      <p className="font-semibold text-gray-900">
                        ₹{Number(incomeSource.amount).toLocaleString()} {getFrequencyDisplay(incomeSource.frequency)}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500">Frequency</p>
                      <p className="font-semibold text-gray-900">{incomeSource.frequency}</p>
                    </div>
                  </div>

                  <div className="text-sm">
                    <p className="text-gray-500">Start Date</p>
                    <p className="font-semibold text-gray-900">
                      {incomeSource.startDate ? new Date(incomeSource.startDate).toLocaleDateString() : "—"}
                    </p>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-2 pt-2">
                    {incomeSource.type === "Property Rent" && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => collectRent(incomeSource, incomeSource.amount)}
                        className="flex-1 bg-transparent hover:bg-green-50"
                      >
                        <DollarSign className="w-4 h-4 mr-1" />
                        Collect Rent
                      </Button>
                    )}

                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEditOpen(incomeSource)}
                      className="flex-1 bg-transparent"
                    >
                      <Edit className="w-4 h-4 mr-1" />
                      Edit
                    </Button>

                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => deleteIncomeSource(incomeSource.id)}
                      className="flex-1"
                    >
                      <Trash2 className="w-4 h-4" />
                      <span className="sm:inline hidden">Delete</span>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )
          })}

          <Dialog
            open={dialogOpen}
            onOpenChange={(o) => {
              if (o) {
                if (!checkLoginBeforeAction()) {
                  setDialogOpen(false)
                  return
                }
              }
              setDialogOpen(o)
            }}
          >
            <DialogTrigger asChild>
              <Card className="border-2 border-dashed border-gray-300 hover:border-green-400 transition-all duration-300 cursor-pointer group">
                <CardContent className="p-8 sm:p-12 text-center">
                  <div className="w-12 h-12 sm:w-16 sm:h-16 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                    <Plus className="w-6 h-6 sm:w-8 sm:h-8 text-white" />
                  </div>
                  <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-2">Add New Income Source</h3>
                  <p className="text-sm sm:text-base text-gray-600">Track a new income stream</p>
                </CardContent>
              </Card>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle className="flex items-center">
                  <Building className="w-5 h-5 mr-2 text-green-600" />
                  Add New Income Source
                </DialogTitle>
                <p className="text-gray-600">Add a new income source to track your earnings</p>
              </DialogHeader>

              <div className="space-y-4 mt-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Income Source Name</Label>
                  <Input
                    id="name"
                    name="name"
                    placeholder="e.g., Property Rent - Downtown Apartment"
                    value={formData.name}
                    onChange={handleChange}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="type">Income Type</Label>
                  <Select value={formData.type} onValueChange={(v) => setFormData((f) => ({ ...f, type: v }))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {incomeTypes.map((t) => (
                        <SelectItem key={t} value={t}>
                          {t}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="amount">Amount</Label>
                  <Input
                    id="amount"
                    name="amount"
                    type="number"
                    placeholder="Enter amount"
                    value={formData.amount}
                    onChange={handleChange}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="frequency">Frequency</Label>
                  <Select
                    value={formData.frequency}
                    onValueChange={(v) => setFormData((f) => ({ ...f, frequency: v }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {frequencyTypes.map((t) => (
                        <SelectItem key={t} value={t}>
                          {t}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="startDate">Start Date</Label>
                  <Input
                    id="startDate"
                    name="startDate"
                    type="date"
                    value={formData.startDate}
                    onChange={handleChange}
                  />
                </div>
              </div>

              <DialogFooter className="mt-6">
                <Button variant="outline" onClick={() => setDialogOpen(false)}>
                  Cancel
                </Button>
                <Button
                  onClick={handleAddSubmit}
                  className="bg-gradient-to-r from-green-600 to-blue-500 hover:from-green-700 hover:to-blue-700"
                >
                  <Plus className="w-4 h-4 mr-2" /> Add Income Source
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      )}

      {!loading && (
        <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
          <DialogContent className="sm:max-w-md max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center">
                <Edit className="w-5 h-5 mr-2 text-green-600" />
                Edit Income Source
              </DialogTitle>
              <p className="text-gray-600">Update your income source information</p>
            </DialogHeader>

            <div className="space-y-4 mt-4">
              <div className="space-y-2">
                <Label htmlFor="edit-name">Income Source Name</Label>
                <Input id="edit-name" name="name" value={formData.name} onChange={handleChange} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="edit-type">Income Type</Label>
                <Select value={formData.type} onValueChange={(v) => setFormData((f) => ({ ...f, type: v }))}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {incomeTypes.map((t) => (
                      <SelectItem key={t} value={t}>
                        {t}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="edit-amount">Amount</Label>
                <Input id="edit-amount" name="amount" type="number" value={formData.amount} onChange={handleChange} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="edit-frequency">Frequency</Label>
                <Select value={formData.frequency} onValueChange={(v) => setFormData((f) => ({ ...f, frequency: v }))}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {frequencyTypes.map((t) => (
                      <SelectItem key={t} value={t}>
                        {t}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="edit-startDate">Start Date</Label>
                <Input
                  id="edit-startDate"
                  name="startDate"
                  type="date"
                  value={formData.startDate}
                  onChange={handleChange}
                />
              </div>
            </div>

            <DialogFooter className="mt-6">
              <Button variant="outline" onClick={() => setEditDialogOpen(false)}>
                Cancel
              </Button>
              <Button
                onClick={handleEditSubmit}
                className="bg-gradient-to-r from-green-600 to-blue-500 hover:from-green-700 hover:to-blue-700"
              >
                <CheckCircle className="w-4 h-4 mr-2" /> Update Income Source
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </div>
  )
}

export default IncomeSource
