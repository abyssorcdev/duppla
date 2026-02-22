import client from './client'

export const jobsApi = {
  list: (params = {}) => client.get('/jobs', { params }),
  get: (jobId) => client.get(`/jobs/${jobId}`),
}
