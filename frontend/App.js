import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { StatusBar, StyleSheet } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import BusinessCardScanner from './components/BusinessCardScanner';
import LeadForm from './components/LeadForm';
import CRMSelector from './components/CRMSelector';
import OAuthCallback from './components/OAuthCallback';
import theme from './theme';

const Stack = createStackNavigator();

export default function App() {
  return (
    <SafeAreaProvider>
      <NavigationContainer theme={theme}>
        <StatusBar barStyle="light-content" backgroundColor={theme.colors.primary} />
        <Stack.Navigator
          screenOptions={{
            headerStyle: styles.header,
            headerTintColor: theme.colors.white,
            headerTitleStyle: styles.headerTitle,
          }}
        >
          <Stack.Screen name="Scanner" component={BusinessCardScanner} options={{ title: 'Scan Business Card' }} />
          <Stack.Screen name="LeadForm" component={LeadForm} options={{ title: 'Lead Form' }} />
          <Stack.Screen name="CRMSelector" component={CRMSelector} options={{ title: 'CRM Selector' }} />
          <Stack.Screen name="OAuthCallback" component={OAuthCallback} options={{ title: 'OAuth Callback' }} />
        </Stack.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  header: {
    backgroundColor: theme.colors.primary,
    elevation: 0,
    shadowOpacity: 0,
  },
  headerTitle: {
    color: theme.colors.white,
    fontWeight: 'bold',
  },
});