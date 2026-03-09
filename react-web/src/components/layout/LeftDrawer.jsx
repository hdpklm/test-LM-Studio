import React from 'react';
import { useChat } from '../../context/ChatContext';
import { MessageSquare, FolderClock, Menu, Zap, Bot, Workflow, Clock } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';

const LeftDrawer = () => {
	const { leftDrawerOpen, toggleLeftDrawer, historyList, setCurrentChatId, currentChatId, chatMode, setChatMode } = useChat();
	const navigate = useNavigate();
	const location = useLocation();

	const handleModeSelect = (mode) => {
		setChatMode(mode);
		setCurrentChatId(null);
		navigate('/');
	};

	return (
		<div
			className={`h-full bg-zinc-950/80 backdrop-blur-md border-r border-zinc-800 transition-all duration-300 flex flex-col shrink-0 ${leftDrawerOpen ? 'w-64 translate-x-0' : 'w-0 -translate-x-full opacity-0 overflow-hidden border-r-0'
				}`}
		>
			<div className="p-3 border-b border-zinc-800/50 space-y-1">
				<div className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider mb-2 px-2">Agentes</div>

				<button
					onClick={() => navigate('/ayudante')}
					className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors text-left ${location.pathname === '/ayudante' ? 'bg-zinc-800 text-[#f4ba3e] font-medium' : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200'
						}`}
				>
					<Clock className="w-4 h-4 shrink-0" />
					<span>Ayudante</span>
				</button>

				<button
					onClick={() => handleModeSelect('free')}
					className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors text-left ${location.pathname !== '/ayudante' && chatMode === 'free' ? 'bg-zinc-800 text-[#f4ba3e] font-medium' : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200'
						}`}
				>
					<Zap className="w-4 h-4 shrink-0" />
					<span>Free Chat</span>
				</button>

				<button
					onClick={() => handleModeSelect('syspro')}
					className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors text-left ${location.pathname !== '/ayudante' && chatMode === 'syspro' ? 'bg-zinc-800 text-[#f4ba3e] font-medium' : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200'
						}`}
				>
					<Bot className="w-4 h-4 shrink-0" />
					<span>SysPro-Gen</span>
				</button>

				<button
					onClick={() => handleModeSelect('longloop')}
					className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors text-left ${location.pathname !== '/ayudante' && chatMode === 'longloop' ? 'bg-zinc-800 text-[#f4ba3e] font-medium' : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200'
						}`}
				>
					<Workflow className="w-4 h-4 shrink-0" />
					<span>LongLoop-Agent</span>
				</button>
			</div>

			<div className="p-4 flex items-center justify-between border-b border-zinc-800/50">
				<div className="flex items-center gap-2 text-zinc-100 font-semibold font-mono">
					<FolderClock className="w-5 h-5 text-[#f4ba3e]" />
					<span>Historial</span>
				</div>
			</div>

			<div className="flex-1 overflow-y-auto p-2 scrollbar-thin space-y-1">
				{historyList.length === 0 ? (
					<div className="text-zinc-500 text-sm p-4 text-center italic">No hay conversaciones previas</div>
				) : (
					historyList.map((item) => (
						<button
							key={item.id}
							onClick={() => setCurrentChatId(item.id)}
							className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors text-left ${currentChatId === item.id
								? 'bg-zinc-800 text-zinc-100'
								: 'text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200'
								}`}
						>
							<MessageSquare className="w-4 h-4 shrink-0" />
							<span className="truncate">{item.name}</span>
						</button>
					))
				)}
			</div>

			<div className="p-4 border-t border-zinc-800/50">
				<button
					onClick={() => setCurrentChatId(null)}
					className="w-full py-2 px-4 rounded-lg bg-[#f4ba3e] hover:bg-[#dca331] text-zinc-950 font-bold transition-colors shadow-[0_0_15px_rgba(244,186,62,0.3)] text-sm"
				>
					Nuevo Chat
				</button>
			</div>
		</div>
	);
};

export default LeftDrawer;
