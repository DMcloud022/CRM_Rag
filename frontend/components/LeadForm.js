import React, { useState } from 'react';
import { View, TextInput, Button, StyleSheet } from 'react-native';
import theme from '../theme';

export default function LeadForm({ route, navigation }) {
  const { lead } = route.params;
  const [formData, setFormData] = useState(lead);

  const handleChange = (key, value) => {
    setFormData({ ...formData, [key]: value });
  };

  const handleSubmit = () => {
    navigation.navigate('CRMSelector', { lead: formData });
  };

  return (
    <View style={styles.container}>
      <View style={styles.formContainer}>
        <TextInput
          style={[styles.input, styles.nameInput]}
          value={formData.name}
          onChangeText={(text) => handleChange('name', text)}
          placeholder="Name"
          placeholderTextColor={theme.colors.placeholder}
        />
        <TextInput
          style={[styles.input, styles.emailInput]}
          value={formData.email}
          onChangeText={(text) => handleChange('email', text)}
          placeholder="Email"
          placeholderTextColor={theme.colors.placeholder}
          keyboardType="email-address"
        />
        <TextInput
          style={[styles.input, styles.phoneInput]}
          value={formData.phone}
          onChangeText={(text) => handleChange('phone', text)}
          placeholder="Phone"
          placeholderTextColor={theme.colors.placeholder}
          keyboardType="phone-pad"
        />
        <TextInput
          style={[styles.input, styles.companyInput]}
          value={formData.company}
          onChangeText={(text) => handleChange('company', text)}
          placeholder="Company"
          placeholderTextColor={theme.colors.placeholder}
        />
        <TextInput
          style={[styles.input, styles.positionInput]}
          value={formData.position}
          onChangeText={(text) => handleChange('position', text)}
          placeholder="Position"
          placeholderTextColor={theme.colors.placeholder}
        />
      </View>
      <View style={styles.buttonContainer}>
        <Button
          title="Submit"
          onPress={handleSubmit}
          color={theme.colors.primary}
          style={styles.submitButton}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
    padding: 20,
    justifyContent: 'space-between',
  },
  formContainer: {
    flex: 1,
    justifyContent: 'center',
  },
  input: {
    height: 50,
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: 8,
    marginBottom: 16,
    paddingHorizontal: 12,
    fontSize: 16,
    color: theme.colors.text,
  },
  nameInput: {
    marginTop: 16,
  },
  emailInput: {
    keyboardType: 'email-address',
  },
  phoneInput: {
    keyboardType: 'phone-pad',
  },
  buttonContainer: {
    marginBottom: 24,
  },
  submitButton: {
    borderRadius: 8,
  },
});