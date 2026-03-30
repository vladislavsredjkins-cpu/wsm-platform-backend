import { createContext, useContext, useState, useEffect } from 'react';
import { login as apiLogin } from './api';
const AuthContext = createContext(null);
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    if (token && savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);
  const login = async (email, password) => {
    const res = await apiLogin(email, password);
    const { access_token, email: userEmail, role, athlete_id, judge_id, organizer_id } = res.data;
    localStorage.setItem('token', access_token);
    const userData = { email: userEmail, role, athlete_id, judge_id, organizer_id };
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
    return userData;
  };
  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };
  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}
export function useAuth() {
  return useContext(AuthContext);
}
