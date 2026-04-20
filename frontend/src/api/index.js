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
  chat(message, history = [], extraOptions = {}) {
    return http.post('/chat', { message, history, ...extraOptions }).then(r => r.data)
  },

  async chatStream(message, history = [], extraOptions = {}, onChunk) {
    const payload = { message, history, ...extraOptions };
    const token = localStorage.getItem("token");
    let url = http.defaults.baseURL ? `${http.defaults.baseURL}/chat` : '/api/chat';
    
    const headers = {
      'Content-Type': 'application/json'
    };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status}`);
    }

    const sessionId = response.headers.get("X-Session-ID") || extraOptions.session_id;

    if (!response.body) {
      const text = await response.text();
      return { reply: text, session_id: sessionId };
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let fullReply = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value, { stream: true });
      fullReply += chunk;
      if (onChunk) {
        onChunk(chunk, fullReply);
      }
    }

    return { reply: fullReply, session_id: Number(sessionId) || sessionId };
  },

  getChatSessions() {
    return http.get('/chat/sessions').then(r => r.data)
  },
  createChatSession() {
    return http.post('/chat/sessions').then(r => r.data)
  },
  updateChatSession(sessionId, title) {
    return http.patch(`/chat/sessions/${sessionId}`, { title }).then(r => r.data)
  },
  deleteChatSession(sessionId) {
    return http.delete(`/chat/sessions/${sessionId}`).then(r => r.data)
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
    const base = `${window.location.protocol}//${window.location.host}`
    return `${base}/api/files/download?path=${encodeURIComponent(filePath)}`
  },
  saveFileAs(filePath) {
    return http.post(`/files/save-as?path=${encodeURIComponent(filePath)}`).then(r => r.data)
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

  /* ---- Team Announcements ---- */
  getAnnouncements(teamId) {
    return http.get(`/teams/${teamId}/announcements`).then(r => r.data)
  },
  createAnnouncement(teamId, content) {
    return http.post(`/teams/${teamId}/announcements`, { content }).then(r => r.data)
  },
  deleteAnnouncement(teamId, annId) {
    return http.delete(`/teams/${teamId}/announcements/${annId}`).then(r => r.data)
  },

  /* ---- Team Tasks ---- */
  getTeamTasks(teamId) {
    return http.get(`/teams/${teamId}/tasks`).then(r => r.data)
  },
  createTeamTask(teamId, data) {
    return http.post(`/teams/${teamId}/tasks`, data).then(r => r.data)
  },
  updateTeamTaskStatus(teamId, taskId, status) {
    return http.patch(`/teams/${teamId}/tasks/${taskId}`, { status }).then(r => r.data)
  },
  deleteTeamTask(teamId, taskId) {
    return http.delete(`/teams/${teamId}/tasks/${taskId}`).then(r => r.data)
  },

  /* ---- KB Update ---- */
  updateKB(kbId, data) {
    return http.patch(`/kb/${kbId}`, data).then(r => r.data)
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

  /* ---- LLM Settings ---- */
  getLLMConfig() {
    return http.get('/settings/llm').then(r => r.data)
  },
  updateLLMConfig(data) {
    return http.put('/settings/llm', data).then(r => r.data)
  },

  /* ---- Inbox ---- */
  getInbox() {
    return http.get('/inbox').then(r => r.data)
  },
  getUnreadCount() {
    return http.get('/inbox/unread-count').then(r => r.data)
  },
  markRead(msgId) {
    return http.patch(`/inbox/${msgId}/read`).then(r => r.data)
  },
  acceptInvite(msgId) {
    return http.post(`/inbox/${msgId}/accept`).then(r => r.data)
  },
  rejectInvite(msgId) {
    return http.post(`/inbox/${msgId}/reject`).then(r => r.data)
  },
  sendInboxMessage(data) {
    return http.post('/inbox/send', data).then(r => r.data)
  },
  deleteInboxMessage(msgId) {
    return http.delete(`/inbox/${msgId}`).then(r => r.data)
  },

  /* ---- Memos ---- */
  listMemos() {
    return http.get('/memos').then(r => r.data)
  },
  createMemo(data) {
    return http.post('/memos', data).then(r => r.data)
  },
  updateMemo(memoId, data) {
    return http.patch(`/memos/${memoId}`, data).then(r => r.data)
  },
  deleteMemo(memoId) {
    return http.delete(`/memos/${memoId}`).then(r => r.data)
  },

  /* ---- Profile ---- */
  updateProfile(data) {
    return http.put('/auth/profile', data).then(r => r.data)
  },
  uploadAvatar(formData) {
    return http.post('/auth/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(r => r.data)
  },

  /* ---- File Preview ---- */
  previewFile(filePath) {
    return http.get(`/files/preview?path=${encodeURIComponent(filePath)}`).then(r => r.data)
  },
  openLocalFile(path) {
    return http.post('/files/open-local', { path }).then(r => r.data)
  },
  writeBack(outputPath, sourcePath) {
    return http.post('/doc-ops/write-back', { output_path: outputPath, source_path: sourcePath }).then(r => r.data)
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
