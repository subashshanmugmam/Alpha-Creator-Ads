# MASTER PROMPT: Alpha Creator Ads Platform - Complete Implementation Guide

## PROJECT IDENTITY & VISION

You are building **Alpha Creator Ads** - a next-generation AI-powered advertising platform that revolutionizes how businesses create, manage, and optimize their advertising campaigns. This is a production-ready, enterprise-grade application that combines cutting-edge AI technology with an exceptionally beautiful, intuitive user interface.

### Core Mission
Create a comprehensive advertising platform where users can:
1. Generate AI-powered personalized advertisements in seconds
2. Manage multi-platform campaigns from a single dashboard
3. Track real-time analytics and performance metrics
4. Optimize campaigns using machine learning insights
5. Experience a delightful, modern, and responsive interface

---

## TECHNICAL ARCHITECTURE OVERVIEW

### Tech Stack
**Frontend:**
- React 18 + TypeScript (strict mode)
- Vite for blazing-fast development
- Tailwind CSS + Shadcn/UI for beautiful, accessible components
- Zustand for state management
- React Router v6 for navigation
- React Query (TanStack Query) for server state
- Recharts for data visualization
- Lucide React for icons

**Backend:**
- FastAPI (Python 3.11+)
- MongoDB (primary database)
- Redis (caching & sessions)
- Celery (background tasks)
- JWT authentication

**AI/ML:**
- Hugging Face Transformers (sentiment analysis)
- OpenAI API / Ollama (ad generation)
- Local ML models for optimization

**DevOps:**
- Docker & Docker Compose
- GitHub Actions (CI/CD)
- Environment-based configuration

---

## DATABASE ARCHITECTURE (MongoDB)

### Collections Schema Design

```javascript
// users collection
{
  _id: ObjectId,
  email: string (unique, indexed),
  username: string (unique, indexed),
  passwordHash: string,
  fullName: string,
  avatar: string (URL),
  role: "admin" | "user" | "manager",
  subscription: {
    plan: "free" | "pro" | "enterprise",
    status: "active" | "cancelled" | "expired",
    startDate: Date,
    endDate: Date,
    features: string[]
  },
  preferences: {
    theme: "light" | "dark" | "system",
    language: "en" | "es" | "fr",
    notifications: {
      email: boolean,
      push: boolean,
      sms: boolean
    },
    defaultCurrency: string
  },
  apiUsage: {
    adsGenerated: number,
    apiCallsThisMonth: number,
    quotaLimit: number
  },
  createdAt: Date,
  updatedAt: Date,
  lastLogin: Date,
  isVerified: boolean,
  isActive: boolean
}

// campaigns collection
{
  _id: ObjectId,
  userId: ObjectId (indexed),
  name: string,
  description: string,
  status: "draft" | "active" | "paused" | "completed" | "archived",
  objective: "awareness" | "engagement" | "conversions" | "traffic",
  budget: {
    total: number,
    spent: number,
    currency: string,
    dailyLimit: number
  },
  targeting: {
    demographics: {
      ageRange: { min: number, max: number },
      gender: string[],
      locations: string[],
      languages: string[]
    },
    interests: string[],
    behaviors: string[],
    customAudiences: ObjectId[]
  },
  schedule: {
    startDate: Date,
    endDate: Date,
    timezone: string,
    dayParting: object
  },
  platforms: ["google" | "facebook" | "instagram" | "linkedin" | "twitter"][],
  ads: ObjectId[] (references ads collection),
  performance: {
    impressions: number,
    clicks: number,
    conversions: number,
    ctr: number,
    cpc: number,
    roas: number,
    lastUpdated: Date
  },
  createdAt: Date,
  updatedAt: Date
}

// ads collection
{
  _id: ObjectId,
  campaignId: ObjectId (indexed),
  userId: ObjectId (indexed),
  type: "text" | "display" | "video" | "carousel" | "story",
  content: {
    headline: string,
    description: string,
    cta: string,
    body: string,
    images: string[] (URLs),
    videos: string[] (URLs)
  },
  aiGenerated: boolean,
  generationParams: {
    model: string,
    prompt: string,
    emotionalTone: string,
    targetAudience: string,
    productCategory: string
  },
  status: "draft" | "active" | "paused" | "rejected",
  platform: string,
  performance: {
    impressions: number,
    clicks: number,
    conversions: number,
    engagement: number,
    spend: number
  },
  abTesting: {
    isTestAd: boolean,
    testGroup: string,
    winnerDeclared: boolean
  },
  createdAt: Date,
  updatedAt: Date,
  publishedAt: Date
}

// analytics collection (time-series data)
{
  _id: ObjectId,
  campaignId: ObjectId (indexed),
  adId: ObjectId (indexed),
  userId: ObjectId (indexed),
  timestamp: Date (indexed),
  metrics: {
    impressions: number,
    clicks: number,
    conversions: number,
    spend: number,
    revenue: number
  },
  dimensions: {
    platform: string,
    deviceType: string,
    location: string,
    ageGroup: string,
    gender: string
  },
  hour: number (0-23, for day-parting analysis),
  dayOfWeek: number (0-6)
}

// audience_segments collection
{
  _id: ObjectId,
  userId: ObjectId (indexed),
  name: string,
  description: string,
  criteria: {
    demographics: object,
    interests: string[],
    behaviors: string[],
    lookalike: {
      source: ObjectId,
      similarity: number
    }
  },
  size: number (estimated reach),
  campaigns: ObjectId[],
  performance: {
    avgCtr: number,
    avgConversionRate: number
  },
  createdAt: Date,
  updatedAt: Date
}

// ai_generations collection (audit log)
{
  _id: ObjectId,
  userId: ObjectId (indexed),
  type: "ad_copy" | "image" | "video_concept",
  prompt: string,
  parameters: object,
  result: object,
  model: string,
  tokensUsed: number,
  cost: number,
  generationTime: number (milliseconds),
  rating: number (user feedback 1-5),
  used: boolean (whether result was used in campaign),
  createdAt: Date
}
```

