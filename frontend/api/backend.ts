import { API_BASE_URL } from '../constants';
import axios from 'axios';

export const exchangeCodeForTokens = async (apiBaseUrl: string, code: string, crmName: string) => {
  try {
    const response = await axios.post(`${apiBaseUrl}/oauth/${crmName}/token`, {
      code,
      redirect_uri: 'your_redirect_uri_here',  // Use your actual redirect URI
      client_id: 'your_client_id_here',  // Your client ID
      client_secret: 'your_client_secret_here',  // Your client secret
      grant_type: 'authorization_code',
    });

    return response.data;  // Assuming the response contains access_token, refresh_token, expires_at
  } catch (error) {
    console.error('Token exchange failed:', error);
    throw new Error('Failed to exchange authorization code for tokens');
  }
};


export const initiateOauth = async (crmName: string) => {
  const response = await fetch(`${API_BASE_URL}/oauth/${crmName}/initiate`);
  return response.url;
};

export const oauthCallback = async (crmName: string, code: string) => {
  const response = await fetch(`${API_BASE_URL}/oauth/${crmName}/callback?code=${code}`);
  if (!response.ok) {
    throw new Error('OAuth callback failed');
  }
  return response.json();
};

export const refreshToken = async (crmName: string, refreshToken: string) => {
  const response = await fetch(`${API_BASE_URL}/oauth/${crmName}/refresh`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  if (!response.ok) {
    throw new Error('Token refresh failed');
  }
  return response.json();
};