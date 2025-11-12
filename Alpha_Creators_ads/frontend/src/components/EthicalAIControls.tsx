import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/hooks/use-toast';
import {
  Shield,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Eye,
  EyeOff,
  Users,
  Globe,
  Brain,
  Zap,
  Target,
  TrendingUp,
  Settings,
  Info,
  RefreshCw
} from 'lucide-react';
import { useAIStore } from '@/stores/aiStore';
import { useUserStore } from '@/stores/userStore';

interface EthicalAIControlsProps {
  className?: string;
}

export const EthicalAIControls: React.FC<EthicalAIControlsProps> = ({ className }) => {
  const { toast } = useToast();
  
  const {
    ethicalCompliance,
    biasDetections,
    biasMonitoringEnabled,
    availableModels,
    activeModels,
    usage,
    detectBias,
    checkCompliance,
    enableBiasMonitoring,
    disableBiasMonitoring,
    moderateContent,
    setActiveModel
  } = useAIStore();
  
  const { currentUser, updatePrivacySettings } = useUserStore();
  
  const [testContent, setTestContent] = useState('');
  const [isTestingBias, setIsTestingBias] = useState(false);
  const [complianceSettings, setComplianceSettings] = useState({
    gdprEnabled: true,
    ccpaEnabled: true,
    coppaEnabled: true,
    accessibilityLevel: 'AA',
    inclusivityTarget: 85,
    biasThreshold: 0.3
  });
  
  // Monitor compliance scores
  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate compliance monitoring
      if (biasMonitoringEnabled) {
        // This would typically check recent AI generations
        console.log('Running ethical AI monitoring...');
      }
    }, 60000); // Every minute
    
    return () => clearInterval(interval);
  }, [biasMonitoringEnabled]);
  
  const handleBiasTest = async () => {
    if (!testContent.trim()) {
      toast({
        title: "No Content",
        description: "Please enter content to test for bias.",
        variant: "destructive"
      });
      return;
    }
    
    setIsTestingBias(true);
    
    try {
      const biases = await detectBias(testContent);
      
      if (biases.length === 0) {
        toast({
          title: "Bias Check Complete",
          description: "No bias detected in the content.",
        });
      } else {
        toast({
          title: "Bias Detected",
          description: `Found ${biases.length} potential bias issue(s).`,
          variant: "destructive"
        });
      }
    } catch (error) {
      toast({
        title: "Bias Test Failed",
        description: "Failed to analyze content for bias.",
        variant: "destructive"
      });
    } finally {
      setIsTestingBias(false);
    }
  };
  
  const handleComplianceCheck = async () => {
    if (!testContent.trim()) {
      toast({
        title: "No Content",
        description: "Please enter content to check compliance.",
        variant: "destructive"
      });
      return;
    }
    
    try {
      await checkCompliance(testContent, ['gdpr', 'ccpa', 'coppa']);
      toast({
        title: "Compliance Check Complete",
        description: "Content has been analyzed for compliance.",
      });
    } catch (error) {
      toast({
        title: "Compliance Check Failed",
        description: "Failed to check content compliance.",
        variant: "destructive"
      });
    }
  };
  
  const getComplianceColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };
  
  const getComplianceIcon = (isCompliant: boolean) => {
    return isCompliant ? (
      <CheckCircle className="h-4 w-4 text-green-600" />
    ) : (
      <XCircle className="h-4 w-4 text-red-600" />
    );
  };
  
  const getBiasScoreColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };
  
  return (
    <div className={`w-full max-w-6xl mx-auto space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Shield className="h-8 w-8 text-green-600" />
            Ethical AI Controls
          </h1>
          <p className="text-muted-foreground mt-1">
            Monitor and control AI ethics, bias, and compliance
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <Badge variant={biasMonitoringEnabled ? "default" : "secondary"}>
            {biasMonitoringEnabled ? "Monitoring Active" : "Monitoring Disabled"}
          </Badge>
          <Switch
            checked={biasMonitoringEnabled}
            onCheckedChange={(checked) => 
              checked ? enableBiasMonitoring() : disableBiasMonitoring()
            }
          />
        </div>
      </div>
      
      {/* Compliance Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Bias Score</p>
                <p className={`text-2xl font-bold ${getComplianceColor(ethicalCompliance.biasScore)}`}>
                  {ethicalCompliance.biasScore}/100
                </p>
              </div>
              <div className={`h-12 w-12 rounded-full ${getBiasScoreColor(ethicalCompliance.biasScore)} flex items-center justify-center`}>
                <Brain className="h-6 w-6 text-white" />
              </div>
            </div>
            <Progress value={ethicalCompliance.biasScore} className="mt-3" />
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Accessibility</p>
                <p className={`text-2xl font-bold ${getComplianceColor(ethicalCompliance.accessibilityScore)}`}>
                  {ethicalCompliance.accessibilityScore}/100
                </p>
              </div>
              <Eye className="h-8 w-8 text-blue-600" />
            </div>
            <Progress value={ethicalCompliance.accessibilityScore} className="mt-3" />
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Inclusivity</p>
                <p className={`text-2xl font-bold ${getComplianceColor(ethicalCompliance.inclusivityScore)}`}>
                  {ethicalCompliance.inclusivityScore}/100
                </p>
              </div>
              <Users className="h-8 w-8 text-purple-600" />
            </div>
            <Progress value={ethicalCompliance.inclusivityScore} className="mt-3" />
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Issues Found</p>
                <p className={`text-2xl font-bold ${biasDetections.length > 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {biasDetections.length}
                </p>
              </div>
              <AlertTriangle className={`h-8 w-8 ${biasDetections.length > 0 ? 'text-red-600' : 'text-green-600'}`} />
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Compliance Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Globe className="h-5 w-5" />
            Regulatory Compliance
          </CardTitle>
          <CardDescription>
            Current compliance status with major regulations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <h4 className="font-semibold">GDPR</h4>
                <p className="text-sm text-muted-foreground">EU Data Protection</p>
              </div>
              {getComplianceIcon(ethicalCompliance.gdprCompliant)}
            </div>
            
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <h4 className="font-semibold">CCPA</h4>
                <p className="text-sm text-muted-foreground">California Privacy</p>
              </div>
              {getComplianceIcon(ethicalCompliance.ccpaCompliant)}
            </div>
            
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <h4 className="font-semibold">COPPA</h4>
                <p className="text-sm text-muted-foreground">Children's Privacy</p>
              </div>
              {getComplianceIcon(ethicalCompliance.coppaCompliant)}
            </div>
          </div>
          
          <div className="mt-4 text-sm text-muted-foreground">
            Last audit: {ethicalCompliance.lastAudit.toLocaleDateString()}
          </div>
        </CardContent>
      </Card>
      
      {/* Bias Detection Issues */}
      {biasDetections.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-orange-600">
              <AlertTriangle className="h-5 w-5" />
              Detected Issues
            </CardTitle>
            <CardDescription>
              Recent bias and ethical issues found in content
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {biasDetections.slice(0, 5).map((bias, index) => (
                <Alert key={index} className={`${
                  bias.severity === 'critical' ? 'border-red-500' :
                  bias.severity === 'high' ? 'border-orange-500' :
                  bias.severity === 'medium' ? 'border-yellow-500' :
                  'border-blue-500'
                }`}>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge variant={
                            bias.severity === 'critical' ? 'destructive' :
                            bias.severity === 'high' ? 'destructive' :
                            bias.severity === 'medium' ? 'default' :
                            'secondary'
                          }>
                            {bias.severity}
                          </Badge>
                          <span className="text-sm font-medium capitalize">{bias.type} Bias</span>
                        </div>
                        <p className="text-sm mb-2">{bias.description}</p>
                        <p className="text-sm font-medium text-green-700">{bias.suggestion}</p>
                        <div className="flex gap-1 mt-2">
                          {bias.affectedGroups.map((group, i) => (
                            <Badge key={i} variant="outline" className="text-xs">
                              {group}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {bias.detectedAt.toLocaleDateString()}
                      </div>
                    </div>
                  </AlertDescription>
                </Alert>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Tools and Testing */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Bias Testing Tool
            </CardTitle>
            <CardDescription>
              Test content for potential bias before publishing
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="test-content">Content to Test</Label>
              <Textarea
                id="test-content"
                placeholder="Enter ad copy, messaging, or content to test for bias..."
                value={testContent}
                onChange={(e) => setTestContent(e.target.value)}
                className="min-h-[100px]"
              />
            </div>
            
            <div className="flex gap-2">
              <Button
                onClick={handleBiasTest}
                disabled={isTestingBias || !testContent.trim()}
                className="flex-1"
              >
                {isTestingBias ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Testing...
                  </>
                ) : (
                  <>
                    <Brain className="h-4 w-4 mr-2" />
                    Test for Bias
                  </>
                )}
              </Button>
              <Button
                variant="outline"
                onClick={handleComplianceCheck}
                disabled={!testContent.trim()}
              >
                <Shield className="h-4 w-4 mr-2" />
                Check Compliance
              </Button>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              AI Model Settings
            </CardTitle>
            <CardDescription>
              Configure AI models for ethical performance
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Text Generation Model</Label>
              <Select 
                value={activeModels.text || ''} 
                onValueChange={(value) => setActiveModel('text', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select text model" />
                </SelectTrigger>
                <SelectContent>
                  {availableModels
                    .filter(model => model.type === 'text')
                    .map(model => (
                      <SelectItem key={model.id} value={model.id}>
                        {model.name} - Bias Score: {model.performance?.accuracy || 'N/A'}
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>Image Generation Model</Label>
              <Select 
                value={activeModels.image || ''} 
                onValueChange={(value) => setActiveModel('image', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select image model" />
                </SelectTrigger>
                <SelectContent>
                  {availableModels
                    .filter(model => model.type === 'image')
                    .map(model => (
                      <SelectItem key={model.id} value={model.id}>
                        {model.name} - Reliability: {model.performance?.reliability || 'N/A'}
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="pt-4 border-t">
              <h4 className="font-medium mb-3">Usage Limits</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Daily Requests</span>
                  <span>{usage.requestsToday} / {usage.dailyLimit}</span>
                </div>
                <Progress value={(usage.requestsToday / usage.dailyLimit) * 100} />
                <div className="flex justify-between">
                  <span>Total Cost</span>
                  <span>${usage.totalCost.toFixed(2)}</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Privacy Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <EyeOff className="h-5 w-5" />
            Privacy Controls
          </CardTitle>
          <CardDescription>
            Manage user privacy and data protection settings
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="data-collection" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="data-collection">Data Collection</TabsTrigger>
              <TabsTrigger value="consent">Consent Management</TabsTrigger>
              <TabsTrigger value="retention">Data Retention</TabsTrigger>
            </TabsList>
            
            <TabsContent value="data-collection" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h4 className="font-medium">Behavioral Tracking</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="browsing-history">Browsing History</Label>
                      <Switch
                        id="browsing-history"
                        checked={currentUser?.privacySettings?.dataCollection || false}
                        onCheckedChange={(checked) => 
                          updatePrivacySettings({ dataCollection: checked })
                        }
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <Label htmlFor="click-tracking">Click Tracking</Label>
                      <Switch
                        id="click-tracking"
                        checked={currentUser?.privacySettings?.analytics || false}
                        onCheckedChange={(checked) => 
                          updatePrivacySettings({ analytics: checked })
                        }
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <Label htmlFor="purchase-history">Purchase History</Label>
                      <Switch
                        id="purchase-history"
                        checked={currentUser?.privacySettings?.dataCollection || false}
                        onCheckedChange={(checked) => 
                          updatePrivacySettings({ dataCollection: checked })
                        }
                      />
                    </div>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <h4 className="font-medium">Data Sharing</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="third-party">Third-party Sharing</Label>
                      <Switch
                        id="third-party"
                        checked={currentUser?.privacySettings?.thirdPartySharing || false}
                        onCheckedChange={(checked) => 
                          updatePrivacySettings({ thirdPartySharing: checked })
                        }
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <Label htmlFor="analytics">Analytics Data</Label>
                      <Switch
                        id="analytics"
                        checked={currentUser?.privacySettings?.analytics || false}
                        onCheckedChange={(checked) => 
                          updatePrivacySettings({ analytics: checked })
                        }
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <Label htmlFor="personalization">Personalization</Label>
                      <Switch
                        id="personalization"
                        checked={currentUser?.privacySettings?.personalization || false}
                        onCheckedChange={(checked) => 
                          updatePrivacySettings({ personalization: checked })
                        }
                      />
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>
            
            <TabsContent value="consent" className="space-y-4">
              <div className="space-y-4">
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertDescription>
                    Consent management ensures compliance with GDPR, CCPA, and other privacy regulations.
                  </AlertDescription>
                </Alert>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium mb-3">Consent Status</h4>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between p-2 border rounded">
                        <span className="text-sm">Marketing Cookies</span>
                        <Badge variant={currentUser?.privacySettings?.marketingEmails ? "default" : "secondary"}>
                          {currentUser?.privacySettings?.marketingEmails ? "Granted" : "Denied"}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between p-2 border rounded">
                        <span className="text-sm">Analytics Cookies</span>
                        <Badge variant={currentUser?.privacySettings?.analytics ? "default" : "secondary"}>
                          {currentUser?.privacySettings?.analytics ? "Granted" : "Denied"}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between p-2 border rounded">
                        <span className="text-sm">Functional Cookies</span>
                        <Badge variant={currentUser?.privacySettings?.dataCollection ? "default" : "secondary"}>
                          {currentUser?.privacySettings?.dataCollection ? "Granted" : "Denied"}
                        </Badge>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-medium mb-3">Data Rights</h4>
                    <div className="space-y-2">
                      <Button variant="outline" size="sm" className="w-full justify-start">
                        <Eye className="h-4 w-4 mr-2" />
                        View My Data
                      </Button>
                      <Button variant="outline" size="sm" className="w-full justify-start">
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Update Preferences
                      </Button>
                      <Button variant="outline" size="sm" className="w-full justify-start text-red-600">
                        <XCircle className="h-4 w-4 mr-2" />
                        Delete My Data
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>
            
            <TabsContent value="retention" className="space-y-4">
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <Label htmlFor="retention-period">Data Retention Period</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select retention period" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="30days">30 days</SelectItem>
                        <SelectItem value="90days">90 days</SelectItem>
                        <SelectItem value="1year">1 year</SelectItem>
                        <SelectItem value="2years">2 years</SelectItem>
                        <SelectItem value="indefinite">Indefinite</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div>
                    <Label htmlFor="auto-delete">Auto-delete Inactive Data</Label>
                    <Switch
                      id="auto-delete"
                      checked={currentUser?.privacySettings?.dataCollection || false}
                      onCheckedChange={(checked) => 
                        updatePrivacySettings({ dataCollection: checked })
                      }
                    />
                  </div>
                </div>
                
                <div className="pt-4 border-t">
                  <h4 className="font-medium mb-3">Data Categories</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Profile Data</span>
                      <span>Retained indefinitely</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Behavioral Data</span>
                      <span>90 days</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Campaign Data</span>
                      <span>2 years</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Analytics Data</span>
                      <span>1 year</span>
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default EthicalAIControls;