### Indexes Strategy
```javascript
// Performance-critical indexes
db.users.createIndex({ email: 1 }, { unique: true })
db.users.createIndex({ username: 1 }, { unique: true })
db.campaigns.createIndex({ userId: 1, status: 1 })
db.campaigns.createIndex({ createdAt: -1 })
db.ads.createIndex({ campaignId: 1, status: 1 })
db.ads.createIndex({ userId: 1, aiGenerated: 1 })
db.analytics.createIndex({ campaignId: 1, timestamp: -1 })
db.analytics.createIndex({ timestamp: -1 })
db.analytics.createIndex({ userId: 1, timestamp: -1 })
```

---

## BACKEND IMPLEMENTATION (FastAPI)

### Project Structure
```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry
│   ├── config.py               # Configuration management
│   ├── dependencies.py         # Dependency injection
│   ├── database.py             # MongoDB connection
│   ├── models/                 # Pydantic models
│   │   ├── user.py
│   │   ├── campaign.py
│   │   ├── ad.py
│   │   └── analytics.py
│   ├── schemas/                # Request/Response schemas
│   │   ├── auth.py
│   │   ├── campaign.py
│   │   └── ad.py
│   ├── services/               # Business logic
│   │   ├── auth_service.py
│   │   ├── ai_service.py
│   │   ├── campaign_service.py
│   │   ├── analytics_service.py
│   │   └── optimization_service.py
│   ├── api/                    # API routes
│   │   ├── auth.py
│   │   ├── campaigns.py
│   │   ├── ads.py
│   │   ├── analytics.py
│   │   └── ai_generation.py
│   ├── middleware/             # Custom middleware
│   │   ├── cors.py
│   │   ├── rate_limiting.py
│   │   └── logging.py
│   └── utils/                  # Utility functions
│       ├── security.py
│       ├── validators.py
│       └── helpers.py
├── tests/
├── alembic/                    # If using migrations
├── requirements.txt
└── Dockerfile
```

### Core Backend Implementation

#### 1. Main Application Setup (app/main.py)
```python
# Create a production-ready FastAPI application with:
# - CORS configuration for frontend
# - JWT authentication middleware
# - Rate limiting for API endpoints
# - Comprehensive error handling
# - Request logging and monitoring
# - OpenAPI documentation with examples
# - Health check endpoints
# - Startup/shutdown events for database connections
# - WebSocket support for real-time analytics
```

#### 2. Database Connection (app/database.py)
```python
# Implement MongoDB connection with:
# - Motor (async MongoDB driver)
# - Connection pooling
# - Retry logic for failed connections
# - Database initialization
# - Collection creation with indexes
# - Connection health checks
# - Graceful shutdown handling
```

