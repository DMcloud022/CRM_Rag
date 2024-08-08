import axios from 'axios';
import * as FileSystem from 'expo-file-system';

const API_BASE_URL = 'http://localhost:8000';

export const scanBusinessCard = async (imageUri) => {
  try {
    const formData = new FormData();
    const fileInfo = await FileSystem.getInfoAsync(imageUri);
    
    formData.append('image', {
      uri: imageUri,
      type: 'image/jpeg',
      name: 'business_card.jpg',
      size: fileInfo.size,
    });

    const response = await axios.post(`${API_BASE_URL}/scan-business-card`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    return response.data;
  } catch (error) {
    console.error('Error scanning business card:', error);
    throw error;
  }
};

export const sendLeadToCRM = async (crmName, lead, code = null) => {
  try {
    const url = `${API_BASE_URL}/send-to-crm/${crmName}`;
    const headers = {};
    if (code) {
      headers['Authorization'] = `Bearer ${code}`;
    }
    const response = await axios.post(url, lead, { headers });
    return response.data;
  } catch (error) {
    console.error(`Error sending lead to ${crmName}:`, error);
    throw error;
  }
};

export const initiateCRMOAuth = async (crmName) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/oauth/${crmName}/initiate`);
    return response.data.authUrl;
  } catch (error) {
    console.error(`Error initiating OAuth for ${crmName}:`, error);
    throw error;
  }
};