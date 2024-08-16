import React from "react";
import { TouchableOpacity, Image, Text } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useAppContext } from "@/global/AppContext";
import { router } from "expo-router";

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
      <TouchableOpacity
        className="flex-row items-center bg-blue-600 py-2 px-5 rounded-lg"
        onPress={handleSignIn}
      >
        <Image
          source={require("@/assets/images/HSLogo2.png")}
          className="w-6 h-6 mr-3 ml-[-5]"
        />
        <Text className="text-white text-base font-bold">
          Log in with HubSpot
        </Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
}
