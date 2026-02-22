import { useState, useEffect, useRef, useCallback } from 'react'
import { jobsApi } from '../api/jobs'

const TERMINAL_STATES = ['completed', 'failed']
const POLL_INTERVAL   = 3000
const MAX_ERRORS      = 3   // stop only after 3 consecutive failures

export default function useJobPolling(jobId) {
  const [job, setJob]         = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)
  const [isPolling, setIsPolling] = useState(false)

  const intervalRef   = useRef(null)
  const isTerminalRef = useRef(false)
  const errorCountRef = useRef(0)

  const stopPolling = useCallback(() => {
    clearInterval(intervalRef.current)
    intervalRef.current = null
    setIsPolling(false)
  }, [])

  const fetchJob = useCallback(async () => {
    if (!jobId || isTerminalRef.current) return
    try {
      const { data } = await jobsApi.get(jobId)
      errorCountRef.current = 0
      setJob(data)
      if (TERMINAL_STATES.includes(data.status)) {
        isTerminalRef.current = true
        stopPolling()
      }
    } catch (err) {
      errorCountRef.current += 1
      if (errorCountRef.current >= MAX_ERRORS) {
        setError(err.response?.data?.detail || 'Error al consultar el job')
        stopPolling()
      }
    } finally {
      setLoading(false)
    }
  }, [jobId, stopPolling])

  // Main polling effect
  useEffect(() => {
    if (!jobId) return
    isTerminalRef.current = false
    errorCountRef.current = 0

    fetchJob()
    intervalRef.current = setInterval(fetchJob, POLL_INTERVAL)
    setIsPolling(true)

    return () => stopPolling()
  }, [jobId, fetchJob, stopPolling])

  // Re-fetch immediately when the browser tab becomes visible again.
  // Browsers throttle setInterval in background tabs, so if the user
  // switches tabs while the job is running, the next poll fires as soon
  // as they come back instead of waiting up to POLL_INTERVAL seconds.
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && !isTerminalRef.current) {
        fetchJob()
      }
    }
    document.addEventListener('visibilitychange', handleVisibilityChange)
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange)
  }, [fetchJob])

  return { job, loading, error, isPolling }
}
