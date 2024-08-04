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
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen name="Scanner" component={BusinessCardScanner} />
        <Stack.Screen name="LeadForm" component={LeadForm} />
        <Stack.Screen name="CRMSelector" component={CRMSelector} />
        <Stack.Screen name="OAuthCallback" component={OAuthCallback} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}