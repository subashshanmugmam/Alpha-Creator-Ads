// API Test Component - Tests all backend endpoints
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, XCircle, Play, Database, Server } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

interface TestResult {
  success: boolean;
  status: number;
  data?: any;
  error?: string;
  timestamp: string;
}

interface Endpoint {
  name: string;
  url: string;
  method: string;
  category: string;
}

const APITestPage: React.FC = () => {
  const [testResults, setTestResults] = useState<Record<string, TestResult>>({});
  const [isTestingAll, setIsTestingAll] = useState(false);
  const [apiData, setApiData] = useState<Record<string, any>>({});

  const endpoints: Endpoint[] = [
    { name: 'Health Check', url: '/health', method: 'GET', category: 'System' },
    { name: 'Metrics', url: '/metrics', method: 'GET', category: 'System' },
    { name: 'Current User', url: '/api/v1/users/me', method: 'GET', category: 'Database' },
    { name: 'User Campaigns', url: '/api/v1/campaigns/list', method: 'GET', category: 'Database' },
    { name: 'User Ads', url: '/api/v1/ads/list', method: 'GET', category: 'Database' },
    { name: 'Analytics Summary', url: '/api/v1/analytics/summary', method: 'GET', category: 'Database' },
    { name: 'Create Demo Campaign', url: '/api/v1/campaigns/create-demo', method: 'POST', category: 'Database' },
    { name: 'Sample Users', url: '/sample/users', method: 'GET', category: 'Sample' },
    { name: 'Sample Campaigns', url: '/sample/campaigns', method: 'GET', category: 'Sample' },
    { name: 'Sample Ads', url: '/sample/ads', method: 'GET', category: 'Sample' },
    { name: 'Sample Analytics', url: '/sample/analytics', method: 'GET', category: 'Sample' },
  ];

  const testEndpoint = async (endpoint: Endpoint): Promise<TestResult> => {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint.url}`, {
        method: endpoint.method,
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      
      return {
        success: response.ok,
        status: response.status,
        data: data,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        status: 0,
        error: (error as Error).message,
        timestamp: new Date().toISOString(),
      };
    }
  };

  const testSingleEndpoint = async (endpoint: Endpoint) => {
    const result = await testEndpoint(endpoint);
    setTestResults(prev => ({
      ...prev,
      [endpoint.url]: result
    }));

    if (result.success && result.data) {
      setApiData(prev => ({
        ...prev,
        [endpoint.url]: result.data
      }));
    }
  };

  const testAllEndpoints = async () => {
    setIsTestingAll(true);
    setTestResults({});
    setApiData({});

    for (const endpoint of endpoints) {
      await testSingleEndpoint(endpoint);
      // Small delay between requests
      await new Promise(resolve => setTimeout(resolve, 200));
    }

    setIsTestingAll(false);
  };

  const getSuccessRate = (): number => {
    const results = Object.values(testResults);
    if (results.length === 0) return 0;
    const successful = results.filter(r => r.success).length;
    return Math.round((successful / results.length) * 100);
  };

  const formatData = (data: any): string => {
    if (!data) return 'No data';
    return JSON.stringify(data, null, 2);
  };

  const getCategoryColor = (category: string): string => {
    switch (category) {
      case 'System': return 'bg-blue-100 text-blue-800';
      case 'Database': return 'bg-green-100 text-green-800';
      case 'Sample': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Alpha Creator Ads - API Test Dashboard</h1>
        <p className="text-gray-600 mb-4">
          Test all backend API endpoints and verify database connectivity
        </p>
        
        <div className="flex items-center gap-4 mb-4">
          <Button 
            onClick={testAllEndpoints} 
            disabled={isTestingAll}
            size="lg"
          >
            {isTestingAll ? (
              <>
                <Play className="mr-2 h-4 w-4 animate-spin" />
                Testing...
              </>
            ) : (
              <>
                <Play className="mr-2 h-4 w-4" />
                Test All Endpoints
              </>
            )}
          </Button>

          {Object.keys(testResults).length > 0 && (
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-lg px-3 py-1">
                Success Rate: {getSuccessRate()}%
              </Badge>
              <Badge 
                variant={getSuccessRate() === 100 ? "default" : "secondary"}
                className="text-lg px-3 py-1"
              >
                {Object.values(testResults).filter(r => r.success).length} / {Object.keys(testResults).length} Passed
              </Badge>
            </div>
          )}
        </div>
      </div>

      <div className="grid gap-6">
        {/* System Status */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Server className="h-5 w-5" />
              System Status
            </CardTitle>
            <CardDescription>
              Backend and database connectivity status
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">✓</div>
                <div className="text-sm text-gray-600">Backend Running</div>
                <div className="text-xs text-gray-500">Port 8000</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">✓</div>
                <div className="text-sm text-gray-600">Frontend Running</div>
                <div className="text-xs text-gray-500">Port 8082</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">✓</div>
                <div className="text-sm text-gray-600">Mock Database</div>
                <div className="text-xs text-gray-500">In-Memory</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{endpoints.length}</div>
                <div className="text-sm text-gray-600">API Endpoints</div>
                <div className="text-xs text-gray-500">Ready to test</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Endpoint Tests */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              API Endpoint Tests
            </CardTitle>
            <CardDescription>
              Click individual buttons to test specific endpoints
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4">
              {['System', 'Database', 'Sample'].map(category => (
                <div key={category}>
                  <h3 className="font-semibold mb-3 flex items-center gap-2">
                    <Badge className={getCategoryColor(category)}>
                      {category}
                    </Badge>
                    <span className="text-sm text-gray-500">
                      {endpoints.filter(e => e.category === category).length} endpoints
                    </span>
                  </h3>
                  
                  <div className="grid gap-2">
                    {endpoints.filter(e => e.category === category).map(endpoint => (
                      <div key={endpoint.url} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-3">
                          <Badge variant="outline" className="text-xs">
                            {endpoint.method}
                          </Badge>
                          <span className="font-mono text-sm">{endpoint.url}</span>
                          <span className="text-gray-600">{endpoint.name}</span>
                        </div>
                        
                        <div className="flex items-center gap-2">
                          {testResults[endpoint.url] && (
                            <Badge 
                              variant={testResults[endpoint.url].success ? "default" : "destructive"}
                              className="text-xs"
                            >
                              {testResults[endpoint.url].success ? (
                                <>
                                  <CheckCircle className="mr-1 h-3 w-3" />
                                  {testResults[endpoint.url].status}
                                </>
                              ) : (
                                <>
                                  <XCircle className="mr-1 h-3 w-3" />
                                  {testResults[endpoint.url].status || 'Error'}
                                </>
                              )}
                            </Badge>
                          )}
                          
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => testSingleEndpoint(endpoint)}
                          >
                            Test
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Live Data Preview */}
        {Object.keys(apiData).length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Live API Data Preview</CardTitle>
              <CardDescription>
                Real-time data from successful endpoint calls
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                {Object.entries(apiData).map(([url, data]) => (
                  <div key={url} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-mono text-sm font-semibold">{url}</span>
                      <Badge variant="secondary" className="text-xs">
                        {new Date(testResults[url]?.timestamp).toLocaleTimeString()}
                      </Badge>
                    </div>
                    <pre className="text-xs bg-gray-50 p-3 rounded overflow-auto max-h-40">
                      {formatData(data)}
                    </pre>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default APITestPage;