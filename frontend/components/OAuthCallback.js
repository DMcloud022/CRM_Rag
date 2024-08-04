import React, { useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { WebView } from 'react-native-webview';
import { sendLeadToCRM } from '../services/api';

export default function OAuthCallback({ route, navigation }) {
  const { crmName, authUrl, lead } = route.params;

  const handleNavigationStateChange = async (newNavState) => {
    const { url } = newNavState;
    if (url.includes('oauth_callback')) {
      const code = url.split('code=')[1];
      try {
        const result = await sendLeadToCRM(crmName, lead, code);
        alert(`Lead sent to ${crmName} successfully!`);
        navigation.navigate('Scanner');
      } catch (error) {
        console.error(`Error sending lead to ${crmName}:`, error);
        alert(`Error sending lead to ${crmName}: ${error.message}`);
      }
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.text}>Authorizing {crmName}...</Text>
      <WebView
        source={{ uri: authUrl }}
        onNavigationStateChange={handleNavigationStateChange}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  text: {
    fontSize: 18,
    textAlign: 'center',
    marginVertical: 10,
  },
});