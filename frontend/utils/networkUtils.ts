import * as Network from 'expo-network';

export const getApiBaseUrl = async (): Promise<string> => {
  try {
    const ipAddress = await Network.getIpAddressAsync();
    return `http://${ipAddress}:8081`; // Adjust the port as needed
  } catch (error) {
    console.error('Failed to get IP address:', error);
    // Fallback to a default URL
    return 'http://192.168.1.13:8081'; // Replace with your default development URL
  }
};