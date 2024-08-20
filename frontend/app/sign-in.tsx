import React from 'react';
import { View, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import OAuthHandler from './oAuthHandler';

export default function SignInScreen() {
  const navigation = useNavigation();

  const handleOAuthSuccess = () => {
    // navigation.navigate('Home');
  };

  const handleOAuthError = (error: string) => {
    console.error('OAuth error:', error);
    // You might want to show an error message to the user here
  };

  return (
    <SafeAreaView style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text style={{ fontSize: 24, marginBottom: 20 }}>Business Card Analyzer</Text>
      <View style={{ width: '80%' }}>
        <OAuthHandler
          crmName="hubspot"
          onSuccess={handleOAuthSuccess}
          onError={handleOAuthError}
        />
        <View style={{ height: 20 }} />
        <OAuthHandler
          crmName="zoho"
          onSuccess={handleOAuthSuccess}
          onError={handleOAuthError}
        />
      </View>
    </SafeAreaView>
  );
}