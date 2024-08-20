import AsyncStorage from '@react-native-async-storage/async-storage';

interface Tokens {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
}

export const storeTokens = async (crmName: string, tokens: Tokens) => {
  await AsyncStorage.setItem(`${crmName}_tokens`, JSON.stringify(tokens));
};

export const getTokens = async (crmName: string): Promise<Tokens | null> => {
  const tokensString = await AsyncStorage.getItem(`${crmName}_tokens`);
  return tokensString ? JSON.parse(tokensString) : null;
};

export const removeTokens = async (crmName: string) => {
  await AsyncStorage.removeItem(`${crmName}_tokens`);
};