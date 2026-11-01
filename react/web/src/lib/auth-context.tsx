"use client";

import { createContext, useContext, useEffect, useState } from "react";

type User = {
  role: "farmer" | "buyer" | "guest";
  id: number | null;
  name: string;
  [key: string]: any;
};

type AuthContextType = {
  user: User | null;
  ready: boolean;
  setUser: (user: User | null) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType>({
  user: null,
  ready: false,
  setUser: () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("agriconnect_user");
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        if (parsed?.role && parsed.role !== "guest") {
          setUser(parsed);
        } else {
          localStorage.removeItem("agriconnect_user");
        }
      } catch {
        localStorage.removeItem("agriconnect_user");
      }
    }
    setReady(true);
  }, []);

  useEffect(() => {
    if (user && user.role !== "guest") {
      localStorage.setItem("agriconnect_user", JSON.stringify(user));
    } else {
      localStorage.removeItem("agriconnect_user");
    }
  }, [user]);

  const logout = () => {
    localStorage.removeItem("agriconnect_user");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, ready, setUser, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