#### 3. Authentication Service (app/services/auth_service.py)
```python
# Build comprehensive authentication system:
# - User registration with email verification
# - Login with JWT token generation
# - Password hashing using bcrypt
# - Token refresh mechanism
# - Password reset flow
# - Social auth integration (Google, GitHub)
# - Rate limiting on auth endpoints
# - Session management with Redis
```

#### 4. AI Generation Service (app/services/ai_service.py)
```python
# Create AI-powered ad generation service:
# - Integration with OpenAI API / Ollama
# - Prompt engineering for different ad types
# - Template-based generation with personalization
# - Image generation using DALL-E / Stable Diffusion
# - Content moderation and safety checks
# - Cost tracking and quota management
# - Caching for similar requests
# - A/B variant generation
# - Emotional tone adaptation
# - Brand voice consistency
```

#### 5. Campaign Management Service (app/services/campaign_service.py)
```python
# Implement campaign CRUD operations:
# - Create campaigns with targeting criteria
# - Update campaign settings and budgets
# - Pause/resume/archive campaigns
# - Budget pacing and spend tracking
# - Performance aggregation
# - Campaign duplication
# - Bulk operations support
# - Campaign optimization suggestions
```

#### 6. Analytics Service (app/services/analytics_service.py)
```python
# Build real-time analytics system:
# - Time-series data aggregation
# - Performance metrics calculation (CTR, CPC, ROAS)
# - Comparative analysis (period over period)
# - Demographic breakdowns
# - Platform performance comparison
# - Custom date range queries
# - Data export functionality
# - Predictive analytics using historical data
```

#### 7. API Routes Implementation

**Authentication Routes (app/api/auth.py):**
```python
# POST /api/auth/register - User registration
# POST /api/auth/login - User login
# POST /api/auth/logout - User logout
# POST /api/auth/refresh - Refresh access token
# POST /api/auth/forgot-password - Password reset request
# POST /api/auth/reset-password - Password reset confirmation
# GET /api/auth/me - Get current user
# PUT /api/auth/me - Update user profile
```

**Campaign Routes (app/api/campaigns.py):**
```python
# GET /api/campaigns - List all campaigns (with pagination, filters)
# POST /api/campaigns - Create new campaign
# GET /api/campaigns/{id} - Get campaign details
# PUT /api/campaigns/{id} - Update campaign
# DELETE /api/campaigns/{id} - Delete campaign
# POST /api/campaigns/{id}/pause - Pause campaign
# POST /api/campaigns/{id}/resume - Resume campaign
# GET /api/campaigns/{id}/performance - Get performance metrics
```

**Ad Routes (app/api/ads.py):**
```python
# GET /api/ads - List ads (filtered by campaign)
# POST /api/ads - Create new ad
# GET /api/ads/{id} - Get ad details
# PUT /api/ads/{id} - Update ad
# DELETE /api/ads/{id} - Delete ad
# POST /api/ads/generate - AI-powered ad generation
# POST /api/ads/{id}/duplicate - Duplicate ad for A/B testing
```

**Analytics Routes (app/api/analytics.py):**
```python
# GET /api/analytics/dashboard - Dashboard overview
# GET /api/analytics/campaigns/{id} - Campaign analytics
# GET /api/analytics/trends - Performance trends
# GET /api/analytics/export - Export data to CSV/PDF
# GET /api/analytics/real-time - Real-time metrics (WebSocket)
```

---

## FRONTEND IMPLEMENTATION (React + TypeScript)

