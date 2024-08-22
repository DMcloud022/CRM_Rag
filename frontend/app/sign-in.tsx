import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import OAuthHandler from './oAuthHandler';

export default function SignInScreen() {
  const handleOAuthSuccess = () => {
    // Navigation or other actions on successful OAuth
    // navigation.navigate('Home');
  };

  const handleOAuthError = (error: string) => {
    console.error('OAuth error:', error);
    // Show an error message to the user here if needed
  };

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>Business Card Analyzer</Text>
      <View style={styles.buttonContainer}>
        <OAuthHandler
          crmName="hubspot"
          onSuccess={handleOAuthSuccess}
          onError={handleOAuthError}
        />
        <View style={styles.spacing} />
        <OAuthHandler
          crmName="zoho"
          onSuccess={handleOAuthSuccess}
          onError={handleOAuthError}
        />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    marginBottom: 20,
  },
  buttonContainer: {
    width: '80%',
  },
  spacing: {
    height: 20,
  },
});
