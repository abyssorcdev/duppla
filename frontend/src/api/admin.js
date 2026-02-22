import client from './client'

export const adminApi = {
  listUsers:   (params = {}) => client.get('/admin/users', { params }),
  approveUser: (userId, role) => client.patch(`/admin/users/${userId}/approve`, { role }),
  disableUser: (userId)       => client.patch(`/admin/users/${userId}/disable`),
  listLogs:    (params = {})  => client.get('/admin/logs', { params }),
}