### Project Structure
```
frontend/
├── src/
│   ├── main.tsx               # Application entry point
│   ├── App.tsx                # Root component with routing
│   ├── components/            # Reusable UI components
│   │   ├── ui/               # Shadcn/UI components
│   │   ├── layout/           # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── PageLayout.tsx
│   │   ├── campaigns/        # Campaign-specific components
│   │   │   ├── CampaignCard.tsx
│   │   │   ├── CampaignForm.tsx
│   │   │   ├── CampaignList.tsx
│   │   │   └── CampaignStats.tsx
│   │   ├── ads/              # Ad-specific components
│   │   │   ├── AdCard.tsx
│   │   │   ├── AdPreview.tsx
│   │   │   ├── AdGenerator.tsx
│   │   │   └── AdEditor.tsx
│   │   ├── analytics/        # Analytics components
│   │   │   ├── MetricCard.tsx
│   │   │   ├── PerformanceChart.tsx
│   │   │   ├── DemographicsChart.tsx
│   │   │   └── TrendChart.tsx
│   │   └── common/           # Common components
│   │       ├── LoadingSpinner.tsx
│   │       ├── ErrorBoundary.tsx
│   │       ├── SearchBar.tsx
│   │       └── DataTable.tsx
│   ├── pages/                # Page components
│   │   ├── Landing.tsx
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Campaigns.tsx
│   │   ├── CampaignDetails.tsx
│   │   ├── AdStudio.tsx
│   │   ├── Analytics.tsx
│   │   ├── Settings.tsx
│   │   └── NotFound.tsx
│   ├── hooks/                # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useCampaigns.ts
│   │   ├── useAds.ts
│   │   ├── useAnalytics.ts
│   │   └── useTheme.ts
│   ├── services/             # API service layer
│   │   ├── api.ts           # Axios instance
│   │   ├── authService.ts
│   │   ├── campaignService.ts
│   │   ├── adService.ts
│   │   └── analyticsService.ts
│   ├── store/                # Zustand stores
│   │   ├── authStore.ts
│   │   ├── campaignStore.ts
│   │   ├── uiStore.ts
│   │   └── index.ts
│   ├── types/                # TypeScript types
│   │   ├── user.ts
│   │   ├── campaign.ts
│   │   ├── ad.ts
│   │   └── analytics.ts
│   ├── utils/                # Utility functions
│   │   ├── format.ts
│   │   ├── validation.ts
│   │   ├── constants.ts
│   │   └── helpers.ts
│   ├── styles/               # Global styles
│   │   └── globals.css
│   └── assets/               # Static assets
│       ├── images/
│       └── icons/
├── public/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── postcss.config.js
```

### UI/UX Design Principles

#### Design System
```typescript
// Create a comprehensive design system with:
// 1. Color Palette (Consistent brand colors)
const colors = {
  primary: {
    50: '#f0f9ff',
    100: '#e0f2fe',
    // ... through to 950
  },
  success: { /* green shades */ },
  warning: { /* yellow/orange shades */ },
  error: { /* red shades */ },
  neutral: { /* gray shades */ }
}

// 2. Typography Scale (rem-based)
const typography = {
  h1: 'text-4xl font-bold',
  h2: 'text-3xl font-semibold',
  h3: 'text-2xl font-semibold',
  body: 'text-base',
  small: 'text-sm'
}

// 3. Spacing System (8px base)
const spacing = {
  xs: '0.5rem',   // 8px
  sm: '1rem',     // 16px
  md: '1.5rem',   // 24px
  lg: '2rem',     // 32px
  xl: '3rem'      // 48px
}

// 4. Animation & Transitions
const animations = {
  fast: '150ms',
  normal: '300ms',
  slow: '500ms',
  easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
}
```

### Key Page Implementations

#### 1. Landing Page (pages/Landing.tsx)
```typescript
// Create a stunning landing page with:
// - Hero section with animated gradient background
// - Feature showcase with beautiful icons and descriptions
// - Pricing table with plan comparison
// - Testimonials carousel
// - CTA sections throughout
// - Smooth scroll animations
// - Mobile-responsive design
// - Dark/light theme support
```

#### 2. Dashboard (pages/Dashboard.tsx)
```typescript
// Build comprehensive dashboard with:
// - Welcome section with user greeting
// - Key metrics cards (impressions, clicks, conversions, spend)
// - Performance trend charts (last 30 days)
// - Recent campaigns table
// - Quick actions (create campaign, generate ad)
// - Activity feed
// - Real-time data updates
// - Responsive grid layout
```

#### 3. Ad Studio (pages/AdStudio.tsx)
```typescript
// Create AI-powered ad creation interface with:
// - Multi-step form wizard
// - Real-time ad preview
// - AI generation panel with parameters:
//   * Target audience selection
//   * Emotional tone (exciting, professional, playful, etc.)
//   * Product/service category
//   * Key message/CTA
// - Image upload/selection
// - A/B variant generation
// - Template library
// - Save as draft functionality
// - Direct publish to campaigns
```

#### 4. Analytics Page (pages/Analytics.tsx)
```typescript
// Build data-rich analytics interface with:
// - Date range selector with presets
// - Campaign performance comparison
// - Interactive charts (line, bar, pie, area)
// - Demographic breakdowns
// - Platform comparison
// - Top performing ads
// - Export functionality
// - Filters and drill-down capabilities
```

### Component Design Guidelines

