import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  
  // Demographics
  demographics: {
    age: number;
    location: string;
    gender: string;
    occupation: string;
    income: string;
    education: string;
    maritalStatus: string;
  };
  
  // Behavioral patterns
  behaviors: {
    browsingHistory: Array<{
      url: string;
      category: string;
      timeSpent: number;
      timestamp: Date;
    }>;
    clickPatterns: Array<{
      elementType: string;
      position: { x: number; y: number };
      timestamp: Date;
    }>;
    purchaseHistory: Array<{
      product: string;
      category: string;
      amount: number;
      timestamp: Date;
    }>;
    deviceUsage: {
      desktop: number;
      mobile: number;
      tablet: number;
    };
  };
  
  // Psychographic profiling
  psychographics: {
    personality: {
      openness: number;
      conscientiousness: number;
      extraversion: number;
      agreeableness: number;
      neuroticism: number;
    };
    values: string[];
    lifestyle: string[];
    interests: string[];
    motivations: string[];
  };
  
  // Real-time context
  context: {
    currentDevice: 'desktop' | 'mobile' | 'tablet';
    timeOfDay: 'morning' | 'afternoon' | 'evening' | 'night';
    currentMood: string;
    intent: 'browsing' | 'purchasing' | 'researching' | 'entertainment';
    location: string;
    weatherCondition?: string;
  };
  
  // Privacy settings
  privacySettings: {
    dataCollection: boolean;
    personalization: boolean;
    analytics: boolean;
    thirdPartySharing: boolean;
    marketingEmails: boolean;
    profileVisibility: 'public' | 'private' | 'limited';
  };
  
  // Ad preferences
  adPreferences: {
    preferredFormats: string[];
    blockedCategories: string[];
    maxAdsPerDay: number;
    preferredTimes: string[];
  };
}

interface UserStore {
  currentUser: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  setUser: (user: UserProfile) => void;
  updateProfile: (updates: Partial<UserProfile>) => void;
  updateDemographics: (demographics: Partial<UserProfile['demographics']>) => void;
  updateBehaviors: (behaviors: Partial<UserProfile['behaviors']>) => void;
  updatePsychographics: (psychographics: Partial<UserProfile['psychographics']>) => void;
  updateContext: (context: Partial<UserProfile['context']>) => void;
  updatePrivacySettings: (settings: Partial<UserProfile['privacySettings']>) => void;
  addBrowsingHistory: (entry: UserProfile['behaviors']['browsingHistory'][0]) => void;
  addClickPattern: (pattern: UserProfile['behaviors']['clickPatterns'][0]) => void;
  addPurchaseHistory: (purchase: UserProfile['behaviors']['purchaseHistory'][0]) => void;
  logout: () => void;
  setLoading: (loading: boolean) => void;
}

export const useUserStore = create<UserStore>()(
  persist(
    (set, get) => ({
      currentUser: null,
      isAuthenticated: false,
      isLoading: false,
      
      setUser: (user) => set({ currentUser: user, isAuthenticated: true }),
      
      updateProfile: (updates) => set((state) => ({
        currentUser: state.currentUser ? { ...state.currentUser, ...updates } : null
      })),
      
      updateDemographics: (demographics) => set((state) => ({
        currentUser: state.currentUser ? {
          ...state.currentUser,
          demographics: { ...state.currentUser.demographics, ...demographics }
        } : null
      })),
      
      updateBehaviors: (behaviors) => set((state) => ({
        currentUser: state.currentUser ? {
          ...state.currentUser,
          behaviors: { ...state.currentUser.behaviors, ...behaviors }
        } : null
      })),
      
      updatePsychographics: (psychographics) => set((state) => ({
        currentUser: state.currentUser ? {
          ...state.currentUser,
          psychographics: { ...state.currentUser.psychographics, ...psychographics }
        } : null
      })),
      
      updateContext: (context) => set((state) => ({
        currentUser: state.currentUser ? {
          ...state.currentUser,
          context: { ...state.currentUser.context, ...context }
        } : null
      })),
      
      updatePrivacySettings: (settings) => set((state) => ({
        currentUser: state.currentUser ? {
          ...state.currentUser,
          privacySettings: { ...state.currentUser.privacySettings, ...settings }
        } : null
      })),
      
      addBrowsingHistory: (entry) => set((state) => ({
        currentUser: state.currentUser ? {
          ...state.currentUser,
          behaviors: {
            ...state.currentUser.behaviors,
            browsingHistory: [...state.currentUser.behaviors.browsingHistory, entry]
          }
        } : null
      })),
      
      addClickPattern: (pattern) => set((state) => ({
        currentUser: state.currentUser ? {
          ...state.currentUser,
          behaviors: {
            ...state.currentUser.behaviors,
            clickPatterns: [...state.currentUser.behaviors.clickPatterns, pattern]
          }
        } : null
      })),
      
      addPurchaseHistory: (purchase) => set((state) => ({
        currentUser: state.currentUser ? {
          ...state.currentUser,
          behaviors: {
            ...state.currentUser.behaviors,
            purchaseHistory: [...state.currentUser.behaviors.purchaseHistory, purchase]
          }
        } : null
      })),
      
      logout: () => set({ currentUser: null, isAuthenticated: false }),
      
      setLoading: (loading) => set({ isLoading: loading })
    }),
    {
      name: 'user-store',
      partialize: (state) => ({
        currentUser: state.currentUser,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
);
