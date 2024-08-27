import React, { useState, useEffect } from 'react';
import * as WebBrowser from 'expo-web-browser';
import { Button, Alert } from 'react-native';
import { useOAuth } from '@/hooks/useOAuth';
import { getApiBaseUrl } from '@/utils/networkUtils';
import { exchangeCodeForTokens } from '@/api/backend';
import * as Linking from 'expo-linking';

interface OAuthHandlerProps {
  crmName: string;
  onSuccess: () => void;
  onError: (error: string) => void;
}

const OAuthHandler: React.FC<OAuthHandlerProps> = ({ crmName, onSuccess, onError }) => {
  const { handleOAuthCallback } = useOAuth();
  const [apiBaseUrl, setApiBaseUrl] = useState<string | null>(null);

  useEffect(() => {
    getApiBaseUrl().then(setApiBaseUrl);
  }, []);

  const handlePress = async () => {
    if (!apiBaseUrl) {
      Alert.alert('Error', 'API URL not available. Please try again.');
      return;
    }

    try {
      console.log('API Base URL:', apiBaseUrl);
  
      const redirectUrl = Linking.createURL('oauth-callback');
      console.log('Redirect URL:', redirectUrl);
  
      const param = new URLSearchParams();
      param.set("redirectUrl", redirectUrl);
      const authUrl = `http://crm-rag.onrender.com/oauth/${crmName}/initiate?=${param}`; 
      console.log('Auth URL:', authUrl);

      const result = await WebBrowser.openAuthSessionAsync(authUrl, redirectUrl);

      if (result.type === 'success' && result.url) {
        const url = new URL(result.url);
        const code = url.searchParams.get('code');
        const access_token = url.searchParams.get('access_token');
        const refresh_token = url.searchParams.get('refresh_token');
        const expires_in = url.searchParams.get('expires_in');

        if (code && access_token && refresh_token && expires_in) {
          const expires_at = Math.floor(Date.now() / 1000) + parseInt(expires_in);
          await handleOAuthCallback(access_token, refresh_token, expires_at, crmName);
          onSuccess();
        } else {
          const error = 'Missing tokens or code in URL.';
          console.error(error);
          Alert.alert('Error', error);
          onError(error);
        }
      } else if (result.type === 'dismiss') {
        Alert.alert('Authentication was dismissed.');
      } else {
        const error = `Authentication failed with type: ${result.type}`;
        console.error(error);
        Alert.alert('Error', error);
        onError(error);
      }
    } catch (error) {
      console.error('OAuth Error:', error);
      Alert.alert('Error', 'An unexpected error occurred during OAuth.');
      onError('An unexpected error occurred during OAuth.');
    }
  };

  return (
    <Button 
      title={`Sign in with ${crmName}`} 
      onPress={handlePress}
      disabled={!apiBaseUrl}
    />
  );
};

export default OAuthHandler;