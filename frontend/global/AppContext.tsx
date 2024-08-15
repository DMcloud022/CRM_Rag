import React, { createContext, useState, useContext, ReactNode } from 'react';

interface AppContextState {
  user: string | null;
  setUser: (user: string | null) => void;
  appIsReady: boolean
  setAppIsReady: (appIsReady: boolean) => void
}

const AppContext = createContext<AppContextState | undefined>(undefined);

export const AppProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<string | null>(null);
  const [appIsReady, setAppIsReady] = useState<boolean>(false);

  return (
    <AppContext.Provider value={{ user, setUser, appIsReady, setAppIsReady }}>
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};
