import React from "react";
import { View } from "react-native";
import ImageBox from "@/components/photo/ImageBox";
import ActionButton from "@/components/common/ActionButton";
import { useCamera } from "@/hooks/useCamera";
import { SafeAreaView } from "react-native-safe-area-context";

export default function App() {
  const { photoUri, handleCameraAction } = useCamera();
  const redirectTo = "/lead-form";

  return (
    <SafeAreaView className="flex-1 items-center justify-center bg-white p-4">
      <View className="items-center">
        <ImageBox uri={photoUri} />
        <ActionButton
          title={photoUri ? "Confirm Photo" : "Take Photo"}
          onPress={() => handleCameraAction(redirectTo)}
          style={photoUri ? "bg-green-500 mt-4" : "bg-blue-500 mt-4"}
        />
      </View>
    </SafeAreaView>
  );
}