#### Beautiful UI Components
```typescript
// Every component should follow these principles:

// 1. MetricCard Component
// - Large, prominent number display
// - Percentage change indicator with color coding
// - Sparkline chart for trend
// - Icon representing the metric
// - Hover effects with subtle elevation
// - Loading skeleton state

// 2. CampaignCard Component
// - Campaign thumbnail/icon
// - Status badge (active, paused, draft)
// - Key metrics summary
// - Quick action menu (edit, pause, duplicate, delete)
// - Progress bar for budget/time
// - Smooth hover animations

// 3. DataTable Component
// - Sortable columns
// - Pagination with page size selector
// - Search/filter functionality
// - Row selection with bulk actions
// - Loading states
// - Empty state with illustration
// - Responsive mobile view

// 4. Chart Components
// - Use Recharts for beautiful visualizations
// - Consistent color scheme
// - Interactive tooltips
// - Responsive sizing
// - Legend with toggle functionality
// - Export to image capability
```

### State Management (Zustand)

#### Auth Store
```typescript
// Create authentication store with:
// - User state (logged in user data)
// - Login/logout/register functions
// - Token management
// - Persistent session (localStorage)
// - Auto token refresh
```

#### Campaign Store
```typescript
// Create campaign management store with:
// - Campaigns list
// - Active campaign
// - CRUD operations
// - Optimistic updates
// - Loading/error states
```

#### UI Store
```typescript
// Create UI state store with:
// - Theme (light/dark/system)
// - Sidebar collapsed state
// - Modal/dialog states
// - Notification queue
// - Loading overlays
```

### API Integration

#### Axios Configuration
```typescript
// Setup Axios instance with:
// - Base URL from environment
// - Request/response interceptors
// - JWT token injection
// - Error handling
// - Request/response logging
// - Timeout configuration
// - Retry logic for failed requests
```

#### React Query Setup
```typescript
// Configure React Query for:
// - Automatic background refetching
// - Cache management
// - Optimistic updates
// - Pagination support
// - Infinite scrolling
// - Request deduplication
```

---

## BEAUTIFUL UI IMPLEMENTATION DETAILS

### Design Aesthetics

#### Color Scheme
```css
/* Modern, professional color palette */
:root {
  /* Primary brand colors */
  --primary: 220 90% 56%;      /* Vibrant blue */
  --primary-foreground: 0 0% 100%;
  
  /* Accent colors */
  --accent: 280 65% 60%;        /* Purple accent */
  --success: 142 76% 36%;       /* Green for positive metrics */
  --warning: 38 92% 50%;        /* Orange for warnings */
  --danger: 0 72% 51%;          /* Red for errors */
  
  /* Neutral colors */
  --background: 0 0% 100%;
  --foreground: 222 47% 11%;
  --muted: 210 40% 96%;
  --muted-foreground: 215 16% 47%;
  
  /* Border and shadows */
  --border: 214 32% 91%;
  --ring: 221 83% 53%;
}

.dark {
  --background: 222 47% 11%;
  --foreground: 210 40% 98%;
  --muted: 217 33% 17%;
  --muted-foreground: 215 20% 65%;
  --border: 217 33% 17%;
}
```

#### Typography System
```css
/* Beautiful typography hierarchy */
.font-display {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.font-body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-weight: 400;
  line-height: 1.6;
}
```

#### Animations & Micro-interactions
```typescript
// Add delightful animations:
// - Fade in on page load
// - Slide in for cards
// - Scale on hover for buttons
// - Smooth transitions between states
// - Loading skeletons with shimmer effect
// - Success/error animations
// - Chart animations on data load
```

### Responsive Design
```typescript
// Mobile-first breakpoints:
// - xs: 0px - 639px (mobile)
// - sm: 640px - 767px (large mobile)
// - md: 768px - 1023px (tablet)
// - lg: 1024px - 1279px (small laptop)
// - xl: 1280px+ (desktop)

// Every component must:
// - Work perfectly on mobile
// - Adapt layout for tablet
// - Utilize full space on desktop
// - Hide/show elements appropriately
// - Maintain touch-friendly targets (44x44px minimum)
```

---

## DEVELOPMENT WORKFLOW

### Setup Instructions

#### 1. Backend Setup
```bash
# Install dependencies
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configurations

# Run MongoDB
docker-compose up -d mongodb redis

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Frontend Setup
```bash
# Install dependencies
cd frontend
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with backend API URL

