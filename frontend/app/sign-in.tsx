import React from "react";
import { TouchableOpacity, Image, Text } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useAppContext } from "@/global/AppContext";
import { router } from "expo-router";
import LoginButton from "@/components/common/LoginButton";

// sign in via hubspot -> camera app -> business card analyzer -> generate lead -> receive lead data -> coconfirm user -> sesend hubspot lead
export default function SignIn() {
  const { user, setUser } = useAppContext();

  const handleSignIn = async () => {
    setUser("John");
    console.log(user);
    router.replace("/(app)/");
  };

  return (
    <SafeAreaView className="flex-1 items-center justify-center bg-white">
      <LoginButton
        providerName="HubSpot"
        backgroundColor="bg-blue-600"
        logoSource={require("@/assets/images/HSLogo2.png")}
        onPress={handleSignIn}
      />
    </SafeAreaView>
  );
}
