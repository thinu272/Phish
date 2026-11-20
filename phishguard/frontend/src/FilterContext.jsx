import React, { createContext, useContext, useState } from 'react'

const Ctx = createContext(null)
export const useFilters = () => useContext(Ctx)

const EMPTY = { from: '', to: '', department: '', attack_type: '', severity: '', status: '', country: '', domain: '', preset: 'YTD' }

export function FilterProvider({ children }) {
  const [filters, setFilters] = useState(EMPTY)
  const set = (patch) => setFilters((f) => ({ ...f, ...patch }))
  const reset = () => setFilters(EMPTY)
  return <Ctx.Provider value={{ filters, set, reset }}>{children}</Ctx.Provider>
}