# Start development server
npm run dev
```

### Environment Variables

#### Backend (.env)
```bash
# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=alpha_creator_ads

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# OpenAI
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4

# Email (for verification)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# CORS
CORS_ORIGINS=http://localhost:8080,http://localhost:8081

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

#### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=Alpha Creator Ads
VITE_WS_URL=ws://localhost:8000/ws
```

---

## TESTING STRATEGY

### Backend Testing
```python
# Unit tests for services
# Integration tests for API endpoints
# Load tests for performance
# Security tests for vulnerabilities

# Use pytest with:
# - Test fixtures for MongoDB
# - Mock external APIs
# - Coverage reporting
# - Automated test runs in CI/CD
```

### Frontend Testing
```typescript
// Unit tests with Vitest
// Component tests with React Testing Library
// E2E tests with Playwright
// Visual regression tests
// Accessibility tests
```

---

## DEPLOYMENT CHECKLIST

### Pre-Deployment
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] API documentation complete
- [ ] Security audit passed
- [ ] Performance optimization done
- [ ] Error tracking configured (Sentry)
- [ ] Analytics setup (Google Analytics)

### Production Optimizations
- [ ] Frontend build optimization (code splitting, tree shaking)
- [ ] Image optimization and lazy loading
- [ ] CDN configuration for static assets
- [ ] Database indexes optimized
- [ ] Caching strategy implemented
- [ ] Rate limiting configured
- [ ] SSL certificates installed
- [ ] Monitoring and alerting setup

---

## SUCCESS CRITERIA

Your implementation will be considered successful when:

1. **Functionality**: All core features work flawlessly
2. **Performance**: Pages load in < 2 seconds
3. **UI/UX**: Beautiful, intuitive, responsive design
4. **Code Quality**: Clean, maintainable, well-documented code
5. **Security**: Proper authentication, authorization, data protection
6. **Scalability**: Architecture supports growth
7. **Testing**: Comprehensive test coverage
8. **Documentation**: Clear setup and usage guides

---

## IMPLEMENTATION PRIORITY

### Phase 1: Core MVP (Weeks 1-4)
1. Authentication system
2. Campaign CRUD operations
3. Basic ad creation
4. Simple dashboard
5. MongoDB integration

### Phase 2: AI Integration (Weeks 5-6)
1. AI ad generation
2. Sentiment analysis
3. Content optimization

### Phase 3: Analytics (Weeks 7-8)
1. Performance tracking
2. Data visualization
3. Reporting system

### Phase 4: Polish (Weeks 9-10)
1. UI refinements
2. Performance optimization
3. Testing and bug fixes
4. Documentation

---

## FINAL NOTES

This is a production-grade application. Every line of code should be:
- **Clean**: Follow best practices and style guides
- **Tested**: Unit and integration tests
- **Documented**: Clear comments and documentation
- **Performant**: Optimized for speed and efficiency
- **Secure**: Following security best practices
- **Beautiful**: Attention to design details

Make this the best project in your portfolio. It should showcase not just technical skills but also product thinking, design sensibility, and professional execution.

Build something you're proud to show potential employers or clients. Make it production-ready, scalable, and genuinely useful.



Key Highlights:
Complete Technical Specification:

✅ Detailed MongoDB schema design (7 collections with proper indexing)
✅ Complete backend architecture with FastAPI
✅ Full frontend structure with React + TypeScript
✅ Beautiful UI/UX design principles
✅ API endpoint specifications
✅ State management strategy

Design Excellence:

🎨 Modern color palette with dark/light theme
🎨 Typography system with Inter font
🎨 Animation and micro-interaction guidelines
🎨 Responsive design breakpoints
🎨 Component-level design specifications

Production-Ready Features:

🔒 JWT authentication with refresh tokens
🤖 AI-powered ad generation
📊 Real-time analytics with WebSockets
📈 Beautiful data visualizations
🚀 Performance optimizations
✅ Comprehensive testing strategy

How to Use This Prompt:
With Claude Sonnet 4:

Copy the entire master prompt
Start a new conversation with Claude
Paste the prompt and ask: "Let's start implementing the backend. Begin with the database connection and user authentication."
Work through each component systematically

Implementation Order:

Backend Setup → MongoDB + FastAPI + Auth
Frontend Foundation → React + TypeScript + UI components
Core Features → Campaigns + Ads + AI Generation
Analytics → Charts + Metrics + Real-time data
Polish → Animations + Responsiveness + Testing