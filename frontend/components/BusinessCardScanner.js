import React, { useState, useEffect } from 'react';
import { View, Button, Image, StyleSheet, Text } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { scanBusinessCard } from '../services/api';
import theme from '../theme';

export default function BusinessCardScanner({ navigation }) {
  const [image, setImage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    (async () => {
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== 'granted') {
        alert('Sorry, we need camera permissions to make this work!');
      }
    })();
  }, []);

  const takePicture = async () => {
    try {
      setIsLoading(true);
      let result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 1,
      });

      if (!result.canceled) {
        setImage(result.uri);
        const lead = await scanBusinessCard(result.uri);
        navigation.navigate('LeadForm', { lead });
      }
      setIsLoading(false);
    } catch (error) {
      setIsLoading(false);
      console.error("Error taking picture:", error);
      alert("An error occurred while taking the picture. Please try again.");
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.contentContainer}>
        <Text style={styles.title}>Scan a Business Card</Text>
        <Text style={styles.subtitle}>Take a picture of a business card to get started.</Text>
        <Button
          title={isLoading ? 'Loading...' : 'Take Picture'}
          onPress={takePicture}
          color={theme.colors.primary}
          disabled={isLoading}
        />
        {image && (
          <View style={styles.imageContainer}>
            <Image source={{ uri: image }} style={styles.image} />
          </View>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
    alignItems: 'center',
    justifyContent: 'center',
  },
  contentContainer: {
    padding: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
    color: theme.colors.primary,
  },
  subtitle: {
    fontSize: 16,
    marginBottom: 20,
    color: theme.colors.secondary,
  },
  imageContainer: {
    marginTop: 20,
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: 8,
    overflow: 'hidden',
  },
  image: {
    width: 200,
    height: 200,
  },
});