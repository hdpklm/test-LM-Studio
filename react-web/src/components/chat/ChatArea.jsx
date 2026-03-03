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

	const inputRef = useRef(null);

	const handleAddToInput = () => {
		if (selectionData?.text && inputRef.current) {
			// Crear el nodo HTML del badge
			const badgeHtml = `<span contenteditable="false" class="inline-flex items-center gap-1 bg-yellow-500/20 border border-yellow-500/50 text-yellow-200 px-2 py-0.5 rounded-md text-sm mx-1 cursor-default align-middle group">
				<span class="truncate max-w-[150px] inline-block" title="${selectionData.text.replace(/"/g, '&quot;')}">"${selectionData.text}"</span>
				<span class="text-yellow-500/50 hover:text-red-400 cursor-pointer p-0.5 ml-1" onclick="this.parentElement.remove()">
					<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
				</span>
			</span>&#8203;`;

			// Insertarlo en el contentEditable al final o en el cursor actual
			inputRef.current.focus();
			document.execCommand('insertHTML', false, badgeHtml);

			// Forzar actualización del state aunque sea contentEditable
			setInput(inputRef.current.innerHTML);

			setSelectionData(null);
			window.getSelection().removeAllRanges();
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
		// Extract raw text and quotes for the backend
		let finalContent = "";
		if (inputRef.current) {
			// Parsea el interior del contentEditable para convertir spans a formato texto
			const tempDiv = document.createElement('div');
			tempDiv.innerHTML = inputRef.current.innerHTML;

			// Extraer cada nodo y montar el string final
			Array.from(tempDiv.childNodes).forEach(node => {
				if (node.nodeType === Node.TEXT_NODE) {
					finalContent += node.textContent;
				} else if (node.nodeType === Node.ELEMENT_NODE) {
					if (node.tagName === 'SPAN' && node.classList.contains('inline-flex')) {
						// Es un badge
						const quoteText = node.querySelector('.truncate')?.textContent || node.textContent;
						finalContent += `\n> ${quoteText}\n`;
					} else if (node.tagName === 'DIV' || node.tagName === 'BR') {
						finalContent += '\n' + node.textContent;
					} else {
						finalContent += node.textContent;
					}
				}
			});
		}

		finalContent = finalContent.trim().replace(/\u200B/g, ''); // Fix zero-width chars

		if (!finalContent && !input.trim() || isLoading) return;

		const userMessage = { role: 'user', content: finalContent };
		setMessages(prev => [...prev, userMessage]);

		setInput('');
		if (inputRef.current) inputRef.current.innerHTML = '';
		setSelectionData(null);
		setIsLoading(true);

		try {
			const payload = {
				message: finalContent,
				history_id: currentChatId
			};
			const response = await axios.post('http://localhost:8000/api/chat', payload);

			const assistantMessage = { role: 'assistant', content: response.data.response };
			setMessages(prev => [...prev, assistantMessage]);

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
			setMessages(prev => [...prev, {
				role: 'system',
				content: `*Archivo subido exitosamente: [${file.name}](http://localhost:8000/${res.data.path.replace(/\\/g, '/')})*`
			}]);
		} catch (error) {
			console.error("Error uploading", error);
		} finally {
			setUploading(false);
			if (fileInputRef.current) fileInputRef.current.value = '';
		}
	};

	return (
		<div className="flex flex-col h-screen w-full bg-zinc-900 transition-all relative">
			{/* Floating Action Button for Selection */}
			{selectionData && (
				<button
					onMouseDown={(e) => e.preventDefault()}
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
				className="flex-1 overflow-y-auto p-4 md:px-20 lg:px-40 xl:px-60 scrollbar-thin relative pb-32"
			>
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

			{/* Input Area Editable */}
			<div className="absolute bottom-0 w-full p-4 md:px-20 lg:px-40 xl:px-60 bg-gradient-to-t from-zinc-950 via-zinc-900 to-transparent">
				<form onSubmit={handleSend} className="relative flex flex-col gap-2 bg-zinc-800 border-[1px] border-zinc-700/50 rounded-2xl p-2 transition-shadow focus-within:ring-2 focus-within:ring-[#f4ba3e]/50 focus-within:bg-zinc-800/80 shadow-lg">
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

						<div className="relative w-full flex items-center min-h-[44px] cursor-text bg-transparent">
							{!input && (
								<div className="absolute left-0 text-zinc-500 pointer-events-none px-1">
									Pregunta a LM-Studio...
								</div>
							)}
							<div
								ref={inputRef}
								contentEditable
								onInput={(e) => setInput(e.currentTarget.innerHTML)}
								onKeyDown={(e) => {
									if (e.key === 'Enter' && !e.shiftKey) {
										e.preventDefault();
										handleSend();
									}
								}}
								className="w-full max-h-48 bg-transparent text-zinc-100 outline-none py-3 scrollbar-thin overflow-y-auto z-10 break-words empty:before:content-none whitespace-pre-wrap px-1"
								suppressContentEditableWarning={true}
							/>
						</div>

						<button
							type="submit"
							disabled={!input.trim() || Boolean(isLoading)}
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
