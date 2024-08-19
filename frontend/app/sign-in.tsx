import React, { useState } from "react";
import { TouchableOpacity, Image, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useAppContext } from "@/global/AppContext";
import { router } from "expo-router";
import * as Linking from "expo-linking"; // Import Linking from expo
import { initiateOauth, oauthCallback } from "@/api/backend";

export default function SignIn() {
  const { setUser } = useAppContext();
  const [isLoading, setIsLoading] = useState(false);

  const handleSignIn = (crmName: string) => {
    setIsLoading(true);
    try {
      // Replace 127.0.0.1 with your local IP address (192.168.1.13)
      const oauthUrl = `http://localhost:8000/oauth/${crmName}/initiate`;
      Linking.openURL(oauthUrl);
    } catch (error) {
      console.error("Sign-in failed:", error);
    } finally {
      setIsLoading(false);
    }
  };
  

  return (
    <SafeAreaView className="flex-1 items-center justify-center bg-gray-100 p-6">
      <View className="items-center mb-12">
        {/* <Image
          source={require("@/assets/images/logo.png")}
          className="w-24 h-24 mb-4"
        /> */}
        <Text className="text-2xl font-bold text-gray-800">
          Business Card Analyzer
        </Text>
      </View>
      
      <View className="w-full max-w-xs">
        <TouchableOpacity
          className="flex-row items-center justify-center bg-orange-500 py-3 px-4 rounded-lg mb-4"
          onPress={() => handleSignIn("hubspot")}
          disabled={isLoading}
        >
          {/* <Image
            source={require("@/assets/images/HSLogo2.png")}
            className="w-6 h-6 mr-3"
          /> */}
          <Text className="text-white text-base font-bold">
            Sign in with HubSpot
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          className="flex-row items-center justify-center bg-red-600 py-3 px-4 rounded-lg"
          onPress={() => handleSignIn("zoho")}
          disabled={isLoading}
        >
          {/* <Image
            source={require("@/assets/images/ZohoLogo.png")}
            className="w-6 h-6 mr-3"
          /> */}
          <Text className="text-white text-base font-bold">
            Sign in with Zoho
          </Text>
        </TouchableOpacity>
      </View>

      {isLoading && (
        <Text className="mt-6 text-base text-gray-600">
          Signing in...
        </Text>
      )}
    </SafeAreaView>
  );
}