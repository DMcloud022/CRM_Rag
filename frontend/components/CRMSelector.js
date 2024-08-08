import React from 'react';
import { View, Button, StyleSheet, Text } from 'react-native';
import { sendLeadToCRM, initiateCRMOAuth } from '../services/api';
import theme from '../theme';

export default function CRMSelector({ route, navigation }) {
  const { lead } = route.params;

  const handleCRMSelection = async (crmName) => {
    try {
      const authUrl = await initiateCRMOAuth(crmName);
      if (authUrl) {
        navigation.navigate('OAuthCallback', { crmName, authUrl, lead });
      } else {
        const result = await sendLeadToCRM(crmName, lead);
        alert(`Lead sent to ${crmName} successfully!`);
      }
    } catch (error) {
      console.error(`Error with ${crmName} CRM:`, error);
      alert(`Error sending lead to ${crmName}: ${error.message}`);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Select a CRM to send the lead</Text>
      <View style={styles.buttonContainer}>
        <Button
          title="Send to Zoho"
          onPress={() => handleCRMSelection('zoho')}
          color={theme.colors.primary}
          style={styles.button}
        />
        <Button
          title="Send to Salesforce"
          onPress={() => handleCRMSelection('salesforce')}
          color={theme.colors.primary}
          style={styles.button}
        />
        <Button
          title="Send to HubSpot"
          onPress={() => handleCRMSelection('hubspot')}
          color={theme.colors.primary}
          style={styles.button}
        />
        <Button
          title="Send to Microsoft Dynamics"
          onPress={() => handleCRMSelection('dynamics')}
          color={theme.colors.primary}
          style={styles.button}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 24,
    color: theme.colors.text,
  },
  buttonContainer: {
    flexDirection: 'column',
    alignItems: 'center',
  },
  button: {
    marginVertical: 8,
    width: '100%',
    borderRadius: 8,
  },
});