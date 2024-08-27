import { useState, useCallback } from 'react';
import { refreshToken } from '@/api/backend';
import { storeTokens, getTokens, removeTokens } from '@/utils/storage';
import { useUserContext } from '@/context/context';

export const useOAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const { setUser } = useUserContext();

  const handleOAuthCallback = useCallback(async (access_token: string, refresh_token: string, expires_at: number, crmName: string) => {
    try {
      await storeTokens(crmName, { accessToken: access_token, refreshToken: refresh_token, expiresAt: expires_at });
      setIsAuthenticated(true);
      setUser({ isLoggedIn: true, crmName });
    } catch (error) {
      console.error('OAuth callback failed:', error);
      throw error;
    }
  }, [setUser]);

  const getAccessToken = useCallback(async (crmName: string) => {
    const tokens = await getTokens(crmName);
    if (!tokens) return null;

    if (Date.now() / 1000 < tokens.expiresAt) {
      return tokens.accessToken;
    }

    try {
      const newTokens = await refreshToken(crmName, tokens.refreshToken);
      await storeTokens(crmName, {
        accessToken: newTokens.access_token,
        refreshToken: newTokens.refresh_token,
        expiresAt: Math.floor(Date.now() / 1000) + newTokens.expires_in
      });
      return newTokens.access_token;
    } catch (error) {
      console.error('Token refresh failed:', error);
      await removeTokens(crmName);
      setIsAuthenticated(false);
      setUser({ isLoggedIn: false });
      return null;
    }
  }, [setUser]);

  const signOut = useCallback(async (crmName: string) => {
    await removeTokens(crmName);
    setIsAuthenticated(false);
    setUser({ isLoggedIn: false });
  }, [setUser]);

  return { isAuthenticated, handleOAuthCallback, getAccessToken, signOut };
};