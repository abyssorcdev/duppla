import { useState, useEffect, useCallback } from 'react'
import { jobsApi } from '../api/jobs'

export default function useJobs(initialFilters = {}) {
  const [jobs, setJobs] = useState([])
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({ page: 1, page_size: 10, ...initialFilters })

  const fetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const clean = Object.fromEntries(
        Object.entries(filters).filter(([, v]) => v !== '' && v !== null && v !== undefined)
      )
      const { data } = await jobsApi.list(clean)
      setJobs(data.items)
      setTotal(data.total)
      setTotalPages(data.total_pages)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al cargar jobs')
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => { fetch() }, [fetch])

  const updateFilter = (key, value) =>
    setFilters((prev) => ({ ...prev, [key]: value, page: key === 'page' ? value : 1 }))

  const refresh = () => fetch()

  return { jobs, total, totalPages, loading, error, filters, updateFilter, refresh }
}
