import { useState } from "react";
import * as ImagePicker from "expo-image-picker";
import { Href, router } from "expo-router";

export const useCamera = () => {
  const [photoUri, setPhotoUri] = useState<string | undefined>();

  const handleCameraAction = async (redirectTo: string): Promise<void> => {
    if (!photoUri) {
      try {
        const { granted } = await ImagePicker.getCameraPermissionsAsync();
        if (granted) {
          const result = await ImagePicker.launchCameraAsync();
          if (!result.canceled && result.assets?.[0]?.uri) {
            setPhotoUri(result.assets[0].uri);
          }
        } else {
          await ImagePicker.requestCameraPermissionsAsync();
        }
      } catch (error) {
        console.error("Error while using camera:", error);
      }
    } else {
      router.replace("/(app)/loading-indicator");
      // Navigate to the desired route after the loading indicator screen
      setTimeout(() => {
        router.replace(redirectTo as Href<string>);
      }, 500); // Adjust timeout as needed
    }
  };

  return { photoUri, handleCameraAction };
};
