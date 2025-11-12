// MongoDB initialization script
// Creates the alpha creator ads database and initial collections

use('alphacreator_ads');

// Create collections with initial structure
db.createCollection('users');
db.createCollection('campaigns');
db.createCollection('ads');
db.createCollection('analytics');
db.createCollection('ai_generations');
db.createCollection('campaign_optimizations');

// Create indexes for better performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "username": 1 }, { unique: true });
db.campaigns.createIndex({ "userId": 1 });
db.campaigns.createIndex({ "status": 1 });
db.ads.createIndex({ "campaignId": 1 });
db.ads.createIndex({ "userId": 1 });
db.analytics.createIndex({ "campaignId": 1, "timestamp": 1 });

// Insert sample data
db.users.insertOne({
  email: "demo@alphacreatorads.com",
  username: "demouser",
  fullName: "Demo User",
  role: "user",
  subscription: {
    plan: "professional",
    status: "active",
    startDate: new Date(),
    endDate: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000)
  },
  preferences: {
    theme: "light",
    language: "en",
    notifications: { email: true, push: true },
    defaultCurrency: "USD"
  },
  apiUsage: {
    adsGenerated: 25,
    apiCallsThisMonth: 150,
    quotaLimit: 1000
  },
  createdAt: new Date(),
  updatedAt: new Date(),
  isVerified: true,
  isActive: true
});

print("✅ Alpha Creator Ads database initialized successfully!");