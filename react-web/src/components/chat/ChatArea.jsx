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
	const [activeQuotes, setActiveQuotes] = useState([]);
	const [highlightRects, setHighlightRects] = useState([]);
	const fileInputRef = useRef(null);
	const messagesEndRef = useRef(null);
	const chatContainerRef = useRef(null);

	const scrollToBottom = () => {
		messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
	};

	useEffect(() => {
		const handleMouseUp = () => {
			let text = '';
			let rect = null;
			let range = null;
			let msgIndex = null;

			// Handle input/textarea selection (like LiveEditor inside React Live)
			const activeEl = document.activeElement;
			if (activeEl && (activeEl.tagName === 'TEXTAREA' || activeEl.tagName === 'INPUT')) {
				if (activeEl.selectionStart !== activeEl.selectionEnd) {
					text = activeEl.value.substring(activeEl.selectionStart, activeEl.selectionEnd);
					// Fallback rect for textareas (center top of the element roughly)
					const elRect = activeEl.getBoundingClientRect();
					rect = {
						bottom: elRect.top + 20,
						left: elRect.left + (elRect.width / 2),
						width: 0
					};
					// Fake range obj to bypass range clone needs later
					range = 'textarea_fake_range';

					const containerNode = activeEl.closest('[data-message-index]');
					if (containerNode) msgIndex = parseInt(containerNode.getAttribute('data-message-index'));
				}
			} else {
				// Regular document selection
				const selection = window.getSelection();
				if (selection && !selection.isCollapsed && selection.toString().trim()) {
					text = selection.toString();
					try {
						range = selection.getRangeAt(0);
						// Usa commonAncestorContainer para revisar si está en el chat container
						if (chatContainerRef.current && chatContainerRef.current.contains(range.commonAncestorContainer)) {
							rect = range.getBoundingClientRect();
							const containerNode = range.commonAncestorContainer.nodeType === 3 ? range.commonAncestorContainer.parentNode.closest('[data-message-index]') : range.commonAncestorContainer.closest('[data-message-index]');
							if (containerNode) msgIndex = parseInt(containerNode.getAttribute('data-message-index'));
						} else {
							text = ''; // No pertenece al chat
						}
					} catch (e) {
						text = '';
					}
				}
			}

			if (!text.trim()) {
				setSelectionData(null);
				return;
			}

			if (rect) {
				setSelectionData({
					text: text,
					top: rect.bottom + 10,
					left: rect.left + (rect.width / 2) - 16,
					range: range,
					msgIndex: msgIndex
				});
			} else {
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
			if (selectionData && !e.target.closest('button')) {
				// Prevent default clearing if it's clicking on our custom action button
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
	const quoteCounter = useRef(1);
	const savedRangeRef = useRef(null);

	const saveSelection = () => {
		const selection = window.getSelection();
		if (selection.rangeCount > 0 && inputRef.current?.contains(selection.anchorNode)) {
			savedRangeRef.current = selection.getRangeAt(0).cloneRange();
		}
	};

	const handleAddToInput = () => {
		if (selectionData?.text && inputRef.current) {
			const currentCount = quoteCounter.current++;
			const quoteId = `quote-${currentCount}`;

			let start = -1;
			let stop = -1;
			if (selectionData.msgIndex !== null && messages[selectionData.msgIndex]) {
				const rawText = messages[selectionData.msgIndex].content;
				start = rawText.indexOf(selectionData.text);
				if (start !== -1) {
					stop = start + selectionData.text.length;
				}
			}

			// Guardar referencia activa local
			const newQuote = {
				id: quoteId,
				range: selectionData.range !== 'textarea_fake_range' ? selectionData.range.cloneRange() : 'textarea_fake_range',
				msgIndex: selectionData.msgIndex,
				isBlinking: false
			};
			setActiveQuotes(prev => [...prev, newQuote]);

			const payload = `selected(${selectionData.msgIndex !== null ? selectionData.msgIndex : 'unknown'}, ${start}, ${stop})`;

			// Crear el nodo HTML del badge (pequeño, 1 línea, sin mostrar el texto adentro)
			const badgeHtml = `<span contenteditable="false" data-quote-id="${quoteId}" data-quote-payload="${payload}" data-quote-text="${selectionData.text.replace(/"/g, '&quot;')}" onclick="window.dispatchEvent(new CustomEvent('blink-quote', {detail: '${quoteId}'}))" class="inline-flex items-center justify-center gap-1 bg-yellow-500/20 border border-yellow-500/50 hover:bg-yellow-500/40 transition-colors text-yellow-500 px-1.5 rounded text-[11px] font-mono h-[18px] leading-none mx-1 cursor-pointer align-baseline select-none">
					<span>sel-${currentCount}</span>
					<span class="hover:text-red-400 cursor-pointer p-0.5 ml-0.5 flex items-center justify-center" onclick="event.stopPropagation(); this.parentElement.remove(); window.dispatchEvent(new Event('input'))">
						<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
					</span>
				</span>&#8203;`;

			// Restore selection if exists and belongs to the input
			inputRef.current.focus();
			if (savedRangeRef.current) {
				const selection = window.getSelection();
				selection.removeAllRanges();
				selection.addRange(savedRangeRef.current);
			}

			// Insertarlo en el contentEditable al final o en el cursor actual
			document.execCommand('insertHTML', false, badgeHtml);

			// Update the saved range to be exactly after insertion
			saveSelection();

			// Forzar actualización del state aunque sea contentEditable
			setInput(inputRef.current.innerHTML);

			setSelectionData(null);
			if (window.getSelection) {
				window.getSelection().removeAllRanges();
			}
		}
	};

	useEffect(() => {
		scrollToBottom();
	}, [messages]);

	// Highlight Rectangles engine
	useEffect(() => {
		const updateRects = () => {
			if (!chatContainerRef.current) return;
			const containerRect = chatContainerRef.current.getBoundingClientRect();
			const newRects = [];
			activeQuotes.forEach(quote => {
				if (quote.range === 'textarea_fake_range') {
					// Fallback highlight for Code Blocks (LiveEditor Textareas)
					const msgEl = chatContainerRef.current.querySelector(`[data-message-index="${quote.msgIndex}"]`);
					if (msgEl) {
						const r = msgEl.getBoundingClientRect();
						newRects.push({
							id: quote.id,
							isBlinking: quote.isBlinking,
							top: r.top - containerRect.top + chatContainerRef.current.scrollTop,
							left: r.left - containerRect.left,
							width: r.width,
							height: r.height,
							isFallback: true
						});
					}
				} else {
					try {
						const rects = Array.from(quote.range.getClientRects() || []);
						rects.forEach(r => {
							if (r.width > 0 && r.height > 0) {
								newRects.push({
									id: quote.id,
									isBlinking: quote.isBlinking,
									top: r.top - containerRect.top + chatContainerRef.current.scrollTop,
									left: r.left - containerRect.left,
									width: r.width,
									height: r.height,
									isFallback: false
								});
							}
						});
					} catch (e) {
						// disconnected range or invalid
					}
				}
			});
			setHighlightRects(newRects);
		};

		updateRects();
		const container = chatContainerRef.current;
		if (container) {
			container.addEventListener('scroll', updateRects);
			window.addEventListener('resize', updateRects);
		}
		return () => {
			if (container) container.removeEventListener('scroll', updateRects);
			window.removeEventListener('resize', updateRects);
		}
	}, [activeQuotes]);

	// Evento de blink
	useEffect(() => {
		const blinkHandler = (e) => {
			const id = e.detail;
			setActiveQuotes(prev => prev.map(q => q.id === id ? { ...q, isBlinking: true } : q));
			setTimeout(() => {
				setActiveQuotes(prev => prev.map(q => q.id === id ? { ...q, isBlinking: false } : q));
			}, 800);
		};
		window.addEventListener('blink-quote', blinkHandler);
		return () => window.removeEventListener('blink-quote', blinkHandler);
	}, []);

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
						// Es un badge, extraemos el payload con el ID y las coordenadas start/stop
						const quoteText = node.getAttribute('data-quote-text') || node.textContent;
						const quotePayload = node.getAttribute('data-quote-payload') || 'selected(unknown)';
						finalContent += `\n> ${quotePayload} "${quoteText}"\n`;
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
		setActiveQuotes([]); // Clear highlights
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
					onMouseDown={(e) => {
						e.preventDefault();
						e.stopPropagation();
					}}
					onMouseUp={(e) => {
						e.preventDefault();
						e.stopPropagation();
					}}
					onClick={(e) => {
						e.preventDefault();
						e.stopPropagation();
						handleAddToInput();
					}}
					style={{
						position: 'fixed',
						top: selectionData.top,
						left: selectionData.left,
						zIndex: 50
					}}
					className="bg-[#f4ba3e] text-zinc-900 p-2 rounded-full shadow-lg hover:bg-[#dca331] transition-all animate-in fade-in zoom-in duration-200 hover:scale-110"
					title="Citar en el chat"
					type="button"
				>
					<MessageSquarePlus className="w-4 h-4 pointer-events-none" />
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
				{/* Background Highlights for Active Quotes */}
				{highlightRects.map((r, i) => (
					<div
						key={i}
						className={`absolute pointer-events-none transition-all duration-300 ${r.isFallback ? (r.isBlinking ? 'bg-yellow-400/20 border-l-4 border-yellow-400 animate-pulse' : 'bg-yellow-500/5 border-l-4 border-yellow-500/50') : (r.isBlinking ? 'bg-yellow-400/80 saturate-200 mix-blend-screen animate-pulse' : 'bg-yellow-500/30 mix-blend-screen')}`}
						style={{ top: r.top, left: r.left, width: r.width, height: r.height, zIndex: 0 }}
					/>
				))}

				{messages.length === 0 ? (
					<div className="h-full flex flex-col items-center justify-center text-zinc-500 gap-4 relative z-10">
						<div className="w-16 h-16 rounded-2xl bg-[#f4ba3e]/10 flex items-center justify-center">
							<Menu className="w-8 h-8 text-[#f4ba3e]" />
						</div>
						<p>¿En qué puedo ayudarte hoy?</p>
					</div>
				) : (
					messages.map((msg, index) => (
						<MessageBubble key={index} message={msg} msgIndex={index} />
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
								onInput={(e) => {
									setInput(e.currentTarget.innerHTML);
									saveSelection();
									// Sync active badges deletions
									if (inputRef.current) {
										const presentIds = Array.from(inputRef.current.querySelectorAll('[data-quote-id]')).map(n => n.getAttribute('data-quote-id'));
										setActiveQuotes(prev => prev.filter(q => presentIds.includes(q.id)));
									}
								}}
								onKeyUp={saveSelection}
								onMouseUp={saveSelection}
								onBlur={saveSelection}
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
