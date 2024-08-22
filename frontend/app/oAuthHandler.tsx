import React, { useState, useEffect } from 'react';
import * as WebBrowser from 'expo-web-browser';
import * as Linking from 'expo-linking';
import { Button, Alert } from 'react-native';
import { useOAuth } from '@/hooks/useOAuth';
import { getApiBaseUrl } from '@/utils/networkUtils';
import { exchangeCodeForTokens } from '@/api/backend';

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
    console.log("entered");
    if (!apiBaseUrl) {
      Alert.alert('Error', 'API URL not available. Please try again.');
      return;
    }
  
    try {
      console.log('API Base URL:', apiBaseUrl);
  
      const redirectUrl = Linking.createURL('oauth-callback');
      console.log('Redirect URL:', redirectUrl);
  
      const authUrl = `http://crm-rag.onrender.com/oauth/${crmName}/initiate`;
      console.log('Auth URL:', authUrl);
  
      const result = await WebBrowser.openAuthSessionAsync(authUrl, redirectUrl);
      console.log('Result:', result);
  
      if (result.type === 'success' && result.url) {
        const url = new URL(result.url);
        const code = url.searchParams.get('code');
        console.log('Authorization Code:', code);
  
        if (code) {
          const { access_token, refresh_token, expires_at } = await exchangeCodeForTokens(apiBaseUrl, code, crmName);
          if (access_token && refresh_token && expires_at) {
            await handleOAuthCallback(access_token, refresh_token, expires_at, crmName);
            onSuccess();
          } else {
            const error = 'Missing tokens after exchange.';
            console.error(error);
            Alert.alert('Error', error);
            onError(error);
          }
        } else {
          const error = 'Authorization code missing in URL.';
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
      // Alert.alert('Error', error.message);
      // onError(error.message);
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