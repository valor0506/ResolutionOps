import { Plus, Search, Filter } from 'lucide-react'

export function CasesPage() {
  return (
    <div className="p-8 max-w-7xl">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Cases</h1>
          <p className="text-sm text-slate-500 mt-1">
            Manage and investigate customer support cases
          </p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors">
          <Plus className="h-4 w-4" />
          New Case
        </button>
      </div>

      {/* Search and filters */}
      <div className="flex items-center gap-3 mb-6">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search cases by ID, title, or customer..."
            className="w-full rounded-lg border border-slate-200 bg-white py-2 pl-10 pr-4 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <button className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-600 hover:bg-slate-50 transition-colors">
          <Filter className="h-4 w-4" />
          Filters
        </button>
      </div>

      {/* Empty state */}
      <div className="rounded-xl border border-slate-200 bg-white">
        <div className="px-6 py-3 border-b border-slate-100">
          <div className="grid grid-cols-12 gap-4 text-xs font-medium text-slate-500 uppercase tracking-wider">
            <div className="col-span-1">ID</div>
            <div className="col-span-3">Title</div>
            <div className="col-span-2">Customer</div>
            <div className="col-span-1">Priority</div>
            <div className="col-span-2">Status</div>
            <div className="col-span-1">Owner</div>
            <div className="col-span-2">Updated</div>
          </div>
        </div>
        <div className="p-12 text-center text-sm text-slate-400">
          No cases yet. Create a case to get started.
        </div>
      </div>
    </div>
  )
}
