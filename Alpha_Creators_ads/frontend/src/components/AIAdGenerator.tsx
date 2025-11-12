import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/hooks/use-toast';
import { 
  Sparkles, 
  Image, 
  Type, 
  Video, 
  Wand2, 
  RefreshCw, 
  Download, 
  Heart, 
  ThumbsUp, 
  ThumbsDown,
  Settings,
  Palette,
  Layers,
  Zap,
  Brain,
  Target,
  BarChart3,
  Shield,
  AlertTriangle,
  Eye
} from 'lucide-react';
import { useAdStore } from '@/stores/adStore';
import { useUserStore } from '@/stores/userStore';
import { useAIStore } from '@/stores/aiStore';

interface AIAdGeneratorProps {
  className?: string;
}

export const AIAdGenerator: React.FC<AIAdGeneratorProps> = ({ className }) => {
  const { toast } = useToast();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  // Store hooks
  const { 
    templates, 
    selectedTemplate, 
    isGenerating, 
    generationProgress,
    generateAd,
    selectTemplate,
    loadTemplates 
  } = useAdStore();
  
  const { currentUser } = useUserStore();
  
  const {
    generateContent,
    detectBias,
    moderateContent,
    isGenerating: isAIGenerating,
    generationHistory,
    ethicalCompliance,
    biasDetections
  } = useAIStore();
  
  // Local state
  const [generationConfig, setGenerationConfig] = useState({
    prompt: '',
    style: 'modern',
    tone: 'friendly',
    platform: 'google',
    format: 'display',
    targetAudience: '',
    primaryGoal: 'conversion',
    brandGuidelines: '',
    customizations: {
      backgroundColor: '#ffffff',
      textColor: '#000000',
      accentColor: '#007bff',
      fontSize: 16,
      fontFamily: 'Inter',
      layout: 'standard'
    }
  });
  
  const [currentStep, setCurrentStep] = useState(1);
  const [generatedVariations, setGeneratedVariations] = useState<any[]>([]);
  const [selectedVariation, setSelectedVariation] = useState<any>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [realTimePreview, setRealTimePreview] = useState(true);
  
  // Initialize templates on mount
  useEffect(() => {
    loadTemplates();
  }, [loadTemplates]);
  
  // Handle AI content generation
  const handleGenerateContent = async () => {
    try {
      if (!selectedTemplate || !generationConfig.prompt) {
        toast({
          title: "Missing Information",
          description: "Please select a template and provide a prompt.",
          variant: "destructive"
        });
        return;
      }
      
      // Check content safety first
      const moderationResult = await moderateContent(generationConfig.prompt);
      if (!moderationResult.isAppropriate) {
        toast({
          title: "Content Flag",
          description: "Your prompt contains inappropriate content. Please revise.",
          variant: "destructive"
        });
        return;
      }
      
      // Generate multiple variations
      const variations = [];
      for (let i = 0; i < 3; i++) {
        const textContent = await generateContent(
          `Create an ad ${generationConfig.style} style with ${generationConfig.tone} tone for ${generationConfig.platform}: ${generationConfig.prompt}`,
          'text',
          {
            temperature: 0.7 + (i * 0.1),
            max_tokens: 200
          }
        );
        
        const ad = await generateAd(
          selectedTemplate.id,
          currentUser,
          {
            ...generationConfig.customizations,
            generatedText: textContent.generatedContent.text,
            variation: i
          }
        );
        
        variations.push(ad);
      }
      
      setGeneratedVariations(variations);
      setSelectedVariation(variations[0]);
      setCurrentStep(3);
      
      // Detect bias in generated content
      if (variations.length > 0) {
        await detectBias(variations[0].content.headline + ' ' + variations[0].content.description);
      }
      
      toast({
        title: "Success!",
        description: `Generated ${variations.length} ad variations.`,
      });
      
    } catch (error) {
      console.error('Generation failed:', error);
      toast({
        title: "Generation Failed",
        description: "Failed to generate ads. Please try again.",
        variant: "destructive"
      });
    }
  };
  
  // Handle real-time preview updates
  useEffect(() => {
    if (realTimePreview && selectedVariation) {
      updateCanvasPreview();
    }
  }, [selectedVariation, generationConfig.customizations, realTimePreview]);
  
  const updateCanvasPreview = () => {
    const canvas = canvasRef.current;
    if (!canvas || !selectedVariation) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Clear canvas
    ctx.fillStyle = generationConfig.customizations.backgroundColor;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw text elements
    ctx.fillStyle = generationConfig.customizations.textColor;
    ctx.font = `bold ${generationConfig.customizations.fontSize + 4}px ${generationConfig.customizations.fontFamily}`;
    ctx.fillText(selectedVariation.content.headline, 20, 40);
    
    ctx.font = `${generationConfig.customizations.fontSize}px ${generationConfig.customizations.fontFamily}`;
    const lines = wrapText(ctx, selectedVariation.content.description, canvas.width - 40);
    lines.forEach((line, index) => {
      ctx.fillText(line, 20, 80 + (index * 25));
    });
    
    // Draw CTA button
    ctx.fillStyle = generationConfig.customizations.accentColor;
    ctx.fillRect(20, canvas.height - 60, 120, 40);
    ctx.fillStyle = '#ffffff';
    ctx.font = `${generationConfig.customizations.fontSize}px ${generationConfig.customizations.fontFamily}`;
    ctx.fillText(selectedVariation.content.callToAction, 30, canvas.height - 35);
  };
  
  const wrapText = (ctx: CanvasRenderingContext2D, text: string, maxWidth: number) => {
    const words = text.split(' ');
    const lines = [];
    let currentLine = words[0];
    
    for (let i = 1; i < words.length; i++) {
      const word = words[i];
      const width = ctx.measureText(currentLine + ' ' + word).width;
      if (width < maxWidth) {
        currentLine += ' ' + word;
      } else {
        lines.push(currentLine);
        currentLine = word;
      }
    }
    lines.push(currentLine);
    return lines;
  };
  
  const handleCustomizationChange = (key: string, value: any) => {
    setGenerationConfig(prev => ({
      ...prev,
      customizations: {
        ...prev.customizations,
        [key]: value
      }
    }));
  };
  
  const exportAd = (format: 'png' | 'pdf' | 'html') => {
    if (!selectedVariation) return;
    
    if (format === 'png' && canvasRef.current) {
      const link = document.createElement('a');
      link.download = `ad-${selectedVariation.id}.png`;
      link.href = canvasRef.current.toDataURL();
      link.click();
    }
    
    toast({
      title: "Export Complete",
      description: `Ad exported as ${format.toUpperCase()}.`,
    });
  };
  
  return (
    <div className={`w-full max-w-7xl mx-auto p-6 space-y-6 ${className}`}>
      {/* Header with Progress */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Sparkles className="h-8 w-8 text-blue-600" />
            AI Ad Generator
          </h1>
          <p className="text-muted-foreground mt-1">
            Create personalized, high-converting ads with AI
          </p>
        </div>
        
        <div className="flex items-center gap-4">
          {/* Ethical AI Indicators */}
          <div className="flex items-center gap-2">
            <Badge variant={ethicalCompliance.biasScore > 80 ? "default" : "destructive"}>
              <Shield className="h-3 w-3 mr-1" />
              Bias Score: {ethicalCompliance.biasScore}
            </Badge>
            {biasDetections.length > 0 && (
              <Badge variant="destructive">
                <AlertTriangle className="h-3 w-3 mr-1" />
                {biasDetections.length} Issues
              </Badge>
            )}
          </div>
        </div>
      </div>
      
      {/* Progress Indicator */}
      <div className="w-full">
        <div className="flex justify-between mb-2">
          {['Configure', 'Generate', 'Customize', 'Export'].map((step, index) => (
            <div
              key={step}
              className={`flex items-center ${
                currentStep > index + 1 ? 'text-green-600' : 
                currentStep === index + 1 ? 'text-blue-600' : 'text-muted-foreground'
              }`}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                currentStep > index + 1 ? 'bg-green-600 text-white' :
                currentStep === index + 1 ? 'bg-blue-600 text-white' : 'bg-muted'
              }`}>
                {index + 1}
              </div>
              <span className="ml-2 font-medium">{step}</span>
            </div>
          ))}
        </div>
        <Progress value={(currentStep / 4) * 100} className="h-2" />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Step 1: Configuration */}
          {currentStep === 1 && (
            <div className="space-y-6"
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Settings className="h-5 w-5" />
                    Ad Configuration
                  </CardTitle>
                  <CardDescription>
                    Configure your ad parameters and targeting
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="platform">Platform</Label>
                      <Select
                        value={generationConfig.platform}
                        onValueChange={(value) => setGenerationConfig(prev => ({ ...prev, platform: value }))}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select platform" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="google">Google Ads</SelectItem>
                          <SelectItem value="facebook">Facebook</SelectItem>
                          <SelectItem value="instagram">Instagram</SelectItem>
                          <SelectItem value="linkedin">LinkedIn</SelectItem>
                          <SelectItem value="twitter">Twitter</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div>
                      <Label htmlFor="format">Ad Format</Label>
                      <Select
                        value={generationConfig.format}
                        onValueChange={(value) => setGenerationConfig(prev => ({ ...prev, format: value }))}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select format" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="display">Display Ad</SelectItem>
                          <SelectItem value="text">Text Ad</SelectItem>
                          <SelectItem value="video">Video Ad</SelectItem>
                          <SelectItem value="social">Social Post</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div>
                      <Label htmlFor="style">Style</Label>
                      <Select
                        value={generationConfig.style}
                        onValueChange={(value) => setGenerationConfig(prev => ({ ...prev, style: value }))}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select style" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="modern">Modern</SelectItem>
                          <SelectItem value="classic">Classic</SelectItem>
                          <SelectItem value="bold">Bold</SelectItem>
                          <SelectItem value="minimal">Minimal</SelectItem>
                          <SelectItem value="playful">Playful</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div>
                      <Label htmlFor="tone">Tone</Label>
                      <Select
                        value={generationConfig.tone}
                        onValueChange={(value) => setGenerationConfig(prev => ({ ...prev, tone: value }))}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select tone" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="friendly">Friendly</SelectItem>
                          <SelectItem value="professional">Professional</SelectItem>
                          <SelectItem value="urgent">Urgent</SelectItem>
                          <SelectItem value="casual">Casual</SelectItem>
                          <SelectItem value="authoritative">Authoritative</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  
                  <div>
                    <Label htmlFor="prompt">Ad Prompt</Label>
                    <Textarea
                      id="prompt"
                      placeholder="Describe your product, service, or campaign. Be specific about benefits, target audience, and key messages..."
                      value={generationConfig.prompt}
                      onChange={(e) => setGenerationConfig(prev => ({ ...prev, prompt: e.target.value }))}
                      className="min-h-[100px]"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="targetAudience">Target Audience</Label>
                    <Input
                      id="targetAudience"
                      placeholder="e.g., Young professionals interested in fitness"
                      value={generationConfig.targetAudience}
                      onChange={(e) => setGenerationConfig(prev => ({ ...prev, targetAudience: e.target.value }))}
                    />
                  </div>
                  
                  <Button
                    onClick={() => setCurrentStep(2)}
                    className="w-full"
                    disabled={!generationConfig.prompt}
                  >
                    Continue to Templates
                  </Button>
                </CardContent>
              </Card>
            </div>
          )}
          
          {/* Step 2: Template Selection & Generation */}
          {currentStep === 2 && (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Layers className="h-5 w-5" />
                    Choose Template
                  </CardTitle>
                  <CardDescription>
                    Select a template that matches your campaign goals
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    {templates.map((template) => (
                      <Card
                        key={template.id}
                        className={`cursor-pointer transition-all ${
                          selectedTemplate?.id === template.id ? 'ring-2 ring-blue-600' : ''
                        }`}
                        onClick={() => selectTemplate(template)}
                      >
                        <CardContent className="p-4">
                          <div className="flex items-center justify-between mb-2">
                            <h3 className="font-semibold">{template.name}</h3>
                            <Badge variant="outline">{template.category}</Badge>
                          </div>
                          <p className="text-sm text-muted-foreground mb-3">
                            {template.template.headline}
                          </p>
                          <div className="flex gap-2">
                            <Badge variant="secondary">{template.format}</Badge>
                            <Badge variant="secondary">{template.platform}</Badge>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                  
                  <div className="flex gap-3">
                    <Button
                      variant="outline"
                      onClick={() => setCurrentStep(1)}
                    >
                      Back
                    </Button>
                    <Button
                      onClick={handleGenerateContent}
                      disabled={!selectedTemplate || isGenerating || isAIGenerating}
                      className="flex-1"
                    >
                      {isGenerating || isAIGenerating ? (
                        <>
                          <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                          Generating...
                        </>
                      ) : (
                        <>
                          <Wand2 className="h-4 w-4 mr-2" />
                          Generate Ads
                        </>
                      )}
                    </Button>
                  </div>
                  
                  {(isGenerating || isAIGenerating) && (
                    <div className="mt-4">
                      <Progress value={generationProgress} className="mb-2" />
                      <p className="text-sm text-muted-foreground text-center">
                        Creating personalized ad variations...
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          )}
          
          {/* Step 3: Customization */}
          {currentStep === 3 && generatedVariations.length > 0 && (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Palette className="h-5 w-5" />
                    Customize Your Ad
                  </CardTitle>
                  <CardDescription>
                    Fine-tune the design and content
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Tabs defaultValue="variations" className="w-full">
                    <TabsList className="grid w-full grid-cols-3">
                      <TabsTrigger value="variations">Variations</TabsTrigger>
                      <TabsTrigger value="design">Design</TabsTrigger>
                      <TabsTrigger value="content">Content</TabsTrigger>
                    </TabsList>
                    
                    <TabsContent value="variations" className="space-y-4">
                      {generatedVariations.map((variation, index) => (
                        <Card
                          key={variation.id}
                          className={`cursor-pointer transition-all ${
                            selectedVariation?.id === variation.id ? 'ring-2 ring-blue-600' : ''
                          }`}
                          onClick={() => setSelectedVariation(variation)}
                        >
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between mb-2">
                              <h3 className="font-semibold">Variation {index + 1}</h3>
                              <div className="flex items-center gap-2">
                                <Badge variant="outline">
                                  CTR: {(variation.predictions.expectedCTR * 100).toFixed(1)}%
                                </Badge>
                                <Badge variant="outline">
                                  Confidence: {(variation.generation.confidence * 100).toFixed(0)}%
                                </Badge>
                              </div>
                            </div>
                            <h4 className="font-medium text-lg mb-1">{variation.content.headline}</h4>
                            <p className="text-muted-foreground mb-3">{variation.content.description}</p>
                            <Button variant="outline" size="sm">
                              {variation.content.callToAction}
                            </Button>
                          </CardContent>
                        </Card>
                      ))}
                    </TabsContent>
                    
                    <TabsContent value="design" className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label>Background Color</Label>
                          <Input
                            type="color"
                            value={generationConfig.customizations.backgroundColor}
                            onChange={(e) => handleCustomizationChange('backgroundColor', e.target.value)}
                          />
                        </div>
                        <div>
                          <Label>Text Color</Label>
                          <Input
                            type="color"
                            value={generationConfig.customizations.textColor}
                            onChange={(e) => handleCustomizationChange('textColor', e.target.value)}
                          />
                        </div>
                        <div>
                          <Label>Accent Color</Label>
                          <Input
                            type="color"
                            value={generationConfig.customizations.accentColor}
                            onChange={(e) => handleCustomizationChange('accentColor', e.target.value)}
                          />
                        </div>
                        <div>
                          <Label>Font Size</Label>
                          <Slider
                            value={[generationConfig.customizations.fontSize]}
                            onValueChange={(value) => handleCustomizationChange('fontSize', value[0])}
                            min={12}
                            max={24}
                            step={1}
                          />
                        </div>
                      </div>
                    </TabsContent>
                    
                    <TabsContent value="content" className="space-y-4">
                      {selectedVariation && (
                        <div className="space-y-4">
                          <div>
                            <Label>Headline</Label>
                            <Input
                              value={selectedVariation.content.headline}
                              onChange={(e) => {
                                const updated = {
                                  ...selectedVariation,
                                  content: { ...selectedVariation.content, headline: e.target.value }
                                };
                                setSelectedVariation(updated);
                              }}
                            />
                          </div>
                          <div>
                            <Label>Description</Label>
                            <Textarea
                              value={selectedVariation.content.description}
                              onChange={(e) => {
                                const updated = {
                                  ...selectedVariation,
                                  content: { ...selectedVariation.content, description: e.target.value }
                                };
                                setSelectedVariation(updated);
                              }}
                            />
                          </div>
                          <div>
                            <Label>Call to Action</Label>
                            <Input
                              value={selectedVariation.content.callToAction}
                              onChange={(e) => {
                                const updated = {
                                  ...selectedVariation,
                                  content: { ...selectedVariation.content, callToAction: e.target.value }
                                };
                                setSelectedVariation(updated);
                              }}
                            />
                          </div>
                        </div>
                      )}
                    </TabsContent>
                  </Tabs>
                  
                  <div className="flex gap-3 mt-6">
                    <Button
                      variant="outline"
                      onClick={() => setCurrentStep(2)}
                    >
                      Back
                    </Button>
                    <Button
                      onClick={() => setCurrentStep(4)}
                      className="flex-1"
                    >
                      Continue to Export
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
          
          {/* Step 4: Export */}
          {currentStep === 4 && selectedVariation && (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Download className="h-5 w-5" />
                    Export Your Ad
                  </CardTitle>
                  <CardDescription>
                    Download your ad in various formats
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-3 gap-4">
                    <Button onClick={() => exportAd('png')} variant="outline">
                      <Image className="h-4 w-4 mr-2" />
                      PNG
                    </Button>
                    <Button onClick={() => exportAd('pdf')} variant="outline">
                      <Type className="h-4 w-4 mr-2" />
                      PDF
                    </Button>
                    <Button onClick={() => exportAd('html')} variant="outline">
                      <Layers className="h-4 w-4 mr-2" />
                      HTML
                    </Button>
                  </div>
                  
                  <div className="flex gap-3">
                    <Button
                      variant="outline"
                      onClick={() => setCurrentStep(3)}
                    >
                      Back to Customize
                    </Button>
                    <Button
                      onClick={() => setCurrentStep(1)}
                      className="flex-1"
                    >
                      Create New Ad
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
        
        {/* Preview Panel */}
        <div className="space-y-6">
          <Card className="sticky top-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                Live Preview
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="aspect-square border-2 border-dashed border-muted-foreground/25 rounded-lg flex items-center justify-center mb-4">
                <canvas
                  ref={canvasRef}
                  width={400}
                  height={400}
                  className="max-w-full max-h-full"
                />
              </div>
              
              {selectedVariation && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Badge variant="outline">Performance Score</Badge>
                    <span className="font-semibold">
                      {Math.round(selectedVariation.predictions.expectedCTR * 1000) / 10}/10
                    </span>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Expected CTR</span>
                      <span>{(selectedVariation.predictions.expectedCTR * 100).toFixed(2)}%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Engagement Score</span>
                      <span>{(selectedVariation.predictions.expectedEngagement * 100).toFixed(0)}%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Conversion Rate</span>
                      <span>{(selectedVariation.predictions.expectedConversion * 100).toFixed(2)}%</span>
                    </div>
                  </div>
                  
                  <div className="flex gap-2 pt-3">
                    <Button size="sm" variant="outline">
                      <Heart className="h-4 w-4 mr-1" />
                      Save
                    </Button>
                    <Button size="sm" variant="outline">
                      <ThumbsUp className="h-4 w-4 mr-1" />
                      Like
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
          
          {/* AI Insights */}
          {biasDetections.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-orange-600">
                  <AlertTriangle className="h-5 w-5" />
                  Ethical AI Alerts
                </CardTitle>
              </CardHeader>
              <CardContent>
                {biasDetections.slice(0, 3).map((bias, index) => (
                  <div key={index} className="mb-3 p-3 bg-orange-50 rounded-lg">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge variant={bias.severity === 'high' ? 'destructive' : 'secondary'}>
                        {bias.severity}
                      </Badge>
                      <span className="text-sm font-medium">{bias.type}</span>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">{bias.description}</p>
                    <p className="text-sm font-medium">{bias.suggestion}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
// ... existing code ...
};

