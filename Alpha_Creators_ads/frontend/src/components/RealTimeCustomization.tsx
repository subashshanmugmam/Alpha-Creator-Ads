import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/hooks/use-toast';
import {
  Palette,
  Type,
  Image,
  Layout,
  Zap,
  Eye,
  Play,
  Pause,
  RotateCcw,
  Save,
  Share,
  Download,
  Sparkles,
  Target,
  TrendingUp
} from 'lucide-react';
import { useAdStore } from '@/stores/adStore';
import { useAIStore } from '@/stores/aiStore';

interface RealTimeCustomizationProps {
  adId?: string;
  className?: string;
}

export const RealTimeCustomization: React.FC<RealTimeCustomizationProps> = ({ 
  adId, 
  className 
}) => {
  const { toast } = useToast();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  
  const { generatedAds, updateAd } = useAdStore();
  const { generateContent, optimizePrompt } = useAIStore();
  
  const [selectedAd, setSelectedAd] = useState(
    adId ? generatedAds.find(ad => ad.id === adId) : generatedAds[0]
  );
  
  const [customizations, setCustomizations] = useState({
    // Visual customizations
    backgroundColor: '#ffffff',
    textColor: '#000000',
    accentColor: '#007bff',
    fontSize: 16,
    fontFamily: 'Inter',
    borderRadius: 8,
    shadow: 2,
    
    // Layout customizations
    layout: 'standard',
    imagePosition: 'left',
    textAlignment: 'left',
    padding: 20,
    
    // Animation settings
    animationType: 'none',
    animationDuration: 1000,
    autoPlay: false,
    
    // Content variations
    headlineVariation: 0,
    descriptionVariation: 0,
    ctaVariation: 0,
    
    // AI optimization settings
    realTimeOptimization: true,
    audienceAdaptation: true,
    performanceTuning: true
  });
  
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [optimizationScore, setOptimizationScore] = useState(85);
  const [previewMode, setPreviewMode] = useState<'desktop' | 'mobile' | 'tablet'>('desktop');
  const [isLivePreview, setIsLivePreview] = useState(true);
  
  // Real-time preview updates
  useEffect(() => {
    if (isLivePreview) {
      updatePreview();
    }
  }, [customizations, selectedAd, previewMode, isLivePreview]);
  
  // Auto-optimization interval
  useEffect(() => {
    if (customizations.realTimeOptimization) {
      intervalRef.current = setInterval(async () => {
        await performAutoOptimization();
      }, 30000); // Every 30 seconds
      
      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      };
    }
  }, [customizations.realTimeOptimization]);
  
  const updatePreview = () => {
    const canvas = canvasRef.current;
    if (!canvas || !selectedAd) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Adjust canvas size based on preview mode
    const dimensions = getCanvasDimensions(previewMode);
    canvas.width = dimensions.width;
    canvas.height = dimensions.height;
    
    // Clear canvas
    ctx.fillStyle = customizations.backgroundColor;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Apply border radius
    if (customizations.borderRadius > 0) {
      ctx.save();
      roundRect(ctx, 0, 0, canvas.width, canvas.height, customizations.borderRadius);
      ctx.clip();
    }
    
    // Draw background gradient if accent color is different
    if (customizations.accentColor !== customizations.backgroundColor) {
      const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
      gradient.addColorStop(0, customizations.backgroundColor);
      gradient.addColorStop(1, customizations.accentColor + '20'); // 20% opacity
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
    
    // Calculate layout positions
    const layout = calculateLayout(canvas.width, canvas.height);
    
    // Draw headline
    ctx.fillStyle = customizations.textColor;
    ctx.font = `bold ${customizations.fontSize + 4}px ${customizations.fontFamily}`;
    ctx.textAlign = customizations.textAlignment as CanvasTextAlign;
    
    const headline = getContentVariation('headline', selectedAd.content.headline);
    drawText(ctx, headline, layout.headline.x, layout.headline.y, layout.headline.maxWidth);
    
    // Draw description
    ctx.font = `${customizations.fontSize}px ${customizations.fontFamily}`;
    const description = getContentVariation('description', selectedAd.content.description);
    drawText(ctx, description, layout.description.x, layout.description.y, layout.description.maxWidth);
    
    // Draw CTA button
    const cta = getContentVariation('cta', selectedAd.content.callToAction);
    drawButton(ctx, cta, layout.cta.x, layout.cta.y, layout.cta.width, layout.cta.height);
    
    // Apply shadow effect
    if (customizations.shadow > 0) {
      ctx.shadowColor = 'rgba(0, 0, 0, 0.1)';
      ctx.shadowBlur = customizations.shadow * 2;
      ctx.shadowOffsetX = customizations.shadow;
      ctx.shadowOffsetY = customizations.shadow;
    }
    
    // Apply animation if enabled
    if (customizations.animationType !== 'none') {
      applyAnimation();
    }
    
    if (customizations.borderRadius > 0) {
      ctx.restore();
    }
  };
  
  const getCanvasDimensions = (mode: string) => {
    switch (mode) {
      case 'mobile':
        return { width: 320, height: 400 };
      case 'tablet':
        return { width: 768, height: 500 };
      default:
        return { width: 600, height: 400 };
    }
  };
  
  const calculateLayout = (width: number, height: number) => {
    const padding = customizations.padding;
    
    switch (customizations.layout) {
      case 'centered':
        return {
          headline: { x: width / 2, y: padding + 40, maxWidth: width - (padding * 2) },
          description: { x: width / 2, y: padding + 100, maxWidth: width - (padding * 2) },
          cta: { x: width / 2 - 60, y: height - padding - 50, width: 120, height: 40 }
        };
      case 'split':
        return {
          headline: { x: padding, y: padding + 40, maxWidth: width / 2 - padding },
          description: { x: padding, y: padding + 100, maxWidth: width / 2 - padding },
          cta: { x: width / 2 + padding, y: height / 2 - 20, width: 120, height: 40 }
        };
      default: // standard
        return {
          headline: { x: padding, y: padding + 40, maxWidth: width - (padding * 2) },
          description: { x: padding, y: padding + 100, maxWidth: width - (padding * 2) },
          cta: { x: padding, y: height - padding - 50, width: 120, height: 40 }
        };
    }
  };
  
  const getContentVariation = (type: 'headline' | 'description' | 'cta', originalText: string) => {
    // In a real implementation, this would pull from generated variations
    const variations = {
      headline: [
        originalText,
        originalText + ' - Limited Time!',
        'New: ' + originalText,
        originalText + ' 🔥'
      ],
      description: [
        originalText,
        originalText + ' Act now!',
        'Exclusive: ' + originalText,
        originalText + ' Don\'t miss out!'
      ],
      cta: [
        originalText,
        'Get Started',
        'Learn More',
        'Try Now',
        'Shop Today'
      ]
    };
    
    const variationIndex = customizations[`${type}Variation` as keyof typeof customizations] as number;
    return variations[type][variationIndex] || originalText;
  };
  
  const drawText = (ctx: CanvasRenderingContext2D, text: string, x: number, y: number, maxWidth: number) => {
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
    
    lines.forEach((line, index) => {
      ctx.fillText(line, x, y + (index * (customizations.fontSize + 5)));
    });
  };
  
  const drawButton = (ctx: CanvasRenderingContext2D, text: string, x: number, y: number, width: number, height: number) => {
    // Button background
    ctx.fillStyle = customizations.accentColor;
    ctx.fillRect(x, y, width, height);
    
    // Button text
    ctx.fillStyle = '#ffffff';
    ctx.font = `bold ${customizations.fontSize}px ${customizations.fontFamily}`;
    ctx.textAlign = 'center';
    ctx.fillText(text, x + width / 2, y + height / 2 + customizations.fontSize / 3);
  };
  
  const roundRect = (ctx: CanvasRenderingContext2D, x: number, y: number, width: number, height: number, radius: number) => {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
  };
  
  const applyAnimation = () => {
    // Animation implementation would go here
    // This could include fade-in, slide, bounce effects
  };
  
  const performAutoOptimization = async () => {
    if (!selectedAd || isOptimizing) return;
    
    setIsOptimizing(true);
    
    try {
      // Simulate AI optimization
      const optimizedPrompt = await optimizePrompt(selectedAd.content.headline, 'ctr');
      
      // Update optimization score
      const newScore = Math.min(100, optimizationScore + Math.random() * 5);
      setOptimizationScore(newScore);
      
      // Apply subtle optimizations
      setCustomizations(prev => ({
        ...prev,
        fontSize: Math.max(14, Math.min(20, prev.fontSize + (Math.random() - 0.5) * 2)),
        // Slight color adjustments for better contrast
        textColor: adjustColorForOptimization(prev.textColor),
        accentColor: adjustColorForOptimization(prev.accentColor)
      }));
      
    } catch (error) {
      console.error('Auto-optimization failed:', error);
    } finally {
      setIsOptimizing(false);
    }
  };
  
  const adjustColorForOptimization = (color: string) => {
    // Simple color optimization logic
    return color; // In real implementation, this would adjust for better contrast/performance
  };
  
  const handleCustomizationChange = (key: string, value: any) => {
    setCustomizations(prev => ({
      ...prev,
      [key]: value
    }));
    
    // Update the ad store
    if (selectedAd) {
      updateAd(selectedAd.id, {
        content: {
          ...selectedAd.content,
          visualElements: {
            ...selectedAd.content.visualElements,
            [key]: value
          }
        }
      });
    }
  };
  
  const saveCustomizations = () => {
    if (!selectedAd) return;
    
    updateAd(selectedAd.id, {
      content: {
        ...selectedAd.content,
        visualElements: {
          ...selectedAd.content.visualElements,
          ...customizations
        }
      }
    });
    
    toast({
      title: "Customizations Saved",
      description: "Your ad customizations have been saved successfully.",
    });
  };
  
  const exportAd = () => {
    if (!canvasRef.current) return;
    
    const link = document.createElement('a');
    link.download = `customized-ad-${selectedAd?.id}.png`;
    link.href = canvasRef.current.toDataURL();
    link.click();
    
    toast({
      title: "Ad Exported",
      description: "Your customized ad has been exported as PNG.",
    });
  };
  
  return (
    <div className={`w-full max-w-7xl mx-auto space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Zap className="h-6 w-6 text-orange-600" />
            Real-time Customization
          </h2>
          <p className="text-muted-foreground">
            Live preview and AI-powered optimization
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <Badge variant={isOptimizing ? "default" : "secondary"}>
            {isOptimizing ? "Optimizing..." : `Score: ${optimizationScore}/100`}
          </Badge>
          <Switch
            checked={isLivePreview}
            onCheckedChange={setIsLivePreview}
          />
          <span className="text-sm">Live Preview</span>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Customization Controls */}
        <div className="lg:col-span-1 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="h-5 w-5" />
                Customization
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="visual" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="visual">Visual</TabsTrigger>
                  <TabsTrigger value="layout">Layout</TabsTrigger>
                  <TabsTrigger value="content">Content</TabsTrigger>
                </TabsList>
                
                <TabsContent value="visual" className="space-y-4">
                  <div>
                    <Label>Background Color</Label>
                    <Input
                      type="color"
                      value={customizations.backgroundColor}
                      onChange={(e) => handleCustomizationChange('backgroundColor', e.target.value)}
                    />
                  </div>
                  
                  <div>
                    <Label>Text Color</Label>
                    <Input
                      type="color"
                      value={customizations.textColor}
                      onChange={(e) => handleCustomizationChange('textColor', e.target.value)}
                    />
                  </div>
                  
                  <div>
                    <Label>Accent Color</Label>
                    <Input
                      type="color"
                      value={customizations.accentColor}
                      onChange={(e) => handleCustomizationChange('accentColor', e.target.value)}
                    />
                  </div>
                  
                  <div>
                    <Label>Font Size: {customizations.fontSize}px</Label>
                    <Slider
                      value={[customizations.fontSize]}
                      onValueChange={(value) => handleCustomizationChange('fontSize', value[0])}
                      min={12}
                      max={24}
                      step={1}
                    />
                  </div>
                  
                  <div>
                    <Label>Border Radius: {customizations.borderRadius}px</Label>
                    <Slider
                      value={[customizations.borderRadius]}
                      onValueChange={(value) => handleCustomizationChange('borderRadius', value[0])}
                      min={0}
                      max={20}
                      step={1}
                    />
                  </div>
                  
                  <div>
                    <Label>Shadow: {customizations.shadow}px</Label>
                    <Slider
                      value={[customizations.shadow]}
                      onValueChange={(value) => handleCustomizationChange('shadow', value[0])}
                      min={0}
                      max={10}
                      step={1}
                    />
                  </div>
                </TabsContent>
                
                <TabsContent value="layout" className="space-y-4">
                  <div>
                    <Label>Layout Style</Label>
                    <div className="grid grid-cols-1 gap-2 mt-2">
                      {['standard', 'centered', 'split'].map((layout) => (
                        <Button
                          key={layout}
                          variant={customizations.layout === layout ? "default" : "outline"}
                          onClick={() => handleCustomizationChange('layout', layout)}
                          className="justify-start"
                        >
                          <Layout className="h-4 w-4 mr-2" />
                          {layout.charAt(0).toUpperCase() + layout.slice(1)}
                        </Button>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <Label>Text Alignment</Label>
                    <div className="grid grid-cols-3 gap-2 mt-2">
                      {['left', 'center', 'right'].map((align) => (
                        <Button
                          key={align}
                          variant={customizations.textAlignment === align ? "default" : "outline"}
                          onClick={() => handleCustomizationChange('textAlignment', align)}
                          size="sm"
                        >
                          {align}
                        </Button>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <Label>Padding: {customizations.padding}px</Label>
                    <Slider
                      value={[customizations.padding]}
                      onValueChange={(value) => handleCustomizationChange('padding', value[0])}
                      min={10}
                      max={40}
                      step={5}
                    />
                  </div>
                </TabsContent>
                
                <TabsContent value="content" className="space-y-4">
                  <div>
                    <Label>Headline Variation</Label>
                    <Slider
                      value={[customizations.headlineVariation]}
                      onValueChange={(value) => handleCustomizationChange('headlineVariation', value[0])}
                      min={0}
                      max={3}
                      step={1}
                    />
                  </div>
                  
                  <div>
                    <Label>Description Variation</Label>
                    <Slider
                      value={[customizations.descriptionVariation]}
                      onValueChange={(value) => handleCustomizationChange('descriptionVariation', value[0])}
                      min={0}
                      max={3}
                      step={1}
                    />
                  </div>
                  
                  <div>
                    <Label>CTA Variation</Label>
                    <Slider
                      value={[customizations.ctaVariation]}
                      onValueChange={(value) => handleCustomizationChange('ctaVariation', value[0])}
                      min={0}
                      max={4}
                      step={1}
                    />
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
          
          {/* AI Optimization Controls */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5" />
                AI Optimization
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Label>Real-time Optimization</Label>
                <Switch
                  checked={customizations.realTimeOptimization}
                  onCheckedChange={(checked) => handleCustomizationChange('realTimeOptimization', checked)}
                />
              </div>
              
              <div className="flex items-center justify-between">
                <Label>Audience Adaptation</Label>
                <Switch
                  checked={customizations.audienceAdaptation}
                  onCheckedChange={(checked) => handleCustomizationChange('audienceAdaptation', checked)}
                />
              </div>
              
              <div className="flex items-center justify-between">
                <Label>Performance Tuning</Label>
                <Switch
                  checked={customizations.performanceTuning}
                  onCheckedChange={(checked) => handleCustomizationChange('performanceTuning', checked)}
                />
              </div>
              
              <Separator />
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Optimization Score</span>
                  <span className="font-medium">{optimizationScore}/100</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-orange-500 to-green-500 h-2 rounded-full transition-all duration-1000"
                    style={{ width: `${optimizationScore}%` }}
                  />
                </div>
              </div>
              
              <Button 
                onClick={performAutoOptimization} 
                disabled={isOptimizing}
                className="w-full"
              >
                {isOptimizing ? (
                  <>
                    <RotateCcw className="h-4 w-4 mr-2 animate-spin" />
                    Optimizing...
                  </>
                ) : (
                  <>
                    <Target className="h-4 w-4 mr-2" />
                    Optimize Now
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </div>
        
        {/* Preview Panel */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                Live Preview
              </CardTitle>
              <CardDescription>
                Real-time preview of your customizations
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Preview Mode Selector */}
              <div className="flex gap-2 mb-6">
                {['desktop', 'tablet', 'mobile'].map((mode) => (
                  <Button
                    key={mode}
                    variant={previewMode === mode ? "default" : "outline"}
                    onClick={() => setPreviewMode(mode as any)}
                    size="sm"
                  >
                    {mode.charAt(0).toUpperCase() + mode.slice(1)}
                  </Button>
                ))}
              </div>
              
              {/* Canvas Preview */}
              <div className="flex justify-center">
                <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-4">
                  <canvas
                    ref={canvasRef}
                    className="max-w-full max-h-full shadow-lg rounded"
                  />
                </div>
              </div>
              
              {/* Action Buttons */}
              <div className="flex justify-center gap-3 mt-6">
                <Button onClick={saveCustomizations} variant="outline">
                  <Save className="h-4 w-4 mr-2" />
                  Save
                </Button>
                <Button onClick={exportAd} variant="outline">
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
                <Button variant="outline">
                  <Share className="h-4 w-4 mr-2" />
                  Share
                </Button>
              </div>
            </CardContent>
          </Card>
          
          {/* Performance Metrics */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Predicted Performance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-green-600">
                    {(2.1 + (optimizationScore / 100) * 1.5).toFixed(1)}%
                  </p>
                  <p className="text-sm text-muted-foreground">Expected CTR</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-blue-600">
                    {(15.3 + (optimizationScore / 100) * 8).toFixed(1)}%
                  </p>
                  <p className="text-sm text-muted-foreground">Engagement Rate</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-purple-600">
                    {(optimizationScore + Math.random() * 10).toFixed(0)}
                  </p>
                  <p className="text-sm text-muted-foreground">Quality Score</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default RealTimeCustomization;
