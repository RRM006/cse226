import { supabase } from './supabase';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function getAuthHeaders() {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session?.access_token) {
    throw new Error('No session found');
  }
  return {
    'Authorization': `Bearer ${session.access_token}`,
    'Content-Type': 'application/json'
  };
}

export async function getCurrentUser() {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/api/v1/me`, {
    headers
  });
  if (response.status === 403) {
    const error = await response.json();
    throw new Error(error.detail || 'Only @northsouth.edu accounts are allowed');
  }
  if (!response.ok) {
    throw new Error('Failed to get user');
  }
  return response.json();
}

export async function uploadCSV(file, program, auditLevel, waivers = '', knowledgeFile = '') {
  const headers = await getAuthHeaders();
  const formData = new FormData();
  formData.append('file', file);
  formData.append('program', program);
  formData.append('audit_level', auditLevel.toString());
  formData.append('waivers', waivers);
  if (knowledgeFile) {
    formData.append('knowledge_file', knowledgeFile);
  }

  const response = await fetch(`${API_URL}/api/v1/audit/csv`, {
    method: 'POST',
    headers: {
      'Authorization': headers['Authorization']
    },
    body: formData
  });

  if (response.status === 403) {
    const error = await response.json();
    throw new Error(error.detail || 'Only @northsouth.edu accounts are allowed');
  }
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to upload CSV');
  }

  return response.json();
}

export async function uploadOCR(file, program, auditLevel, waivers = '') {
  const headers = await getAuthHeaders();
  const formData = new FormData();
  formData.append('file', file);
  formData.append('program', program);
  formData.append('audit_level', auditLevel.toString());
  formData.append('waivers', waivers);

  const response = await fetch(`${API_URL}/api/v1/audit/ocr`, {
    method: 'POST',
    headers: {
      'Authorization': headers['Authorization']
    },
    body: formData
  });

  if (response.status === 403) {
    const error = await response.json();
    throw new Error(error.detail || 'Only @northsouth.edu accounts are allowed');
  }
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to process OCR');
  }

  return response.json();
}

export async function getHistory(limit = 20, offset = 0) {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/api/v1/history?limit=${limit}&offset=${offset}`, {
    headers
  });

  if (response.status === 403) {
    const error = await response.json();
    throw new Error(error.detail || 'Only @northsouth.edu accounts are allowed');
  }
  if (!response.ok) {
    throw new Error('Failed to get history');
  }

  return response.json();
}

export async function getScanById(scanId) {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/api/v1/history/${scanId}`, {
    headers
  });

  if (response.status === 403) {
    const error = await response.json();
    throw new Error(error.detail || 'Only @northsouth.edu accounts are allowed');
  }
  if (!response.ok) {
    throw new Error('Failed to get scan');
  }

  return response.json();
}

export async function deleteScan(scanId) {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/api/v1/history/${scanId}`, {
    method: 'DELETE',
    headers
  });

  if (response.status === 403) {
    const error = await response.json();
    throw new Error(error.detail || 'Only @northsouth.edu accounts are allowed');
  }
  if (!response.ok) {
    throw new Error('Failed to delete scan');
  }

  return response.json();
}

export async function getAllUsers() {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/api/v1/users`, {
    headers
  });

  if (response.status === 403) {
    const error = await response.json();
    throw new Error(error.detail || 'Only @northsouth.edu accounts are allowed');
  }
  if (!response.ok) {
    throw new Error('Failed to get users');
  }

  return response.json();
}

export async function updateUserRole(userId, role) {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/api/v1/users/${userId}/role`, {
    method: 'PATCH',
    headers: {
      ...headers,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ role })
  });

  if (response.status === 403) {
    const error = await response.json();
    throw new Error(error.detail || 'Only @northsouth.edu accounts are allowed');
  }
  if (!response.ok) {
    throw new Error('Failed to update role');
  }

  return response.json();
}

export async function getUserHistory(userId, limit = 20, offset = 0) {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/api/v1/history/user/${userId}?limit=${limit}&offset=${offset}`, {
    headers
  });

  if (response.status === 403) {
    const error = await response.json();
    throw new Error(error.detail || 'Only @northsouth.edu accounts are allowed');
  }
  if (!response.ok) {
    throw new Error('Failed to get user history');
  }

  return response.json();
}
