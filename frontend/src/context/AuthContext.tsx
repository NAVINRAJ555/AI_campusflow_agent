import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, UserRole } from '../types';
import { authApi } from '../services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: any) => Promise<void>;
  logout: () => void;
  hasRole: (roles: UserRole[]) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const savedUser = localStorage.getItem('cf_user');
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('cf_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const verifyUser = async () => {
      if (token) {
        try {
          const res = await authApi.getMe();
          setUser(res.data);
          localStorage.setItem('cf_user', JSON.stringify(res.data));
        } catch (err) {
          logout();
        }
      }
      setIsLoading(false);
    };
    verifyUser();
  }, [token]);

  const login = async (email: string, password: string) => {
    const res = await authApi.login({ email, password });
    const { access_token, user_id, name, role, department_id } = res.data;
    setToken(access_token);
    localStorage.setItem('cf_token', access_token);

    const currentUser: User = {
      id: user_id,
      name,
      email,
      role,
      department_id,
      created_at: new Date().toISOString()
    };
    setUser(currentUser);
    localStorage.setItem('cf_user', JSON.stringify(currentUser));
  };

  const register = async (userData: any) => {
    await authApi.register(userData);
    await login(userData.email, userData.password);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('cf_token');
    localStorage.removeItem('cf_user');
  };

  const hasRole = (roles: UserRole[]): boolean => {
    if (!user) return false;
    return roles.includes(user.role);
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, register, logout, hasRole }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
