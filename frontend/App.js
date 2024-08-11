import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import BusinessCardScanner from './components/BusinessCardScanner';
import LeadForm from './components/LeadForm';
import CRMSelector from './components/CRMSelector';
import OAuthCallback from './components/OAuthCallback';

const Stack = createStackNavigator();

export default function App() {
  return (
    <NavigationContainer
      fallback={<Text>Loading...</Text>}
      onError={(error) => console.error('Navigation error:', error)}
    >
      <Stack.Navigator
        screenOptions={{
          headerStyle: {
            backgroundColor: '#f4511e',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        <Stack.Screen 
          name="Scanner" 
          component={BusinessCardScanner} 
          options={{ title: 'Business Card Scanner' }}
        />
        <Stack.Screen 
          name="LeadForm" 
          component={LeadForm} 
          options={{ title: 'Lead Information' }}
        />
        <Stack.Screen 
          name="CRMSelector" 
          component={CRMSelector} 
          options={{ title: 'Select CRM' }}
        />
        <Stack.Screen 
          name="OAuthCallback" 
          component={OAuthCallback} 
          options={{ title: 'CRM Authorization' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}