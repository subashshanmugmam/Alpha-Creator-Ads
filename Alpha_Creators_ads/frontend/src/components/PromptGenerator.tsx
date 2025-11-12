import React, { useState } from 'react';

const PromptGenerator: React.FC = () => {
  const [title, setTitle] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleGeneratePrompt = async () => {
    if (!title.trim()) {
      alert('Please enter a title');
      return;
    }

    setIsLoading(true);
    
    try {
      const webhookUrl = `http://localhost:5678/webhook/prompt-generator?title=${encodeURIComponent(title)}`;
      
      const response = await fetch(webhookUrl, {
        method: 'GET',
        mode: 'no-cors', // Avoid CORS issues
      });

      console.log('Webhook called successfully:', webhookUrl);
      alert('Prompt generation started successfully!');
      setTitle(''); // Clear the input
      
    } catch (error) {
      console.error('Error calling webhook:', error);
      alert('Failed to generate prompt. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Enter title"
        disabled={isLoading}
      />
      <button onClick={handleGeneratePrompt} disabled={isLoading}>
        {isLoading ? 'Generating...' : 'Generate Prompt'}
      </button>
    </div>
  );
};

export default PromptGenerator;
