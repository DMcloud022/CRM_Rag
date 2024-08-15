import { Text } from 'react-native';
import { Redirect, Stack } from 'expo-router';
import { useAppContext } from '@/global/AppContext';

export default function AppLayout() {
    const {user, appIsReady, setUser} = useAppContext()

    if (!appIsReady) {
        return <Text>Loading...</Text>;
      }

    if (!user) {
        return <Redirect href="/sign-in" />;
    }
  
    return <Stack />;
}