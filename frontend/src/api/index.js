import http from './http.js'

export default {
  /* ---- Auth ---- */
  register(data) {
    return http.post('/auth/register', data).then(r => r.data)
  },
  login(data) {
    return http.post('/auth/login', data).then(r => r.data)
  },
  getMe() {
    return http.get('/auth/me').then(r => r.data)
  },

  /* ---- Knowledge Base ---- */
  getKBStats(kbId = 'default') {
    return http.get(`/kb/stats?kb_id=${kbId}`).then(r => r.data)
  },
  clearKB(kbId = 'default') {
    return http.delete(`/kb/clear?kb_id=${kbId}`).then(r => r.data)
  },
  listKBs() {
    return http.get('/kb/list').then(r => r.data)
  },
  createKB(data) {
    return http.post('/kb/create', data).then(r => r.data)
  },
  deleteKB(kbId) {
    return http.delete(`/kb/${kbId}`).then(r => r.data)
  },
  listKBDocuments(kbId = 'default', query = '', fileFormat = '') {
    return http.get(`/kb/documents?kb_id=${kbId}&query=${encodeURIComponent(query)}&file_format=${encodeURIComponent(fileFormat)}`).then(r => r.data)
  },
  deleteKBDocument(fileName, kbId = 'default') {
    return http.delete(`/kb/documents/${encodeURIComponent(fileName)}?kb_id=${kbId}`).then(r => r.data)
  },
  listKBPermissions(kbId) {
    return http.get(`/kb/${kbId}/permissions`).then(r => r.data)
  },
  setKBPermission(kbId, data) {
    return http.post(`/kb/${kbId}/permissions`, data).then(r => r.data)
  },
  removeKBPermission(kbId, userId) {
    return http.delete(`/kb/${kbId}/permissions/${userId}`).then(r => r.data)
  },

  /* ---- Document Upload ---- */
  uploadFiles(formData) {
    return http.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(r => r.data)
  },
  uploadFilesAsync(formData) {
    return http.post('/documents/upload-async', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(r => r.data)
  },

  /* ---- Tasks ---- */
  getTask(taskId) {
    return http.get(`/tasks/${taskId}`).then(r => r.data)
  },
  listTasks() {
    return http.get('/tasks').then(r => r.data)
  },

  /* ---- Chat ---- */
  chat(message, history = []) {
    return http.post('/chat', { message, history }).then(r => r.data)
  },

  /* ---- Table Fill ---- */
  previewTemplate(formData) {
    return http.post('/table/preview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 180000,
    }).then(r => r.data)
  },
  fillTemplate(formData) {
    return http.post('/table/fill', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 180000,
    }).then(r => r.data)
  },

  getDownloadUrl(filePath) {
    return `/api/files/download?path=${encodeURIComponent(filePath)}`
  },

  /* ---- Document Operations ---- */
  executeDocOp(formData) {
    return http.post('/doc-ops/execute', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(r => r.data)
  },
  compareDocuments(formData) {
    return http.post('/doc-ops/compare', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 180000,
    }).then(r => r.data)
  },

  /* ---- Teams ---- */
  listTeams() {
    return http.get('/teams').then(r => r.data)
  },
  createTeam(data) {
    return http.post('/teams', data).then(r => r.data)
  },
  getTeam(teamId) {
    return http.get(`/teams/${teamId}`).then(r => r.data)
  },
  updateTeam(teamId, data) {
    return http.patch(`/teams/${teamId}`, data).then(r => r.data)
  },
  deleteTeam(teamId) {
    return http.delete(`/teams/${teamId}`).then(r => r.data)
  },
  inviteTeamMember(teamId, data) {
    return http.post(`/teams/${teamId}/members`, data).then(r => r.data)
  },
  updateTeamMemberRole(teamId, userId, role) {
    return http.patch(`/teams/${teamId}/members/${userId}`, { role }).then(r => r.data)
  },
  removeTeamMember(teamId, userId) {
    return http.delete(`/teams/${teamId}/members/${userId}`).then(r => r.data)
  },
  transferTeamOwnership(teamId, newOwnerId) {
    return http.post(`/teams/${teamId}/transfer`, { new_owner_id: newOwnerId }).then(r => r.data)
  },
  getTeamActivity(teamId, limit = 30) {
    return http.get(`/teams/${teamId}/activity?limit=${limit}`).then(r => r.data)
  },

  /* ---- API Keys ---- */
  listApiKeys() {
    return http.get('/api-keys').then(r => r.data)
  },
  createApiKey(data) {
    return http.post('/api-keys', data).then(r => r.data)
  },
  deleteApiKey(keyId) {
    return http.delete(`/api-keys/${keyId}`).then(r => r.data)
  },

  /* ---- Webhooks ---- */
  listWebhooks() {
    return http.get('/webhooks').then(r => r.data)
  },
  createWebhook(data) {
    return http.post('/webhooks', data).then(r => r.data)
  },
  deleteWebhook(id) {
    return http.delete(`/webhooks/${id}`).then(r => r.data)
  },

  /* ---- Knowledge Graph ---- */
  getKGFiles(kbId = 'default') {
    return http.get(`/knowledge-graph/files?kb_id=${kbId}`).then(r => r.data)
  },
  generateKG(fileNames = null, kbId = 'default') {
    return http.post(`/knowledge-graph/generate?kb_id=${kbId}`, { file_names: fileNames }).then(r => r.data)
  },
  getKGResult(taskId) {
    return http.get(`/knowledge-graph/result/${taskId}`).then(r => r.data)
  },

  /* ---- Analytics ---- */
  getAnalyticsOverview() {
    return http.get('/analytics/overview').then(r => r.data)
  },
  getAnalyticsUsage(days = 7) {
    return http.get(`/analytics/usage?days=${days}`).then(r => r.data)
  },
  getAuditLogs(page = 1, pageSize = 20, action = '') {
    return http.get(`/audit/logs?page=${page}&page_size=${pageSize}&action=${action}`).then(r => r.data)
  },
}
