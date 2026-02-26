import React from 'react';
import { useChat } from '../../context/ChatContext';
import { MessageSquare, FolderClock, Menu } from 'lucide-react';

const LeftDrawer = () => {
	const { leftDrawerOpen, toggleLeftDrawer, historyList, setCurrentChatId, currentChatId } = useChat();

	return (
		<div
			className={`fixed top-0 left-0 h-full bg-zinc-950/80 backdrop-blur-md border-r border-zinc-800 transition-transform duration-300 z-40 flex flex-col ${leftDrawerOpen ? 'translate-x-0 w-64' : '-translate-x-full w-64'
				}`}
		>
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
