import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';
import type { User } from '../types';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, pass: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  isAdmin: boolean;
  isInventoryManager: boolean;
  isSalesStaff: boolean;
  isAccountant: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('dharma_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('dharma_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const checkAuth = async () => {
      const storedToken = localStorage.getItem('dharma_token');
      if (storedToken) {
        try {
          const res = await api.get('/auth/me');
          setUser(res.data);
          localStorage.setItem('dharma_user', JSON.stringify(res.data));
        } catch {
          logout();
        }
      }
      setIsLoading(false);
    };
    checkAuth();
  }, []);

  const login = async (email: string, pass: string) => {
    const res = await api.post('/auth/login-json', { email, password: pass });
    const { access_token, user: userData } = res.data;
    localStorage.setItem('dharma_token', access_token);
    localStorage.setItem('dharma_user', JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('dharma_token');
    localStorage.removeItem('dharma_user');
    setToken(null);
    setUser(null);
  };

  const role = user?.role;
  const isAdmin = role === 'admin';
  const isInventoryManager = isAdmin || role === 'inventory_manager';
  const isSalesStaff = isAdmin || role === 'sales_staff';
  const isAccountant = isAdmin || role === 'accountant';

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        logout,
        isLoading,
        isAdmin,
        isInventoryManager,
        isSalesStaff,
        isAccountant,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
