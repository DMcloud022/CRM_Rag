import { useState, useCallback } from 'react';
import { refreshToken } from '@/api/backend';
import { storeTokens, getTokens, removeTokens } from '@/utils/storage';
import { useUserContext } from '@/context/context'; // Updated import to use the new context

export const useOAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const { setUser } = useUserContext(); // Updated to use the new context

  const handleOAuthCallback = useCallback(async (access_token: string, refresh_token: string, expires_at: string, crmName: string) => {
    try {
      const expiresAt = new Date(expires_at).getTime();
      await storeTokens(crmName, { accessToken: access_token, refreshToken: refresh_token, expiresAt });
      setIsAuthenticated(true);
      setUser({ isLoggedIn: true, crmName }); // Using context to update user state
    } catch (error) {
      console.error('OAuth callback failed:', error);
      throw error;
    }
  }, [setUser]);

  const getAccessToken = useCallback(async (crmName: string) => {
    const tokens = await getTokens(crmName);
    if (!tokens) return null;

    if (Date.now() < tokens.expiresAt) {
      return tokens.accessToken;
    }

    try {
      const newTokens = await refreshToken(crmName, tokens.refreshToken);
      await storeTokens(crmName, newTokens);
      return newTokens.access_token;
    } catch (error) {
      console.error('Token refresh failed:', error);
      await removeTokens(crmName);
      setIsAuthenticated(false);
      setUser({ isLoggedIn: false }); // Using context to update user state
      return null;
    }
  }, [setUser]);

  const signOut = useCallback(async (crmName: string) => {
    await removeTokens(crmName);
    setIsAuthenticated(false);
    setUser({ isLoggedIn: false }); // Using context to update user state
  }, [setUser]);

  return { isAuthenticated, handleOAuthCallback, getAccessToken, signOut };
};
