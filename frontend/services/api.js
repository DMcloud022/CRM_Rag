import axios from 'axios';
import * as FileSystem from 'expo-file-system';
import { Platform } from 'react-native';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';
const API_KEY = process.env.API_KEY;

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,
  },
});

const handleApiError = (error, customMessage) => {
  console.error(customMessage, error);
  if (error.response) {
    throw new Error(`${customMessage}: ${error.response.data.message || error.response.statusText}`);
  } else if (error.request) {
    throw new Error(`${customMessage}: No response received from server`);
  } else {
    throw new Error(`${customMessage}: ${error.message}`);
  }
};

export const scanBusinessCard = async (imageUri) => {
  try {
    const formData = new FormData();
    const fileInfo = await FileSystem.getInfoAsync(imageUri);

    formData.append('image', {
      uri: Platform.OS === 'ios' ? imageUri.replace('file://', '') : imageUri,
      type: 'image/jpeg',
      name: 'business_card.jpg',
    });

    const response = await api.post('/scan-business-card', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    return response.data;
  } catch (error) {
    handleApiError(error, 'Error scanning business card');
  }
};

export const sendLeadToCRM = async (crmName, lead, code = null) => {
  try {
    const url = `/send-to-crm/${crmName}`;
    const headers = code ? { Authorization: `Bearer ${code}` } : {};
    const response = await api.post(url, lead, { headers });
    return response.data;
  } catch (error) {
    handleApiError(error, `Error sending lead to ${crmName}`);
  }
};

export const initiateCRMOAuth = async (crmName) => {
  try {
    const response = await api.get(`/oauth/${crmName}/initiate`);
    return response.data.authUrl;
  } catch (error) {
    handleApiError(error, `Error initiating OAuth for ${crmName}`);
  }
};