import {
  DarkTheme,
  DefaultTheme,
  ThemeProvider,
} from "@react-navigation/native";
import { useFonts } from "expo-font";
import * as SplashScreen from "expo-splash-screen";
import { useEffect } from "react";
import "react-native-reanimated";
import { Slot, Stack } from "expo-router";
import { AppProvider, useAppContext } from "@/global/AppContext";
import { useColorScheme } from "@/hooks/useColorScheme";
import { StatusBar } from "react-native";
import * as Linking from 'expo-linking';
import { useOAuth } from '@/hooks/useOAuth';
import { UserProvider } from "@/context/context";

// Prevent the splash screen from auto-hiding before asset loading is complete.
SplashScreen.preventAutoHideAsync();

function RootLayoutInner() {
  const { setAppIsReady } = useAppContext();
  const colorScheme = useColorScheme();
  const { handleOAuthCallback } = useOAuth();
  const [loaded] = useFonts({
    SpaceMono: require("../assets/fonts/SpaceMono-Regular.ttf"),
  });

  useEffect(() => {
    if (loaded) {
      SplashScreen.hideAsync().then(() => setAppIsReady(true));
    }
  }, [loaded]);

  useEffect(() => {
    const handleDeepLink = (event: { url: string }) => {
      const { path, queryParams } = Linking.parse(event.url) || {};
      if (path === 'oauth-callback') {
          const { access_token, refresh_token, expires_at, crm_name } = queryParams || {};
          if (access_token && refresh_token && expires_at && crm_name) {
              handleOAuthCallback(
                  access_token as string,
                  refresh_token as string,
                  expires_at as string,
                  crm_name as string
              );
          }
      }
  };
  

    Linking.addEventListener('url', handleDeepLink as any);
    
    // Check for initial URL
    Linking.getInitialURL().then((url) => {
      if (url) {
        handleDeepLink({ url });
      }
    });

  }, [handleOAuthCallback]);

  if (!loaded) {
    return null;
  }

  return (
    <ThemeProvider value={colorScheme === "dark" ? DarkTheme : DefaultTheme}>
      <Slot />
    </ThemeProvider>
  );
}

export default function RootLayout() {
  return (
    <UserProvider>
      <AppProvider>
        <RootLayoutInner />
      </AppProvider>
    </UserProvider>
  );
}