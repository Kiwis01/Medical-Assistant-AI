// App.tsx
import React, { useRef, useState, useEffect } from 'react';
import './App.css';
import './ChatbotStyles.css'; // Import the override styles
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUserDoctor, faUser, faImage } from '@fortawesome/free-solid-svg-icons';
import ReactMarkdown from 'react-markdown';
import { API_BASE_URL } from '../../constants';

// Loading dots animation component
const LoadingDots = ({ label = '' }) => {
  const [dots, setDots] = useState(1);

  useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => prev < 3 ? prev + 1 : 1);
    }, 500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="loading-container">
      {label && <span className="loading-label">{label}</span>}
      <div className="loading-dots">
        <div className={`dot ${dots >= 1 ? 'active' : ''}`}></div>
        <div className={`dot ${dots >= 2 ? 'active' : ''}`}></div>
        <div className={`dot ${dots >= 3 ? 'active' : ''}`}></div>
      </div>
    </div>
  );
};

interface Message {
  text?: string;
  sender: 'user' | 'bot';
  imageUrl?: string;
  isLoading?: boolean;
  loadingLabel?: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [zoomedImage, setZoomedImage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleSendMessage = async () => {
    // Handle image upload and message
    if (imagePreview && imageFile) {
      try {
        // First, add user message with preview to UI immediately
        const userMessage: Message = { sender: 'user', imageUrl: imagePreview, text: 'Uploading image...' };
        setMessages(prevMessages => [...prevMessages, userMessage]);
        
        // Clear input state
        setImagePreview(null);
        setImageFile(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
        
        // Then upload image to backend (this might take time)
        const serverPath = await uploadImageToBackend(imageFile);
        
        // Update the user message with the actual server path
        setMessages(prevMessages => {
          const updatedMessages = [...prevMessages];
          const lastIndex = updatedMessages.length - 1;
          if (lastIndex >= 0 && updatedMessages[lastIndex].sender === 'user') {
            updatedMessages[lastIndex] = { ...updatedMessages[lastIndex], text: serverPath };
          }
          return updatedMessages;
        });
        
        // Prepare backend history (only text messages)
        const backendHistory = messages
          .filter((msg) => typeof msg.text === "string" && msg.text)
          .map((msg) => ({
            role: msg.sender === "user" ? "user" : "model",
            text: msg.text as string,
          }));
        
        // Add a loading message with animation
        setMessages(prevMessages => [...prevMessages, { sender: 'bot', isLoading: true, loadingLabel: 'Analyzing image' }]);
        
        // Send to backend
        const data = await sendMessageToBackend(serverPath, backendHistory, "12345");
        
        // Replace the loading message with actual response
        setMessages(prevMsgs => {
          
          // Map the response history to our message format
          const responseMessages = data.history.map((msg: any) => {
            if (msg.role === "user") {
              // Find a local user message with a matching text and imageUrl
              const local = prevMsgs.find(
                m => m.sender === "user" && m.text === msg.text && m.imageUrl
              );
              if (local) {
                return { ...msg, sender: "user", imageUrl: local.imageUrl };
              }
            }
            // If bot message and text is an image path, set imageUrl
            if (
              msg.role !== "user" &&
              typeof msg.text === "string" &&
              (msg.text.startsWith("/uploads/") || msg.text.startsWith("/generated/"))
            ) {
              return { ...msg, sender: "bot", imageUrl: msg.text };
            }
            return { text: msg.text, sender: msg.role === "user" ? "user" : "bot" };
          });
          
          return responseMessages;
        });
      } catch (err) {
        console.error(err);
        // Show error message
        setMessages(prevMessages => [...prevMessages.slice(0, -1), { sender: 'bot', text: 'Error processing image. Please try again.' }]);
      }
      return;
    }

    // Send text message
    if (inputText.trim() !== "") {
      const userInputCopy = inputText.trim();
      
      // Immediately add user message to UI
      setMessages(prevMessages => [...prevMessages, { sender: 'user', text: userInputCopy }]);
      
      // Clear input field right away
      setInputText('');
      
      // Add a loading message with animation
      setMessages(prevMessages => [...prevMessages, { sender: 'bot', isLoading: true, loadingLabel: 'Thinking' }]);
      
      // Prepare backend history format (only text messages)
      const backendHistory = messages
        .filter((msg) => typeof msg.text === "string" && msg.text)
        .map((msg) => ({
          role: msg.sender === "user" ? "user" : "model",
          text: msg.text as string,
        }));

      try {
        const data = await sendMessageToBackend(userInputCopy, backendHistory, "12345");
        
        // Replace the loading message with actual response
        setMessages(prevMsgs => {
          // Map the response history to our message format
          const responseMessages = data.history.map((msg: any) => {
            if (msg.role === "user") {
              const local = prevMsgs.find(
                m => m.sender === "user" && m.text === msg.text && m.imageUrl
              );
              if (local) {
                return { ...msg, sender: "user", imageUrl: local.imageUrl };
              }
            }
            return { text: msg.text, sender: msg.role === "user" ? "user" : "bot" };
          });
          
          return responseMessages;
        });
      } catch (err) {
        console.error(err);
        // Show error message instead of loading
        setMessages(prevMessages => [...prevMessages.slice(0, -1), { sender: 'bot', text: 'Sorry, I encountered an error. Please try again.' }]);
      }
    }
  };


  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
        setImageFile(file);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleCancelImage = () => {
    setImagePreview(null);
    setImageFile(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.sender} fade-in`}
          >
            <span className="icon">
              {message.sender === 'user' ? <FontAwesomeIcon icon={faUser} /> : <FontAwesomeIcon icon={faUserDoctor} />}
            </span>
            {(message.imageUrl || (typeof message.text === "string" && (message.text.startsWith("/uploads/") || message.text.startsWith("/generated/")))) ? (
              <img
                src={
                  message.imageUrl
                    ? (message.imageUrl.startsWith("/uploads/") || message.imageUrl.startsWith("/generated/")
                        ? `${API_BASE_URL}${message.imageUrl}`
                        : message.imageUrl)
                    : `${API_BASE_URL}${message.text}`
                }
                alt="uploaded"
                className="message-image"
                style={{ maxWidth: 180, maxHeight: 180, borderRadius: 12, marginRight: 8, cursor: 'pointer' }}
                onClick={() => {
                  const url = message.imageUrl
                    ? (message.imageUrl.startsWith("/uploads/") || message.imageUrl.startsWith("/generated/")
                        ? `${API_BASE_URL}${message.imageUrl}`
                        : message.imageUrl)
                    : `${API_BASE_URL}${message.text}`;
                  setZoomedImage(url);
                }}
              />
            ) : message.isLoading ? (
              <LoadingDots label={message.loadingLabel} />

            ) : (
              message.sender === 'bot' ? (
                <span className="message-text">
                  <ReactMarkdown>{message.text || ''}</ReactMarkdown>
                </span>
              ) : (
                <span className="message-text">{message.text}</span>
              )
            )}
          </div>
        ))}
      </div>
      {/* Image Zoom Modal */}
      {zoomedImage && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            background: 'rgba(0,0,0,0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}
          onClick={() => setZoomedImage(null)}
        >
          <img
            src={zoomedImage}
            alt="zoomed"
            style={{
              maxWidth: '90vw',
              maxHeight: '90vh',
              borderRadius: 16,
              boxShadow: '0 0 16px #000',
              background: '#fff',
              padding: 8
            }}
            onClick={e => e.stopPropagation()}
          />
          <button
            onClick={() => setZoomedImage(null)}
            style={{
              position: 'absolute',
              top: 32,
              right: 48,
              fontSize: 32,
              background: 'none',
              border: 'none',
              color: '#fff',
              cursor: 'pointer',
              zIndex: 1001
            }}
            aria-label="Close zoomed image"
          >
            &times;
          </button>
        </div>
      )}
      <div className="chat-input">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="Type a message..."
        />
        <label htmlFor="image-upload" className="image-upload-btn" title="Upload image">
          <FontAwesomeIcon icon={faImage} size="lg" />
          <input
            ref={fileInputRef}
            id="image-upload"
            type="file"
            accept="image/*"
            style={{ display: 'none' }}
            onChange={handleImageChange}
          />
        </label>
        {imagePreview && (
          <div className="image-preview-container">
            <img src={imagePreview} alt="preview" className="image-preview" style={{ maxWidth: 100, maxHeight: 100, borderRadius: 8, marginRight: 8 }} />
            <button className="cancel-image-btn" onClick={handleCancelImage} type="button">Cancel</button>
          </div>
        )}
        <button onClick={handleSendMessage}>Send</button>
      </div>
    </div>
  );
}

// Upload image to backend and get server path
async function uploadImageToBackend(file: File): Promise<string> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Image upload failed');
  const data = await res.json();
  return data.image_path; // e.g. '/uploads/filename.jpg'
}

async function sendMessageToBackend(
  query: string,
  history: { role: string; text: string }[],
  user_id = "12345"
): Promise<{ response: string; history: any[]; specialty: string }> {
  const res = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, history, user_id }),
  });
  if (!res.ok) throw new Error("Network error");
  return res.json();
}

export default App;