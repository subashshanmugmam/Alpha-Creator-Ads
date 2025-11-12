# Alpha Creators Ads - Frontend

Modern React/TypeScript frontend for the Alpha Creators Ads platform - an emotion-aware advertising system.

## 🚀 Tech Stack

- **React 18** - UI framework with hooks and functional components
- **TypeScript** - Type-safe JavaScript development
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework
- **Shadcn/UI** - Modern UI components
- **React Router** - Client-side routing
- **React Query** - Server state management
- **Zustand** - Client state management
- **Chart.js** - Data visualization
- **React Hook Form** - Form handling
- **Zod** - Schema validation

## 📁 Project Structure

```
frontend/
├── public/                 # Static assets
│   ├── favicon.ico
│   ├── placeholder.svg
│   └── robots.txt
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── ui/            # Shadcn/UI components
│   │   ├── AppSidebar.tsx
│   │   ├── Header.tsx
│   │   ├── HeroSection.tsx
│   │   └── ...
│   ├── pages/             # Page components
│   │   ├── auth/          # Authentication pages
│   │   ├── onboarding/    # User onboarding
│   │   ├── Dashboard.tsx
│   │   ├── Campaigns.tsx
│   │   ├── Analytics.tsx
│   │   └── ...
│   ├── hooks/             # Custom React hooks
│   ├── lib/               # Utility functions
│   ├── assets/            # Images and static files
│   ├── App.tsx            # Main application component
│   ├── main.tsx           # Application entry point
│   └── index.css          # Global styles
├── package.json           # Dependencies and scripts
├── vite.config.ts         # Vite configuration
├── tailwind.config.ts     # Tailwind CSS configuration
├── tsconfig.json          # TypeScript configuration
└── README.md              # This file
```

## 🏗️ Features

### 🎯 Core Pages
- **Dashboard** - Campaign overview and metrics
- **Campaign Management** - Create and manage ad campaigns
- **Analytics** - Performance insights and reporting
- **Ad Generation** - AI-powered ad creation
- **Settings** - User preferences and configuration

### 🔐 Authentication
- User registration and login
- JWT token management
- Protected routes
- Session management

### 📊 Analytics Dashboard
- Real-time campaign performance
- Interactive charts and graphs
- ROI and conversion tracking
- Multi-platform metrics

### 🎨 UI/UX Features
- Responsive design for all devices
- Dark/light theme support
- Accessibility compliance
- Modern component library
- Smooth animations and transitions

### 🔄 Real-time Features
- Live campaign updates
- Real-time notifications
- Auto-refreshing metrics
- WebSocket integration

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ or Bun
- Backend API running on http://localhost:8000

### Installation

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd Alpha_Creators_ads/frontend

# Install dependencies
npm install
# or
bun install

# Start development server
npm run dev
# or
bun dev
```

### Development Server
The application will be available at:
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/api/docs

## 📜 Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run type-check   # TypeScript type checking

# Using Bun
bun dev             # Start development server
bun run build       # Build for production
bun run preview     # Preview production build
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the frontend directory:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws

# Authentication
VITE_JWT_SECRET=your-jwt-secret-here
VITE_TOKEN_STORAGE_KEY=alphaads_token

# Features
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_NOTIFICATIONS=true
VITE_ENABLE_DARK_MODE=true

# External Services
VITE_GOOGLE_ANALYTICS_ID=GA-XXXXXXXXX
VITE_SENTRY_DSN=your-sentry-dsn-here

# Development
VITE_DEV_MODE=true
VITE_API_MOCK=false
```

### API Integration
The frontend connects to the backend API for:
- User authentication
- Campaign management
- Analytics data
- Real-time updates

Base API URL: `http://localhost:8000/api/v1`

## 🎨 Styling & Themes

### Tailwind CSS
- Utility-first CSS framework
- Custom color palette for brand consistency
- Responsive design utilities
- Dark mode support

### Component Library
- Shadcn/UI components
- Consistent design system
- Accessible components
- Customizable themes

