import { useEffect, useMemo, useRef, useState } from "react";
import { motion } from "framer-motion";
import { ArrowLeft, Send, Mic, MicOff } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from '@/components/ui/button';
import { API_BASE } from '@/lib/api';
import axios from 'axios';

const OPENAI_API_KEY = import.meta.env.VITE_OPENAI_API_KEY;

const SYSTEM_PROMPT = `
You are "TrackSpendAI Assistant", an advanced AI financial guide with natural language understanding and context awareness.

🎯 **Core Capabilities:**
- **Natural Language Processing**: Understand questions like "How much did I spend last month?" or "What about the last 3 months?"
- **Context Awareness**: Remember previous questions and provide follow-up responses
- **Intelligent Suggestions**: Offer actionable recommendations based on user queries
- **Multi-Modal Support**: Handle text and voice inputs seamlessly

📊 **Financial Modules You Support:**
- **Dashboard** → Overall financial health, balances, trends
- **Transactions** → Income, expenses, spending analysis
- **Accounts** → Account management and balance tracking
- **Analytics** → Data insights, charts, performance reports
- **Budgets** → Budget creation, tracking, optimization
- **Debt Tracker** → Repayment progress, interest analysis, payoff timelines
- **Goals** → Goal completion predictions, savings strategies
- **Portfolio** → Investment performance, risk/return insights
- **Simulator** → Financial planning and "what-if" scenarios
- **AI Insights** → Smart recommendations, forecasts, anomaly detection

🧠 **Advanced Features:**
- **Time Reference Understanding**: "last month", "past 3 months", "this year"
- **Follow-up Context**: "What about...", "How about...", "Also..."
- **Intent Recognition**: Spending, income, balance, budget, goal, debt queries
- **Actionable Suggestions**: Context-aware recommendations and next steps

💬 **Conversation Style:**
- Be conversational and friendly
- Provide direct answers with context
- Offer relevant follow-up suggestions
- Maintain conversation flow naturally
- Remember previous topics for continuity

⚠️ **Important Rules:**
- Only handle finance-related queries
- Maintain context across conversation turns
- Provide specific, actionable advice
- Use natural, human-like responses
- Always offer helpful next steps
`;

// Natural language questions for users to get started
  const defaultQuestions = [
    "How much did I spend last month?",
    "What's my current balance?",
    "Show me my budget progress",
    "What about the last 3 months?",
    "How are my investments performing?",
    "When will I reach my savings goal?",
    "What unusual spending did you detect?",
    "Give me personalized recommendations"
  ];

function SeedWelcome() {
  return {
    role: "assistant",
    content:
      "👋 Hi! I'm your TrackSpendAI Assistant with advanced natural language understanding! I can understand questions like 'How much did I spend last month?' and remember our conversation context. Ask me anything about your finances - I'll provide direct answers, contextual explanations, and actionable suggestions. You can type or speak your questions naturally! Here are some examples to get started:",
  };
}

