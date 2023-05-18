import React, { useState } from 'react';
import axios from 'axios';

const BOT_IMG = 'https://cdn-icons-png.flaticon.com/512/7611/7611368.png';
const PERSON_IMG = 'https://cdn4.iconfinder.com/data/icons/neutral-character-traits-alphabet-c/236/neutral-c010-512.png';
const BOT_NAME = 'Wise Help AI';
const PERSON_NAME = 'You';
interface BotResponse {
  answer: string;
  urls_used: string[];
}
const formatDate = (date: Date): string => {
  const h = `0${date.getHours()}`.slice(-2);
  const m = `0${date.getMinutes()}`.slice(-2);
  return `${h}:${m}`;
};

const Chatbot = () => {
  const [messages, setMessages] = useState([
    {
      name: BOT_NAME,
      img: BOT_IMG,
      side: 'left',
      text: 'How may I help You?',
      time: new Date(),
    },
  ]);
  const [inputText, setInputText] = useState('');

  const appendMessage = (name: string, img: string, side: string, text: any) => {
    const newMessage = {
      name,
      img,
      side,
      text,
      time: new Date(),
    };
    setMessages(prevMessages => [...prevMessages, newMessage]);
  };
  const botResponse = async (rawText: string) => {
    try {
      const response = await axios.get<BotResponse>('/answer', { params: { question: rawText } });
      const data = response.data;

      const msgText = data.answer;
      appendMessage(BOT_NAME, BOT_IMG, 'left', msgText);

      if (data.urls_used.length > 0) {
        let text = 'These help articles were used to answer your question:\n';
        data.urls_used.forEach(url => {
          text += `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>\n`;
        });
        appendMessage(BOT_NAME, BOT_IMG, 'left', <span dangerouslySetInnerHTML={{ __html: text }} />);
      }
    } catch (error) {
      console.error(error);
    }
  };


  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!inputText) return;

    appendMessage(PERSON_NAME, PERSON_IMG, 'right', inputText);
    setInputText('');
    botResponse(inputText);
  };

  return (
      <section className="container">
        <h2 className="title">An LLM-powered Customer Support Agent for Wise</h2>
        <section className="msger">
          <main className="msger-chat">
            {messages.map((message, index) => (
                <div key={index} className={`msg ${message.side}-msg`}>
                  <div className="msg-img-container">
                    <img className="msg-img" src={message.img} alt="Profile" />
                  </div>
                  <div className="msg-bubble">
                    <div className="msg-info">
                      <div className="msg-info-name">{message.name}</div>
                      <div className="msg-info-time">{formatDate(message.time)}</div>
                    </div>
                    <div className="msg-text">{message.text}</div>
                  </div>
                </div>
            ))}
          </main>
          <form className="msger-inputarea" onSubmit={handleSubmit}>
            <input
                type="text"
                className="msger-input"
                placeholder="Enter your message..."
                value={inputText}
                onChange={e => setInputText(e.target.value)}
            />
            <button type="submit" className="msger-send-btn">
              Send
            </button>
          </form>
        </section>
        <footer className="footer">
          This is a private project, with no affiliation to Wise.
          It is using publicly available information at{' '}
          <a href="https://wise.com/help" target="_blank" rel="noopener noreferrer">
            https://wise.com/help
          </a>{' '}
          . Use it only for testing purposes!
        </footer>
      </section>
  );
};

export default Chatbot;
