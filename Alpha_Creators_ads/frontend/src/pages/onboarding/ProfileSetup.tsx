import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { 
  Sparkles, 
  ArrowLeft, 
  ArrowRight, 
  User, 
  Target, 
  Palette, 
  Upload,
  CheckCircle
} from "lucide-react";

const ProfileSetup = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    // Step 1: Demographics
    age: "",
    location: "",
    industry: "",
    companySize: "",
    
    // Step 2: Marketing Goals
    objectives: [] as string[],
    audienceSize: "",
    budget: "",
    adFormats: [] as string[],
    
    // Step 3: AI Preferences
    toneOfVoice: "",
    visualStyle: "",
    contentTypes: [] as string[],
    automationLevel: "",
    
    // Step 4: Brand Setup
    brandColors: "",
    brandGuidelines: "",
    restrictions: "",
    logoUploaded: false
  });

  const totalSteps = 4;
  const progress = (currentStep / totalSteps) * 100;

  const handleNext = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    } else {
      // Complete onboarding
      window.location.href = "/dashboard";
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const toggleSelection = (field: keyof typeof formData, value: string) => {
    const currentArray = formData[field] as string[];
    const newArray = currentArray.includes(value)
      ? currentArray.filter(item => item !== value)
      : [...currentArray, value];
    setFormData({...formData, [field]: newArray});
  };

  const renderStep1 = () => (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <div className="p-3 bg-primary/10 rounded-full w-16 h-16 flex items-center justify-center mx-auto">
          <User className="h-8 w-8 text-primary" />
        </div>
        <h2 className="text-2xl font-bold">Tell us about yourself</h2>
        <p className="text-muted-foreground">Help us personalize your AI ad generation experience</p>
      </div>

      <div className="grid gap-4">
        <div className="space-y-2">
          <Label>Age Range</Label>
          <Select value={formData.age} onValueChange={(value) => setFormData({...formData, age: value})}>
            <SelectTrigger>
              <SelectValue placeholder="Select your age range" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="18-25">18-25</SelectItem>
              <SelectItem value="26-35">26-35</SelectItem>
              <SelectItem value="36-45">36-45</SelectItem>
              <SelectItem value="46-55">46-55</SelectItem>
              <SelectItem value="55+">55+</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label>Location</Label>
          <Select value={formData.location} onValueChange={(value) => setFormData({...formData, location: value})}>
            <SelectTrigger>
              <SelectValue placeholder="Select your location" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="us">United States</SelectItem>
              <SelectItem value="ca">Canada</SelectItem>
              <SelectItem value="uk">United Kingdom</SelectItem>
              <SelectItem value="au">Australia</SelectItem>
              <SelectItem value="de">Germany</SelectItem>
              <SelectItem value="other">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label>Industry</Label>
          <Select value={formData.industry} onValueChange={(value) => setFormData({...formData, industry: value})}>
            <SelectTrigger>
              <SelectValue placeholder="Select your industry" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="tech">Technology</SelectItem>
              <SelectItem value="finance">Finance</SelectItem>
              <SelectItem value="healthcare">Healthcare</SelectItem>
              <SelectItem value="retail">Retail/E-commerce</SelectItem>
              <SelectItem value="education">Education</SelectItem>
              <SelectItem value="real-estate">Real Estate</SelectItem>
              <SelectItem value="other">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label>Company Size</Label>
          <Select value={formData.companySize} onValueChange={(value) => setFormData({...formData, companySize: value})}>
            <SelectTrigger>
              <SelectValue placeholder="Select company size" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="solo">Solo (1 person)</SelectItem>
              <SelectItem value="small">Small (2-10 people)</SelectItem>
              <SelectItem value="medium">Medium (11-50 people)</SelectItem>
              <SelectItem value="large">Large (51-200 people)</SelectItem>
              <SelectItem value="enterprise">Enterprise (200+ people)</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <div className="p-3 bg-accent/10 rounded-full w-16 h-16 flex items-center justify-center mx-auto">
          <Target className="h-8 w-8 text-accent" />
        </div>
        <h2 className="text-2xl font-bold">Marketing Goals</h2>
        <p className="text-muted-foreground">Define your advertising objectives and preferences</p>
      </div>

      <div className="space-y-6">
        <div className="space-y-3">
          <Label>Campaign Objectives (Select all that apply)</Label>
          <div className="grid grid-cols-2 gap-2">
            {["Brand Awareness", "Lead Generation", "Sales", "Engagement", "App Downloads", "Website Traffic"].map((objective) => (
              <Button
                key={objective}
                variant={formData.objectives.includes(objective) ? "default" : "outline"}
                size="sm"
                onClick={() => toggleSelection("objectives", objective)}
                className="justify-start"
              >
                {formData.objectives.includes(objective) && <CheckCircle className="h-4 w-4 mr-2" />}
                {objective}
              </Button>
            ))}
          </div>
        </div>

        <div className="space-y-2">
          <Label>Target Audience Size</Label>
          <Select value={formData.audienceSize} onValueChange={(value) => setFormData({...formData, audienceSize: value})}>
            <SelectTrigger>
              <SelectValue placeholder="Expected audience reach" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="small">Small (1K - 10K)</SelectItem>
              <SelectItem value="medium">Medium (10K - 100K)</SelectItem>
              <SelectItem value="large">Large (100K - 1M)</SelectItem>
              <SelectItem value="massive">Massive (1M+)</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label>Monthly Ad Budget</Label>
          <Select value={formData.budget} onValueChange={(value) => setFormData({...formData, budget: value})}>
            <SelectTrigger>
              <SelectValue placeholder="Select budget range" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="under-1k">Under $1,000</SelectItem>
              <SelectItem value="1k-5k">$1,000 - $5,000</SelectItem>
              <SelectItem value="5k-25k">$5,000 - $25,000</SelectItem>
              <SelectItem value="25k-100k">$25,000 - $100,000</SelectItem>
              <SelectItem value="over-100k">Over $100,000</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-3">
          <Label>Preferred Ad Formats</Label>
          <div className="grid grid-cols-2 gap-2">
            {["Display Ads", "Social Media", "Video Ads", "Search Ads", "Email", "Native Ads"].map((format) => (
              <Button
                key={format}
                variant={formData.adFormats.includes(format) ? "default" : "outline"}
                size="sm"
                onClick={() => toggleSelection("adFormats", format)}
                className="justify-start"
              >
                {formData.adFormats.includes(format) && <CheckCircle className="h-4 w-4 mr-2" />}
                {format}
              </Button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <div className="p-3 bg-accent-orange/10 rounded-full w-16 h-16 flex items-center justify-center mx-auto">
          <Palette className="h-8 w-8 text-accent-orange" />
        </div>
        <h2 className="text-2xl font-bold">AI Preferences</h2>
        <p className="text-muted-foreground">Customize how AI creates content for your brand</p>
      </div>

      <div className="space-y-6">
        <div className="space-y-2">
          <Label>Tone of Voice</Label>
          <Select value={formData.toneOfVoice} onValueChange={(value) => setFormData({...formData, toneOfVoice: value})}>
            <SelectTrigger>
              <SelectValue placeholder="Select your brand's tone" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="professional">Professional</SelectItem>
              <SelectItem value="casual">Casual & Friendly</SelectItem>
              <SelectItem value="bold">Bold & Confident</SelectItem>
              <SelectItem value="playful">Playful & Fun</SelectItem>
              <SelectItem value="luxury">Luxury & Sophisticated</SelectItem>
              <SelectItem value="technical">Technical & Informative</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label>Visual Style</Label>
          <Select value={formData.visualStyle} onValueChange={(value) => setFormData({...formData, visualStyle: value})}>
            <SelectTrigger>
              <SelectValue placeholder="Select visual style preference" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="modern">Modern & Clean</SelectItem>
              <SelectItem value="classic">Classic & Timeless</SelectItem>
              <SelectItem value="minimalist">Minimalist</SelectItem>
              <SelectItem value="vibrant">Vibrant & Colorful</SelectItem>
              <SelectItem value="luxury">Luxury & Premium</SelectItem>
              <SelectItem value="creative">Creative & Artistic</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-3">
          <Label>Content Types to Generate</Label>
          <div className="grid grid-cols-1 gap-2">
            {["Text-only Ads", "Image + Text Ads", "Video Scripts", "Social Media Posts", "Email Campaigns", "Landing Page Copy"].map((type) => (
              <Button
                key={type}
                variant={formData.contentTypes.includes(type) ? "default" : "outline"}
                size="sm"
                onClick={() => toggleSelection("contentTypes", type)}
                className="justify-start"
              >
                {formData.contentTypes.includes(type) && <CheckCircle className="h-4 w-4 mr-2" />}
                {type}
              </Button>
            ))}
          </div>
        </div>

        <div className="space-y-2">
          <Label>Automation Level</Label>
          <Select value={formData.automationLevel} onValueChange={(value) => setFormData({...formData, automationLevel: value})}>
            <SelectTrigger>
              <SelectValue placeholder="How much AI automation do you want?" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="full">Full AI Automation</SelectItem>
              <SelectItem value="review">AI with Human Review</SelectItem>
              <SelectItem value="suggestions">AI Suggestions Only</SelectItem>
              <SelectItem value="manual">Manual with AI Assistance</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );

  const renderStep4 = () => (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <div className="p-3 bg-primary-glow/10 rounded-full w-16 h-16 flex items-center justify-center mx-auto">
          <Upload className="h-8 w-8 text-primary" />
        </div>
        <h2 className="text-2xl font-bold">Brand Setup</h2>
        <p className="text-muted-foreground">Upload your brand assets and set guidelines</p>
      </div>

      <div className="space-y-6">
        <div className="space-y-2">
          <Label>Brand Colors</Label>
          <Input
            placeholder="#3b82f6, #ef4444, #10b981 (optional)"
            value={formData.brandColors}
            onChange={(e) => setFormData({...formData, brandColors: e.target.value})}
          />
          <p className="text-sm text-muted-foreground">Enter hex color codes separated by commas</p>
        </div>

        <div className="space-y-2">
          <Label>Logo Upload</Label>
          <div className="border-2 border-dashed border-border rounded-lg p-8 text-center space-y-3">
            <Upload className="h-12 w-12 text-muted-foreground mx-auto" />
            <div>
              <Button variant="outline" onClick={() => setFormData({...formData, logoUploaded: true})}>
                Upload Logo
              </Button>
              <p className="text-sm text-muted-foreground mt-2">PNG, JPG up to 5MB</p>
            </div>
            {formData.logoUploaded && (
              <Badge variant="default" className="mt-2">
                <CheckCircle className="h-4 w-4 mr-1" />
                Logo uploaded successfully
              </Badge>
            )}
          </div>
        </div>

        <div className="space-y-2">
          <Label>Brand Guidelines</Label>
          <Textarea
            placeholder="Describe your brand voice, values, and messaging guidelines..."
            value={formData.brandGuidelines}
            onChange={(e) => setFormData({...formData, brandGuidelines: e.target.value})}
            rows={4}
          />
        </div>

        <div className="space-y-2">
          <Label>Content Restrictions</Label>
          <Textarea
            placeholder="Any topics, words, or themes to avoid in your ads..."
            value={formData.restrictions}
            onChange={(e) => setFormData({...formData, restrictions: e.target.value})}
            rows={3}
          />
        </div>

        <div className="bg-accent/10 rounded-lg p-4 space-y-2">
          <h4 className="font-medium text-accent">Privacy & Data Usage</h4>
          <p className="text-sm text-muted-foreground">
            Your brand information will be used to personalize AI-generated content. 
            We follow GDPR guidelines and IEEE 7003-2024 standards for ethical AI.
          </p>
          <div className="flex items-center space-x-2">
            <Checkbox id="consent" required />
            <Label htmlFor="consent" className="text-sm">
              I consent to using this data for AI personalization
            </Label>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-primary/5 to-accent/10 p-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <div className="p-2 rounded-lg bg-gradient-primary">
              <Sparkles className="h-6 w-6 text-primary-foreground" />
            </div>
            <span className="text-2xl font-bold bg-gradient-hero bg-clip-text text-transparent">
              Alpha Creators Ads
            </span>
          </div>
          <h1 className="text-3xl font-bold mb-2">Complete Your Profile</h1>
          <p className="text-muted-foreground">
            Step {currentStep} of {totalSteps} - This helps us create better AI-powered ads for you
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <Progress value={progress} className="h-2" />
          <div className="flex justify-between mt-2 text-sm text-muted-foreground">
            <span>Demographics</span>
            <span>Goals</span>
            <span>AI Preferences</span>
            <span>Brand Setup</span>
          </div>
        </div>

        {/* Form Content */}
        <Card className="p-8 shadow-elevated bg-gradient-card border">
          {currentStep === 1 && renderStep1()}
          {currentStep === 2 && renderStep2()}
          {currentStep === 3 && renderStep3()}
          {currentStep === 4 && renderStep4()}

          {/* Navigation */}
          <div className="flex justify-between mt-8">
            <Button
              variant="outline"
              onClick={handleBack}
              disabled={currentStep === 1}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <Button variant="hero" onClick={handleNext}>
              {currentStep === totalSteps ? "Complete Setup" : "Next"}
              {currentStep < totalSteps && <ArrowRight className="h-4 w-4 ml-2" />}
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default ProfileSetup;