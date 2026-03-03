import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { useChat } from '../../context/ChatContext';
import MessageBubble from './MessageBubble';
import { Send, Menu, Paperclip, FileCode2, MessageSquarePlus, X } from 'lucide-react';

const ChatArea = () => {
	const { toggleLeftDrawer, toggleRightDrawer, currentChatId, setHistoryList, fetchData } = useChat();
	const [messages, setMessages] = useState([]);
	const [input, setInput] = useState('creame una pagina en react de login');
	const [isLoading, setIsLoading] = useState(false);
	const [uploading, setUploading] = useState(false);
	const [selectionData, setSelectionData] = useState(null);
	const [quotedContent, setQuotedContent] = useState(null);
	const [highlightRects, setHighlightRects] = useState([]);
	const fileInputRef = useRef(null);
	const messagesEndRef = useRef(null);
	const chatContainerRef = useRef(null);

	const scrollToBottom = () => {
		messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
	};

	useEffect(() => {
		const handleMouseUp = () => {
			const selection = window.getSelection();
			if (!selection || selection.isCollapsed || !selection.toString().trim()) {
				setSelectionData(null);
				return;
			}

			// Verify selection is within chat container
			// Use commonAncestorContainer to handle selections across nodes
			try {
				const range = selection.getRangeAt(0);
				if (chatContainerRef.current && chatContainerRef.current.contains(range.commonAncestorContainer)) {
					const rect = range.getBoundingClientRect();

					setSelectionData({
						text: selection.toString(),
						top: rect.bottom + 10,
						left: rect.left + (rect.width / 2) - 16,
						range: range.cloneRange() // Clone range to persist
					});
				} else {
					setSelectionData(null);
				}
			} catch (e) {
				setSelectionData(null);
			}
		};

		// Clear selection button if selection is cleared (e.g. clicking away)
		// BUT only if we are NOT clicking the button itself (handled via preventDefault on button)
		// Actually, let's remove the aggressive clearing on selectionchange since it causes issues
		// We'll rely on global click listener or just re-evaluating on selectionchange but without clearing if non-empty?
		// User reported "se deselecta el texto". This usually happens if focus is lost or a re-render happens.
		// Let's just remove the selectionchange listener that clears data.
		// Instead, we can clear when starting a new selection or clicking elsewhere.

		const handleMouseDown = (e) => {
			// If clicking outside chat area and button, clear selection data
			// (Simple heuristic)
			if (selectionData && !e.target.closest('button')) {
				// Don't clear immediately, let browser handle selection change
			}
		};

		document.addEventListener('mouseup', handleMouseUp);
		document.addEventListener('keyup', handleMouseUp);
		document.addEventListener('mousedown', handleMouseDown);

		return () => {
			document.removeEventListener('mouseup', handleMouseUp);
			document.removeEventListener('keyup', handleMouseUp);
			document.removeEventListener('mousedown', handleMouseDown);
		};
	}, []);

	const handleAddToInput = () => {
		if (selectionData?.text && selectionData.range && chatContainerRef.current) {
			setQuotedContent(selectionData.text);

			// Calculate relative rects for highlighting
			const range = selectionData.range;
			const rects = Array.from(range.getClientRects());
			const containerRect = chatContainerRef.current.getBoundingClientRect();
			const scrollTop = chatContainerRef.current.scrollTop;
			const scrollLeft = chatContainerRef.current.scrollLeft;

			const relativeRects = rects.map(r => ({
				top: r.top - containerRect.top + scrollTop,
				left: r.left - containerRect.left + scrollLeft,
				width: r.width,
				height: r.height
			}));

			setHighlightRects(relativeRects);
			setSelectionData(null);
			window.getSelection().removeAllRanges();
		} else if (selectionData?.text) {
			// Fallback if range is missing
			setQuotedContent(selectionData.text);
			setSelectionData(null);
		}
	};

	useEffect(() => {
		scrollToBottom();
	}, [messages]);

	// Load history if currentChatId changes by user explicitly
	useEffect(() => {
		if (currentChatId) {
			axios.get(`http://localhost:8000/api/history/${currentChatId}`)
				.then(res => setMessages(res.data.messages || []))
				.catch(err => console.error("Could not load history", err));
		} else {
			setMessages([]);
		}
	}, [currentChatId]);

	const handleSend = async (e) => {
		e?.preventDefault();
		if ((!input.trim() && !quotedContent) || isLoading) return;

		let finalContent = input;
		if (quotedContent) {
			finalContent = `> ${quotedContent}\n\n${input}`;
		}

		const userMessage = { role: 'user', content: finalContent };
		setMessages(prev => [...prev, userMessage]);
		setInput('');
		setQuotedContent(null);
		setHighlightRects([]); // Clear highlights
		setIsLoading(true);

		try {
			const payload = {
				message: finalContent,
				history_id: currentChatId
			};
			const response = await axios.post('http://localhost:8000/api/chat', payload);

			const assistantMessage = { role: 'assistant', content: response.data.response };
			setMessages(prev => [...prev, assistantMessage]);

			// En una implementación completa el backend enviaría un nuevo chatId si era una convnueva
			// y actualizaríamos la lista. Aquí refrescamos por si hay nuevas convers.
			fetchData();
		} catch (error) {
			console.error("Error sending message", error);
			setMessages(prev => [...prev, { role: 'system', content: `Error: ${error.message}` }]);
		} finally {
			setIsLoading(false);
		}
	};

	const handleFileUpload = async (e) => {
		const file = e.target.files?.[0];
		if (!file) return;

		const formData = new FormData();
		formData.append('file', file);

		setUploading(true);
		try {
			const res = await axios.post('http://localhost:8000/api/upload', formData, {
				headers: { 'Content-Type': 'multipart/form-data' }
			});
			// Add a system notification to chat about the upload
			setMessages(prev => [...prev, {
				role: 'system',
				content: `*Archivo subido exitosamente: [${file.name}](http://localhost:8000/${res.data.path.replace(/\\/g, '/')})*`
			}]);
		} catch (error) {
			console.error("Error uploading", error);
		} finally {
			setUploading(false);
			// Reset input
			if (fileInputRef.current) fileInputRef.current.value = '';
		}
	};

	return (
		<div className="flex flex-col h-screen w-full bg-zinc-900 transition-all relative">
			{/* Floating Action Button for Selection */}
			{selectionData && (
				<button
					onMouseDown={(e) => e.preventDefault()} // Prevent focus loss/selection clear
					onClick={handleAddToInput}
					style={{
						position: 'fixed',
						top: selectionData.top,
						left: selectionData.left,
						zIndex: 50
					}}
					className="bg-[#f4ba3e] text-zinc-900 p-2 rounded-full shadow-lg hover:bg-[#dca331] transition-all animate-in fade-in zoom-in duration-200 hover:scale-110"
					title="Citar en el chat"
				>
					<MessageSquarePlus className="w-4 h-4" />
				</button>
			)}

			{/* Header Mobile / Drawers Toggle */}
			<div className="flex items-center justify-between p-4 border-b border-zinc-800 bg-zinc-950/50 backdrop-blur-sm z-10">
				<button onClick={toggleLeftDrawer} className="p-2 -ml-2 text-zinc-400 hover:text-white rounded-lg hover:bg-zinc-800 transition-colors">
					<Menu className="w-5 h-5" />
				</button>
				<div className="font-semibold text-zinc-200">
					{currentChatId ? 'Conversación Actual' : 'Nueva Conversación'}
				</div>
				<button onClick={toggleRightDrawer} className="p-2 -mr-2 text-zinc-400 hover:text-white rounded-lg hover:bg-zinc-800 transition-colors">
					<FileCode2 className="w-5 h-5" />
				</button>
			</div>

			{/* Messages Area */}
			<div
				ref={chatContainerRef}
				className="flex-1 overflow-y-auto p-4 md:px-20 lg:px-40 xl:px-60 scrollbar-thin relative"
			>
				{/* Highlight Overlays */}
				{highlightRects.map((rect, i) => (
					<div
						key={i}
						style={{
							position: 'absolute',
							top: rect.top,
							left: rect.left,
							width: rect.width,
							height: rect.height,
							backgroundColor: '#f4ba3e', // Yellow/Gold
							opacity: 0.3,
							pointerEvents: 'none', // Allow clicks to pass through
							zIndex: 0 // Behind text if possible, but absolute usually is on top. Opacity helps.
						}}
					/>
				))}

				{messages.length === 0 ? (
					<div className="h-full flex flex-col items-center justify-center text-zinc-500 gap-4">
						<div className="w-16 h-16 rounded-2xl bg-[#f4ba3e]/10 flex items-center justify-center">
							<Menu className="w-8 h-8 text-[#f4ba3e]" />
						</div>
						<p>¿En qué puedo ayudarte hoy?</p>
					</div>
				) : (
					messages.map((msg, index) => (
						<MessageBubble key={index} message={msg} />
					))
				)}
				{isLoading && (
					<div className="flex justify-start mb-6">
						<div className="flex items-center gap-2 p-3 bg-zinc-800 text-zinc-400 rounded-xl rounded-tl-sm text-sm">
							<div className="flex space-x-1">
								<div className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
								<div className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
								<div className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce"></div>
							</div>
						</div>
					</div>
				)}
				<div ref={messagesEndRef} />
			</div>

			<div className="p-4 md:px-20 lg:px-40 xl:px-60 bg-gradient-to-t from-zinc-950 via-zinc-900 to-transparent">
				<form onSubmit={handleSend} className="relative flex flex-col gap-2 bg-zinc-800 border-[1px] border-zinc-700/50 rounded-2xl p-2 transition-shadow focus-within:ring-2 focus-within:ring-[#f4ba3e]/50 focus-within:bg-zinc-800/80 shadow-lg">

					{/* Badge de Cita (Quote) Superior dentro del Input */}
					{quotedContent && (
						<div className="mx-2 mt-2 bg-zinc-700/50 rounded-lg p-2 flex items-center justify-between animate-in slide-in-from-bottom-2 fade-in">
							<div className="text-zinc-300 text-sm italic truncate border-l-4 border-[#f4ba3e] pl-3 flex-1">
								"{quotedContent}"
							</div>
							<button
								onClick={() => {
									setQuotedContent(null);
									setHighlightRects([]);
								}}
								className="text-zinc-400 hover:text-red-400 p-1 rounded-md hover:bg-zinc-600/50 transition-colors ml-2 shrink-0"
								type="button"
								title="Eliminar cita"
							>
								<X className="w-4 h-4" />
							</button>
						</div>
					)}

					<div className="flex items-end gap-2 w-full">
						<input
							type="file"
							ref={fileInputRef}
							className="hidden"
							onChange={handleFileUpload}
							accept="image/*,audio/*,video/*,.pdf,.txt,.js,.py,.md"
						/>
						<button
							type="button"
							onClick={() => fileInputRef.current?.click()}
							disabled={uploading}
							className="p-3 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-700 rounded-xl transition-colors disabled:opacity-50 shrink-0"
						>
							<Paperclip className="w-5 h-5" />
						</button>

						<textarea
							value={input}
							onChange={(e) => setInput(e.target.value)}
							onKeyDown={(e) => {
								if (e.key === 'Enter' && !e.shiftKey) {
									e.preventDefault();
									handleSend();
								}
							}}
							placeholder="Pregunta a LM-Studio..."
							className="w-full max-h-48 min-h-[44px] bg-transparent text-zinc-100 placeholder-zinc-500 resize-none outline-none py-3 scrollbar-thin"
							rows="1"
						/>

						<button
							type="submit"
							disabled={!input.trim() || isLoading}
							className={`p-3 rounded-xl transition-all shrink-0 ${!input.trim() || isLoading
								? 'bg-zinc-700 text-zinc-500'
								: 'bg-[#f4ba3e] text-zinc-950 hover:bg-[#dca331] shadow-[0_0_15px_rgba(244,186,62,0.3)]'
								}`}
						>
							<Send className="w-5 h-5" />
						</button>
					</div>
				</form>
				<div className="text-center text-xs text-zinc-500 mt-2">
					LM-Studio Local API · AI can make mistakes
				</div>
			</div>
		</div>
	);
};

export default ChatArea;
