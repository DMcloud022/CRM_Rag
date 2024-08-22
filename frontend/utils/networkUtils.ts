import * as Network from 'expo-network';

export const getApiBaseUrl = async (): Promise<string> => {
  try {
    const ipAddress = await Network.getIpAddressAsync();
    return `https://crm-rag.onrender.com/`; // Adjust the port as needed
  } catch (error) {
    console.error('Failed to get IP address:', error);
    // Fallback to a default URL
    return 'https://crm-rag.onrender.com/'; // Replace with your default development URL
  }
};