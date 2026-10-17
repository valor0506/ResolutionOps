import { Search, Building2 } from 'lucide-react'

export function CustomersPage() {
  return (
    <div className="p-8 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-slate-900">Customers</h1>
        <p className="text-sm text-slate-500 mt-1">
          Customer accounts, environments, and case history
        </p>
      </div>

      <div className="relative max-w-md mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
        <input
          type="text"
          placeholder="Search customers..."
          className="w-full rounded-lg border border-slate-200 bg-white py-2 pl-10 pr-4 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-12 text-center">
        <Building2 className="h-10 w-10 text-slate-300 mx-auto mb-3" />
        <p className="text-sm text-slate-500">Customer data will load from Firestore</p>
        <p className="text-xs text-slate-400 mt-1">Seeded with 5 fictional B2B customers</p>
      </div>
    </div>
  )
}
