import React from 'react'
import { useApi } from '../api'
import { useFilters } from '../FilterContext'

/** Fetches /api/<endpoint> with the current slicers and renders children(data). */
export default function Page({ endpoint, children }) {
  const { filters } = useFilters()
  const { data, loading, error } = useApi(endpoint, filters)
  if (error && !data) return <div className="err">Could not load /api/{endpoint}: {error}. Is the backend running on port 8000?</div>
  if (!data) return <div className="empty">Loading…</div>
  return <>{loading && <div className="loading">● updating…</div>}{children(data)}</>
}
