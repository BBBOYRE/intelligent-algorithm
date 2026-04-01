const BASE_URL = '/api'

async function request(url, options = {}) {
  const res = await fetch(`${BASE_URL}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const errBody = await res.json().catch(() => ({}))
    throw new Error(errBody.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export default {
  /* ---- Knowledge Base ---- */
  getKBStats() {
    return request('/kb/stats')
  },

  /* ---- Document Upload ---- */
  uploadFiles(formData) {
    return fetch(`${BASE_URL}/documents/upload`, {
      method: 'POST',
      body: formData, // multipart/form-data, no Content-Type header
    }).then(async (res) => {
      if (!res.ok) {
        const errBody = await res.json().catch(() => ({}))
        throw new Error(errBody.detail || `HTTP ${res.status}`)
      }
      return res.json()
    })
  },

  /* ---- Chat ---- */
  chat(message, history = []) {
    return request('/chat', {
      method: 'POST',
      body: JSON.stringify({ message, history }),
    })
  },

  /* ---- Table Fill ---- */
  fillTemplate(formData) {
    return fetch(`${BASE_URL}/table/fill`, {
      method: 'POST',
      body: formData,
    }).then(async (res) => {
      if (!res.ok) {
        const errBody = await res.json().catch(() => ({}))
        throw new Error(errBody.detail || `HTTP ${res.status}`)
      }
      return res.json()
    })
  },

  getDownloadUrl(filePath) {
    return `${BASE_URL}/files/download?path=${encodeURIComponent(filePath)}`
  },
}
