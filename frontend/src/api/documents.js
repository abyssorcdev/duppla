import client from './client'

export const documentsApi = {
  list: (params = {}) => client.get('/documents', { params }),

  get: (id) => client.get(`/documents/${id}`),

  create: (data) => client.post('/documents', data),

  update: (id, data) => client.put(`/documents/${id}`, data),

  changeStatus: (id, newStatus, comment = null) =>
    client.patch(`/documents/${id}/status`, {
      new_status: newStatus,
      ...(comment ? { comment } : {}),
    }),

  processBatch: (documentIds) =>
    client.post('/documents/batch/process', { document_ids: documentIds }),
}