export default function TrackSpendAIChat() {
    const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const scrollerRef = useRef(null);
  const recognitionRef = useRef(null);

  // Check for speech recognition support
  useEffect(() => {
    console.log('Checking speech recognition support...');
    
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      console.log('Speech recognition is supported');
      setSpeechSupported(true);
      
      try {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognitionRef.current = new SpeechRecognition();
        
        recognitionRef.current.continuous = false;
        recognitionRef.current.interimResults = true;
        recognitionRef.current.lang = 'en-US';
        recognitionRef.current.maxAlternatives = 1;
        
        recognitionRef.current.onstart = () => {
          console.log('Speech recognition started');
          setIsListening(true);
        };
        
        recognitionRef.current.onresult = (event) => {
          console.log('Speech recognition result:', event);
          console.log('Number of results:', event.results.length);
          
          // Only process final results, ignore interim results
          let finalTranscript = '';
          for (let i = event.results.length - 1; i >= 0; i--) {
            if (event.results[i].isFinal) {
              finalTranscript = event.results[i][0].transcript;
              break;
            }
          }
          
          console.log('Final transcript:', finalTranscript);
          
          // Only proceed if we have a final result
          if (finalTranscript && finalTranscript.trim()) {
            setInput(finalTranscript.trim());
            setIsListening(false);
            
            // Don't show success message, just set the input
            console.log('Voice input set:', finalTranscript.trim());
          }
        };
        
        recognitionRef.current.onerror = (event) => {
          console.error('Speech recognition error:', event.error);
          setIsListening(false);
          
          let errorMessage = '';
          switch (event.error) {
            case 'no-speech':
              errorMessage = '⚠️ No speech detected. Please speak louder and try again.';
              break;
            case 'audio-capture':
              errorMessage = '⚠️ No microphone found. Please check your microphone connection.';
              break;
            case 'not-allowed':
              errorMessage = '⚠️ Microphone permission denied. Please allow microphone access and refresh the page.';
              break;
            case 'network':
              errorMessage = '⚠️ Network error. Please check your internet connection.';
              break;
            case 'aborted':
              errorMessage = '⚠️ Voice search was interrupted. Please try again.';
              break;
            default:
              errorMessage = `⚠️ Voice search error: ${event.error}. Please try typing your question instead.`;
          }
          
          const errorMsg = {
            role: "assistant",
            content: errorMessage,
          };
          setMessages((prev) => [...prev, errorMsg]);
        };
        
        recognitionRef.current.onend = () => {
          console.log('Speech recognition ended');
          setIsListening(false);
          
          // If we're still listening and no final result was captured, show error
          if (isListening) {
            const errorMsg = {
              role: "assistant",
              content: "⚠️ I couldn't understand what you said. Please try speaking more clearly or use the text input.",
            };
            setMessages((prev) => [...prev, errorMsg]);
          }
        };
        
        console.log('Speech recognition initialized successfully');
      } catch (error) {
        console.error('Error initializing speech recognition:', error);
        setSpeechSupported(false);
      }
    } else {
      console.log('Speech recognition not supported in this browser');
      setSpeechSupported(false);
    }
  }, []);

  // Load from localStorage
  useEffect(() => {
    const stored = localStorage.getItem("financeChat");
    if (stored && stored !== "[]") {
      setMessages(JSON.parse(stored));
    } else {
      const seed = SeedWelcome();
      setMessages([seed]);
      localStorage.setItem("financeChat", JSON.stringify([seed]));
    }
  }, []);

  // Save chat to localStorage
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem("financeChat", JSON.stringify(messages));
    }
  }, [messages]);

  // Scroll to bottom
  useEffect(() => {
    if (scrollerRef.current) {
      scrollerRef.current.scrollTop = scrollerRef.current.scrollHeight;
    }
  }, [messages]);

  const openAIMessages = useMemo(() => {
    const rest = messages.map((m) => ({ role: m.role, content: m.content }));
    return [{ role: "system", content: SYSTEM_PROMPT }, ...rest];
  }, [messages]);

   const navigateToHelpCenter = () => {
    navigate("/help"); // navigate function का उपयोग करें
  };

  const startVoiceSearch = () => {
    console.log('Starting voice search...');
    
    if (!speechSupported) {
      console.log('Speech recognition not supported');
      const errorMsg = {
        role: "assistant",
        content: "⚠️ Voice search is not supported in your browser. Please use Chrome, Edge, or Safari for voice search.",
      };
      setMessages((prev) => [...prev, errorMsg]);
      return;
    }
    
    if (!recognitionRef.current) {
      console.log('Speech recognition not initialized');
      const errorMsg = {
        role: "assistant",
        content: "⚠️ Voice search is not available. Please try typing your question instead.",
      };
      setMessages((prev) => [...prev, errorMsg]);
      return;
    }
    
    if (isListening) {
      console.log('Already listening');
      return;
    }
    
    try {
      console.log('Starting speech recognition...');
      recognitionRef.current.start();
      
      // Set a timeout to stop listening after 10 seconds
      setTimeout(() => {
        if (isListening) {
          console.log('Voice search timeout - stopping recognition');
          stopVoiceSearch();
          const timeoutMsg = {
            role: "assistant",
            content: "⚠️ Voice search timed out. Please try speaking again or use text input.",
          };
          setMessages((prev) => [...prev, timeoutMsg]);
        }
      }, 10000);
      
    } catch (error) {
      console.error('Error starting speech recognition:', error);
      setIsListening(false);
      const errorMsg = {
        role: "assistant",
        content: "⚠️ Could not start voice search. Please check your microphone permissions and try again.",
      };
      setMessages((prev) => [...prev, errorMsg]);
    }
  };

  const stopVoiceSearch = () => {
    console.log('Stopping voice search...');
    
    if (recognitionRef.current && isListening) {
      try {
        recognitionRef.current.stop();
      } catch (error) {
        console.error('Error stopping speech recognition:', error);
      }
    }
    setIsListening(false);
  };

  const handleQuestionClick = async (question) => {
    // Add user message
    const userMsg = { role: "user", content: question };
    setMessages((prev) => [...prev, userMsg]);

    try {
      setLoading(true);
      
      // Get user ID from localStorage or use a default
      const userId = localStorage.getItem('userId') || 'user_001';
      
      // Use the enhanced natural language AI engine
      try {
        const response = await axios.post(`${API_BASE}/ai/natural-chat/`, {
          query: question,
          user_id: userId
        });

        const result = response.data;
        let aiText = result.response;
        
        // Add context-aware suggestions if available
        if (result.suggested_actions && result.suggested_actions.length > 0) {
          aiText += "\n\n💡 **Suggested Actions:**\n";
          result.suggested_actions.forEach(action => {
            aiText += `• ${action}\n`;
          });
        }

        const aiMsg = { 
          role: "assistant", 
          content: aiText,
          natural_language: result.natural_language,
          context_aware: result.context_aware,
          query_type: result.query_type,
          category: result.category
        };

        setMessages((prev) => [...prev, aiMsg]);
      } catch (nlError) {
        console.log("Natural Language AI failed, trying basic AI:", nlError);
        
        // Fallback to basic AI engine
        const response = await axios.post(`${API_BASE}/ai/chat/`, {
          query: question,
          user_id: userId
        });

        const aiText = response.data.response;
        const aiMsg = { role: "assistant", content: aiText };

        setMessages((prev) => [...prev, aiMsg]);
      }
    } catch (err) {
      console.error(err);
      const errMsg = {
        role: "assistant",
        content: "⚠️ Sorry, something went wrong while getting your financial data. Please make sure you have accounts and transactions set up.",
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    const content = input.trim();
    if (!content || loading) return;

    const userMsg = { role: "user", content };
    setInput("");
    setMessages((prev) => [...prev, userMsg]);

    try {
      setLoading(true);
      
      // Get user ID from localStorage or use a default
      const userId = localStorage.getItem('userId') || 'user_001';
      
      // First try the enhanced natural language AI engine
      try {
        const response = await axios.post(`${API_BASE}/ai/natural-chat/`, {
          query: content,
          user_id: userId
        });

        const result = response.data;
        let aiText = result.response;
        
        // Add context-aware suggestions if available
        if (result.suggested_actions && result.suggested_actions.length > 0) {
          aiText += "\n\n💡 **Suggested Actions:**\n";
          result.suggested_actions.forEach(action => {
            aiText += `• ${action}\n`;
          });
        }
        
        // Add follow-up context if this is a follow-up query
        if (result.follow_up_intent && result.follow_up_intent !== 'new_query') {
          aiText += `\n\n🔄 *I understand you're following up on our previous discussion about ${result.category || 'your finances'}.*`;
        }

        const aiMsg = { 
          role: "assistant", 
          content: aiText,
          natural_language: result.natural_language,
          context_aware: result.context_aware,
          query_type: result.query_type,
          category: result.category
        };

        setMessages((prev) => [...prev, aiMsg]);
        return;
      } catch (nlError) {
        console.log("Natural Language AI failed, trying basic AI:", nlError);
        
        // Fallback to basic AI engine
        try {
          const response = await axios.post(`${API_BASE}/ai/chat/`, {
            query: content,
            user_id: userId
          });

          const aiText = response.data.response;
          const aiMsg = { role: "assistant", content: aiText };

          setMessages((prev) => [...prev, aiMsg]);
          return;
        } catch (dbError) {
          console.log("Database AI failed, trying OpenAI:", dbError);
          
          // Final fallback to OpenAI for general conversation
          const resp = await fetch("https://api.openai.com/v1/chat/completions", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${OPENAI_API_KEY}`,
            },
            body: JSON.stringify({
              model: "gpt-4o-mini",
              messages: [...openAIMessages, userMsg],
              temperature: 0.5,
            }),
          });

          if (!resp.ok) throw new Error("OpenAI request failed");

          const data = await resp.json();
          const aiText = data?.choices?.[0]?.message?.content || "…";
          const aiMsg = { role: "assistant", content: aiText };

          setMessages((prev) => [...prev, aiMsg]);
        }
      }
    } catch (err) {
      console.error(err);
      const errMsg = {
        role: "assistant",
        content: "⚠️ Sorry, something went wrong while processing your natural language query. Please try rephrasing your question.",
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    const seed = SeedWelcome();
    setMessages([seed]);
    localStorage.setItem("financeChat", JSON.stringify([seed]));
  };

  return (
    <div className="h-screen bg-gradient-to-br from-blue-50 to-slate-100">
      <div className="h-full flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center p-4 bg-white/80 backdrop-blur-sm border-b">
            <button
              onClick={navigateToHelpCenter}
              className="flex items-center text-blue-600 hover:text-blue-800 mr-4"
            >
              <ArrowLeft className="w-5 h-5 mr-1" />
              Back to Help
            </button>
          <h1 className="text-2xl font-bold text-slate-800">
            💰 TrackSpendAI Assistant
          </h1>
          <button
            onClick={clearChat}
            className="px-4 py-2 rounded-xl bg-white shadow-md border hover:bg-gray-100 transition"
          >
            Clear Chat
          </button>
        </div>

        {/* Chat box */}
        <div
          ref={scrollerRef}
          className="flex-1 bg-white/70 backdrop-blur-md p-4 space-y-3 overflow-y-auto"
        >
          {messages.map((m, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className={`max-w-[80%] px-4 py-3 rounded-2xl whitespace-pre-wrap shadow ${
                m.role === "user"
                  ? "ml-auto bg-blue-600 text-white rounded-br-none"
                  : "mr-auto bg-gray-100 text-slate-800 rounded-bl-none"
              }`}
            >
              {/* Natural Language & Context Indicators */}
              {m.role === "assistant" && (m.natural_language || m.context_aware) && (
                <div className="flex items-center gap-2 mb-2 text-xs">
                  {m.natural_language && (
                    <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded-full">
                      🧠 Natural Language
                    </span>
                  )}
                  {m.context_aware && (
                    <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full">
                      🔄 Context Aware
                    </span>
                  )}
                  {m.query_type && m.query_type !== 'general_query' && (
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full">
                      📊 {m.query_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </span>
                  )}
                </div>
              )}
              
              {m.content}
            </motion.div>
          ))}

          {/* Typing indicator */}
          {loading && (
            <div className="mr-auto flex items-center gap-1 bg-gray-100 px-4 py-3 rounded-2xl text-slate-600">
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></span>
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></span>
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-300"></span>
            </div>
          )}

          {/* Voice listening indicator */}
          {isListening && (
            <div className="mr-auto flex items-center gap-2 bg-red-50 px-4 py-3 rounded-2xl text-red-600 border border-red-200">
              <div className="relative">
                <Mic className="w-4 h-4 animate-pulse" />
                <div className="absolute inset-0 w-4 h-4 border-2 border-red-400 rounded-full animate-ping"></div>
              </div>
              <span className="text-sm font-medium">Listening... Speak clearly into your microphone</span>
            </div>
          )}
        </div>

        {/* Quick Questions */}
        <div className="p-4 bg-white/70 backdrop-blur-md border-t">
          <p className="text-sm text-gray-600 mb-3">💡 Quick Questions:</p>
          <div className="flex flex-wrap gap-2">
            {defaultQuestions.map((question, index) => (
              <Button
                key={index}
                variant="outline"
                size="sm"
                onClick={() => handleQuestionClick(question)}
                className="text-xs hover:bg-blue-50 hover:border-blue-300"
              >
                {question}
              </Button>
            ))}
          </div>
        </div>

        {/* Input bar */}
        <div className="p-4 bg-white/70 backdrop-blur-md border-t flex gap-2 items-center">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your budget, anomalies, forecasts, or goals..."
            className="flex-1 border rounded-2xl p-3 bg-white shadow-md min-h-[60px] resize-none focus:outline-none focus:ring-2 focus:ring-blue-400"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
          />
          
          {/* Voice Search Button */}
          {speechSupported ? (
            <button
              onClick={isListening ? stopVoiceSearch : startVoiceSearch}
              disabled={loading}
              className={`p-3 rounded-full shadow-md transition ${
                isListening 
                  ? 'bg-red-500 text-white hover:bg-red-600 animate-pulse' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
              title={isListening ? "Stop listening" : "Start voice search"}
            >
              {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
            </button>
          ) : (
            <button
              disabled
              className="p-3 rounded-full bg-gray-100 text-gray-400 shadow-md"
              title="Voice search not supported in this browser"
            >
              <Mic className="w-5 h-5" />
            </button>
          )}
          
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="p-3 rounded-full bg-blue-600 text-white shadow-md hover:bg-blue-700 disabled:opacity-50 transition"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
