#!/usr/bin/env python3

import os
from extract_solution import extract_solution

llm_response = """
```tsx
// src/App.tsx
import React, { JSX } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { StudentLayout } from "./components/StudentLayout";
import { AdminLayout } from "./components/AdminLayout";
import { StudentLogin } from "./pages/student/StudentLogin";
import { MyClasses } from "./pages/student/MyClasses";
import { RegisterClass } from "./pages/student/RegisterClass";
import { AdminLogin } from "./pages/admin/AdminLogin";
import { AdminDashboard } from "./pages/admin/AdminDashboard";
import { NewClass } from "./pages/admin/NewClass";
import { EditClass } from "./pages/admin/EditClass";

const RedirectIfLoggedIn: React.FC<{children: JSX.Element; role: "student" | "admin";}> = ({ children, role }) => {
  const { isAuthenticated, userRole } = useAuth();
  if (isAuthenticated && userRole === role) return <Navigate to={role === "student" ? "/" : "/admin"} replace />;
  return children;
};

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<RedirectIfLoggedIn role="student"><StudentLogin /></RedirectIfLoggedIn>} />
      <Route element={<StudentLayout />}>
        <Route path="/" element={<MyClasses />} />
        <Route path="/register-class" element={<RegisterClass />} />
      </Route>
      <Route path="/admin/login" element={<RedirectIfLoggedIn role="admin"><AdminLogin /></RedirectIfLoggedIn>} />
      <Route path="/admin" element={<AdminLayout />}>
        <Route index element={<AdminDashboard />} />
        <Route path="new-class" element={<NewClass />} />
        <Route path="edit-class/:classId" element={<EditClass />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return <BrowserRouter><AuthProvider><AppRoutes /></AuthProvider></BrowserRouter>;
}

export default App;
```

```tsx
// src/main.tsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

```typescript
// src/types.ts
export interface Attachment {
  name: string;
  url: string;
}

export interface Class {
  id: string;
  title: string;
  instructor: string;
  schedule: string;
  room: string;
  attachments: Attachment[];
}

export interface UserCredentials {
  email: string;
  password: string;
}
```

```tsx
// src/contexts/AuthContext.tsx
import React, { createContext, useState, useContext, ReactNode, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { students, admins } from "../data.ts";
import { UserCredentials } from "../types";

type Role = "student" | "admin" | null;

interface AuthContextType {
  isAuthenticated: boolean;
  userRole: Role;
  login: (credentials: UserCredentials, role: "student" | "admin") => boolean;
  logout: () => void;
}

const AUTH_STORAGE_KEY = 'auth_state';

interface StoredAuthState {
  isAuthenticated: boolean;
  userRole: Role;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [userRole, setUserRole] = useState<Role>(null);
  const navigate = useNavigate();
  const location = useLocation();

  // Only restore auth state from localStorage, no navigation
  useEffect(() => {
    const storedAuth = localStorage.getItem(AUTH_STORAGE_KEY);
    if (storedAuth) {
      const { isAuthenticated: storedIsAuth, userRole: storedRole } = JSON.parse(storedAuth) as StoredAuthState;
      setIsAuthenticated(storedIsAuth);
      setUserRole(storedRole);
    }
  }, []);

  useEffect(() => {
    const isLoginPage = location.pathname === '/login' || location.pathname === '/admin/login';
    
    if (isLoginPage && isAuthenticated && userRole) {
      navigate(userRole === "student" ? "/" : "/admin");
    }
  }, [isAuthenticated, userRole, location.pathname, navigate]);

  const login = (
    credentials: UserCredentials,
    role: "student" | "admin"
  ): boolean => {
    const users = role === "student" ? students : admins;
    const user = users.find(
      (u) =>
        u.email === credentials.email && u.password === credentials.password
    );

    if (user) {
      const newAuthState = {
        isAuthenticated: true,
        userRole: role
      };
      
      setIsAuthenticated(true);
      setUserRole(role);
      localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(newAuthState));
      
      navigate(role === "student" ? "/" : "/admin");
      return true;
    } else {
      setIsAuthenticated(false);
      setUserRole(null);
      localStorage.removeItem(AUTH_STORAGE_KEY);
      return false;
    }
  };

  const logout = () => {
    const previousRole = userRole;
    setIsAuthenticated(false);
    setUserRole(null);
    localStorage.removeItem(AUTH_STORAGE_KEY);
    navigate(previousRole === "student" ? "/login" : "/admin/login");
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, userRole, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
```

```tsx
// src/components/LoginForm.tsx
import React, { useState, FormEvent } from "react";
import { useAuth } from "../contexts/AuthContext";
import {BookOpenIcon, ShieldCheckIcon, AtSymbolIcon, LockClosedIcon, ExclamationCircleIcon, ArrowRightEndOnRectangleIcon, ArrowPathIcon} from "@heroicons/react/24/outline";

interface LoginFormProps {role: "student" | "admin";}

export const LoginForm: React.FC<LoginFormProps> = ({ role }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    setTimeout(() => {
      const success = login({ email, password }, role);
      if (!success) setError("Wrong credentials");
      setIsLoading(false);
    }, 600);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-gray-50 to-gray-100">
      <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden w-full max-w-md">
        <div className={`${role === "student" ? "bg-gradient-to-r from-indigo-500 to-indigo-700" : "bg-gradient-to-r from-purple-500 to-purple-700"} p-6 text-center`}>
          <div className="bg-white/20 w-16 h-16 mx-auto rounded-full flex items-center justify-center mb-3">
            {role === "student" ? (<BookOpenIcon className="h-8 w-8 text-white" />) : (<ShieldCheckIcon className="h-8 w-8 text-white" />)}
          </div>
          <h1 className="text-2xl font-bold text-white capitalize">{role} Login</h1>
          <p className="text-white/80 text-sm mt-1">Enter your credentials to access the {role} portal</p>
        </div>
        <div className="p-6">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <AtSymbolIcon className="h-5 w-5 text-gray-400" />
                </div>
                <input type="email" id="email" value={email} onChange={(e) => setEmail(e.target.value)} required
                  placeholder="your@email.com"
                  className="w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors" />
              </div>
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <LockClosedIcon className="h-5 w-5 text-gray-400" />
                </div>
                <input type="password" id="password" value={password} onChange={(e) => setPassword(e.target.value)} required
                  placeholder="••••••••"
                  className="w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors" />
              </div>
            </div>
            {error && (
              <div className="bg-red-50 border-l-4 border-red-500 p-3 rounded-md flex items-center">
                <ExclamationCircleIcon className="h-5 w-5 text-red-500 mr-2" />
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            )}
            <button type="submit" id="login" disabled={isLoading}
              className={`w-full ${role === "student" ? "bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800" 
                : "bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800"} text-white py-2.5 px-4 rounded-lg hover:shadow-lg transition-all duration-200 font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 ${
                role === "student" ? "focus:ring-indigo-500" : "focus:ring-purple-500"} flex items-center justify-center`}>
              {isLoading ? (<><ArrowPathIcon className="animate-spin h-5 w-5 mr-3 text-white" />Authenticating...</>) 
                : (<><ArrowRightEndOnRectangleIcon className="h-5 w-5 mr-2" />Login</>)}
            </button>
            <div className="text-center mt-4">
              <p className="text-sm text-gray-600">
                {role === "student" ? (<>Are you an administrator? <a href="/admin/login" className="text-indigo-600 hover:text-indigo-800 font-medium">Admin Login</a></>) 
                  : (<>Are you a student? <a href="/login" className="text-purple-600 hover:text-purple-800 font-medium">Student Login</a></>)}
              </p>
            </div>
          </form>
        </div>
      </div>
      <div className="mt-8 text-center text-sm text-gray-500">
        <p>© {new Date().getFullYear()} Student Portal. All rights reserved.</p>
      </div>
    </div>
  );
};
```

```tsx
// src/components/ClassForm.tsx
import React, { useState, ChangeEvent, FormEvent, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { BookOpenIcon, CloudArrowUpIcon, CheckCircleIcon, DocumentTextIcon, ArrowPathIcon } from "@heroicons/react/24/outline";
import { saveClass, getClassById } from "../services/classService";

interface FormData {title: string; instructor: string; schedule: string; room: string;}
interface FormErrors {title?: string; instructor?: string; schedule?: string; room?: string;}
interface ClassFormProps {mode: 'new' | 'edit'; classId?: string;}

export const ClassForm: React.FC<ClassFormProps> = ({ mode, classId }) => {
  const navigate = useNavigate();
  const initialFormData: FormData = { title: "", instructor: "", schedule: "", room: "" };
  const initialTouched = { title: false, instructor: false, schedule: false, room: false };
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [files, setFiles] = useState<FileList | null>(null);
  const [errors, setErrors] = useState<FormErrors>({});
  const [touched, setTouched] = useState(initialTouched);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    if (mode === 'edit' && classId) {
      const loadClass = async () => {
        const classData = await getClassById(classId);
        if (classData) {
          setFormData({
            title: classData.title,
            instructor: classData.instructor,
            schedule: classData.schedule,
            room: classData.room
          });
        }
      };
      loadClass();
    }
  }, [mode, classId]);

  const validateField = (name: keyof FormData, value: string): string | undefined => {
    if (!value.trim()) return `${name.charAt(0).toUpperCase() + name.slice(1)} cannot be blank`;
    return undefined;
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};
    let isValid = true;
    Object.keys(formData).forEach((key) => {
      const fieldName = key as keyof FormData;
      const error = validateField(fieldName, formData[fieldName]);
      if (error) {
        newErrors[fieldName] = error;
        isValid = false;
      }
    });
    setErrors(newErrors);
    return isValid;
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target as { name: keyof FormData; value: string };
    setFormData(prev => ({ ...prev, [name]: value }));
    if (touched[name]) {
      const error = validateField(name, value);
      setErrors(prev => ({ ...prev, [name]: error }));
    }
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target as { name: keyof FormData; value: string };
    setTouched(prev => ({ ...prev, [name]: true }));
    const error = validateField(name, value);
    setErrors(prev => ({ ...prev, [name]: error }));
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    setFiles(e.target.files);
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setTouched(Object.keys(formData).reduce((acc, key) => ({ ...acc, [key]: true }), {} as typeof touched));
    if (!validateForm()) return;
    setIsSubmitting(true);
    setSuccessMessage(null);
    try {
      const response = await saveClass({ ...formData, id: classId });
      if (response.success) {
        if (mode === 'new') {
          setSuccessMessage('New class saved successfully.');
        } else {
          setSuccessMessage('Class updates saved successfully.');
        }
        
        if (mode === 'new') {
          setFormData(initialFormData);
          setFiles(null);
          setErrors({});
          setTouched(initialTouched);
          const fileInput = document.getElementById("files") as HTMLInputElement;
          if (fileInput) fileInput.value = "";
        }
        
        setTimeout(() => navigate('/admin'), 1000);
      }
    } catch (error) {
      console.error("Error saving class:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const isFormValid = () => Object.values(formData).every(value => value.trim() !== '');

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">{mode === 'new' ? 'New Class' : 'Edit Class'}</h1>
      <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
        <div className="bg-gradient-to-r from-purple-500 to-purple-700 p-4">
          <h2 className="text-xl font-bold text-white flex items-center">
            <BookOpenIcon className="h-5 w-5 mr-2" />Class Information
          </h2>
        </div>
        <div className="p-6">
          <form onSubmit={handleSubmit} className="space-y-5">
            {['title', 'instructor', 'schedule', 'room'].map((field) => (
              <div key={field}>
                <label htmlFor={field} className="block text-sm font-medium text-gray-700 mb-1">
                  {field.charAt(0).toUpperCase() + field.slice(1)}
                </label>
                <input
                  type="text" id={field} name={field}
                  value={formData[field as keyof FormData]}
                  onChange={handleChange} onBlur={handleBlur} required
                  placeholder={field === 'schedule' ? 'e.g., Mon/Wed 10:00 AM - 11:30 AM' : field === 'room' ? 'e.g., Building C, Room 201' : ''}
                  className={`w-full px-4 py-2.5 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-colors ${
                    touched[field as keyof FormData] && errors[field as keyof FormData] ? "border-red-500 bg-red-50" : "border-gray-300"}`}
                />
                {touched[field as keyof FormData] && errors[field as keyof FormData] && (
                  <span id={`${field}-error`} className="text-red-500 text-xs mt-1 block">{errors[field as keyof FormData]}</span>
                )}
              </div>
            ))}
            <div className="bg-gray-50 p-4 rounded-lg">
              <label htmlFor="files" className="block text-sm font-medium text-gray-700 mb-3">
                Course Materials <span className="text-gray-500 text-xs">(PDF only, optional)</span>
              </label>
              <div className="flex flex-col space-y-3">
                <div className="flex items-center">
                  <input 
                    type="file" 
                    id="files" 
                    multiple 
                    accept=".pdf" 
                    onChange={handleFileChange} 
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4
                      file:rounded-full file:border-0 file:text-sm file:font-semibold
                      file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100
                      cursor-pointer focus:outline-none" 
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">Select one or more PDF files (max 2MB each)</p>
              </div>
              {files && files.length > 0 && (
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Selected Files ({files.length})</h3>
                  <ul className="bg-white rounded-lg border border-gray-200 overflow-hidden">
                    {Array.from(files).map((file, index) => (
                      <li key={index} className="px-3 py-2 border-b border-gray-200 last:border-b-0 text-sm flex items-center">
                        <DocumentTextIcon className="h-4 w-4 text-purple-500 mr-2" />{file.name}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            {successMessage && (
              <div id="success-message" className="p-4 bg-green-100 border-l-4 border-green-500 text-green-700 rounded-lg flex items-center animate-pulse">
                <CheckCircleIcon className="h-5 w-5 mr-2 text-green-500" />{successMessage}
              </div>
            )}
            <div className="pt-3">
              <button
                type="submit" disabled={!isFormValid() || isSubmitting}
                className={`w-full font-bold py-2.5 px-4 rounded-lg transition-all duration-200 ${
                  isFormValid() && !isSubmitting
                    ? "bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
                    : "bg-gray-200 text-gray-500 cursor-not-allowed"}`}
              >
                {isSubmitting ? (
                  <div className="flex items-center justify-center">
                    <ArrowPathIcon className="animate-spin h-5 w-5 mr-2 text-white" />Saving...
                  </div>
                ) : (`Save Class`)}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
```

```tsx
// src/components/StudentSidebar.tsx
import React from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import {
  BookOpenIcon,
  UserCircleIcon,
  ChevronRightIcon,
  AcademicCapIcon,
  ArrowRightStartOnRectangleIcon
} from "@heroicons/react/24/outline";

export const StudentSidebar: React.FC = () => {
  const { logout } = useAuth();

  const activeClassName = "bg-indigo-600 text-white";
  const inactiveClassName =
    "text-indigo-100 hover:bg-indigo-700/50 hover:text-white";
  const commonClasses =
    "group flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-all duration-200";

  return (
    <div className="w-64 bg-gradient-to-b from-indigo-800 to-indigo-900 text-white flex flex-col min-h-screen shadow-xl">
      <div className="flex items-center justify-center h-20 flex-shrink-0 border-b border-indigo-700/50">
        <div className="flex items-center space-x-2">
          <div className="p-2 bg-white rounded-lg">
            <AcademicCapIcon className="h-6 w-6 text-indigo-700" />
          </div>
          <span className="text-xl font-bold tracking-wide">Student Portal</span>
        </div>
      </div>
      
      <div className="px-4 py-6">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-indigo-300 mb-3">
          Main Menu
        </h3>
        <nav className="flex-1 space-y-2">
          <NavLink
            id="my-classes"
            to="/"
            end
            className={({ isActive }) =>
              `${commonClasses} ${isActive ? activeClassName : inactiveClassName}`
            }
          >
            <BookOpenIcon className="h-5 w-5 mr-3" />
            My Classes
            <span className="ml-auto transform transition-transform duration-200 group-hover:translate-x-1">
              <ChevronRightIcon className="h-4 w-4" />
            </span>
          </NavLink>
        </nav>
      </div>
      
      <div className="mt-auto">
        <div className="px-4 py-2 border-t border-indigo-700/50">
          <div className="flex items-center px-3 py-3 mb-3 rounded-lg bg-indigo-700/30">
            <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center mr-3">
              <UserCircleIcon className="h-4 w-4 text-white" />
            </div>
            <div className="text-sm">
              <p className="font-medium text-white">Student</p>
              <p className="text-xs text-indigo-200">Active</p>
            </div>
          </div>
          
          <button
            id="logout"
            onClick={logout}
            className="flex items-center w-full px-4 py-3 text-sm font-medium text-indigo-100 hover:text-white rounded-lg transition-colors duration-200 hover:bg-red-500/20 group"
          >
            <ArrowRightStartOnRectangleIcon className="h-5 w-5 mr-3 text-indigo-300 group-hover:text-red-300" />
            Logout
          </button>
        </div>
      </div>
    </div>
  );
};
```

```tsx
// src/components/ClassCard.tsx
import React from "react";
import { Class, Attachment } from "../types";
import {UserIcon, CalendarIcon, BuildingOfficeIcon, DocumentTextIcon, ArrowDownTrayIcon, XCircleIcon} from "@heroicons/react/24/outline";

interface ClassCardProps {classData: Class; onDropOut?: (classId: string) => void; showDropOut?: boolean;}

export const ClassCard: React.FC<ClassCardProps> = ({classData, onDropOut, showDropOut = false}) => {
  const handleDownload = (attachment: Attachment) => {
    const pdfUrl = '/dummy.pdf';
    const link = document.createElement("a");
    link.href = pdfUrl;
    link.download = attachment.name || 'course-material.pdf';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden transition-all duration-300 hover:shadow-xl hover:border-indigo-100 transform hover:-translate-y-1">
      <div className="bg-gradient-to-r from-indigo-500 to-indigo-700 p-4 flex justify-between items-center">
        <h3 className="text-xl font-bold text-white">{classData.title}</h3>
        {showDropOut && onDropOut && 
          <button onClick={() => onDropOut(classData.id)} className="text-white hover:text-red-200 transition-colors duration-200 flex items-center gap-1 text-sm font-medium" aria-label={`Drop out of ${classData.title}`}>
            <XCircleIcon className="h-5 w-5" /><span>Drop Out</span>
          </button>
        }
      </div>
      <div className="p-5">
        <div className="grid grid-cols-1 gap-3 mb-4">
          <div className="flex items-center">
            <div className="text-indigo-500 mr-2"><UserIcon className="h-5 w-5" /></div>
            <p className="text-gray-700"><span className="font-medium text-gray-900">Instructor:</span> {classData.instructor}</p>
          </div>
          <div className="flex items-center">
            <div className="text-indigo-500 mr-2"><CalendarIcon className="h-5 w-5" /></div>
            <p className="text-gray-700"><span className="font-medium text-gray-900">Schedule:</span> {classData.schedule}</p>
          </div>
          <div className="flex items-center">
            <div className="text-indigo-500 mr-2"><BuildingOfficeIcon className="h-5 w-5" /></div>
            <p className="text-gray-700"><span className="font-medium text-gray-900">Room:</span> {classData.room}</p>
          </div>
        </div>
        {classData.attachments.length > 0 && 
          <div className="mt-4 border-t border-gray-100 pt-4">
            <h4 className="text-sm uppercase tracking-wider text-gray-500 font-semibold mb-2">Course Materials</h4>
            <ul className="space-y-2">
              {classData.attachments.map((att, index) => 
                <li key={index} className="flex items-center">
                  <DocumentTextIcon className="h-4 w-4 text-indigo-400 mr-2" />
                  <button onClick={() => handleDownload(att)} className="text-indigo-600 hover:text-indigo-800 text-sm font-medium transition-colors duration-200 group flex items-center" aria-label={`Download ${att.name}`}>
                    {att.name}
                    <span className="ml-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                      <ArrowDownTrayIcon className="h-4 w-4" />
                    </span>
                  </button>
                </li>
              )}
            </ul>
          </div>
        }
      </div>
    </div>
  );
};
```

```tsx
// src/components/AdminLayout.tsx
import React, { useState, useEffect } from "react";
import { Outlet, Navigate, NavLink } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { ArrowRightStartOnRectangleIcon, HomeIcon } from "@heroicons/react/24/outline";

export const AdminLayout: React.FC = () => {
  const { isAuthenticated, userRole, logout } = useAuth();
  const [isLoading, setIsLoading] = useState(true);

  // Wait for auth state to be restored from localStorage
  useEffect(() => {
    const storedAuth = localStorage.getItem('auth_state');
    if (storedAuth) {
      // Give a moment for the auth context to process the stored auth
      const timer = setTimeout(() => {
        setIsLoading(false);
      }, 100);
      return () => clearTimeout(timer);
    } else {
      setIsLoading(false);
    }
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || userRole !== "admin") {
    return <Navigate to="/admin/login" replace />;
  }

  const activeClassName = "bg-purple-700 text-white";
  const inactiveClassName = "text-purple-100 hover:bg-purple-600 hover:text-white";
  const commonClasses =
    "px-3 py-2 rounded-md text-sm font-medium transition-colors duration-150 flex items-center";

  return (
    <div className="min-h-screen flex flex-col">
      <nav className="bg-gradient-to-r from-purple-800 to-purple-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <span className="font-bold text-lg mr-6">Admin Portal</span>
              <div className="flex space-x-4">
                <NavLink
                  to="/admin"
                  end
                  className={({ isActive }) =>
                    `${commonClasses} ${
                      isActive ? activeClassName : inactiveClassName
                    }`
                  }
                >
                  <HomeIcon className="h-4 w-4 mr-2" />
                  Dashboard
                </NavLink>
              </div>
            </div>
            <div>
              <button
                id="logout"
                onClick={logout}
                className={`${commonClasses} ${inactiveClassName}`}
              >
                <ArrowRightStartOnRectangleIcon className="h-4 w-4 mr-2" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>
      <main className="flex-1 p-6 lg:p-8 bg-gray-50">
        <Outlet />
      </main>
    </div>
  );
};
```

```tsx
// src/components/StudentLayout.tsx
import React, { useEffect, useState } from "react";
import { Outlet, Navigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { StudentSidebar } from "./StudentSidebar";

export const StudentLayout: React.FC = () => {
  const { isAuthenticated, userRole } = useAuth();
  const [isLoading, setIsLoading] = useState(true);

  // Wait for auth state to be restored from localStorage
  useEffect(() => {
    const storedAuth = localStorage.getItem('auth_state');
    if (storedAuth) {
      const timer = setTimeout(() => {
        setIsLoading(false);
      }, 100);
      return () => clearTimeout(timer);
    } else {
      setIsLoading(false);
    }
  }, []);

  if (isLoading) {
    return null;
  }

  if (!isLoading && (!isAuthenticated || userRole !== "student")) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="flex min-h-screen">
      <StudentSidebar />
      <main className="flex-1 p-6 lg:p-8 bg-gray-100 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
};
```

```tsx
// src/pages/student/StudentLogin.tsx
import React from "react";
import { LoginForm } from "../../components/LoginForm";

export const StudentLogin: React.FC = () => {
  return <LoginForm role="student" />;
};
```

```tsx
// src/pages/student/RegisterClass.tsx
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Class } from "../../types";
import { getClasses } from "../../services/classService";
import {ArchiveBoxIcon, ClipboardDocumentCheckIcon, XMarkIcon, ExclamationTriangleIcon, ArrowPathIcon} from "@heroicons/react/24/outline";

const STORAGE_KEY = 'registered_classes';
const fetchRegisteredClassIds = (): string[] => JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');

export const RegisterClass: React.FC = () => {
  const [allAvailableClasses, setAllAvailableClasses] = useState<Class[]>([]);
  const [selectedClasses, setSelectedClasses] = useState<Class[]>([]);
  const [registeredClassIds, setRegisteredClassIds] = useState<Set<string>>(new Set());
  const [isRegistering, setIsRegistering] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const loadData = async () => {
      const classes = await getClasses();
      setAllAvailableClasses(classes);
      setRegisteredClassIds(new Set(fetchRegisteredClassIds()));
    };
    loadData();
  }, []);

  const handleSelectClass = (cls: Class, isSelected: boolean) => {
    setSelectedClasses(prev => isSelected ? [...prev, cls] : prev.filter(c => c.id !== cls.id));
  };

  const handleRemoveSelected = (classId: string) => {
    setSelectedClasses(prev => prev.filter(c => c.id !== classId));
  };

  const handleRegister = () => {
    if (selectedClasses.length === 0) return;
    setIsRegistering(true);
    
    const currentRegisteredIds = fetchRegisteredClassIds();
    const newRegisteredIds = [...currentRegisteredIds, ...selectedClasses.map(c => c.id)];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newRegisteredIds));
    setRegisteredClassIds(new Set(newRegisteredIds));
    setSelectedClasses([]);
    setIsRegistering(false);

    const successMessage = document.getElementById('success-message');
    if (successMessage) {
      successMessage.classList.remove('hidden');
      setTimeout(() => successMessage.classList.add('hidden'), 3000);
    }

    const refreshClasses = async () => {
      const classes = await getClasses();
      setAllAvailableClasses(classes);
    };
    refreshClasses();
  };

  const availableForSelection = allAvailableClasses.filter(cls => !registeredClassIds.has(cls.id));

  return (
    <div className="max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Register Class</h1>
        <div id="success-message" className="hidden bg-green-100 border-l-4 border-green-500 text-green-700 p-2 px-4 rounded animate-pulse">
          Classes registered successfully!
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
          <div className="bg-gradient-to-r from-indigo-500 to-indigo-700 p-4">
            <h2 className="text-xl font-bold text-white flex items-center">
              <ArchiveBoxIcon className="h-5 w-5 mr-2" />Available Classes
            </h2>
          </div>
          
          <div className="p-4">
            <div className="bg-gray-50 rounded-lg mb-3 p-3 text-sm text-gray-600">
              Select classes you want to register. View your selections on the right.
            </div>

            <div className="overflow-x-auto bg-white shadow-sm rounded-lg">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-16">Select</th>
                    <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Class</th>
                    <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Instructor</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {availableForSelection.map(cls => {
                    const isRegistered = registeredClassIds.has(cls.id);
                    const isSelected = selectedClasses.some(c => c.id === cls.id);
                    return (
                      <tr key={cls.id} className={`group transition-colors hover:bg-indigo-50 ${isRegistered ? "opacity-60 registered" : ""}`}>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <div className="flex items-center justify-center">
                            <input type="checkbox" className="h-5 w-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500 transition-all cursor-pointer"
                              checked={isSelected} onChange={e => handleSelectClass(cls, e.target.checked)}
                              disabled={isRegistered} aria-label={`Select ${cls.title}`}/>
                          </div>
                        </td>
                        <td className={`px-4 py-4 whitespace-nowrap text-sm font-medium ${isRegistered ? "registered text-gray-400 line-through" : "text-gray-800 group-hover:text-indigo-700"}`}>
                          {cls.title}
                        </td>
                        <td className={`px-4 py-4 whitespace-nowrap text-sm ${isRegistered ? "registered text-gray-400 line-through" : "text-gray-500 group-hover:text-gray-700"}`}>
                          {cls.instructor}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
              {availableForSelection.length === 0 && 
                <div className="text-center py-8">
                  <ExclamationTriangleIcon className="h-12 w-12 mx-auto text-gray-300 mb-3" />
                  <p className="text-gray-500 font-medium">No classes available for registration.</p>
                </div>
              }
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden flex flex-col">
          <div className="bg-gradient-to-r from-purple-500 to-purple-700 p-4">
            <h2 className="text-xl font-bold text-white flex items-center">
              <ClipboardDocumentCheckIcon className="h-5 w-5 mr-2" />Selected for Registration
            </h2>
          </div>
          
          <div className="p-5 flex-grow flex flex-col">
            <div className="flex-grow mb-4">
              {selectedClasses.length > 0 ? 
                <ul className="space-y-2">
                  {selectedClasses.map(cls => 
                    <li key={cls.id} className="flex justify-between items-center bg-gray-50 p-3 rounded-lg hover:bg-gray-100 transition-colors border border-gray-100 shadow-sm">
                      <span className="text-gray-800 font-medium">{cls.title}</span>
                      <button onClick={() => handleRemoveSelected(cls.id)} className="flex items-center text-red-500 hover:text-red-700 hover:bg-red-50 rounded-full p-1 transition-colors duration-200" aria-label={`Remove ${cls.title}`}>
                        <XMarkIcon className="h-5 w-5" />
                        <span className="ml-1 text-sm font-medium">Remove</span>
                      </button>
                    </li>
                  )}
                </ul> : 
                <div className="flex flex-col items-center justify-center h-full py-10">
                  <ClipboardDocumentCheckIcon className="h-16 w-16 text-gray-200 mb-4" />
                  <p className="text-center text-gray-500 italic">No class selected</p>
                </div>
              }
            </div>
            
            <button id="register" onClick={handleRegister}
              disabled={selectedClasses.length === 0 || isRegistering}
              className={`w-full font-bold py-3 px-4 rounded-lg transition-all duration-200 ease-in-out flex items-center justify-center ${
                selectedClasses.length > 0 && !isRegistering
                  ? "bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white shadow-md hover:shadow-lg transform hover:-translate-y-1"
                  : "bg-gray-200 text-gray-400 cursor-not-allowed"
              }`}>
              {isRegistering ? 
                <><ArrowPathIcon className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" />Processing...</> : 
                <>Register Selected Classes</>
              }
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
```

```tsx
// src/pages/student/MyClasses.tsx
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { ClassCard } from "../../components/ClassCard";
import { Class } from "../../types";
import { getClasses } from "../../services/classService";

const STORAGE_KEY = 'registered_classes';

const fetchRegisteredClasses = async (): Promise<Class[]> => {
  const registeredIds = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
  if (registeredIds.length === 0) return [];
  
  const allClasses = await getClasses();
  return allClasses.filter(cls => registeredIds.includes(cls.id));
};

export const MyClasses: React.FC = () => {
  const [registeredClasses, setRegisteredClasses] = useState<Class[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    const loadRegistered = async () => {
      const classes = await fetchRegisteredClasses();
      setRegisteredClasses(classes);
    };
    loadRegistered();
  }, []);

  const handleDropOut = (classId: string) => {
    const registeredIds = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    const updatedIds = registeredIds.filter((id: string) => id !== classId);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedIds));
    setRegisteredClasses(prev => prev.filter(cls => cls.id !== classId));
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">My Classes</h1>
        <button id="register-class" onClick={() => navigate("/register-class")}
          className="bg-indigo-600 hover:bg-indigo-700 hover:cursor-pointer text-white font-bold py-2 px-4 rounded transition duration-150 ease-in-out">
          Register Class
        </button>
      </div>
      {registeredClasses.length > 0 ? 
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {registeredClasses.map(cls => 
            <ClassCard key={cls.id} classData={cls} onDropOut={handleDropOut} showDropOut={true} />
          )}
        </div> : 
        <p className="text-center text-gray-600 mt-8">No registered class</p>
      }
    </div>
  );
};
```

```tsx
// src/pages/admin/EditClass.tsx
import React from "react";
import { useParams } from "react-router-dom";
import { ClassForm } from "../../components/ClassForm";

export const EditClass: React.FC = () => {
  const { classId } = useParams<{ classId: string }>();
  return <ClassForm mode="edit" classId={classId} />;
};
```

```tsx
// src/pages/admin/AdminLogin.tsx
import React from "react";
import { LoginForm } from "../../components/LoginForm";

export const AdminLogin: React.FC = () => {
  return <LoginForm role="admin" />;
};
```

```tsx
// src/pages/admin/NewClass.tsx
import React from "react";
import { ClassForm } from "../../components/ClassForm";

export const NewClass: React.FC = () => {
  return <ClassForm mode="new" />;
};
```

```tsx
// src/pages/admin/AdminDashboard.tsx
import React, { useState, useEffect } from "react";
import { Class } from "../../types";
import { getClasses, deleteClass } from "../../services/classService";
import { useNavigate } from "react-router-dom";
import { EyeIcon, PencilIcon, TrashIcon, PlusIcon } from "@heroicons/react/24/outline";

export const AdminDashboard: React.FC = () => {
  const [classes, setClasses] = useState<Class[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchAndSetClasses = async () => {
      const data = await getClasses();
      setClasses(data);
    };
    fetchAndSetClasses();
  }, []);

  const handleDelete = async (classId: string) => {
    try {
      await deleteClass(classId);
      // Refresh the classes list after successful deletion
      const updatedClasses = await getClasses();
      setClasses(updatedClasses);
    } catch (error) {
      console.error('Error deleting class:', error);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Dashboard</h1>
        <button id="new-class" onClick={() => navigate("/admin/new-class")} className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md flex items-center transition-colors duration-150">
          <PlusIcon className="h-5 w-5 mr-2" />New Class
        </button>
      </div>
      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-purple-50">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-purple-600 uppercase tracking-wider">Class</th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-purple-600 uppercase tracking-wider">Instructor</th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-purple-600 uppercase tracking-wider">Schedule</th>
              <th scope="col" className="px-6 py-3 text-center text-xs font-medium text-purple-600 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {classes.map((cls) => (
              <tr key={cls.id} className="hover:bg-purple-50 transition-colors duration-150">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{cls.title}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{cls.instructor}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{cls.schedule}</td>
                <td className="px-6 py-4 whitespace-nowrap text-center text-sm font-medium">
                  <button id={`edit-${cls.id}`} onClick={() => navigate(`/admin/edit-class/${cls.id}`)} className="text-yellow-600 hover:text-yellow-900 mr-3 focus:outline-none" title="Edit Class">
                    <PencilIcon className="h-5 w-5 inline" />
                  </button>
                  <button id={`delete-${cls.id}`} onClick={() => handleDelete(cls.id)} className="text-red-600 hover:text-red-900 focus:outline-none" title="Delete Class">
                    <TrashIcon className="h-5 w-5 inline" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {classes.length === 0 && (<p className="text-center text-gray-500 py-4">No classes found.</p>)}
      </div>
    </div>
  );
};
```

```typescript
// src/services/classService.ts
import { Class } from "../types";
import { allClasses as defaultClasses } from "../data";

// Storage key for localStorage
const CLASSES_STORAGE_KEY = 'all_classes';

// Load classes from localStorage or return default classes
const loadClassesFromStorage = (): Class[] => {
  try {
    const stored = localStorage.getItem(CLASSES_STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (error) {
    console.error('Error loading classes from localStorage:', error);
  }
  // If no stored classes or error, return default classes and save them
  saveClassesToStorage(defaultClasses);
  return defaultClasses;
};

// Save classes to localStorage
const saveClassesToStorage = (classes: Class[]): void => {
  try {
    localStorage.setItem(CLASSES_STORAGE_KEY, JSON.stringify(classes));
  } catch (error) {
    console.error('Error saving classes to localStorage:', error);
  }
};

// Initialize classes from localStorage
let allClasses = loadClassesFromStorage();

export const getClasses = async () => {
  await new Promise(resolve => setTimeout(resolve, 100));
  // Always reload from localStorage to get latest data
  allClasses = loadClassesFromStorage();
  return allClasses;
};

export const getClassById = async (id: string): Promise<Class | undefined> => {
  await new Promise(resolve => setTimeout(resolve, 100));
  // Always reload from localStorage to get latest data
  allClasses = loadClassesFromStorage();
  return allClasses.find(cls => cls.id === id);
};

export const saveClass = async (classData: Partial<Class> & { id?: string }): Promise<{ success: boolean }> => {
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Always reload from localStorage to get latest data
  allClasses = loadClassesFromStorage();
  
  if (classData.id) {
    // Update existing class
    const index = allClasses.findIndex(cls => cls.id === classData.id);
    if (index !== -1) {
      allClasses[index] = { ...allClasses[index], ...classData };
    }
  } else {
    // Create new class
    const newClass: Class = {
      id: `class_${Date.now()}`,
      title: classData.title!,
      instructor: classData.instructor!,
      schedule: classData.schedule!,
      room: classData.room!,
      attachments: []
    };
    allClasses.push(newClass);
  }
  
  // Save updated classes to localStorage
  saveClassesToStorage(allClasses);
  return { success: true };
};

export const deleteClass = async (classId: string): Promise<{ success: boolean }> => {
  await new Promise(resolve => setTimeout(resolve, 100));
  
  // Always reload from localStorage to get latest data
  allClasses = loadClassesFromStorage();
  
  // Remove the class from the array
  allClasses = allClasses.filter(cls => cls.id !== classId);
  
  // Save updated classes to localStorage
  saveClassesToStorage(allClasses);
  return { success: true };
}; 
```



"""

try:
    response = extract_solution(llm_response=llm_response)

    if not isinstance(response, list):
        raise ValueError("Expected response to be a list of (file_name, code) tuples.")

    for item in response:
        if not isinstance(item, tuple) or len(item) != 2:
            raise ValueError("Invalid tuple.")

        file_name, code = item

        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_name) or ".", exist_ok=True)

        # Write or create the file
        with open(file_name, "w") as file:
            file.write(code)

        print(f"File '{file_name}' written successfully.")

except Exception as e:
    print(f"An error occurred while running extract solution test: {e}")
