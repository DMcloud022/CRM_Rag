import React, { createContext, useContext, useState, ReactNode } from 'react';

interface UserContextType {
    isLoggedIn: boolean;
    crmName: string;
    setUser: (user: Partial<UserContextType>) => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

interface UserProviderProps {
    children: ReactNode;
}

export const UserProvider: React.FC<UserProviderProps> = ({ children }) => {
    const [user, setUserState] = useState<UserContextType>({
        isLoggedIn: false,
        crmName: '',
        setUser: (userData: Partial<UserContextType>) => {
            setUserState(prevState => ({
                ...prevState,
                ...userData,
            }));
        },
    });

    return (
        <UserContext.Provider value={user}>
            {children}
        </UserContext.Provider>
    );
};

export const useUserContext = () => {
    const context = useContext(UserContext);
    if (context === undefined) {
        throw new Error('useUserContext must be used within a UserProvider');
    }
    return context;
};
