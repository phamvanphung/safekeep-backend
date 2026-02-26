import React, { createContext, useContext, useEffect, useState } from "react";

interface AuthContextValue {
  isAuthenticated: boolean;
  email: string | null;
  accessToken: string | null;
  login: (token: string, email: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [email, setEmail] = useState<string | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem("access_token");
    const storedEmail = localStorage.getItem("user_email");
    if (storedToken) {
      setAccessToken(storedToken);
    }
    if (storedEmail) {
      setEmail(storedEmail);
    }
  }, []);

  const login = (token: string, userEmail: string) => {
    setAccessToken(token);
    setEmail(userEmail);
    localStorage.setItem("access_token", token);
    localStorage.setItem("user_email", userEmail);
  };

  const logout = () => {
    setAccessToken(null);
    setEmail(null);
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_email");
  };

  const value: AuthContextValue = {
    isAuthenticated: Boolean(accessToken),
    email,
    accessToken,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}

