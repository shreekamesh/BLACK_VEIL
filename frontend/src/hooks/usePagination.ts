import { useState, useCallback, useMemo } from 'react'

interface PaginationConfig {
  initialPage?: number
  initialPageSize?: number
  total?: number
}

export function usePagination(config: PaginationConfig = {}) {
  const [page, setPage] = useState(config.initialPage || 0)
  const [pageSize, setPageSize] = useState(config.initialPageSize || 10)
  const [total, setTotal] = useState(config.total || 0)

  const totalPages = useMemo(() => Math.max(1, Math.ceil(total / pageSize)), [total, pageSize])

  const handlePageChange = useCallback((newPage: number) => {
    setPage(newPage)
  }, [])

  const handlePageSizeChange = useCallback((newPageSize: number) => {
    setPageSize(newPageSize)
    setPage(0)
  }, [])

  const handleSetTotal = useCallback((newTotal: number) => {
    setTotal(newTotal)
  }, [])

  const reset = useCallback(() => {
    setPage(0)
    setPageSize(10)
    setTotal(0)
  }, [])

  return {
    page,
    pageSize,
    total,
    totalPages,
    setPage: handlePageChange,
    setPageSize: handlePageSizeChange,
    setTotal: handleSetTotal,
    reset,
    hasNext: page < totalPages - 1,
    hasPrev: page > 0,
    from: page * pageSize + 1,
    to: Math.min((page + 1) * pageSize, total),
  }
}

