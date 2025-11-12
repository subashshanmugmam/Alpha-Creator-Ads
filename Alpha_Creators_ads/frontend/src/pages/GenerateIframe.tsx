import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Sparkles, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const GenerateIframe = () => {
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const { toast } = useToast();

  const handleGeneratePrompt = async () => {
    if (!userInput.trim()) {
      toast({
        title: "Input Required",
        description: "Please enter some text to generate a prompt",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    setError(null);
    
    try {
      // Construct the URL to call n8n webhook
      const webhookUrl = `http://localhost:5678/webhook/prompt-generator?userInput=${encodeURIComponent(userInput)}`;
      
      console.log('Calling webhook:', webhookUrl);
      
      // Since n8n is redirecting and we can't read the redirect due to CORS,
      // we'll construct the URL ourselves or use no-cors mode
      // But first, let's try to get the response
      
      try {
        const response = await fetch(webhookUrl, {
          method: 'GET',
          headers: {
            'Accept': 'text/plain, application/json, */*',
          },
          redirect: 'manual',
        });

        console.log('Response status:', response.status);
        console.log('Response type:', response.type);
        
        let opalUrl = null;

        // Check if this is a redirect response
        if (response.status >= 300 && response.status < 400) {
          opalUrl = response.headers.get('Location');
          console.log('Got redirect URL from Location header:', opalUrl);
        } else if (response.ok) {
          const responseText = await response.text();
          console.log('Raw response from n8n:', responseText);

          // Try to parse as JSON first
          try {
            const data = JSON.parse(responseText);
            console.log('Parsed as JSON:', data);
            opalUrl = data.opalUrl;
          } catch (parseError) {
            // Not JSON, treat as plain text URL
            console.log('Response is not JSON, treating as plain text URL');
            opalUrl = responseText.trim();
          }
        } else {
          const errorData = await response.text();
          console.error('Error response from n8n:', errorData);
          throw new Error(`Webhook returned ${response.status}: ${errorData.substring(0, 200)}`);
        }

        if (opalUrl && opalUrl.startsWith('http')) {
          toast({
            title: "Success!",
            description: "Redirecting to Google Opal...",
          });
          window.location.href = opalUrl;
          return; // Exit early on success
        } else {
          console.error('Invalid URL received:', opalUrl);
          throw new Error(`Received an invalid URL: ${opalUrl || 'empty'}`);
        }
      } catch (fetchError) {
        // If fetch fails due to CORS on redirect, construct URL manually
        console.log('Fetch failed (likely CORS on redirect), constructing URL manually...');
        console.log('Original error:', fetchError);
        
        // Construct the Opal URL with the user's input
        const opalBaseUrl = 'https://opal.google/?flow=drive:/1lcqFI1I3-EE_V1Th-2hv0qckv-PuPxDG&shared&mode=app';
        const opalUrl = `${opalBaseUrl}&prompt=${encodeURIComponent(userInput)}`;
        
        console.log('Constructed Opal URL:', opalUrl);
        
        toast({
          title: "Redirecting...",
          description: "Opening Google Opal with your prompt",
        });
        
        window.location.href = opalUrl;
        return;
      }
      
    } catch (err) {
      console.error('Error calling webhook:', err);
      setError(err.message);
      
      toast({
        title: "Error",
        description: err.message || "Failed to generate prompt",
        variant: "destructive",
      });
      
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-6">
      <Card className="max-w-2xl w-full shadow-2xl">
        <CardHeader className="text-center space-y-4">
          <div className="mx-auto w-20 h-20 bg-gradient-to-br from-purple-500 via-blue-500 to-indigo-500 rounded-2xl flex items-center justify-center shadow-lg">
            <Sparkles className="w-10 h-10 text-white" />
          </div>
          <CardTitle className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
            AI Prompt Generator
          </CardTitle>
          <CardDescription className="text-lg">
            Enter your ideas and let AI generate powerful prompts for your content
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="userInput" className="text-base font-semibold">
              Your Input
            </Label>
            <Input
              id="userInput"
              type="text"
              placeholder="Enter your ideas, keywords, or description..."
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleGeneratePrompt()}
              className="h-12 text-base"
              disabled={isLoading}
            />
          </div>

          <Button 
            onClick={handleGeneratePrompt}
            disabled={isLoading || !userInput.trim()}
            size="lg"
            className="w-full text-lg h-14 bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 shadow-lg hover:shadow-xl transition-all"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-3 h-6 w-6 animate-spin" />
                Generating, please wait...
              </>
            ) : (
              <>
                <Sparkles className="mr-3 h-6 w-6" />
                Generate Prompt and Go
              </>
            )}
          </Button>

          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <p className="text-sm text-red-800 dark:text-red-200">
                <strong>Error:</strong> {error}
              </p>
            </div>
          )}

          <div className="pt-4 border-t space-y-2">
            <p className="text-xs text-center text-muted-foreground">
              💡 <strong>Tip:</strong> Be specific with your input for better results
            </p>
            <p className="text-xs text-center text-muted-foreground">
              Press Enter or click the button to generate and redirect to Google Opal
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default GenerateIframe;
