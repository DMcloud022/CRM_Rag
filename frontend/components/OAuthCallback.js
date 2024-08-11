import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
// import { WebView } from 'react-native-webview';
import { sendLeadToCRM } from '../services/api';

export default function OAuthCallback({ route, navigation }) {
  const { crmName, authUrl, lead } = route.params;
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const handleNavigationStateChange = async (newNavState) => {
    const { url } = newNavState;
    if (url.includes('oauth_callback')) {
      setLoading(true);
      const code = url.split('code=')[1].split('&')[0]; // Extract code more reliably
      try {
        const result = await sendLeadToCRM(crmName, lead, code);
        alert(`Lead sent to ${crmName} successfully!`);
        navigation.navigate('Scanner');
      } catch (error) {
        console.error(`Error sending lead to ${crmName}:`, error);
        setError(`Error sending lead to ${crmName}: ${error.message}`);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Authorizing {crmName}</Text>
      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Please wait...</Text>
        </View>
      )}
      {error && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}
      <WebView
        source={{ uri: authUrl }}
        onNavigationStateChange={handleNavigationStateChange}
        style={styles.webview}
        onLoadStart={() => setLoading(true)}
        onLoadEnd={() => setLoading(false)}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    textAlign: 'center',
    marginVertical: 20,
    color: '#333',
  },
  loadingContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.8)',
    zIndex: 1,
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#333',
  },
  errorContainer: {
    padding: 20,
    backgroundColor: '#ffeeee',
    borderRadius: 10,
    marginHorizontal: 20,
    marginBottom: 20,
  },
  errorText: {
    color: '#ff0000',
    fontSize: 16,
    textAlign: 'center',
  },
  webview: {
    flex: 1,
  },
});