import React, { useState, useEffect, useRef } from 'react';

const AyudanteChat = () => {
	const [messages, setMessages] = useState([]);
	const [input, setInput] = useState('');
	const [status, setStatus] = useState('Conectando...');
	const [isDrawerOpen, setIsDrawerOpen] = useState(false);
	const [schedule, setSchedule] = useState([]);
	const [thinkingStatus, setThinkingStatus] = useState(null);
	const [streamingMessage, setStreamingMessage] = useState('');
	const ws = useRef(null);
	const messagesEndRef = useRef(null);
	const streamingMessageRef = useRef(''); // Ref para evitar clausuras obsoletas en onmessage

	useEffect(() => {
		if ("Notification" in window && Notification.permission === "default") {
			Notification.requestPermission();
		}
	}, []);

	const showNotification = (title, body) => {
		if ("Notification" in window && Notification.permission === "granted") {
			new Notification(title, { body, icon: "/logo192.png" });
		}
	};


	const scrollToBottom = () => {
		messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
	};

	useEffect(() => {
		scrollToBottom();
	}, [messages]);

	useEffect(() => {
		ws.current = new WebSocket('ws://127.0.0.1:8001/ayudante');

		ws.current.onopen = () => {
			setStatus('Conectado');
		};

		ws.current.onmessage = (event) => {
			try {
				const payload = JSON.parse(event.data);
				if (payload.type === 'chat_message') {
					setMessages(prev => [...prev, { role: 'assistant', content: payload.data, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }]);
					showNotification("🤖 Asistente", payload.data);
				} else if (payload.type === 'chat_chunk') {
					setThinkingStatus(null);
					streamingMessageRef.current += payload.data;
					setStreamingMessage(streamingMessageRef.current);
				} else if (payload.type === 'chat_chunk_reset') {
					streamingMessageRef.current = '';
					setStreamingMessage('');
				} else if (payload.type === 'chat_end') {
					setThinkingStatus(null);
					if (streamingMessageRef.current) {
						const finalContent = streamingMessageRef.current;
						setMessages(prev => [...prev, {
							role: 'assistant',
							content: finalContent,
							time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
						}]);
						showNotification("🤖 Asistente", finalContent);
					}
					streamingMessageRef.current = '';
					setStreamingMessage('');
				} else if (payload.type === 'thinking') {
					setThinkingStatus(payload.status);
				} else if (payload.type === 'schedule_update') {
					setSchedule(payload.data);
				} else if (payload.type === 'reset_confirmed') {
					setMessages([]);
					setSchedule([]);
					streamingMessageRef.current = '';
					setStreamingMessage('');
					setThinkingStatus(null);
				}
			} catch (err) {
				// Fallback si el server manda texto plano
				setMessages(prev => [...prev, { role: 'assistant', content: event.data }]);
			}
		};

		ws.current.onclose = () => {
			setStatus('Desconectado. Reconectando en 5s...');
			setTimeout(() => { }, 5000);
		};

		ws.current.onerror = (error) => {
			setStatus('Error en conexión');
		};

		return () => {
			if (ws.current) {
				ws.current.close();
			}
		};
	}, []);

	const handleReset = () => {
		if (ws.current && ws.current.readyState === WebSocket.OPEN) {
			ws.current.send(JSON.stringify({ type: 'reset' }));
		}
	};

	const sendMessage = (e) => {
		e.preventDefault();
		if (input.trim() && ws.current && ws.current.readyState === WebSocket.OPEN) {
			ws.current.send(input);
			setMessages(prev => [...prev, {
				role: 'user',
				content: input,
				time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
			}]);
			setInput('');
		}
	};

	return (
		<div className="flex h-full relative overflow-hidden bg-zinc-900 font-sans">
			{/* Panel Principal del Chat */}
			<div className="flex flex-col flex-1 p-4 transition-all duration-300">
				<div className="flex justify-between items-center mb-4 pb-2 border-b border-zinc-700">
					<h1 className="text-xl font-bold flex items-center gap-2 text-zinc-300">
						🤖 Asistente Personal
						<span className="text-xs font-normal px-2 py-1 rounded bg-zinc-800 text-zinc-400">
							v1.69
						</span>
					</h1>
					<div className="flex items-center gap-3">
						<span className={`text-sm px-2 py-1 rounded ${status === 'Conectado' ? 'bg-emerald-900 text-emerald-300' : 'bg-rose-900 text-rose-300'}`}>
							{status}
						</span>
						<button
							onClick={handleReset}
							className="p-2 bg-rose-900/50 hover:bg-rose-900 rounded-lg text-rose-100 transition-colors flex items-center gap-2 border border-rose-500/30"
							title="Reiniciar chat y schedule"
						>
							<svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path><path d="M3 3v5h5"></path></svg>
							Reset
						</button>
						<button
							onClick={() => setIsDrawerOpen(!isDrawerOpen)}
							className="p-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-zinc-300 transition-colors flex items-center gap-2"
						>
							<svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
							Schedule
						</button>
					</div>
				</div>

				<div className="flex-1 overflow-y-auto mb-4 space-y-4 pr-2 custom-scrollbar">
					{messages.length === 0 && !streamingMessage && !thinkingStatus ? (
						<div className="text-center text-zinc-500 italic mt-10">Esperando indicaciones del asistente o del schedule...</div>
					) : (
						<>
							{messages.map((msg, idx) => (
								<div key={idx} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} gap-1`}>
									<div className={`max-w-[80%] rounded-lg px-4 py-2 ${msg.role === 'user'
										? 'bg-blue-600/50 text-blue-100 border border-blue-500/30'
										: 'bg-zinc-800 text-zinc-300 border border-zinc-700'
										}`}>
										{msg.content}
									</div>
									<span className="text-[10px] text-zinc-500 px-1 opacity-60">
										{msg.time}
									</span>
								</div>
							))}

							{streamingMessage && (
								<div className="flex justify-start">
									<div className="max-w-[80%] rounded-lg px-4 py-2 bg-zinc-800 text-zinc-300 border border-zinc-700 animate-in fade-in duration-300">
										{streamingMessage}
										<span className="inline-block w-2 h-4 ml-1 bg-blue-500 animate-pulse align-middle"></span>
									</div>
								</div>
							)}

							{thinkingStatus && (
								<div className="flex justify-start">
									<div className="flex items-center gap-3 px-4 py-2 bg-zinc-900 border border-blue-500/30 rounded-full text-blue-300 text-sm animate-pulse shadow-lg shadow-blue-500/10">
										<div className="flex gap-1">
											<span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
											<span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
											<span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
										</div>
										{thinkingStatus}
									</div>
								</div>
							)}
						</>
					)}
					<div ref={messagesEndRef} />
				</div>

				<form onSubmit={sendMessage} className="relative mt-auto">
					<input
						className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 pb-3 pt-3 focus:outline-none focus:border-zinc-500 transition-colors text-zinc-200"
						value={input}
						onChange={(e) => setInput(e.target.value)}
						placeholder="Habla con tu asistente..."
						disabled={status !== 'Conectado'}
					/>
					<button
						type="submit"
						className="absolute right-2 top-1/2 -translate-y-1/2 p-2 px-4 bg-zinc-700 hover:bg-zinc-600 rounded text-zinc-300 disabled:opacity-50 transition-colors"
						disabled={status !== 'Conectado' || !input.trim()}
					>
						Enviar
					</button>
				</form>
			</div>

			{/* Schedule Drawer (Panel Derecho) */}
			<div className={`w-80 h-full border-l border-zinc-700 bg-zinc-950/80 backdrop-blur-md p-4 transition-all duration-300 shrink-0 ${isDrawerOpen ? 'translate-x-0' : 'hidden'}`}>
				<h2 className="text-lg font-bold text-zinc-200 mb-4 pb-2 border-b border-zinc-800 flex items-center gap-2">
					<svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-indigo-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
					Schedule Activo
				</h2>
				<div className="space-y-3 overflow-y-auto h-[calc(100vh-100px)] custom-scrollbar">
					{schedule.length === 0 ? (
						<div className="text-zinc-500 text-sm italic py-4 text-center">No hay schedule programado para hoy.</div>
					) : (
						schedule.map((item, idx) => (
							<div key={idx} className="bg-zinc-900 border border-zinc-800 rounded-lg p-3">
								<div className="flex justify-between items-start mb-2">
									<span className="font-mono text-sm font-bold text-[#f4ba3e]">{item.time}</span>
									<span className={`text-xs px-2 py-0.5 rounded-full ${item.status === 'pending' ? 'bg-amber-900/50 text-amber-300' : 'bg-emerald-900/50 text-emerald-300'}`}>
										{item.status}
									</span>
								</div>
								<p className="text-sm text-zinc-300">{item.task}</p>
							</div>
						))
					)}
				</div>
			</div>
		</div>
	);
};

export default AyudanteChat;