### Color Palette
```css
/* Primary Colors */
--primary: #3b82f6      /* Blue */
--primary-dark: #1e40af /* Dark Blue */

/* Secondary Colors */
--secondary: #6366f1    /* Indigo */
--accent: #f59e0b       /* Amber */

/* Neutral Colors */
--background: #ffffff   /* White */
--foreground: #0f172a   /* Dark Gray */
--muted: #f1f5f9       /* Light Gray */
```

## 📱 Responsive Design

### Breakpoints
- **Mobile**: 640px and below
- **Tablet**: 641px - 1024px
- **Desktop**: 1025px and above

### Components
All components are designed to be fully responsive with:
- Mobile-first approach
- Touch-friendly interfaces
- Optimized layouts for each screen size

## 🔒 Security

### Authentication Flow
1. User logs in with credentials
2. Backend returns JWT token
3. Token stored securely in localStorage
4. All API requests include Authorization header
5. Token auto-refresh before expiration

### Security Features
- XSS protection
- CSRF protection
- Secure token storage
- Input sanitization
- Route protection

## 📊 State Management

### Zustand Stores
- **AuthStore** - User authentication state
- **CampaignStore** - Campaign data and operations
- **UIStore** - UI state (theme, sidebar, etc.)
- **NotificationStore** - App notifications

### React Query
- Server state caching
- Background updates
- Optimistic updates
- Error handling
- Pagination support

## 🧪 Testing

### Test Structure
```bash
# Unit Tests
npm run test

# E2E Tests
npm run test:e2e

# Coverage Report
npm run test:coverage
```

### Testing Libraries
- **Vitest** - Unit testing framework
- **React Testing Library** - Component testing
- **Playwright** - E2E testing
- **MSW** - API mocking

## 🚀 Deployment

### Build for Production
```bash
# Create production build
npm run build

# Preview production build locally
npm run preview
```

### Deployment Options
- **Vercel** - Recommended for quick deployment
- **Netlify** - Static site hosting
- **AWS S3 + CloudFront** - Scalable hosting
- **Docker** - Containerized deployment

### Docker Deployment
```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🔧 Development Guide

### Adding New Pages
1. Create component in `src/pages/`
2. Add route in `src/App.tsx`
3. Update navigation in `src/components/AppSidebar.tsx`
4. Add TypeScript types if needed

### Adding New Components
1. Create component in `src/components/`
2. Follow naming conventions
3. Add proper TypeScript types
4. Include JSDoc comments
5. Add to component index if reusable

### API Integration
```typescript
// Example API hook
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';

export const useCampaigns = () => {
  return useQuery({
    queryKey: ['campaigns'],
    queryFn: () => api.get('/campaigns'),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};
```

## 📚 Resources

### Documentation
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Shadcn/UI Components](https://ui.shadcn.com/)

### Design System
- Component library documentation
- Design tokens and variables
- Usage guidelines
- Accessibility standards

## 🐛 Troubleshooting

### Common Issues

#### Build Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

#### TypeScript Errors
```bash
# Type check without compilation
npm run type-check

# Restart TypeScript server in VS Code
Ctrl+Shift+P -> "TypeScript: Restart TS Server"
```

#### API Connection Issues
1. Verify backend is running on port 8000
2. Check CORS configuration
3. Verify API base URL in environment variables
4. Check network console for errors

## 🤝 Contributing

### Development Workflow
1. Create feature branch
2. Make changes with proper TypeScript types
3. Add/update tests
4. Run linting and type checking
5. Create pull request

### Code Standards
- Use TypeScript for all new code
- Follow ESLint and Prettier rules
- Write descriptive component and function names
- Add JSDoc comments for complex functions
- Maintain responsive design standards

---

## 📞 Support

For frontend-related issues:
1. Check the troubleshooting section above
2. Review browser console for errors
3. Verify API connectivity
4. Check component documentation

**Frontend Version**: Latest stable as of September 2025
**Compatibility**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
