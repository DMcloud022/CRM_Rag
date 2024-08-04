import React, { useState } from 'react';
import { View, TextInput, Button, StyleSheet } from 'react-native';

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
      <TextInput
        style={styles.input}
        value={formData.name}
        onChangeText={(text) => handleChange('name', text)}
        placeholder="Name"
      />
      <TextInput
        style={styles.input}
        value={formData.email}
        onChangeText={(text) => handleChange('email', text)}
        placeholder="Email"
      />
      <TextInput
        style={styles.input}
        value={formData.phone}
        onChangeText={(text) => handleChange('phone', text)}
        placeholder="Phone"
      />
      <TextInput
        style={styles.input}
        value={formData.company}
        onChangeText={(text) => handleChange('company', text)}
        placeholder="Company"
      />
      <TextInput
        style={styles.input}
        value={formData.position}
        onChangeText={(text) => handleChange('position', text)}
        placeholder="Position"
      />
      <Button title="Submit" onPress={handleSubmit} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
  input: {
    height: 40,
    borderColor: 'gray',
    borderWidth: 1,
    marginBottom: 10,
    paddingHorizontal: 10,
  },
});