import axios from 'axios';

const API_BASE_URL = 'https://your-domain.com/api/';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'X-Device-ID': localStorage.getItem('deviceId'),
    'X-Auth-Token': localStorage.getItem('authToken'),
    'Content-Type': 'application/json'
  }
});

export const MonitoringAPI = {
  submitLocation: (data) => apiClient.post('location/', data),
  submitCallLog: (data) => apiClient.post('calls/', data),
  submitSocialMedia: (data) => apiClient.post('social-media/', data),
  submitAppUsage: (data) => apiClient.post('app-usage/', data),
  getAlerts: () => apiClient.get('alerts/'),
  checkForCommands: () => apiClient.get('commands/')
};

export const AuthAPI = {
  registerDevice: (parentCode) => apiClient.post('register/', { parent_code: parentCode }),
  renewAuthToken: () => apiClient.post('token-renew/')
};

const checkForDuplicate = async (endpoint, data) => {
  try {
    const response = await axios.get(endpoint, {
      params: {
        child_id: data.child,
        timestamp: data.timestamp,
        ...(endpoint.includes('sms') && { message: data.message }),
        ...(endpoint.includes('calls') && { caller: data.caller, callee: data.callee })
      }
    });
    return response.data.length > 0;
  } catch (error) {
    console.error('Duplicate check error:', error);
    return false;
  }
};

export const sendData = async (endpoint, data) => {
  const isDuplicate = await checkForDuplicate(endpoint, data);
  if (isDuplicate) {
    throw new Error('Duplicate entry detected - not submitting');
  }
  return apiClient.post(endpoint, data);
};

// Secure file upload instance with different content-type
const fileClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'X-Device-ID': localStorage.getItem('deviceId'),
    'X-Auth-Token': localStorage.getItem('authToken'),
    'Content-Type': 'multipart/form-data'
  }
});

export const MediaAPI = {
  uploadPhoto: (file) => {
    const formData = new FormData();
    formData.append('image', file);
    return fileClient.post('photos/', formData)
  }
};