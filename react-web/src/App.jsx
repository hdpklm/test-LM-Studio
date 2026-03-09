import React from 'react';
import { HashRouter, Routes, Route } from 'react-router-dom';
import { ChatProvider } from './context/ChatContext';
import LeftDrawer from './components/layout/LeftDrawer';
import RightDrawer from './components/layout/RightDrawer';
import ChatArea from './components/chat/ChatArea';
import AyudanteChat from './components/chat/AyudanteChat';

const App = () => {
	return (
		<HashRouter>
			<ChatProvider>
				<div className="flex h-screen overflow-hidden bg-zinc-900 font-sans">
					<LeftDrawer />
					<main className="flex-1 w-full min-w-0 transition-all duration-300 relative z-0">
						<Routes>
							<Route path="/" element={<ChatArea />} />
							<Route path="/ayudante" element={<AyudanteChat />} />
						</Routes>
					</main>
					<RightDrawer />
				</div>
			</ChatProvider>
		</HashRouter>
	);
};

export default App;
