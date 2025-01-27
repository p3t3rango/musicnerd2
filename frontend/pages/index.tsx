import { useState, useEffect, useRef } from 'react'
import { v4 as uuidv4 } from 'uuid'

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function Home() {
  const [input, setInput] = useState<string>('')
  const [messages, setMessages] = useState<Message[]>([])
  const [wsReady, setWsReady] = useState<boolean>(false)
  const [artists, setArtists] = useState<string[]>([])
  const wsRef = useRef<WebSocket | null>(null)
  const clientId = useRef<string>(uuidv4())

  useEffect(() => {
    // Fetch available artists
    fetch('/api/artists')
      .then(res => res.json())
      .then(data => setArtists(data.artists))

    // Setup WebSocket
    const ws = new WebSocket(`ws://localhost:8000/chat/${clientId.current}`)
    
    ws.onopen = () => {
      setWsReady(true)
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response
      }])
    }

    wsRef.current = ws
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || !wsReady || !wsRef.current) return

    setMessages(prev => [...prev, {
      role: 'user',
      content: input
    }])

    wsRef.current.send(input)
    setInput('')
  }

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-4">Chat with Annie Mac</h1>
        
        <div className="bg-white rounded-lg shadow p-4 mb-4">
          <h2 className="text-xl mb-2">Available Artists:</h2>
          <div className="flex flex-wrap gap-2">
            {artists.map(artist => (
              <span key={artist} className="bg-blue-100 px-2 py-1 rounded">
                {artist}
              </span>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow mb-4 p-4 h-[500px] overflow-y-auto">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`mb-4 ${
                msg.role === 'user' ? 'text-right' : 'text-left'
              }`}
            >
              <div
                className={`inline-block p-2 rounded-lg ${
                  msg.role === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200'
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}
        </div>

        <form onSubmit={sendMessage} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 p-2 rounded border"
            placeholder="Ask Annie something..."
          />
          <button
            type="submit"
            disabled={!wsReady}
            className="bg-blue-500 text-white px-4 py-2 rounded disabled:bg-gray-300"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  )
} 