import { supabase, getStudentToken, setStudentToken } from './supabase';

const API_URL = import.meta.env.VITE_API_URL;
if (!API_URL) {
  console.warn('VITE_API_URL not set - API calls may fail');
}

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

function getStudentAuthHeaders() {
  const token = getStudentToken();
  if (!token) {
    throw new Error('No student session found');
  }
  return {
    'Authorization': `Bearer ${token}`,
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


// =====================
// STUDENT API FUNCTIONS
// =====================

export async function studentLogin(studentId, password) {
  const response = await fetch(`${API_URL}/api/v1/student/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ student_id: studentId, password })
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Login failed');
  }

  setStudentToken(data.access_token);
  return data;
}

export async function studentChangePassword(currentPassword, newPassword) {
  const headers = getStudentAuthHeaders();
  const response = await fetch(`${API_URL}/api/v1/student/change-password`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword
    })
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Password change failed');
  }
  return data;
}

export async function getStudentProfile() {
  const headers = getStudentAuthHeaders();
  const response = await fetch(`${API_URL}/api/v1/student/me`, { headers });

  if (!response.ok) {
    throw new Error('Failed to get student profile');
  }
  return response.json();
}

export async function getStudentAuditResults(limit = 20, offset = 0) {
  const headers = getStudentAuthHeaders();
  const response = await fetch(
    `${API_URL}/api/v1/student/audit-results?limit=${limit}&offset=${offset}`,
    { headers }
  );

  if (!response.ok) {
    throw new Error('Failed to get audit results');
  }
  return response.json();
}

export async function getStudentAuditResultById(resultId) {
  const headers = getStudentAuthHeaders();
  const response = await fetch(`${API_URL}/api/v1/student/audit-results/${resultId}`, { headers });

  if (!response.ok) {
    throw new Error('Failed to get audit result');
  }
  return response.json();
}

export async function submitStudentRequest(message, auditResultId = null) {
  const headers = getStudentAuthHeaders();
  const body = { message };
  if (auditResultId) body.audit_result_id = auditResultId;

  const response = await fetch(`${API_URL}/api/v1/student/requests`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body)
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to submit request');
  }
  return data;
}

export async function getStudentRequests(limit = 20, offset = 0) {
  const headers = getStudentAuthHeaders();
  const response = await fetch(
    `${API_URL}/api/v1/student/requests?limit=${limit}&offset=${offset}`,
    { headers }
  );

  if (!response.ok) {
    throw new Error('Failed to get requests');
  }
  return response.json();
}

// Admin student management
export async function createStudent(studentId, name = '', email = '') {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/api/v1/students`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ student_id: studentId, name, email })
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to create student');
  }
  return data;
}

export async function getAllStudents(limit = 50, offset = 0) {
  const headers = await getAuthHeaders();
  const response = await fetch(
    `${API_URL}/api/v1/students?limit=${limit}&offset=${offset}`,
    { headers }
  );

  if (!response.ok) {
    throw new Error('Failed to get students');
  }
  return response.json();
}

export async function getStudentById(studentId) {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/api/v1/students/${studentId}`, { headers });

  if (!response.ok) {
    throw new Error('Failed to get student');
  }
  return response.json();
}

export async function updateStudent(studentId, data) {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/api/v1/students/${studentId}`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    throw new Error('Failed to update student');
  }
  return response.json();
}

export async function adminResetPassword(studentId, newPassword) {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/api/v1/students/${studentId}/reset-password`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify({ new_password: newPassword })
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to reset password');
  }
  return data;
}

export async function deleteStudent(studentId) {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/api/v1/students/${studentId}`, {
    method: 'DELETE',
    headers
  });

  if (!response.ok) {
    throw new Error('Failed to delete student');
  }
  return response.json();
}

// Admin audit results
export async function createAuditResult(data) {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/api/v1/audit-results`, {
    method: 'POST',
    headers,
    body: JSON.stringify(data)
  });

  const result = await response.json();
  if (!response.ok) {
    throw new Error(result.detail || 'Failed to create audit result');
  }
  return result;
}

export async function getAllAuditResults(limit = 50, offset = 0) {
  const headers = await getAuthHeaders();
  const response = await fetch(
    `${API_URL}/api/v1/audit-results?limit=${limit}&offset=${offset}`,
    { headers }
  );

  if (!response.ok) {
    throw new Error('Failed to get audit results');
  }
  return response.json();
}

// Admin requests
export async function getAllRequests(limit = 50, offset = 0) {
  const headers = await getAuthHeaders();
  const response = await fetch(
    `${API_URL}/api/v1/requests?limit=${limit}&offset=${offset}`,
    { headers }
  );

  if (!response.ok) {
    throw new Error('Failed to get requests');
  }
  return response.json();
}

export async function getRequestById(requestId) {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/api/v1/requests/${requestId}`, { headers });

  if (!response.ok) {
    throw new Error('Failed to get request');
  }
  return response.json();
}

export async function updateRequestStatus(requestId, status, adminNotes = null) {
  const headers = await getAuthHeaders();
  const body = { status };
  if (adminNotes) body.admin_notes = adminNotes;

  const response = await fetch(`${API_URL}/api/v1/requests/${requestId}`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify(body)
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to update request');
  }
  return data;
}
