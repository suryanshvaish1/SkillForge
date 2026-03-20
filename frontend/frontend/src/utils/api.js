const API_BASE = '/api/v1';

export async function analyseDocuments({ resumeFile, jdFile, resumeText, jdText }) {
  const formData = new FormData();

  if (resumeFile) {
    formData.append('resume_file', resumeFile);
  } else if (resumeText) {
    formData.append('resume_text', resumeText);
  }

  if (jdFile) {
    formData.append('jd_file', jdFile);
  } else if (jdText) {
    formData.append('jd_text', jdText);
  }

  const resp = await fetch(`${API_BASE}/analyse`, {
    method: 'POST',
    body: formData,
  });

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: resp.statusText }));
    throw new Error(err.detail || `HTTP ${resp.status}`);
  }

  return resp.json();
}

export async function healthCheck() {
  const resp = await fetch(`${API_BASE}/health`);
  return resp.json();
}

export async function getCatalogStats() {
  const resp = await fetch(`${API_BASE}/catalog/stats`);
  return resp.json();
}
