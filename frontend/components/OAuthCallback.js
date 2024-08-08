import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { WebView } from 'react-native-webview';
import { sendLeadToCRM } from '../services/api';
import theme from '../theme';

export default function OAuthCallback({ route, navigation }) {
  const { crmName, authUrl, lead } = route.params;
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const handleNavigationStateChange = async (newNavState) => {
    const { url } = newNavState;
    if (url.includes('oauth_callback')) {
      const code = url.split('code=')[1];
      try {
        setIsLoading(true);
        const result = await sendLeadToCRM(crmName, lead, code);
        setIsLoading(false);
        alert(`Lead sent to ${crmName} successfully!`);
        navigation.navigate('Scanner');
      } catch (error) {
        setIsLoading(false);
        setError(`Error sending lead to ${crmName}: ${error.message}`);
        console.error(`Error sending lead to ${crmName}:`, error);
      }
    }
  };

  return (
    <View style={styles.container}>
      {isLoading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
          <Text style={styles.text}>Authorizing {crmName}...</Text>
        </View>
      ) : (
        <>
          {error ? (
            <View style={styles.errorContainer}>
              <Text style={[styles.text, styles.errorText]}>{error}</Text>
            </View>
          ) : (
            <WebView source={{ uri: authUrl }} onNavigationStateChange={handleNavigationStateChange} />
          )}
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  text: {
    fontSize: 18,
    color: theme.colors.text,
    marginTop: 16,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorText: {
    color: theme.colors.error,
  },
});